"""刷题中心与修为系统的引擎。

这个模块负责四件事，彼此之间只通过纯数据交换：

1. **题库**：加载 `data/question_bank.json`，按章节 / 赛道 / 难度索引，
   并在下发给前端时按模式裁剪（实战模式下不能带答案）。
2. **判题**：把用户的多个代码块（Jupyter 那种分块）在一个子进程里依次执行，
   每块单独收集输出与报错，最后再跑题目自带的断言。
3. **积分与修为**：所有加分都走 `award()`，带防重复账本和重复练习衰减，
   等级曲线集中在 `LEVELS` 里，改一处即可整体调平衡。
4. **存储**：每个用户一份 `data/training/<user>.json`，
   原子写入 + 进程内锁，避免边刷题边写坏文件。

放在单独模块的原因很直接：app.py 已经 140KB，把积分数学与判题沙箱再塞进去
会彻底没法维护；而这两块恰好也是最需要单独跑测试的部分。
"""

import json
import os
import re
import subprocess

try:
    import demo_mode
except ImportError:
    demo_mode = None

try:
    import sandbox_guard
except ImportError:      # 单独跑引擎（如自测脚本）时也不该崩
    sandbox_guard = None
import sys
import tempfile
import threading
import time
from datetime import datetime

# ── 路径 ────────────────────────────────────────────────
# 由 app.py 在启动时写成实际可写目录，默认值用于独立跑测试。
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, 'data')
BANK_FILE = os.path.join(DATA_DIR, 'question_bank.json')
STATE_DIR = os.path.join(DATA_DIR, 'training')


def configure(root, data_dir=None):
    """app.py 启动时调用，把读写位置切到 PyInstaller 约定的可写目录。"""
    global ROOT, DATA_DIR, BANK_FILE, STATE_DIR
    ROOT = str(root)
    DATA_DIR = str(data_dir) if data_dir else os.path.join(ROOT, 'data')
    BANK_FILE = os.path.join(DATA_DIR, 'question_bank.json')
    STATE_DIR = os.path.join(DATA_DIR, 'training')
    os.makedirs(STATE_DIR, exist_ok=True)


# ── 积分规则 ────────────────────────────────────────────
# 设计取舍：一道题的价值要能和「看完一节图文讲解」「完成一个知识点」放在
# 同一把尺子上比较。刷题最难、最花时间，所以单题分值最高（12–30 基础分），
# 但一次只看讲解也有分，保证刚入门的人不至于卡在凡人期动不了。
# 难度基础分。三档之间刻意拉开差距（简单→较难 7 倍）：
# 解出一道较难的算法题，收益抵得上 7 道简单题，这样「啃难题」才有明显回报。
QUESTION_BASE = {1: 10, 2: 28, 3: 70}
STAR_MULT = {0: 0.0, 1: 1.0, 2: 1.4, 3: 1.8}  # 星级越高，掌握度评分越高
FIRST_CLEAR_BONUS = 1.5                     # 首次通关额外奖励
REPEAT_DECAY = [1.0, 0.3, 0.12, 0.05]       # 第 1/2/3/4+ 次通关的衰减系数
KP_POINTS = 12                              # 完成一个知识点
CHAPTER_POINTS = 60                         # 一章全部知识点完成
NARRATION_POINTS = 8                        # 看完一节 5 分钟图文讲解
COMIC_POINTS = 50                           # 看完一章漫画
EXAM_FINISH_BASE = 20                       # 完成一次实战组卷
EXAM_FINISH_PER_Q = 5

# 一次加分不超过这个值，防止某处算错把曲线冲垮
MAX_AWARD = 200

# ── 修为等级（10 大境界 × 3 小境界 = 30 级）──────────────
# 阈值曲线：T(n) = 40 + 28 * n^1.82，取 5 的整数倍。
# 校验：全量内容约 1.9 万分，满级门槛约 1.37 万——认真刷完全站可以封顶，
# 只完成一半（约 9500 分）落在「大乘」附近，既不速通也不至于看不到头。
REALMS = [
    ('炼气期', ['初期', '中期', '后期']),
    ('筑基期', ['初期', '中期', '后期']),
    ('金丹期', ['初期', '中期', '后期']),
    ('元婴期', ['初期', '中期', '后期']),
    ('化神期', ['初期', '中期', '后期']),
    ('炼虚期', ['初期', '中期', '后期']),
    ('合体期', ['初期', '中期', '后期']),
    ('大乘期', ['初期', '中期', '后期']),
    ('渡劫期', ['初期', '中期', '后期']),
    ('仙人境', ['散仙', '真仙', '金仙']),
]
MAX_LEVEL = sum(len(stages) for _, stages in REALMS)


# 等级门槛表（累计积分）。30 级，前松后紧：
#   · 1 级 25 分 ≈ 一道简单题满星首通（27 分）——**做完第一道题就能看到升级**；
#   · 5 级 330 分 ≈ 四五道中等题，新手一晚上的进度；
#   · 10 级 1510 分，15 级 4130 分，20 级 8810 分——每级所需分数快速上升；
#   · 30 级 27640 分，接近全站可产出总量（约 3 万），要「渡劫成仙」得几乎刷完。
# 每级增量从 25 一路涨到 2630，涨幅 100 倍，这就是「越往后越难升」的具体体现。
# 想调平衡只改这张表，不用动任何逻辑。
LEVEL_THRESHOLDS = [
    25, 65, 125, 210, 330, 480, 670, 900, 1180, 1510,
    1900, 2350, 2870, 3460, 4130, 4880, 5720, 6650, 7680, 8810,
    10050, 11410, 12900, 14520, 16290, 18220, 20310, 22570, 25010, 27640,
]
# 万一以后把等级扩到 30 级以上，按最后一档的增量外推，保证曲线继续单调上升
LEVEL_TAIL_STEP = 3000


def _threshold(n):
    """第 n 级所需的累计积分（n 从 1 开始）。"""
    if n <= len(LEVEL_THRESHOLDS):
        return LEVEL_THRESHOLDS[n - 1]
    extra = n - len(LEVEL_THRESHOLDS)
    return LEVEL_THRESHOLDS[-1] + extra * LEVEL_TAIL_STEP


def _build_levels():
    levels = [{'level': 0, 'name': '凡人', 'realm': '凡尘', 'stage': '', 'need': 0}]
    idx = 0
    for realm, stages in REALMS:
        for stage in stages:
            idx += 1
            levels.append({
                'level': idx,
                'name': f'{realm}·{stage}' if len(stages) > 1 else f'{realm}·{stage}',
                'realm': realm,
                'stage': stage,
                'need': _threshold(idx),
            })
    return levels


LEVELS = _build_levels()


def level_from_points(points):
    """把总积分换成等级信息（含下一级进度，供等级条直接渲染）。"""
    points = max(0, int(points or 0))
    current = LEVELS[0]
    for lv in LEVELS:
        if points >= lv['need']:
            current = lv
        else:
            break
    nxt = LEVELS[current['level'] + 1] if current['level'] < MAX_LEVEL else None
    if nxt:
        span = max(1, nxt['need'] - current['need'])
        progress = int(max(0.0, min(1.0, (points - current['need']) / span)) * 100)
    else:
        progress = 100
    return {
        'points': points,
        'level': current['level'],
        'name': current['name'],
        'realm': current['realm'],
        'stage': current['stage'],
        'max_level': MAX_LEVEL,
        'is_max': nxt is None,
        'floor': current['need'],
        'next_need': nxt['need'] if nxt else current['need'],
        'next_name': nxt['name'] if nxt else current['name'],
        'to_next': max(0, nxt['need'] - points) if nxt else 0,
        'progress': progress,
        # 每 3 级是一个大境界，阶梯只列大境界的**起点**（炼气期·初期、筑基期·初期…），
        # 既避免 30 个标签糊满屏，也比列「后期」更像一条境界线
        'levels': [{'level': lv['level'], 'name': lv['name'], 'need': lv['need']}
                   for lv in LEVELS[1::3]],
    }


# ── 存储 ────────────────────────────────────────────────
_state_lock = threading.RLock()


def _safe_user(username):
    name = re.sub(r'[^0-9A-Za-z_.@\-\u4e00-\u9fff]', '_', str(username or 'guest'))
    return name[:60] or 'guest'


def state_path(username):
    os.makedirs(STATE_DIR, exist_ok=True)
    return os.path.join(STATE_DIR, _safe_user(username) + '.json')


def _empty_state():
    return {
        'points': 0,
        'rewards': {},        # 防重复账本：key -> 已发积分
        'log': [],            # 最近的加分流水
        'attempts': {},       # 题目 id -> 作答档案
        'drafts': {},         # 题目 id -> 代码块列表
        'exams': [],          # 组卷记录
        'active_exam': '',
    }


def load_state(username):
    # 评审演示账号：状态只存内存，读文件会读到空，所以先问演示模块要
    if demo_mode is not None and demo_mode.is_demo(username):
        return demo_mode.get_training_state()
    path = state_path(username)
    if not os.path.exists(path):
        return _empty_state()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return _empty_state()
    state = _empty_state()
    state.update(data if isinstance(data, dict) else {})
    return state


def save_state(username, state):
    """先写临时文件再原子替换：刷题时会有大量并发写入，
    直接覆写目标文件出现过读到半截 JSON 的情况。"""
    # 演示账号不落盘：评审怎么点都不会污染真实数据，重启即还原
    if demo_mode is not None and demo_mode.is_demo(username):
        demo_mode.set_training_state(state)
        return
    path = state_path(username)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def mutate_state(username, fn):
    """带锁的读-改-写。fn(state) 返回值会写回，异常时保持原样。"""
    with _state_lock:
        state = load_state(username)
        result = fn(state)
        if result is False:
            return state
        save_state(username, state)
        return state


# ── 积分发放 ────────────────────────────────────────────
def award(state, reason, ref, amount, note=''):
    """发积分。同一 (reason, ref) 只发一次，重复调用返回 0。

    返回 (awarded, level_before, level_after)，调用方据此判断是否升级。
    """
    key = f'{reason}:{ref}'
    amount = int(round(max(0, min(MAX_AWARD, amount))))
    before = level_from_points(state.get('points', 0))
    if amount <= 0 or key in (state.get('rewards') or {}):
        return 0, before, before
    state['points'] = int(state.get('points', 0)) + amount
    state.setdefault('rewards', {})[key] = amount
    log = state.setdefault('log', [])
    log.append({
        'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reason': reason, 'ref': ref, 'delta': amount, 'note': note,
    })
    # 流水只留最近 200 条，避免文件无限膨胀
    if len(log) > 200:
        del log[:-200]
    after = level_from_points(state['points'])
    return amount, before, after


def question_points(difficulty, stars, clear_count):
    """单题积分 = 难度基础分 × 星级系数 × 首次奖励 × 重复衰减。"""
    base = QUESTION_BASE.get(int(difficulty or 1), QUESTION_BASE[1])
    mult = STAR_MULT.get(int(stars or 0), 0.0)
    if mult <= 0:
        return 0
    repeat_index = max(0, int(clear_count or 0))  # 0 = 首次通关
    decay = REPEAT_DECAY[min(repeat_index, len(REPEAT_DECAY) - 1)]
    bonus = FIRST_CLEAR_BONUS if repeat_index == 0 else 1.0
    return int(round(base * mult * bonus * decay))


def stars_for(runs, errored_runs, used_ai, skipped=False):
    """星级评分。

    3 星：基本一遍过（报错 ≤ 1 次）且没求助 AI —— 真正独立掌握；
    2 星：报错不多，或借助了 AI 提示后自己写通；
    1 星：反复报错后才通过 / 直接看了 AI 解答 / 跳过后补做。
    """
    if skipped:
        return 1
    if used_ai:
        return 2 if errored_runs <= 3 else 1
    if errored_runs <= 1:
        return 3
    if errored_runs <= 3:
        return 2
    return 1


# ── 题库 ────────────────────────────────────────────────
_bank_cache = {'mtime': None, 'items': [], 'index': {}}


def load_bank(force=False):
    if not os.path.exists(BANK_FILE):
        return []
    mtime = os.path.getmtime(BANK_FILE)
    if force or _bank_cache['mtime'] != mtime:
        with open(BANK_FILE, 'r', encoding='utf-8') as f:
            items = json.load(f)
        _bank_cache['items'] = items
        _bank_cache['index'] = {q['id']: q for q in items}
        _bank_cache['mtime'] = mtime
    return _bank_cache['items']


def bank_index():
    load_bank()
    return _bank_cache['index']


def public_question(q, state=None, reveal=False):
    """下发给前端的题目。实战模式未结束时必须不带答案与断言。"""
    if not q:
        return None
    record = ((state or {}).get('attempts') or {}).get(q['id'], {})
    item = {
        'id': q['id'],
        'title': q['title'],
        'track': q.get('track', 'course'),
        'chapter_id': q.get('chapter_id'),
        'chapter_title': q.get('chapter_title', ''),
        'topic': q.get('topic', ''),
        'difficulty': q.get('difficulty', 1),
        'difficulty_label': {1: '简单', 2: '中等', 3: '较难'}.get(q.get('difficulty', 1), '简单'),
        'tags': q.get('tags', []),
        'statement': q.get('statement', ''),
        'starter_code': q.get('starter_code', ''),
        'hints': q.get('hints', []),
        'expected_output': q.get('expected_output', ''),
        'needs_input': bool(q.get('stdin')),
        'attempts': record.get('attempts', 0),
        'runs': record.get('runs', 0),
        'solved': bool(record.get('solved')),
        'stars': record.get('best_stars', 0),
        'wrong': record.get('wrong', 0),
        'last_error': record.get('last_error', ''),
    }
    if reveal:
        item['solution'] = q.get('solution', '')
        item['explanation'] = q.get('explanation', '')
        item['checks'] = q.get('checks', [])
        item['stdin'] = q.get('stdin', '')
    return item


def question_brief(q, state=None):
    """列表用：不带宽字段。"""
    record = ((state or {}).get('attempts') or {}).get(q['id'], {})
    return {
        'id': q['id'],
        'title': q['title'],
        'track': q.get('track', 'course'),
        'chapter_id': q.get('chapter_id'),
        'topic': q.get('topic', ''),
        'difficulty': q.get('difficulty', 1),
        'tags': q.get('tags', []),
        'solved': bool(record.get('solved')),
        'stars': record.get('best_stars', 0),
        'wrong': record.get('wrong', 0),
    }


def filter_questions(chapters=None, track=None, difficulty=None, topic=None,
                     keyword=None, only=None, state=None, limit=None):
    items = load_bank()
    out = []
    for q in items:
        if chapters and str(q.get('chapter_id')) not in {str(c) for c in chapters}:
            continue
        if track and q.get('track', 'course') != track:
            continue
        if difficulty and int(q.get('difficulty', 1)) != int(difficulty):
            continue
        if topic and q.get('topic') != topic:
            continue
        if keyword:
            blob = (q['title'] + ' ' + q.get('statement', '') + ' '.join(q.get('tags', [])))
            if keyword.lower() not in blob.lower():
                continue
        if only == 'unsolved' and ((state or {}).get('attempts') or {}).get(q['id'], {}).get('solved'):
            continue
        if only == 'solved' and not ((state or {}).get('attempts') or {}).get(q['id'], {}).get('solved'):
            continue
        if only == 'wrong' and not ((state or {}).get('attempts') or {}).get(q['id'], {}).get('wrong'):
            continue
        out.append(q)
    if limit:
        out = out[:int(limit)]
    return out


def bank_chapters(courses=None):
    """题库里的章节清单（课程章节 + 算法专题），带题量与用户进度。"""
    items = load_bank()
    counts, groups = {}, {}
    for q in items:
        cid = q.get('chapter_id')
        counts[cid] = counts.get(cid, 0) + 1
        groups.setdefault(cid, {
            'id': cid,
            'title': q.get('chapter_title', f'第 {cid} 章'),
            'track': q.get('track', 'course'),
            'topic': q.get('topic', ''),
        })
    order = []
    if courses:
        for c in courses:
            if c['id'] in groups:
                info = groups[c['id']]
                info['title'] = c['title']
                info['icon'] = c.get('icon', '')
                info['stage'] = c.get('stage', '')
                order.append(info)
        for cid, info in groups.items():
            if not any(o['id'] == cid for o in order):
                order.append(info)
    else:
        order = sorted(groups.values(), key=lambda g: g['id'])
    for info in order:
        info['count'] = counts.get(info['id'], 0)
    return order


# ── 判题沙箱 ────────────────────────────────────────────
HARNESS = r'''
import json, sys, io, os, traceback, contextlib

# 资源上限由 sandbox_guard.guarded_command() 在启动这个子进程时就套好了
# （Linux 用 resource，Windows 用 Job Object），所以这里不再重复设置 ——
# 早先那段代码写在 HARNESS 里，只对 Linux 生效，线上那台 Windows 上等于没设，
# 一句 bytearray(3*10**9) 就能把 2GB 的机器吃满。

payload = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
cells = payload.get('cells') or []
out_path = sys.argv[2]
fig_dir = sys.argv[3]

results = []
globs = {'__name__': '__main__'}

def clean_tb(exc):
    """只保留用户代码块里的帧，行号天然对应代码块内的真实行号。"""
    frames = traceback.extract_tb(exc.__traceback__)
    user = [f for f in frames if str(f.filename).startswith('<cell')]
    if not user:
        user = frames[-1:]
    lines = []
    for f in user:
        loc = os.path.basename(f.filename).replace('<cell ', 'Cell ').replace('>', '')
        lines.append('%s, 第 %d 行：%s' % (loc, f.lineno, (f.line or '').strip()))
    lines.append('%s: %s' % (type(exc).__name__, exc))
    return '\n'.join(lines)

for index, src in enumerate(cells):
    record = {'index': index, 'stdout': '', 'error': '', 'ok': True, 'stderr': ''}
    buf = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            exec(compile(src, '<cell %d>' % (index + 1), 'exec'), globs)
    except SystemExit:
        pass
    except BaseException as exc:
        record['ok'] = False
        record['error'] = clean_tb(exc)
        record['stdout'] = buf.getvalue()
        record['stderr'] = err.getvalue()
        results.append(record)
        break
    record['stdout'] = buf.getvalue()
    record['stderr'] = err.getvalue()
    results.append(record)

# 判题断言作为最后一个「代码块」执行：先把学生所有代码块的输出与源码注入进去，
# 断言里就能用 _out（全部输出）和 _src（全部源码）来检查，不必跑第二遍。
checks = payload.get('checks') or []
if checks and all(r['ok'] for r in results):
    globs['_out'] = ''.join(r.get('stdout', '') for r in results)
    globs['_src'] = '\n'.join(cells)
    record = {'index': len(cells), 'stdout': '', 'error': '', 'ok': True, 'stderr': ''}
    buf = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            exec(compile('\n'.join(checks), '<cell %d>' % (len(cells) + 1), 'exec'), globs)
    except BaseException as exc:
        record['ok'] = False
        record['error'] = clean_tb(exc)
    record['stdout'] = buf.getvalue()
    record['stderr'] = err.getvalue()
    results.append(record)

figures = []
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for num in plt.get_fignums():
        name = 'fig_%d.png' % num
        path = os.path.join(fig_dir, name)
        plt.figure(num).savefig(path, dpi=110, bbox_inches='tight', facecolor='white')
        figures.append(path)
    plt.close('all')
except Exception:
    pass

with open(out_path, 'w', encoding='utf-8') as fh:
    json.dump({'results': results, 'figures': figures}, fh, ensure_ascii=False)
'''


def _run_python(cells, stdin_text='', timeout=20, checks=None):
    """在子进程里按顺序执行所有代码块，返回每块的输出与报错。

    checks 不为空时，会作为最后一个代码块执行，用来判定题目是否通关。
    """
    # 公网部署时（PYMASTER_SAFE_MODE=1）先过一遍静态检查：
    # 判题是拿服务器直接跑学生的代码，没有沙箱。正常教学代码碰不到被拦的那些操作。
    # 拦下来时**返回一句人话**而不是抛异常 —— 这样 app.py 里所有调用点
    # （run-cell / judge / 练习场）都自动安全，不用各自 try/except。
    if sandbox_guard is not None and sandbox_guard.is_enabled():
        for cell in cells:
            try:
                sandbox_guard.check_source(str(cell))
            except sandbox_guard.UnsafeCode as exc:
                return {'ok': False, 'error': str(exc), 'stdout': '', 'results': [],
                        'blocked': True}

    workdir = tempfile.mkdtemp(prefix='pymaster_cells_')
    try:
        payload_path = os.path.join(workdir, 'payload.json')
        out_path = os.path.join(workdir, 'out.json')
        harness_path = os.path.join(workdir, 'harness.py')
        figures_dir = os.path.join(workdir, 'figures')
        os.makedirs(figures_dir, exist_ok=True)
        with open(payload_path, 'w', encoding='utf-8') as f:
            json.dump({'cells': cells, 'checks': checks or []}, f, ensure_ascii=False)
        with open(harness_path, 'w', encoding='utf-8') as f:
            f.write(HARNESS)

        env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
               'MPLBACKEND': 'Agg'}
        # BLAS 线程数必须在这里压住：OpenBLAS 在 import 时按核数开线程并预留缓冲，
        # 不压的话"import pandas"本身就撑爆内存上限（见 sandbox_guard.BLAS_ENV）。
        if sandbox_guard is not None:
            env.update(sandbox_guard.BLAS_ENV)
        start = time.time()
        # 资源上限（CPU/内存）在这一层加：guarded_command 会用带引导的
        # 命令行启动，Linux 走 resource、Windows 走 Job Object。
        if sandbox_guard is not None and sandbox_guard.is_enabled():
            cmd = sandbox_guard.guarded_command(
                harness_path, [payload_path, out_path, figures_dir])
        else:
            cmd = [sys.executable if not getattr(sys, 'frozen', False) else 'python',
                   '-X', 'utf8', harness_path, payload_path, out_path, figures_dir]
        # 同时跑的执行数也要收着点：2 核机器上十几个并发各跑一份 pandas，
        # 结果是谁都跑不完。排队等不到就给一句人话。
        if sandbox_guard is not None and sandbox_guard.is_enabled():
            if not sandbox_guard.acquire_exec_slot(timeout=20):
                return {'ok': False, 'timeout': False, 'elapsed': 0, 'results': [],
                        'figures': [], 'error': sandbox_guard.BUSY_MESSAGE}
            slot_held = True
        else:
            slot_held = False
        try:
            try:
                proc = subprocess.run(
                    cmd,
                    input=(stdin_text or '').encode('utf-8'),
                    capture_output=True, timeout=timeout, cwd=workdir, env=env,
                )
            except subprocess.TimeoutExpired:
                return {'ok': False, 'timeout': True, 'elapsed': round(time.time() - start, 2),
                        'results': [], 'figures': [],
                        'error': f'⏱ 运行超时（{timeout} 秒）。死循环、等待输入或计算量过大都会这样。'}
        finally:
            if slot_held:
                sandbox_guard.release_exec_slot()

        elapsed = round(time.time() - start, 2)
        if not os.path.exists(out_path):
            raw = (proc.stderr or b'').decode('utf-8', errors='replace')[:800]
            return {'ok': False, 'timeout': False, 'elapsed': elapsed, 'results': [],
                    'figures': [], 'error': '运行环境异常：\n' + (raw or '进程没有产生输出')}

        with open(out_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # input() 撞到 EOF 的原文是 "EOFError: EOF when reading a line"，
        # 对刚学 input 的人等于没说：他不知道要去「测试输入」框里填数据。
        # 只在真的因为缺输入而挂的时候补一句指路，其他报错原样保留。
        for record in data.get('results', []):
            err = record.get('error') or ''
            if 'EOFError' in err or 'EOF when reading' in err:
                record['error'] = err + (
                    '\n\n这段程序在等键盘输入（用了 input），但没有数据可读。'
                    '\n把要输入的内容填到代码块上面的「测试输入」框里（每行一个值），再运行一次。')
                break

        figures = []
        for path in data.get('figures', []):
            try:
                import base64
                with open(path, 'rb') as fh:
                    figures.append('data:image/png;base64,' + base64.b64encode(fh.read()).decode())
            except OSError:
                pass

        return {'ok': True, 'timeout': False, 'elapsed': elapsed,
                'results': data.get('results', []), 'figures': figures, 'error': ''}
    finally:
        import shutil as _shutil
        _shutil.rmtree(workdir, ignore_errors=True)


def run_cells(cells, active=0, stdin_text='', timeout=20, checks=None):
    """执行到第 active 个代码块，返回该块的输出（前序块的输出会被压掉，
    因为用户关心的是「我这一块跑出什么」，不是前面块重复打印的内容）。

    `checks` 不为空时，用户代码全部跑通后会再执行一遍题目断言，并把结论放在
    `checks_run` / `checks_passed` / `check_error` 里。这样「运行」这一步就能顺带
    回答「我这次是不是已经做对了」，不必让学生再点一次提交判题。
    """
    cells = [str(c) for c in (cells or [])]
    if not cells:
        return {'ok': False, 'error': '还没有代码可以运行。', 'stdout': '', 'results': []}
    active = max(0, min(int(active), len(cells) - 1))
    ran = cells[:active + 1]
    checks = [str(c) for c in (checks or []) if str(c).strip()]
    run = _run_python(ran, stdin_text=stdin_text, timeout=timeout, checks=checks)
    if not run['ok']:
        return {'ok': False, 'error': run['error'], 'stdout': '',
                'elapsed': run.get('elapsed'), 'results': run.get('results', []),
                'timeout': run.get('timeout')}

    results = run['results']
    # 断言块是挂在用户代码块后面的，要按长度切出来，否则会被当成「最后一块代码」，
    # 把断言的空输出当成用户这次的运行结果回显出去。
    head, tail = results[:len(ran)], results[len(ran):]
    last = head[-1] if head else {'index': active, 'stdout': '', 'error': '', 'ok': True}
    has_error_earlier = any(not r['ok'] for r in head[:-1])
    stdout = last.get('stdout', '') + (('\n' + last['stderr']) if last.get('stderr', '').strip() else '')
    out = {
        'ok': last.get('ok', True) and not has_error_earlier,
        'error': last.get('error', '') or ('前面有代码块报错，先修好它再运行这一块。' if has_error_earlier else ''),
        'stdout': stdout,
        'figures': run.get('figures', []),
        'elapsed': run.get('elapsed'),
        'cell_ok': last.get('ok', True),
        'results': results,
    }
    if checks:
        check_cell = tail[0] if tail else None
        if check_cell is None:
            # 用户代码自己就报错了，断言根本没轮到执行
            out['checks_run'] = False
            out['checks_passed'] = False
        else:
            out['checks_run'] = True
            out['checks_passed'] = bool(check_cell.get('ok'))
            if not check_cell.get('ok'):
                out['check_error'] = check_cell.get('error', '')
    return out


def judge(question, cells, stdin_text='', timeout=25):
    """把用户代码块 + 题目断言拼起来跑一遍，判定是否通关。"""
    cells = [str(c) for c in (cells or []) if str(c).strip()]
    if not cells:
        return {'passed': False, 'error': '还没有写代码。', 'detail': ''}
    checks = question.get('checks') or []
    run = _run_python(cells, stdin_text=stdin_text, timeout=timeout, checks=checks)
    if not run['ok']:
        return {'passed': False, 'error': run['error'], 'detail': '',
                'timeout': run.get('timeout')}

    results = run['results']
    failed = next((r for r in results if not r['ok']), None)
    if failed:
        is_check_cell = failed['index'] >= len(cells)
        # code_ok 表示"学生自己的代码跑通了，失败发生在断言那一格"。
        # 这正是「该不该交给 AI 复核」的判据：代码根本跑不起来时复核没有意义
        # （AI 也救不了一个报错的程序），只有能跑通的代码才值得再看一眼。
        return {
            'passed': False,
            'error': failed.get('error', ''),
            'detail': '',
            'check_failed': is_check_cell,
            'code_ok': is_check_cell,
            'stdout': ''.join(r.get('stdout', '') for r in results if not is_check_cell),
        }

    student_out = ''.join(r.get('stdout', '') for r in results[:len(cells)])
    if checks:
        return {'passed': True, 'error': '', 'detail': student_out,
                'stdout': student_out, 'checks_passed': len(checks)}

    # 没有断言：看输出是否包含预期片段
    expect = (question.get('expected_output') or '').strip()
    if expect:
        got = [line.strip() for line in student_out.strip().splitlines() if line.strip()]
        wanted = [line.strip() for line in expect.splitlines() if line.strip()]
        missing = [w for w in wanted if w not in got]
        if missing:
            # 这条路上学生代码是跑通的（只是输出对不上），同样可以让 AI 复核
            return {'passed': False, 'detail': student_out, 'code_ok': True,
                    'stdout': student_out, 'check_failed': True,
                    'error': '输出和预期不一致，缺少：' + ' / '.join(missing[:3])}
    return {'passed': True, 'error': '', 'detail': student_out, 'stdout': student_out}


# ── 作答档案 ────────────────────────────────────────────
def record_attempt(state, question, cells, result, mode='practice', exam_id='', used_ai=False,
                   skipped=False, forced_stars=None):
    """把一次提交写进档案，并结算积分。

    返回一份给前端的结算单：星级、本次得分、是否升级、历史通关次数。
    """
    qid = question['id']
    attempts = state.setdefault('attempts', {})
    record = attempts.setdefault(qid, {
        'attempts': 0, 'runs': 0, 'errored_runs': 0, 'solved': False,
        'best_stars': 0, 'clears': 0, 'wrong': 0, 'ai_help': 0,
        'points': 0, 'history': [],
    })
    record['attempts'] += 1
    if not skipped:
        record['runs'] += 1
    if used_ai:
        record['ai_help'] = record.get('ai_help', 0) + 1
    if skipped:
        record['skipped'] = record.get('skipped', 0) + 1
    if not result.get('passed') and not skipped:
        record['errored_runs'] += 1
        record['wrong'] = record.get('wrong', 0) + 1
        record['last_error'] = str(result.get('error', ''))[:400]
    elif result.get('passed'):
        record['last_error'] = ''

    passed = bool(result.get('passed'))
    stars = 0
    gained = 0
    note = ''
    if skipped and not passed:
        # 跳过只记录「这题没做完」，不给星级也不给分——
        # 否则「一路跳过」就能刷分，积分体系立刻失去意义。
        stars = 0
        gained = 0
        note = '这题先跳过，弄懂之后再回来做。'
        record['last_stars'] = 0
    elif passed:
        clears_before = record.get('clears', 0)
        # forced_stars：由调用方直接指定星级。
        # 目前唯一的用途是"断言没过但 AI 复核认定逻辑等价"——那种情况下
        # 按 errored_runs 算会因为判题本身失败而多算一次错，星级被压低，
        # 所以直接钉在 2 星（复核通过的上限，低于"一遍写对"的 3 星）。
        stars = forced_stars or stars_for(record['runs'], record['errored_runs'], used_ai)
        gained = question_points(question.get('difficulty', 1), stars, clears_before)
        record['clears'] = clears_before + 1
        record['solved'] = True
        record['best_stars'] = max(record.get('best_stars', 0), stars)
        record['last_stars'] = stars
        if clears_before == 0:
            record['first_solved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if gained:
            # 账本键带上「第几次通关」：首通是 question:qid，重复练习是 question:qid#2。
            # 这样既能防重复结算，又不会把「递减后的重复奖励」一起挡掉——
            # 早期版本没加序号，导致重复练习一律 0 分，和「衰减」的设计意图不符。
            awarded, before, after = award(
                state, 'question',
                qid if clears_before == 0 else f'{qid}#{clears_before + 1}',
                gained, note=f'{question["title"]}（{stars} 星）')
            gained = awarded
            if after['level'] > before['level']:
                note = f'突破至 {after["name"]}！'
        else:
            note = '重复练习不加分，但手感是练出来的。'
        record['points'] = record.get('points', 0) + gained
        record['history'].append({
            'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stars': stars, 'points': gained, 'mode': mode,
        })
        if len(record['history']) > 30:
            del record['history'][:-30]
    record['last_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    record['last_mode'] = mode
    if exam_id:
        record['last_exam'] = exam_id

    profile = level_from_points(state.get('points', 0))
    return {
        'passed': passed,
        'stars': stars,
        'points': gained,
        'note': note,
        'clears': record.get('clears', 0),
        'best_stars': record.get('best_stars', 0),
        'profile': profile,
    }


# ── 实战组卷 ────────────────────────────────────────────
def build_exam(state, chapters, count, difficulty=None, track=None, seed=None):
    """抽题组卷。同一章节内按难度均衡抽取，保证一份卷子不会全是难题。"""
    import random
    rng = random.Random(seed)
    pool = filter_questions(chapters=chapters, track=track, difficulty=difficulty)
    if not pool:
        return None
    solved = ((state or {}).get('attempts') or {})
    # 优先没做过的题，做过但没通关的排第二，已通关的最后
    def rank(q):
        rec = solved.get(q['id'], {})
        if not rec.get('attempts'):
            return 0
        if not rec.get('solved'):
            return 1
        return 2
    rng.shuffle(pool)
    pool.sort(key=rank)
    picked = pool[:max(1, int(count))]
    rng.shuffle(picked)
    return [q['id'] for q in picked]


def exam_summary(state, exam):
    """给前端用的组卷概况（实战进行中不泄露答案）。"""
    index = bank_index()
    items = []
    for qid in exam.get('questions', []):
        q = index.get(qid)
        if not q:
            continue
        answer = (exam.get('answers') or {}).get(qid, {})
        items.append({
            'id': qid,
            'title': q['title'],
            'chapter_id': q.get('chapter_id'),
            'chapter_title': q.get('chapter_title', ''),
            'topic': q.get('topic', ''),
            'difficulty': q.get('difficulty', 1),
            'status': answer.get('status', 'todo'),
            'stars': answer.get('stars', 0),
        })
    done = sum(1 for i in items if i['status'] in ('done', 'skipped'))
    return {
        'id': exam.get('id', ''),
        'created_at': exam.get('created_at', ''),
        'status': exam.get('status', 'active'),
        'closed': exam.get('status') in ('finished', 'abandoned'),
        'chapters': exam.get('chapters', []),
        'track': exam.get('track', ''),
        'difficulty': exam.get('difficulty'),
        'count': len(items),
        'done': done,
        'items': items,
        'review': exam.get('review', ''),
        'score': exam.get('score'),
        'finished_at': exam.get('finished_at', ''),
    }


def new_exam_id():
    return 'ex' + datetime.now().strftime('%y%m%d%H%M%S') + str(int(time.time() * 1000) % 1000).zfill(3)
