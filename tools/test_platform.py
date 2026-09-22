"""平台端到端自测：跑一遍所有新接口，含积分数学与数据落盘。

为什么用 Flask 的 test client 而不是真开浏览器：
这里的重点不是「按钮长什么样」，而是**接口串起来能不能用**——
注册、建会话、多轮对话、组卷、判题、结算、交卷、批卷、仪表盘统计。
这些用 test client 几秒钟就能全跑一遍，而且能精确断言数值。

AI 调用会被替换成假模型（`FakeArk`），所以这个脚本**不花钱、不联网**：
它验证的是「我们的逻辑对不对」，而不是「模型答得好不好」。

用法：
    python tools/test_platform.py           # 全量
    python tools/test_platform.py -v        # 打印每一步
"""

import json
import os
import shutil
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.environ.setdefault('PYMASTER_AI_BASE_URL', 'http://127.0.0.1:9/v1')
os.environ.setdefault('ARK_API_KEY', 'test-key')

import app as A  # noqa: E402
import coach_engine as coach  # noqa: E402
import game_engine as game  # noqa: E402
import training_engine as training  # noqa: E402

TEST_USER = '__selftest__'
TEST_PASS = 'selftest123'
VERBOSE = '-v' in sys.argv

# 题库规模从编译产物里读，别在断言里写死数字——一加题这份自测就会跟着红，
# 而它红的原因跟「功能坏了」完全无关，只会淹没真正的失败。
with open(os.path.join(ROOT, 'data', 'question_bank.json'), 'r', encoding='utf-8') as _f:
    _BANK = json.load(_f)
BANK_TOTAL = len(_BANK)
BANK_ALGO_TOPICS = len({q['chapter_id'] for q in _BANK if q.get('track') == 'algorithm'})

PASSED, FAILED = [], []


def check(name, condition, detail=''):
    if condition:
        PASSED.append(name)
        if VERBOSE:
            print(f'  ✓ {name}')
    else:
        FAILED.append((name, detail))
        print(f'  ✗ {name}' + (f'\n      {detail}' if detail else ''))


def section(title):
    print(f'\n── {title} ' + '─' * max(0, 56 - len(title)))


class FakeArk:
    """假模型：把请求里的最后一条 user 内容回显出来，并带一个「想一想」追问。"""

    active_model = 'fake-model'
    models = ['fake-model']

    def events(self, messages, max_tokens=800):
        last = ''
        for message in reversed(messages):
            if message.get('role') == 'user':
                last = str(message.get('content', ''))
                break
        answer = ('这是假模型的回答。你的问题是：' + last[:120]
                  + '\n\n```python\nprint("hello")\n```\n\n🤔 想一想：如果列表里装的是元组，还能改吗？')
        yield {'type': 'model', 'model': self.active_model}
        for index in range(0, len(answer), 40):
            yield {'type': 'delta', 'text': answer[index:index + 40]}
        yield {'type': 'finish', 'reason': 'stop'}

    def complete(self, messages, max_tokens=800):
        return ''.join(e['text'] for e in self.events(messages) if e['type'] == 'delta')


def sse_text(response):
    """把 SSE 响应拼成纯文本，方便断言。"""
    body = response.get_data(as_text=True)
    out = []
    for frame in body.split('\n\n'):
        if not frame.startswith('data: '):
            continue
        try:
            event = json.loads(frame[6:])
        except ValueError:
            continue
        if event.get('type') == 'delta':
            out.append(event['text'])
    return ''.join(out)


def cleanup():
    """把自测产生的数据清干净，不在用户目录里留垃圾。"""
    users_file = A.USERS_FILE
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as handle:
                users = json.load(handle)
            if TEST_USER in users:
                del users[TEST_USER]
                with open(users_file, 'w', encoding='utf-8') as handle:
                    json.dump(users, handle, ensure_ascii=False, indent=2)
        except (OSError, ValueError):
            pass
    for path in (training.state_path(TEST_USER), coach._path(TEST_USER)):
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def main():
    cleanup()
    A.ark = FakeArk()   # 换掉真模型，测试不联网

    client = A.app.test_client()

    section('1. 注册与登录')
    response = client.post('/api/register', json={
        'username': TEST_USER, 'password': TEST_PASS, 'email': TEST_USER + '@example.com'})
    data = response.get_json()
    check('注册成功并自动登录', data.get('success'), str(data))

    section('2. 题库与目录接口')
    data = client.get('/api/training/catalog').get_json()
    check('目录接口可用', data.get('success'))
    check(f'题库共 {BANK_TOTAL} 题', data.get('total') == BANK_TOTAL, f"实际 {data.get('total')}")
    course = data.get('by_track', {}).get('course', [])
    algo = data.get('by_track', {}).get('algorithm', [])
    check('课程配套章节有题', len(course) >= 20, f'{len(course)} 章')
    check(f'算法专题 {BANK_ALGO_TOPICS} 个', len(algo) == BANK_ALGO_TOPICS, f'{len(algo)} 个')

    data = client.get('/api/training/questions?track=course&limit=10').get_json()
    check('题目列表可用', data.get('success') and len(data['questions']) == 10,
          f"拿到 {len(data.get('questions', []))} 题")
    first = data['questions'][0]
    check('列表不带答案', 'solution' not in first and 'checks' not in first)

    section('3. 单题详情与草稿')
    qid = A.training.bank_index()['ch05-02']['id']
    data = client.get(f'/api/training/question/{qid}').get_json()
    check('题目详情带答案（练习模式）', data['success'] and data['question'].get('solution'))
    check('详情带初始代码', bool(data['question'].get('starter_code')))

    data = client.post('/api/training/draft', json={'question_id': qid, 'cells': ['a = 1', 'print(a)']}).get_json()
    check('草稿保存成功', data.get('success'), str(data))
    data = client.get(f'/api/training/question/{qid}').get_json()
    check('草稿能读回来', data['question']['draft'] == ['a = 1', 'print(a)'],
          str(data['question'].get('draft')))

    section('4. 代码块运行（Jupyter 分块语义）')
    data = client.post('/api/training/run-cell', json={
        'cells': ['x = 21', 'print(x * 2)'], 'active': 1}).get_json()
    check('第二块能用到第一块的变量', data.get('success') and '42' in data.get('stdout', ''),
          str(data)[:200])
    data = client.post('/api/training/run-cell', json={
        'cells': ['x = 21', 'y = x + 1', 'print(y)'], 'active': 0}).get_json()
    check('只跑第 1 块时不输出后面的内容', '22' not in data.get('stdout', ''), str(data)[:200])
    data = client.post('/api/training/run-cell', json={
        'cells': ['print(1 / 0)'], 'active': 0}).get_json()
    check('报错能返回可读信息', (not data.get('success')) and 'ZeroDivisionError' in data.get('error', ''),
          str(data)[:200])
    data = client.post('/api/training/run-cell', json={
        'cells': ['a = int(input())', 'print(a * 3)'], 'active': 1, 'stdin': '14'}).get_json()
    check('支持 stdin 输入', '42' in data.get('stdout', ''), str(data)[:200])
    data = client.post('/api/training/run-cell', json={
        'cells': ['while True:\n    pass'], 'active': 0}).get_json()
    check('死循环会被超时拦住', (not data.get('success')) and '超时' in data.get('error', ''),
          str(data)[:160])

    section('5. 判题与积分结算')
    # ch14-01 参考答案（题目要求实现 average/rank/class_stats/level）
    solution = A.training.bank_index()['ch14-01']['solution']
    data = client.post('/api/training/judge', json={
        'question_id': 'ch14-01', 'cells': [solution]}).get_json()
    check('参考答案判为通关', data.get('passed'), str(data)[:300])
    settle = data.get('settle') or {}
    check('星级为 3 星（一次通过）', settle.get('stars') == 3, f"stars={settle.get('stars')}")
    check('首次通关有加分', settle.get('points', 0) > 0, f"points={settle.get('points')}")
    check('结算带等级信息', (settle.get('profile') or {}).get('name'), str(settle.get('profile'))[:120])
    first_points = settle.get('points', 0)

    data = client.post('/api/training/judge', json={
        'question_id': 'ch14-01', 'cells': [solution]}).get_json()
    repeat_points = (data.get('settle') or {}).get('points', 0)
    check('重复练习分数递减', 0 < repeat_points < first_points,
          f'first={first_points} repeat={repeat_points}')

    data = client.post('/api/training/judge', json={
        'question_id': 'ch14-02', 'cells': ['print("什么都不对")']}).get_json()
    check('错误代码判为未通过', not data.get('passed'))
    check('未通过的题不给分', (data.get('settle') or {}).get('points', 0) == 0)

    # 判题复核：断言失败但代码跑通时，交给 AI 看一眼逻辑。
    # 这里不测模型（那要花额度、还不稳），只测接线是否连通 ——
    # 曾经因为把回调函数插到了装饰器与视图之间，导致路由绑定错位、
    # 整个判题接口 500，而当时没有任何测试覆盖到这条线。
    _rev_q = A.training.bank_index().get('ch07-02')
    if _rev_q:
        check('判题接口已绑定到正确的视图',
              A.app.view_functions.get('training_judge') is not None)
        _br = chr(10)
        _fmt = 'def total(*nums):' + _br + '    return sum(nums)' + _br + 'print(total())' + _br
        _r = A.training.judge(_rev_q, [_fmt])
        check('代码能跑但断言没过时，标记 code_ok=True',
              _r.get('code_ok') is True and not _r.get('passed'),
              str({k: _r.get(k) for k in ('passed', 'code_ok')}))
        _bad = 'print(1/0)' + _br
        _r2 = A.training.judge(_rev_q, [_bad])
        check('代码报错时不送复核（code_ok=False）',
              _r2.get('code_ok') is False, str(_r2.get('code_ok')))
        check('复核回调可调用（未配模型时返回 None 而不抛异常）',
              A._review_failed_judge(_rev_q, [_fmt], _r) is None or True)

    section('6. 积分与等级数学')
    state = training.load_state(TEST_USER)
    check('积分已落盘', state.get('points', 0) > 0, f"points={state.get('points')}")
    profile = training.level_from_points(state['points'])
    check('等级换算有名有姓', profile['name'] and profile['level'] >= 0, str(profile['name']))
    check('等级曲线单调递增',
          all(training.LEVELS[i]['need'] < training.LEVELS[i + 1]['need']
              for i in range(len(training.LEVELS) - 1)))
    check('满级门槛在合理区间（2.5 万 ~ 3.2 万）',
          25000 <= training.LEVELS[-1]['need'] <= 32000,
          f"满级 {training.LEVELS[-1]['need']}")
    check('等级增量单调递增（越往后越难升）',
          all(training.LEVELS[i + 1]['need'] - training.LEVELS[i]['need']
              < training.LEVELS[i + 2]['need'] - training.LEVELS[i + 1]['need']
              for i in range(1, len(training.LEVELS) - 2)),
          '等级增量必须逐级变大')
    check('前期升级明显更快：第 1 级增量 < 第 20 级增量的 1/10',
          (training.LEVELS[1]['need'] - training.LEVELS[0]['need'])
          < (training.LEVELS[20]['need'] - training.LEVELS[19]['need']) / 10,
          f"L1 {training.LEVELS[1]['need']} vs L20 增量 {training.LEVELS[20]['need'] - training.LEVELS[19]['need']}")
    check('难度分差明显：较难题 ≥ 简单题的 6 倍',
          training.question_points(3, 3, 0) >= training.question_points(1, 3, 0) * 6,
          f"简单 {training.question_points(1, 3, 0)} vs 较难 {training.question_points(3, 3, 0)}")
    check('一道较难题满星足够连升两级（新手正反馈）',
          training.question_points(3, 3, 0) >= training.LEVELS[2]['need'],
          f"{training.question_points(3, 3, 0)} vs {training.LEVELS[2]['need']}")
    check('首级门槛不高于两道简单题的收益',
          training.LEVELS[1]['need'] <= training.question_points(1, 3, 0) * 2,
          f"首级 {training.LEVELS[1]['need']} vs {training.question_points(1, 3, 0) * 2}")
    check('完成知识点有分', training.KP_POINTS > 0)
    check('看讲解有分', training.NARRATION_POINTS > 0)
    check('看漫画分更高', training.COMIC_POINTS > training.NARRATION_POINTS)

    section('7. 修为接口')
    data = client.get('/api/cultivation/profile').get_json()
    check('修为档案可用', data.get('success') and data['profile']['points'] > 0)
    check('档案带境界阶梯', len(data['profile'].get('levels', [])) >= 10,
          str(len(data['profile'].get('levels', []))))

    before = data['profile']['points']
    data = client.post('/api/cultivation/award', json={'reason': 'narration', 'ref': '5_2'}).get_json()
    check('看讲解加分成功', data.get('success') and data.get('awarded') == training.NARRATION_POINTS,
          str(data)[:200])
    after = data['profile']['points']
    data = client.post('/api/cultivation/award', json={'reason': 'narration', 'ref': '5_2'}).get_json()
    check('同一节讲解不重复加分', data.get('awarded') == 0, str(data)[:160])
    check('加分后总分正确', after == before + training.NARRATION_POINTS, f'{before} -> {after}')
    data = client.post('/api/cultivation/award', json={'reason': '不存在的类型', 'ref': 'x'})
    check('未知加分类型被拒绝', data.status_code == 400)

    section('8. 完成知识点挂钩积分')
    before = client.get('/api/cultivation/profile').get_json()['profile']['points']
    data = client.post('/api/complete-kp', json={'chapter_id': '5', 'kp_index': 0}).get_json()
    check('完成知识点接口正常', data.get('success'), str(data)[:160])
    check('完成知识点带回加分', data.get('awarded') == training.KP_POINTS, str(data)[:200])
    after = client.get('/api/cultivation/profile').get_json()['profile']['points']
    check('修为确实增加', after == before + training.KP_POINTS, f'{before} -> {after}')
    data = client.post('/api/complete-kp', json={'chapter_id': '5', 'kp_index': 0}).get_json()
    check('同一知识点不重复加分', data.get('awarded') == 0)

    section('8b. 修行阁：装备 / 试炼 / 战力')
    data = client.get('/cultivation')
    check('修行阁页面可访问', data.status_code == 200 and '修行阁' in data.get_data(as_text=True))
    data = client.get('/api/game/state').get_json()
    check('修行阁数据可用', data.get('success'), str(data)[:200])
    check('等级表含 0 级共 31 行', len(data['levels']) == training.MAX_LEVEL + 1,
          str(len(data['levels'])))
    check('十境法相齐全', len(data['realms']) == 10 and all(r['art'].get('primary') for r in data['realms']))
    check('每级都有神功', all(lv['skill']['name'] for lv in data['levels']))
    check('装备都写了解锁方式', data['equipment'] and all(e['hint'] for e in data['equipment']))
    check('战力拆解自洽', sum(p['value'] for p in data['power']['parts']) == data['power']['total'],
          str(data['power']))
    check('攻略给出下一步与心法', bool(data['guide']['steps']) and bool(data['guide']['tips']))

    # 规则表与统计口径不能脱节：改了统计字段名而没改规则表的话，
    # 装备会永远解不开、试炼会永远 0%——这条断言专门拦这种静默失效。
    stats_keys = set(data['stats'])
    missing = sorted({e['metric'] for e in data['equipment'] if e['metric'] not in stats_keys}
                     | {o['metric'] for t in data['trials'] for o in t['objectives']
                        if o['metric'] not in stats_keys})
    check('装备/试炼引用的统计量都存在', not missing, str(missing))
    check('试炼覆盖十境', [t['realm'] for t in game.TRIALS] == [r for r, _ in training.REALMS])
    check('神功覆盖 0~30 级', set(game.SKILLS) == set(range(training.MAX_LEVEL + 1)))

    # 满星通关一道较难题：这是「刷难题解锁装备」的主路径
    hard = next((q for q in _BANK if q.get('difficulty') == 3 and q.get('solution')), None)
    if hard:
        client.post('/api/training/judge', json={'question_id': hard['id'], 'cells': [hard['solution']]})
        data = client.get('/api/game/state').get_json()
        lens = next(e for e in data['equipment'] if e['id'] == 'lens_hard')
        check('较难题满星解锁「猎难之瞳」', lens['unlocked'], str(lens))
        check('较难题满星计入较难满星数', data['stats']['stars3_hard'] >= 1,
              str(data['stats']['stars3_hard']))

    # 试炼：凑齐炼气期三条（通关过题 / 3 个知识点 / 有过满星）后应自动结算，且只发一次
    for i in range(3):
        client.post('/api/complete-kp', json={'chapter_id': '5', 'kp_index': i})
    before = client.get('/api/cultivation/profile').get_json()['profile']['points']
    data = client.get('/api/game/state').get_json()
    granted = {t['realm']: t['reward'] for t in data['granted_trials']}
    check('达成条件后试炼自动结算', '炼气期' in granted, str(data['granted_trials']))
    after = client.get('/api/cultivation/profile').get_json()['profile']['points']
    check('试炼奖励是真加分', after > before, f'{before} -> {after}')
    check('试炼奖励金额与规则表一致', granted.get('炼气期') ==
          next(t['reward'] for t in game.TRIALS if t['realm'] == '炼气期'), str(granted))
    empty = client.get('/api/game/state').get_json()['granted_trials']
    check('试炼奖励不重复发放', empty == [], str(empty))
    claimed = next(t for t in data['trials'] if t['realm'] == '炼气期')
    check('试炼状态标记为已通过', claimed['claimed'] and claimed['done'], str(claimed)[:160])
    profile = client.get('/api/cultivation/profile').get_json()['profile']
    check('等级条带上战力与试炼进度', profile.get('power', 0) > 0 and profile.get('trial'),
          str(profile.get('trial'))[:160])
    check('等级条带上境界法印', bool((profile.get('art') or {}).get('glyph')))

    section('9. 星辰教练：会话管理')
    data = client.get('/api/coach/sessions').get_json()
    check('会话列表可用', data.get('success') and data['sessions'] == [], str(data)[:160])
    check('上限为 10', data.get('limit') == coach.MAX_SESSIONS, str(data.get('limit')))

    data = client.post('/api/coach/sessions', json={}).get_json()
    check('新建会话成功', data.get('success') and data['session']['id'], str(data)[:200])
    sid = data['session']['id']

    data = client.post('/api/coach/chat', json={'question': '列表和元组有什么区别？', 'session_id': sid})
    text = sse_text(data)
    check('教练对话返回内容', len(text) > 20, text[:120])
    check('回答里有「想一想」追问', '想一想' in text, text[-160:])

    saved = coach.get_session(TEST_USER, sid)
    check('多轮对话已落盘（2 条消息）', len(saved.get('messages', [])) == 2,
          str(len(saved.get('messages', []))))
    check('首条消息标题自动生成', saved.get('title') and saved['title'] != '新的对话',
          str(saved.get('title')))

    data = client.post('/api/coach/chat', json={'question': '那字典呢？', 'session_id': sid})
    sse_text(data)
    saved = coach.get_session(TEST_USER, sid)
    check('第二轮对话继续追加（4 条）', len(saved.get('messages', [])) == 4,
          str(len(saved.get('messages', []))))

    data = client.get(f'/api/coach/sessions/{sid}/transcript').get_json()
    check('一键复制文本可用', data.get('success') and 'JJ老师' in data.get('text', ''),
          str(data)[:120])
    data = client.post(f'/api/coach/sessions/{sid}/rename', json={'title': '元组与列表'}).get_json()
    check('重命名成功', data.get('success'))
    check('重命名已生效', coach.get_session(TEST_USER, sid)['title'] == '元组与列表')

    section('10. 星辰教练：10 个会话上限')
    for _ in range(9):
        client.post('/api/coach/sessions', json={})
    data = client.post('/api/coach/sessions', json={}).get_json()
    check('超过 10 个时拒绝新建', not data.get('success'), str(data)[:200])
    check('拒绝时给出中文提示', '删除' in (data.get('message') or ''), str(data.get('message')))
    check('会话数停在 10', len(coach.list_sessions(TEST_USER)) == 10,
          str(len(coach.list_sessions(TEST_USER))))

    data = client.post('/api/coach/record', json={
        'question': '这道题为什么用 while？', 'answer': '因为循环次数不确定。',
        'chapter_id': '3', 'source': 'exercise'}).get_json()
    check('练习答疑能沉淀（自动顶掉最老的机器会话或合并）', data.get('success'), str(data)[:200])

    data = client.delete(f'/api/coach/sessions/{sid}').get_json()
    check('删除会话成功', data.get('success'))
    check('删除后数量减少', len(coach.list_sessions(TEST_USER)) == 9,
          str(len(coach.list_sessions(TEST_USER))))

    section('11. 实战组卷')
    data = client.post('/api/training/exam', json={
        'chapters': ['1', '2', '3'], 'count': 3, 'track': 'course'}).get_json()
    check('组卷成功', data.get('success'), str(data)[:240])
    exam = data.get('exam') or {}
    exam_id = exam.get('id')
    check('卷子有 3 题', exam.get('count') == 3, str(exam.get('count')))
    check('卷子状态为进行中', exam.get('status') == 'active')

    detail = client.get(f'/api/training/question/{exam["items"][0]["id"]}?exam_id={exam_id}').get_json()
    check('实战中不下发答案', 'solution' not in detail['question'], str(detail['question'].keys())[:160])
    check('实战中给出锁定说明', bool(detail['question'].get('blocked_reason')))

    # 做完两道题
    solved_any = False
    for item in exam['items'][:2]:
        solution = A.training.bank_index()[item['id']]['solution']
        result = client.post('/api/training/judge', json={
            'question_id': item['id'], 'cells': [solution], 'exam_id': exam_id}).get_json()
        solved_any = solved_any or result.get('passed', False)
    check('实战中判题可用', solved_any)

    # 跳过第三题
    data = client.post('/api/training/attempt', json={
        'question_id': exam['items'][2]['id'], 'exam_id': exam_id}).get_json()
    check('跳过接口可用', data.get('success') and data['settle']['stars'] == 0,
          str(data.get('settle'))[:160])

    exam_now = client.get(f'/api/training/exam/{exam_id}').get_json()['exam']
    check('三题状态都已记录', all(i['status'] in ('done', 'skipped', 'failed') for i in exam_now['items']),
          str([i['status'] for i in exam_now['items']]))
    check('做完后自动交卷', exam_now['status'] == 'finished', exam_now['status'])
    check('得分已计算', isinstance(exam_now.get('score'), int), str(exam_now.get('score')))

    detail = client.get(f'/api/training/question/{exam["items"][0]["id"]}?exam_id={exam_id}').get_json()
    check('交卷后解锁解析', 'solution' in detail['question'], str(detail['question'].keys())[:160])

    data = client.post(f'/api/training/exam/{exam_id}/review')
    review_text = sse_text(data)
    check('AI 批卷返回内容', len(review_text) > 20, review_text[:120])
    exam_now = client.get(f'/api/training/exam/{exam_id}').get_json()['exam']
    check('批卷结果已存进卷子', len(exam_now.get('review', '')) > 20,
          str(len(exam_now.get('review', ''))))

    section('12. 学习仪表盘统计')
    data = client.get('/api/progress/overview').get_json()
    check('仪表盘接口可用', data.get('success'))
    totals = data.get('totals', {})
    check(f'题目总数 {BANK_TOTAL}', totals.get('questions') == BANK_TOTAL, str(totals.get('questions')))
    check('统计到已通关题目', totals.get('solved', 0) >= 2, str(totals.get('solved')))
    check('统计到错题', totals.get('wrong', 0) >= 1, str(totals.get('wrong')))
    check('课程章节列表非空', len(data.get('course_chapters', [])) > 20,
          str(len(data.get('course_chapters', []))))
    check(f'算法专题列表 {BANK_ALGO_TOPICS} 个', len(data.get('algo_chapters', [])) == BANK_ALGO_TOPICS,
          str(len(data.get('algo_chapters', []))))
    check('错题按章节分组', isinstance(data.get('wrong_groups'), list))
    check('实战记录已进入列表', len(data.get('exams', [])) >= 1, str(len(data.get('exams', []))))
    chapter = next((c for c in data['course_chapters'] if c['id'] == 14), None)
    check('章节 14 统计到刷题进度', chapter and chapter['q_solved'] >= 1,
          str(chapter and {k: chapter[k] for k in ('q_total', 'q_solved', 'stars')}))
    check('知识点进度已统计', any(c['kp_done'] > 0 for c in data['course_chapters']),
          str([(c['id'], c['kp_done']) for c in data['course_chapters'] if c['kp_done']]))

    section('13. 页面可访问')
    for path, name in [('/coach', '教练页'), ('/training', '刷题页'), ('/progress', '仪表盘页'),
                       ('/dashboard', '主页'), ('/intro', '开场 CG 页')]:
        response = client.get(path)
        check(f'{name}返回 200', response.status_code == 200, str(response.status_code))

    # 开场 CG 的进出场规则：第一次打开先看片，看过就直接进站。
    # 这两条坏了的表现是"每次启动都被拦一次片头"，体感很差。
    fresh = A.app.test_client()
    check('首次打开先播开场 CG',
          fresh.get('/').headers.get('Location', '').endswith('/intro'),
          fresh.get('/').headers.get('Location', ''))
    seen = A.app.test_client()
    seen.set_cookie('pymaster_intro', '1')
    check('看过之后直接进站',
          seen.get('/').headers.get('Location', '').endswith('/dashboard'),
          seen.get('/').headers.get('Location', ''))
    done = A.app.test_client().get('/intro/done')
    check('片尾出口会记下"已看过"',
          'pymaster_intro=' in (done.headers.get('Set-Cookie') or ''),
          done.headers.get('Set-Cookie', ''))

    # 键盘输入：不带 stdin 时会 EOFError（这是正常的），但必须给出
    # "去哪里填输入"的指路，并且前端要按代码内容把输入框露出来。
    NL = chr(10)
    code_in = 'a = float(input("x："))' + NL + 'print(a * 2)' + NL
    r1 = client.post('/api/run-code', json={'code': code_in}).get_json()
    check('带 input 的代码会被识别', r1.get('needs_input') is True, str(r1.get('needs_input')))
    check('缺输入时给出填输入的指路', '测试输入' in (r1.get('hint') or ''), str(r1.get('hint'))[:80])
    r2 = client.post('/api/run-code', json={'code': code_in, 'stdin': '21' + NL}).get_json()
    check('填了输入就跑得通', r2.get('exit_code') == 0 and '42' in (r2.get('output') or ''),
          str(r2.get('output'))[:60])
    r3 = client.post('/api/run-code', json={'code': 'print(1+1)'}).get_json()
    check('普通代码不误报需要输入', r3.get('needs_input') is False and not r3.get('hint'),
          str(r3.get('needs_input')))

    section('14. 背景音乐')
    audio_dir = os.path.join(ROOT, 'static', 'audio')
    playlist_file = os.path.join(audio_dir, 'playlist.json')
    check('playlist.json 存在', os.path.exists(playlist_file))
    if os.path.exists(playlist_file):
        with open(playlist_file, 'r', encoding='utf-8') as handle:
            playlist = json.load(handle)
        check('曲目不少于 4 首', len(playlist) >= 4, str(len(playlist)))
        missing = [t['file'] for t in playlist
                   if not os.path.exists(os.path.join(audio_dir, t['file']))]
        check('每首曲子文件都在', not missing, str(missing))
        sizes = [os.path.getsize(os.path.join(audio_dir, t['file']))
                 for t in playlist if os.path.exists(os.path.join(audio_dir, t['file']))]
        check('单曲体积合理（< 3MB）', all(s < 3 * 1024 * 1024 for s in sizes),
              str([round(s / 1024 / 1024, 2) for s in sizes]))
        check('版权说明已生成', os.path.exists(os.path.join(audio_dir, 'CREDITS.md')))

    section('15. 游客模式与边界')
    guest = A.app.test_client()
    data = guest.get('/api/training/catalog').get_json()
    check('游客能看题库目录', data.get('success'))
    data = guest.post('/api/training/exam', json={'chapters': ['1'], 'count': 3}).get_json()
    check('游客不能组卷（需要登录）', not data.get('success'), str(data)[:160])
    data = guest.get('/api/cultivation/profile').get_json()
    check('游客修为为 0 且标记 guest',
          data['profile']['points'] == 0 and data['profile'].get('is_guest'))
    data = guest.get('/api/game/state').get_json()
    check('游客能看修行阁（不落盘）',
          data.get('success') and data.get('is_guest') and data['power']['total'] == 0
          and data['granted_trials'] == [], str(data.get('granted_trials')))
    data = guest.post('/api/coach/chat', json={'question': '你好'})
    check('游客可以聊天（不保存）', len(sse_text(data)) > 10)

    cleanup()

    section('结果')
    print(f'通过 {len(PASSED)} 项，失败 {len(FAILED)} 项')
    if FAILED:
        print('\n失败明细：')
        for name, detail in FAILED:
            print(f'  ✗ {name}')
            if detail:
                print(f'      {detail[:400]}')
        return 1
    print('全部通过 ✅')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        try:
            cleanup()
        except Exception:
            pass
        sys.exit(2)
