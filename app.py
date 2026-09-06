import json
import os
import sys
import ast
import hashlib
import secrets
import subprocess
import tempfile
import time
import re
import urllib.request
import urllib.error
import threading
import socket
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask import Response

# Lightweight .env loading keeps local one-click launches configured without
# adding a runtime dependency. Values already present in the process win.
def _load_local_env():
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_file):
        return
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"\''))
    except OSError as exc:
        print(f'[config] unable to read .env: {exc}')

_load_local_env()

# PyInstaller compatibility
if getattr(sys, 'frozen', False):
    BUNDLE_DIR = sys._MEIPASS
    WRITE_ROOT = os.path.dirname(sys.executable)
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    WRITE_ROOT = BUNDLE_DIR

from comic_engine import ComicEngine, ComicMemory
from tts_engine import EdgeTTS, DoubaoTTS, BrowserTTS

app = Flask(__name__)
# 持久化 secret key：存到 data 目录，重启后 session 不失效（否则每次重启所有用户被登出，
# 所有需登录的 API 都会 302 重定向，前端表现为"接口报错/转圈"）
SECRET_KEY_FILE = os.path.join(WRITE_ROOT, 'data', '.secret_key')
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r', encoding='utf-8') as _f:
        _persistent_secret = _f.read().strip()
else:
    _persistent_secret = None
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or _persistent_secret or secrets.token_hex(32)
if not _persistent_secret and not os.environ.get('FLASK_SECRET_KEY'):
    os.makedirs(os.path.dirname(SECRET_KEY_FILE), exist_ok=True)
    with open(SECRET_KEY_FILE, 'w', encoding='utf-8') as _f:
        _f.write(app.secret_key)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.template_folder = os.path.join(BUNDLE_DIR, 'templates')
app.static_folder = os.path.join(BUNDLE_DIR, 'static')

# Writable data: next to exe (or project root for dev)
DATA_DIR = os.path.join(WRITE_ROOT, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
WHITELIST_FILE = os.path.join(DATA_DIR, 'whitelist.json')
DAILY_USAGE_FILE = os.path.join(DATA_DIR, 'daily_usage.json')
# Read-only course data: bundled with exe
COURSES_FILE = os.path.join(BUNDLE_DIR, 'data', 'courses.json')

# Admin credentials (change these in production)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin888".encode('utf-8')).hexdigest()

# Initialize Comic Engine and Memory
comic_engine = ComicEngine()
comic_memory = ComicMemory(DATA_DIR)

# Initialize TTS Engines
tts_engine = EdgeTTS()

doubao_tts = DoubaoTTS(
    app_id=os.environ.get('DOUBAO_TTS_APP_ID', ''),
    access_token=os.environ.get('DOUBAO_ACCESS_TOKEN', ''),
    secret_key=os.environ.get('DOUBAO_SECRET_KEY', '')
)
browser_tts = BrowserTTS()


def load_json(filepath):
    if not os.path.exists(filepath):
        return {} if 'users' in filepath else []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


def get_unlock_status(courses, completed_kps, mode='explore'):
    """Return set of (chapter_id, kp_index) that are unlocked."""
    unlocked = set()
    if mode == 'all_unlocked':
        for c in courses:
            for i in range(len(c.get('knowledge_points', []))):
                unlocked.add((c['id'], i))
        return unlocked
    # Explore mode: sequential unlock
    # Build course order index from the courses list (position-based, not ID-based)
    course_order = {c['id']: idx for idx, c in enumerate(courses)}
    sorted_ids = sorted(c['id'] for c in courses)

    unlocked.add((sorted_ids[0], 0))  # First chapter KP0 always unlocked
    for c in courses:
        ch = c['id']
        kps = c.get('knowledge_points', [])
        for i in range(len(kps)):
            if ch == sorted_ids[0] and i == 0:
                continue
            if i == 0:
                # Find previous chapter by position in sorted order
                current_pos = course_order.get(ch)
                if current_pos is None or current_pos == 0:
                    continue
                prev_ch_id = sorted_ids[current_pos - 1]
                prev_c = next((x for x in courses if x['id'] == prev_ch_id), None)
                if not prev_c:
                    continue
                prev_last = len(prev_c.get('knowledge_points', [])) - 1
                prev_key = f"{prev_ch_id}_{prev_last}"
            else:
                prev_key = f"{ch}_{i-1}"
            if prev_key in completed_kps:
                unlocked.add((ch, i))
    return unlocked


# ── Whitelist & Daily Usage ────────────────────────────────

def _load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return {}
    with open(WHITELIST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_whitelist(data):
    with open(WHITELIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load_daily_usage():
    if not os.path.exists(DAILY_USAGE_FILE):
        return {}
    with open(DAILY_USAGE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_daily_usage(data):
    with open(DAILY_USAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_whitelisted(username):
    """Check if user is in whitelist and not expired."""
    wl = _load_whitelist()
    entry = wl.get(username)
    if not entry:
        return False
    expiry = entry.get('expiry_date', '')
    if expiry:
        try:
            exp_date = datetime.strptime(expiry, '%Y-%m-%d').date()
            if datetime.now().date() > exp_date:
                return False
        except ValueError:
            return False
    return True

def check_daily_limit(username):
    """Check if user has reached daily AI query limit. Returns (allowed, used, limit)."""
    wl = _load_whitelist()
    entry = wl.get(username, {})
    daily_limit = entry.get('daily_limit', 0)
    if daily_limit <= 0:
        return True, 0, 0  # unlimited

    today = datetime.now().strftime('%Y-%m-%d')
    usage = _load_daily_usage()
    today_usage = usage.get(today, {})
    used = today_usage.get(username, 0)
    return used < daily_limit, used, daily_limit

def increment_daily_usage(username):
    """Increment user's daily AI usage counter."""
    wl = _load_whitelist()
    entry = wl.get(username, {})
    daily_limit = entry.get('daily_limit', 0)
    if daily_limit <= 0:
        return  # unlimited, no tracking needed

    today = datetime.now().strftime('%Y-%m-%d')
    usage = _load_daily_usage()
    if today not in usage:
        usage[today] = {}
    usage[today][username] = usage[today].get(username, 0) + 1
    _save_daily_usage(usage)


@app.route('/')
def index():
    # 未登录也直接进入仪表盘（游客模式），保证GitHub页面可完整访问
    return redirect(url_for('dashboard'))


@app.route('/login')
def login_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    if len(username) < 3:
        return jsonify({'success': False, 'message': '用户名至少3个字符'})
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'})

    # Whitelist check
    if not is_whitelisted(username):
        return jsonify({'success': False, 'message': '注册失败：该用户名不在白名单中，请联系管理员'})

    users = load_json(USERS_FILE)
    if username in users:
        return jsonify({'success': False, 'message': '用户名已存在'})

    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mode': 'explore',
        'progress': {},
        'completed_kps': [],
        'completed_exercises': [],
        'favorites': [],
        'wrong_answers': [],
        'notes': {}
    }
    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'message': '注册成功，请登录'})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})

    users = load_json(USERS_FILE)
    if username not in users:
        return jsonify({'success': False, 'message': '用户不存在'})

    if users[username]['password'] != hash_password(password):
        return jsonify({'success': False, 'message': '密码错误'})

    # Whitelist check
    if not is_whitelisted(username):
        return jsonify({'success': False, 'message': '登录失败：账号未在白名单中或已过期，请联系管理员'})

    session['username'] = username
    return jsonify({'success': True, 'message': '登录成功'})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    # 游客模式：未登录也可完整访问所有章节页面
    is_guest = 'username' not in session
    if is_guest:
        username = 'guest'
        progress = {}
        mode = 'all_unlocked'  # 游客默认全部解锁
    else:
        users = load_json(USERS_FILE)
        username = session.get('username', 'guest')
        progress = users.get(username, {}).get('progress', {})
        mode = users.get(username, {}).get('mode', 'explore')

    courses = load_json(COURSES_FILE)

    chapters = []
    for course in courses:
        ch_id = str(course['id'])
        ch_progress = progress.get(ch_id, {})
        total = len(course.get('knowledge_points', [])) + len(course.get('exercises', []))
        completed = ch_progress.get('knowledge', 0) + ch_progress.get('exercises', 0)
        pct = round(completed / total * 100) if total > 0 else 0
        chapters.append({
            'id': course['id'],
            'title': course['title'],
            'icon': course['icon'],
            'description': course['description'],
            'progress': pct,
            'ppt_url': course.get('ppt_url', ''),
            'knowledge_count': len(course.get('knowledge_points', [])),
            'exercise_count': len(course.get('exercises', []))
        })

    if is_guest:
        completed_kps = []
    else:
        users = load_json(USERS_FILE)
        user = users.get(username, {})
        completed_kps = user.get('completed_kps', [])

    # Compute chapter unlock status
    if mode == 'all_unlocked':
        chapter_unlocked = {ch['id']: True for ch in chapters}
    else:
        unlock = get_unlock_status(courses, completed_kps, mode)
        chapter_unlocked = {}
        for ch in chapters:
            chapter_unlocked[ch['id']] = any(
                (ch['id'], i) in unlock
                for i in range(ch['knowledge_count'])
            )

    return render_template('dashboard.html', username=username, chapters=chapters,
                          mode=mode, chapter_unlocked=chapter_unlocked)


@app.route('/stars')
def knowledge_stars():
    """Full-screen two-level knowledge universe, matching AI Master's atlas."""
    return render_template('knowledge_stars.html')


@app.route('/api/knowledge-universe')
def knowledge_universe():
    courses = load_json(COURSES_FILE)
    username = session.get('username', 'guest')
    is_guest = username == 'guest'
    user = {} if is_guest else load_json(USERS_FILE).get(username, {})
    completed_kps = set(user.get('completed_kps', []))
    mode = 'all_unlocked' if is_guest else user.get('mode', 'explore')
    unlocked = get_unlock_status(courses, completed_kps, mode)
    galaxies = []
    completed_total = 0

    for course in courses:
        chapter_id = course['id']
        stars = []
        for index, kp in enumerate(course.get('knowledge_points', [])):
            key = f'{chapter_id}_{index}'
            is_completed = key in completed_kps
            is_available = mode == 'all_unlocked' or (chapter_id, index) in unlocked
            status = 'completed' if is_completed else ('available' if is_available else 'locked')
            completed_total += int(is_completed)
            plain_desc = re.sub(r'<[^>]+>', ' ', str(kp.get('content', '')))
            plain_desc = re.sub(r'\s+', ' ', plain_desc).strip()
            stars.append({
                'chapter': chapter_id,
                'index': index,
                'title': kp.get('title', f'知识点 {index + 1}'),
                'desc': plain_desc[:240] or course.get('description', ''),
                'status': status,
                'url': url_for('chapter', chapter_id=chapter_id) + f'#kp-{index + 1}',
            })
        total = len(stars)
        done = sum(1 for star in stars if star['status'] == 'completed')
        connections = [[i, i + 1, 'sequence'] for i in range(max(0, total - 1))]
        connections += [[i, i + 2, 'concept'] for i in range(max(0, total - 2))]
        galaxies.append({
            'id': f'chapter-{chapter_id}',
            'chapter': chapter_id,
            'name': course['title'],
            'name_en': f'SECTOR {chapter_id:02d}',
            'progress': round(done / total * 100) if total else 0,
            'stars': stars,
            'connections': connections,
        })

    return jsonify({
        'success': True,
        'summary': {
            'galaxies': len(galaxies),
            'stars': sum(len(item['stars']) for item in galaxies),
            'completed': completed_total,
        },
        'galaxies': galaxies,
    })


@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    # 游客模式：未登录也可完整访问章节内容
    is_guest = 'username' not in session
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if c['id'] == chapter_id), None)
    if not course:
        return redirect(url_for('dashboard'))

    if is_guest:
        username = 'guest'
        progress = {}
        completed_kps = []
        mode = 'all_unlocked'  # 游客全部解锁
    else:
        users = load_json(USERS_FILE)
        username = session.get('username', 'guest')
        user = users.get(username, {})
        progress = user.get('progress', {}).get(str(chapter_id), {})
        completed_kps = user.get('completed_kps', [])
        mode = user.get('mode', 'explore')

    # Distribute chapter-level exercises across KPs
    chapter_exercises = course.get('exercises', [])
    kps = course.get('knowledge_points', [])
    kp_exercises = {}
    ex_idx = 0
    code_hints = {
        '变量': '创建几个变量并打印它们的值和类型。',
        'Python 是什么': '打印一段关于 Python 的介绍文字。',
        'Python 的安装': '打印你的 Python 版本信息。',
        '第一个 Python': '写一个程序，输出 "Hello, PyMaster!"。',
        'IDE': '用多行字符串写一段注释说明你喜欢的编辑器。',
        '数字类型': '定义整数、浮点数各一个，打印它们的和、差、积。',
        '字符串': '定义字符串，使用 f-string 拼接并输出。',
        '布尔类型': '比较两个数字，打印比较结果。',
        '算术': '计算并打印 (10+5)*3/2 的结果。',
        '比较': '用代码验证 10 是否大于 5 且小于 20。',
        '逻辑': '用 and/or/not 各写一个表达式并打印结果。',
        '赋值': '使用多重赋值交换两个变量的值。',
        'if 条件': '写一个 if-elif-else 判断分数等级的程序。',
        'for 循环': '用 for 循环遍历列表并打印每个元素。',
        'while 循环': '用 while 循环计算 1 到 100 的和。',
        '嵌套循环': '用嵌套循环打印 3x3 乘法表。',
        '切片': '创建一个字符串并用切片反转它。',
        '字符串方法上': '定义字符串，练习 upper/find/replace 方法。',
        '字符串方法下': '用 split 和 join 处理逗号分隔的文本。',
        '字符串格式化': '用 f-string 格式化输出姓名、年龄和分数。',
        '列表基础': '创建一个列表，添加元素，打印长度。',
        '列表增删改查': '创建一个列表，练习 append/pop/remove。',
        '列表排序': '创建一个数字列表并排序输出。',
        '元组': '创建一个元组并解包到多个变量。',
        '字典基础': '创建一个字典存储个人信息并访问。',
        '字典增删改查': '用 get 和 update 方法操作字典。',
        '字典遍历': '遍历字典的键值对并格式化打印。',
        '集合': '创建两个集合并进行交集并集运算。',
        '函数定义': '定义一个计算 BMI 的函数并调用。',
        '参数上': '写一个带默认参数的函数。',
        '参数下': '写一个带 *args 和 **kwargs 的函数。',
        '返回值': '写一个函数返回多个值并解包接收。',
        'Lambda': '用 lambda 和 sorted 对字典列表排序。',
        '装饰器': '写一个简单的日志装饰器。',
        '生成器': '写一个生成斐波那契数列的生成器。',
        '类型提示': '给函数添加类型提示。',
        '文件读取': '写代码用 with open 读取文本文件。',
        '文件写入': '写代码用 with open 写入并追加文本。',
        '异常基础': '用 try-except 捕获除零错误。',
        '异常进阶': '写一个完整的 try-except-else-finally 结构。',
    }

    for i in range(len(kps)):
        kp_title = kps[i]['title']
        exercises = []
        # Assign existing matching exercises
        if ex_idx < len(chapter_exercises):
            ex = dict(chapter_exercises[ex_idx])
            if 'type' not in ex:
                ex['type'] = 'choice'
            ex['ex_idx'] = 0
            exercises.append(ex)
            ex_idx += 1
        # Add a code verification exercise if the assigned one wasn't already code
        if not exercises or exercises[0].get('type') != 'code':
            hint = '请编写代码展示你对本知识点的理解。'
            for key, val in code_hints.items():
                if key in kp_title:
                    hint = val
                    break
            exercises.append({
                'type': 'code',
                'question': f'编写代码验证「{kp_title}」',
                'code_prompt': hint,
                'explanation': '代码成功运行即表示你已掌握本知识点！'
            })
        kp_exercises[i] = exercises

    # Unlock status for all chapters
    if mode == 'all_unlocked':
        kp_unlocked = {i: True for i in range(len(kps))}
    else:
        unlock = get_unlock_status(courses, completed_kps, mode)
        kp_unlocked = {}
        for i in range(len(kps)):
            kp_unlocked[i] = (chapter_id, i) in unlock

    # Check if all KPs in this chapter are completed
    all_kp_keys = [f"{chapter_id}_{i}" for i in range(len(kps))]
    chapter_completed = all(k in completed_kps for k in all_kp_keys) if completed_kps else False
    # KP titles for JJ guide
    chapter_kp_titles = [kp['title'] for kp in kps]
    # User's wrong answers for this chapter (游客无错题记录)
    if is_guest:
        chapter_wrong = []
    else:
        users = load_json(USERS_FILE)
        user = users.get(username, {})
        user_wrong = user.get('wrong_answers', [])
        chapter_wrong = [w for w in user_wrong if str(w.get('chapter_id', '')) == str(chapter_id)]

    return render_template('chapter.html', chapter=course, progress=progress,
                          completed_kps=completed_kps, kp_exercises=kp_exercises,
                          kp_unlocked=kp_unlocked, mode=mode,
                          chapter_completed=chapter_completed,
                          chapter_kp_titles=chapter_kp_titles,
                          chapter_wrong=chapter_wrong)


@app.route('/canvas')
def canvas():
    return render_template('canvas.html')


# ── Python Code Playground ─────────────────────────────────

@app.route('/api/lint-code', methods=['POST'])
def lint_code():
    """Check Python code for syntax errors using ast.parse"""
    data = request.get_json()
    code = data.get('code', '')
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append({
            'line': e.lineno or 1,
            'offset': e.offset or 0,
            'message': str(e),
            'text': e.text or '',
        })
    except Exception as e:
        errors.append({
            'line': 1,
            'offset': 0,
            'message': f'解析错误: {str(e)}',
            'text': '',
        })
    return jsonify({'success': True, 'errors': errors, 'valid': len(errors) == 0})


@app.route('/playground')
def playground():
    return render_template('playground.html')


@app.route('/api/run-code', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '').strip()

    if not code:
        return jsonify({'success': False, 'output': '', 'error': '代码不能为空'})

    if len(code) > 50000:
        return jsonify({'success': False, 'output': '', 'error': '代码过长（最大50000字符）'})

    # Write code to temp file
    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(suffix='.py', prefix='pymaster_')
        os.close(fd)
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(code)

        # Run with timeout and capture output
        start = time.time()
        proc = subprocess.run(
            ['python', '-X', 'utf8', tmp_path],
            capture_output=True,
            timeout=10,
            cwd=os.path.dirname(tmp_path),
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
        )
        elapsed = round(time.time() - start, 2)

        stdout = proc.stdout.decode('utf-8', errors='replace') if proc.stdout else ''
        stderr = proc.stderr.decode('utf-8', errors='replace') if proc.stderr else ''

        output_parts = []
        if stdout:
            output_parts.append(stdout.rstrip())
        if stderr:
            output_parts.append(f'[stderr]\n{stderr.rstrip()}')

        output = '\n'.join(output_parts) if output_parts else '(无输出)'

        return jsonify({
            'success': True,
            'output': output,
            'error': '',
            'exit_code': proc.returncode,
            'elapsed': f'{elapsed}s'
        })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'output': '',
            'error': '⏱ 代码执行超时（10秒限制）\n可能原因：死循环、阻塞操作或计算量过大',
            'exit_code': -1,
            'elapsed': '10s+'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': '',
            'error': f'执行异常: {str(e)}',
            'exit_code': -1,
            'elapsed': '0s'
        })
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


# ── AI 代码评分 ─────────────────────────────────────────

CODE_SCORE_PROMPT = """你是一位非常耐心、鼓励性的 Python 入门老师。你的任务是对初学者的代码进行评分，以鼓励为主。

评分标准（满分100分）：
1. 代码正确性（40分）：代码是否能正常运行？语法是否正确？
2. 代码努力程度（30分）：学生是否认真尝试了？代码是否有合理的逻辑？
3. 输出展示（15分）：代码是否有输出？输出是否展示了知识点？
4. 代码初步规范（15分）：变量命名是否有意义？

评分规则：
- 如果代码有语法错误 → 最多 40 分（鼓励尝试）
- 如果代码能正确运行（即使只是简单 print）→ 至少 80 分
- 如果代码正确演示了知识点核心概念 → 85-95 分
- 如果代码完整且展示了实际应用 → 90-100 分
- 对于初学者，只要语法正确、能运行且与知识点相关 → 至少 80 分
- 请以鼓励为主，对初学者要包容

请返回 JSON 格式（不要包含其他内容）：
{"score": 整数分数, "feedback": "简短的中文评语（50字以内）", "strengths": "优点（30字以内）", "weaknesses": "改进建议（30字以内）"}"""


@app.route('/api/score-code', methods=['POST'])
def score_code():
    data = request.get_json()
    kp_title = data.get('kp_title', '')
    code = data.get('code', '')
    output = data.get('output', '')
    prompt = data.get('prompt', '')

    # Daily limit check (游客跳过限制)
    username = session.get('username', 'guest')
    if username != 'guest':
        allowed, used, limit = check_daily_limit(username)
        if not allowed:
            return jsonify({
                'success': True, 'score': 60,
                'feedback': '今日 AI 评分次数已用完，代码已标记通过',
                'strengths': '', 'weaknesses': ''
            })

    user_message = f"""【知识点】{kp_title}
【练习要求】{prompt}
【学生代码】
```python
{code}
```
【代码输出】
{output}
"""

    answer, error = _call_deepseek(CODE_SCORE_PROMPT, user_message, max_tokens=500)
    if error:
        return jsonify({'success': True, 'score': 70, 'feedback': '代码运行成功（AI评分暂不可用）', 'strengths': '', 'weaknesses': ''})

    # Track usage on successful API call (游客不记录)
    if username != 'guest':
        increment_daily_usage(username)

    try:
        import re
        json_match = re.search(r'\{.*\}', answer, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(answer)
        return jsonify({
            'success': True,
            'score': max(0, min(100, result.get('score', 70))),
            'feedback': result.get('feedback', ''),
            'strengths': result.get('strengths', ''),
            'weaknesses': result.get('weaknesses', '')
        })
    except Exception as e:
        print(f"[AI评分] JSON解析失败: {e} - raw: {answer[:200]}")
        return jsonify({'success': True, 'score': 70, 'feedback': '代码运行成功（AI评分解析失败）', 'strengths': '', 'weaknesses': ''})


# ── Python 智能体 ─────────────────────────────────────────
# OpenAI-compatible endpoint. Secrets are injected through environment variables.
def _normalize_ai_endpoint(raw_url):
    """Normalize a provider base URL to the OpenAI-compatible chat endpoint."""
    base = (raw_url or 'https://ark.cn-beijing.volces.com/api/v3').strip().rstrip('/')
    if base.endswith('/chat/completions'):
        return base
    if base.endswith(('/v1', '/v3')):
        return base + '/chat/completions'
    return base + '/v1/chat/completions'

AI_BASE_URL = _normalize_ai_endpoint(os.environ.get('PYMASTER_AI_BASE_URL'))
from ark_client import ArkClient, ArkError
ark = ArkClient()
AI_API_KEY = ark.key
AI_MODEL = ark.models[0]
AI_CACHE = {}
AI_CACHE_TTL = 300
AI_CONNECT_TIMEOUT = 4
# Keep interactive tutoring bounded: one stalled relay should not make the
# chat feel frozen, while the browser's 12s abort remains a final guard.
AI_READ_TIMEOUT = 8


def _quick_python_answer(question):
    """Return a zero-token answer only for small, unambiguous beginner questions."""
    normalized = re.sub(r'\s+', '', question.lower())
    if 'print' in normalized and any(token in normalized for token in ('什么作用', '有什么用', '是干嘛', '是什么')):
        return "`print()` 用来把内容输出到控制台，方便你看到程序的结果。\n\n```python\nprint('Hello, World!')\n```\n\n运行后会显示 `Hello, World!`。"
    if '变量' in normalized and any(token in normalized for token in ('是什么', '什么是', '什么意思')):
        return "变量是给数据起的名字，程序之后可以通过这个名字使用或更新数据。\n\n```python\nage = 12\nprint(age)\n```\n\n这里 `age` 就是变量，保存了整数 `12`。"
    if '列表' in normalized and any(token in normalized for token in ('是什么', '什么是', '什么意思')):
        return "列表用于按顺序保存多个值，可以通过下标读取其中的元素。\n\n```python\ncolors = ['red', 'blue']\nprint(colors[0])  # red\n```"
    if ('列表推导' in normalized or '推导式' in normalized) and any(token in normalized for token in ('是什么', '怎么写', '例子', '什么意思')):
        return "列表推导式是用一行表达式创建列表的写法，适合简单、清晰的转换或筛选。\n\n```python\nsquares = [n * n for n in range(5)]\nprint(squares)  # [0, 1, 4, 9, 16]\n```\n\n如果逻辑变复杂，使用普通 `for` 循环会更易读。"
    if ('字典' in normalized or 'dict' in normalized) and any(token in normalized for token in ('是什么', '什么是', '什么意思')):
        return "字典用键和值保存有意义的对应关系，适合按名称查找数据。\n\n```python\nuser = {'name': 'Lin', 'level': 1}\nprint(user['name'])\n```"
    if ('if' in normalized or '条件' in normalized) and any(token in normalized for token in ('是什么', '怎么用', '什么意思')):
        return "`if` 根据条件决定是否执行一段代码；可以用 `elif` 添加其他分支，用 `else` 处理剩余情况。\n\n```python\nscore = 86\nif score >= 60:\n    print('通过')\nelse:\n    print('再练一次')\n```"
    if ('for' in normalized or '循环' in normalized) and any(token in normalized for token in ('是什么', '怎么用', '什么意思')):
        return "`for` 会依次取出可迭代对象中的元素，并执行循环体。\n\n```python\nfor name in ['Ada', 'Lin']:\n    print(name)\n```"
    if ('函数' in normalized or 'def' in normalized) and any(token in normalized for token in ('是什么', '什么是', '怎么写', '什么意思')):
        return "函数是可重复调用的代码单元，用参数接收输入，用 `return` 交回结果。\n\n```python\ndef add(a, b):\n    return a + b\n\nprint(add(2, 3))\n```"
    if ('return' in normalized or '返回值' in normalized) and any(token in normalized for token in ('是什么', '什么意思', '什么用')):
        return "`return` 结束当前函数并把一个值交回调用处。没有写 `return` 时，函数默认返回 `None`。"
    if ('import' in normalized or '模块' in normalized) and any(token in normalized for token in ('是什么', '怎么用', '什么意思')):
        return "`import` 把模块加载到当前文件，让你复用已经写好的代码。\n\n```python\nimport math\nprint(math.sqrt(9))\n```"
    if ('异常' in normalized or 'try' in normalized or 'except' in normalized) and any(token in normalized for token in ('是什么', '怎么处理', '什么意思')):
        return "异常是运行时发生的错误。用 `try/except` 可以捕获预期错误，并给用户清晰的处理结果。\n\n```python\ntry:\n    number = int(input('数字：'))\nexcept ValueError:\n    print('请输入整数')\n```"
    return None

JJ_SYSTEM_PROMPT = """你是 JJ老师，一位幽默风趣、耐心细致的 Python 编程老师。
你的学生是正在学习 Python 基础的中学生和编程初学者。

教学风格：
- 用通俗易懂的语言解释概念，善用生活类比
- 回答简洁有条理，重点突出
- 鼓励学生自己思考，适当引导而非直接给答案
- 适当用 emoji 让对话生动
- 如果学生问的是代码题，先分析思路再给参考代码
- 每次回答控制在 300 字以内，除非学生明确要详细解释

课程内容涵盖：Python基础、变量类型、运算符、条件循环、字符串、列表元组、字典集合、函数、文件IO。"""
JJ_SYSTEM_PROMPT += """

边界与准确性：
- 只回答与 Python、当前课程知识点或练习代码直接相关的问题；无关问题请简短说明你是 Python 学习助手。
- 不确定的版本差异、库 API 或运行结果时，明确说出不确定并建议用最小示例验证，不要编造。
- 解析练习时先引用题干中的已知条件，再给思路、关键语法和最小示例；不要泄露未请求的整套答案。
- 使用 Markdown 代码块，代码必须是可运行的 Python 3 语法。
"""

@app.route('/api/ai-config')
def ai_config():
    """Return a safe, non-secret configuration health snapshot for the UI."""
    return jsonify({
        'success': True,
        'configured': bool(AI_API_KEY),
        'model': ark.active_model,
        'fallback_models': ark.models[1:],
        'streaming': True,
        'quota_note': '平台免费余额请以火山控制台为准',
        'endpoint_ready': AI_BASE_URL.endswith('/chat/completions'),
    })


@app.route('/api/ask-jj-stream', methods=['POST'])
def ask_jj_stream():
    data = request.get_json(silent=True) or {}
    question = str(data.get('question', '')).strip()
    context = str(data.get('context', ''))
    if not question or len(question) > 6000 or len(context) > 24000:
        return jsonify(success=False, error='问题不能为空，且问题/上下文过长时请分段发送。'), 400
    username = session.get('username', 'guest')
    if username != 'guest' and not check_daily_limit(username)[0]:
        return jsonify(success=False, error='今日 AI 问答次数已用完。'), 429
    chapter_id = str(data.get('chapter_id', ''))
    messages = [{'role': 'system', 'content': JJ_SYSTEM_PROMPT}]
    messages.append({'role': 'user', 'content': (context + '\n\n' if context else '') + question})
    def generate():
        def encode(event):
            return 'data: ' + json.dumps(event, ensure_ascii=False) + '\n\n'
        answer = ''
        yield encode({'type': 'status', 'message': '正在连接火山方舟…'})
        try:
            for event in ark.events(messages):
                if event['type'] == 'delta':
                    answer += event['text']
                yield encode(event)
            if not answer:
                raise ArkError('模型没有返回正文，请重试。')
            if username != 'guest':
                increment_daily_usage(username)
                if chapter_id:
                    users = load_json(USERS_FILE)
                    if username in users:
                        history = users[username].setdefault('jj_history', {}).setdefault(chapter_id, [])
                        history.append({'question': question, 'answer': answer, 'timestamp': datetime.now().isoformat()})
                        save_json(USERS_FILE, users)
            yield encode({'type': 'done', 'model': ark.active_model})
        except ArkError as exc:
            yield encode({'type': 'error', 'message': str(exc)})
    return Response(generate(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/ask-jj', methods=['POST'])
def ask_jj():
    data = request.get_json(silent=True) or {}
    question = str(data.get('question', '')).strip()
    context = data.get('context', '')  # optional: code or exercise context

    if not question:
        return jsonify({'success': False, 'answer': '', 'error': '问题不能为空'})

    quick_answer = None  # Always use the configured model; never disguise canned answers as AI.
    if quick_answer:
        return jsonify({"success": True, "answer": quick_answer, "error": "", "cached": True, "source": "local"})

    # Daily limit check (游客跳过限制)
    username = session.get('username', 'guest')
    if username != 'guest':
        allowed, used, limit = check_daily_limit(username)
        if not allowed:
            return jsonify({
                'success': False, 'answer': '', 'error': f'今日 AI 问答次数已用完（{used}/{limit}），请联系管理员或明天再试'
            })

    # Build messages
    messages = [{"role": "system", "content": JJ_SYSTEM_PROMPT}]

    if context:
        messages.append({
            "role": "user",
            "content": f"【上下文/代码】\n{context}\n\n【学生提问】\n{question}"
        })
    else:
        messages.append({"role": "user", "content": question})

    cache_key = hashlib.sha256(json.dumps([AI_MODEL, question, context], ensure_ascii=False).encode()).hexdigest()
    cached = AI_CACHE.get(cache_key)
    if cached and time.time() - cached[0] < AI_CACHE_TTL:
        return jsonify({"success": True, "answer": cached[1], "error": "", "cached": True})
    if not AI_API_KEY:
        return jsonify({"success": False, "answer": "", "error": "尚未配置 Python 智能体密钥，请设置 PYMASTER_AI_API_KEY"})

    payload = json.dumps({
        "model": AI_MODEL,
        "messages": messages,
        "max_tokens": 520,
        "temperature": 0.35,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }

    try:
        # A single bounded request is more predictable for an interactive
        # chat than retrying a slow upstream and doubling the perceived wait.
        result, transport_error = _request_ai(payload, headers, retries=0)
        if transport_error:
            return jsonify({"success": False, "answer": "", "error": transport_error})

        answer = result["choices"][0]["message"]["content"]
        AI_CACHE[cache_key] = (time.time(), answer)
        if username != 'guest':
            increment_daily_usage(username)

        # Store JJ chat history per chapter (游客不保存)
        chapter_id = str(data.get('chapter_id', ''))
        if chapter_id and username != 'guest':
            users = load_json(USERS_FILE)
            if username in users:
                if 'jj_history' not in users[username]:
                    users[username]['jj_history'] = {}
                if chapter_id not in users[username]['jj_history']:
                    users[username]['jj_history'][chapter_id] = []
                users[username]['jj_history'][chapter_id].append({
                    'question': question,
                    'answer': answer,
                    'timestamp': datetime.now().isoformat()
                })
                save_json(USERS_FILE, users)

        return jsonify({"success": True, "answer": answer, "error": ""})

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"[JJ老师] DeepSeek API error: {e.code} - {err_body[:300]}")
        return jsonify({
            "success": False,
            "answer": "",
            "error": f"API 调用失败 (HTTP {e.code})，请稍后重试"
        })
    except Exception as e:
        print(f"[JJ老师] Error: {e}")
        return jsonify({
            "success": False,
            "answer": "",
            "error": f"网络错误: {str(e)[:100]}"
        })


def _request_ai(payload, headers, retries=1):
    """Bounded AI transport: fail fast on a stalled relay and retry once only for transient errors."""
    try:
        params = json.loads(payload)
        answer = ark.complete(params['messages'], params.get('max_tokens', 800))
        return {'choices': [{'message': {'content': answer}}]}, None
    except ArkError as exc:
        return None, str(exc)


def _call_deepseek(system_prompt, user_message, max_tokens=520, retries=2):
    """Helper to call DeepSeek API with a given prompt.

    Retries transient failures (5xx / 429 / network) with exponential backoff.
    Returns (answer, error); answer is None when error is set.
    """
    payload = json.dumps({
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.35,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }

    result, error = _request_ai(payload, headers, retries=1)
    if error:
        return None, error
    try:
        return result["choices"][0]["message"]["content"], None
    except (KeyError, IndexError, TypeError):
        return None, "AI 服务返回格式异常，请稍后重试。"


# ── JJ老师 章节指引 ────────────────────────────────────

CHAPTER_GUIDE_PROMPT = """你是 JJ老师，一位幽默风趣、耐心细致的 Python 编程老师。

任务：当学生开始学习一个新章节时，给他们一个简短的学习路线指引。

要求：
- 热情鼓励的语气，让学生感到兴奋
- 简要概述本章要学什么（2-3句话）
- 给出学习建议（2-3条）
- 指出本章内容为什么重要
- 控制在 200 字以内
- 适当用 emoji 让对话生动"""


@app.route('/api/jj-chapter-guide', methods=['POST'])
def jj_chapter_guide():
    data = request.get_json()
    chapter_id = data.get('chapter_id', '')
    chapter_title = data.get('chapter_title', '')
    kp_titles = data.get('kp_titles', [])

    kp_list = '\n'.join(f"- {t}" for t in kp_titles)
    user_msg = f"学生即将开始学习第 {chapter_id} 章：「{chapter_title}」。\n\n本章知识点：\n{kp_list}\n\n请给学生简短的学习路线指引。"

    answer, error = _call_deepseek(CHAPTER_GUIDE_PROMPT, user_msg)
    if error:
        return jsonify({'success': False, 'answer': '', 'error': error})
    return jsonify({'success': True, 'answer': answer})


# ── JJ老师 章节完成分析 ────────────────────────────────

CHAPTER_COMPLETE_PROMPT = """你是 JJ老师，一位幽默风趣、耐心细致的 Python 编程老师。

任务：学生刚刚完成了某一章节的学习，请你：
1. 热情祝贺学生完成本章学习
2. 分析学生的错题（如果有），说明每道错题涉及的知识点
3. 给出本章需要重点复习的知识点
4. 出 2-3 道相似的练习题，让学生巩固

要求：
- 如果学生没有错题，大力表扬并提示可以继续前进
- 如果有错题，温和指出，鼓励学生不要灰心
- 出的练习题要类似原题但不要完全相同
- 练习题请清晰地标上"练习1"、"练习2"等
- 总字数控制在 500 字以内
- 适当用 emoji"""


@app.route('/api/jj-chapter-complete', methods=['POST'])
def jj_chapter_complete():
    data = request.get_json()
    chapter_id = data.get('chapter_id', '')
    chapter_title = data.get('chapter_title', '')
    kp_titles = data.get('kp_titles', [])
    wrong_answers = data.get('wrong_answers', [])

    kp_list = '\n'.join(f"- {t}" for t in kp_titles)

    if wrong_answers:
        wrong_list = '\n'.join(
            f"- 问题：{w.get('question', '')} | 你的答案：{w.get('user_answer', '')} | 正确答案：{w.get('correct_answer', '')}"
            for w in wrong_answers
        )
        user_msg = f"学生刚刚完成了第 {chapter_id} 章：「{chapter_title}」。\n\n本章知识点：\n{kp_list}\n\n学生的错题：\n{wrong_list}\n\n请给予分析、建议和练习题。"
    else:
        user_msg = f"学生刚刚完成了第 {chapter_id} 章：「{chapter_title}」。\n\n本章知识点：\n{kp_list}\n\n学生全部答对，没有错题！请给予表扬并出 2 道巩固练习题。"

    answer, error = _call_deepseek(CHAPTER_COMPLETE_PROMPT, user_msg, max_tokens=1000)
    if error:
        return jsonify({'success': False, 'answer': '', 'error': error})
    return jsonify({'success': True, 'answer': answer})


# ── 章节摘要 ────────────────────────────────────────────

@app.route('/api/chapter-summary/<int:chapter_id>')
def chapter_summary(chapter_id):
    """返回章节标题和知识点列表（供 CG 页面 / 面试页使用）"""
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if c['id'] == chapter_id), None)
    if not course:
        return jsonify({'success': False, 'message': '章节不存在'})
    return jsonify({
        'success': True,
        'chapter_id': chapter_id,
        'title': course['title'],
        'kp_titles': [kp['title'] for kp in course.get('knowledge_points', [])]
    })


# ── 星辰启示 CG ─────────────────────────────────────────

CHAPTER_REVELATION_PROMPT = """你是一位深谙 Python 编程之道的智慧导师，话语充满诗意与哲理。

任务：学生刚刚完成了 PyMaster 某一章节的学习，请你对这一章的核心知识给出一个哲学层面的启示与总结。

格式要求（严格150字以内）：
1. 开头：以编程/成长隐喻引入（如"在代码的森林里，每一个变量都遵循着自己的轨迹..."）
2. 中间：将本章核心技术点转化为哲理洞察（2-3句）
3. 结尾：一句激励学生继续探索的话

风格要求：
- 语言诗意但不晦涩，能让人感受到知识的美感
- 必须与该章节的核心主题高度相关
- 使用"🐍 ✨ 🌟 💻"中2-3个emoji点缀
- 绝对不要出现"这一章"、"知识点"、"学习"等教学用语
- 用隐喻而非直说

请返回纯JSON格式（不要包含其他内容）：
{"title": "3-6字的标题", "text": "150字内的哲理性启示文字"}"""


@app.route('/api/chapter-revelation/<int:chapter_id>')
def chapter_revelation(chapter_id):
    """生成章节完成后的哲学启示（星辰启示 CG 用）"""
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if c['id'] == chapter_id), None)
    if not course:
        return jsonify({'success': False, 'message': '章节不存在'})

    kp_titles = [kp['title'] for kp in course.get('knowledge_points', [])]
    user_msg = f"""学生刚刚完成了第{chapter_id}章：「{course['title']}」。
本章的核心知识点包括：{', '.join(kp_titles[:4])}等。
请生成哲理性启示。"""

    answer, error = _call_deepseek(CHAPTER_REVELATION_PROMPT, user_msg, max_tokens=400)
    if error:
        return jsonify({
            'success': True, 'title': '代码之路',
            'text': '🐍 你已穿越了代码的密林，每一行代码都是通往精通的路标。继续前行，编程者。',
            'chapter_title': course['title']
        })

    try:
        import re as _re
        json_match = _re.search(r'\{.*\}', answer, _re.DOTALL)
        result = json.loads(json_match.group()) if json_match else json.loads(answer)
        result['success'] = True
        result['chapter_title'] = course['title']
        return jsonify(result)
    except Exception as e:
        print(f"[启示CG] JSON解析失败: {e}")
        return jsonify({
            'success': True, 'title': '代码之路',
            'text': '✨ 每一个函数都是你与代码的对话。编程没有捷径，唯有动手才能找到真相。继续前进，编程者。',
            'chapter_title': course['title']
        })


# ── JJ老师 苏格拉底哲思面试 ─────────────────────────────

JJ_INTERVIEW_PROMPT = """你是蛇蛇老师——Python 编程世界里的哲思导师，一位引领初学者穿越知识海洋的智慧长者。

你的身份：
你不是冰冷的考官，而是一位亲切的 Python 编程导师。你说话温柔而富有哲理，但始终紧扣 Python 知识的本质。你记得每一位学员的旅程——他们的困惑、错误和成长。

核心规则：
1. 每次只问一个问题，等学员回答后再根据回答质量决定下一题
2. 如果回答优秀(8-10分)：给予鼓励，出一道更难的进阶题
3. 如果回答一般(5-7分)：温和指出不足，出一道同方向的深入追问
4. 如果回答差(1-4分)：不直接给答案，用苏格拉底式提问引导思考，再出一题
5. 至少进行3-5轮深度对话，直到你确认学员真正理解了知识
6. 每轮给出1-10分评分和简短评语(15字内)
7. 当学员展现出真正的深度理解后(done=true)，给出30字内的总结和评级(S/A/B/C)
8. 全程使用中文，语气温暖而鼓励，像一位耐心的编程导师
9. 用"小码"称呼学员
10. 问"Why"和"What if"类问题，考察推理而非记忆
11. 使用"🐍 ✨ 💻 🐣"等 Python 学习相关 emoji 点缀对话
12. 如果学员有错题记录，优先针对薄弱知识点提问
13. 如果学员有历史面试记录，展现"我记得你"的连续性

出题方向：
- 紧扣本章节的具体 Python 知识点，不能泛泛而谈
- 优先针对学员的错题涉及的知识点进行深度提问
- 考察概念间的联系，而非孤立的记忆
- 让学员展示真正的理解深度

返回纯JSON(不要markdown包裹)：
{"score":1-10,"comment":"简短评语","question":"下一题","done":false}
最后一轮done=true，question放总结祝福语"""


@app.route('/api/jj-interview', methods=['POST'])
def jj_interview():
    """JJ老师苏格拉底式追问面试——检验学员是否真正理解了本章知识"""
    data = request.get_json()
    action = data.get('action', 'start')
    history = data.get('history', [])
    user_answer = data.get('answer', '')
    chapter_id = str(data.get('chapter_id', '1'))
    chapter_title = data.get('chapter_title', '')
    kp_titles = data.get('kp_titles', [])
    wrong_answers = data.get('wrong_answers', [])

    username = session.get('username', 'guest')
    users = load_json(USERS_FILE)
    user = users.get(username, {})

    # Build past session summary from jj_interviews (avoid clashing with ask-jj's jj_history dict)
    past_summary = ''
    jj_interviews = user.get('jj_interviews', [])
    if jj_interviews:
        past_summary = '\n该学员的历史面试记录：\n'
        for rec in jj_interviews[-5:]:
            past_ch = rec.get('chapter_id', '?')
            qa_count = len(rec.get('qa_pairs', []))
            past_summary += f"- 第{past_ch}章：{qa_count}轮对话\n"

    if action == 'start':
        kp_list = '\n'.join(f"- {t}" for t in kp_titles)
        context_parts = [
            f"学员「小码」完成了第{chapter_id}章「{chapter_title}」的学习。",
            f"\n本章知识点：\n{kp_list}",
        ]
        if past_summary:
            context_parts.append(f"\n{past_summary}\n请展现你对这位学员的记忆——提到ta之前的学习历程。")
        if wrong_answers:
            wrong_list = '\n'.join(
                f"- 问题：{w.get('question','')} | 学员答案：{w.get('user_answer','')} | 正确：{w.get('correct_answer','')}"
                for w in wrong_answers
            )
            context_parts.append(f"\n学员本章错题（优先出题考察这些薄弱点）：\n{wrong_list}")
        else:
            context_parts.append("\n学员本章没有错题，请出一道有深度的综合理解题来检验真懂还是假懂。")

        user_msg = ''.join(context_parts)
    elif action == 'answer':
        recent = history[-12:]  # last 6 rounds
        htext = "\n".join([f"{'蛇蛇老师' if h['role']=='assistant' else '学员'}: {h['content'][:150]}" for h in recent])
        user_msg = f"对话历史：\n{htext}\n\n学员刚回答：{user_answer[:300]}\n\n请评分并决定：追问/进阶/总结。"
    elif action == 'skip':
        user_msg = "学员请求跳过。请出一道新题，方向不同。"
    else:
        return jsonify({'success': False, 'error': '未知操作'})

    answer, error = _call_deepseek(JJ_INTERVIEW_PROMPT, user_msg, max_tokens=800)
    if error:
        return jsonify({'success': False, 'error': error})

    try:
        import re as _re
        m = _re.search(r'\{[^{}]*\}', answer, _re.DOTALL)
        if m:
            r = json.loads(m.group())
            # If interview is done, save results to persistent memory
            if r.get('done'):
                _save_jj_results(username, chapter_id, history, r)
            return jsonify({'success': True, 'result': r, 'raw': answer})
    except json.JSONDecodeError:
        pass
    return jsonify({'success': True, 'result': None, 'raw': answer})


def _save_jj_results(username, chapter_id, history, final_result):
    """持久化 JJ 面试记录到用户数据，实现跨会话记忆"""
    users = load_json(USERS_FILE)
    if username not in users:
        return
    user = users[username]
    jj_interviews = user.setdefault('jj_interviews', [])

    qa_pairs = []
    current_q = ''
    for h in history:
        if h['role'] == 'assistant':
            current_q = h['content'][:200]
        elif h['role'] == 'user' and current_q:
            qa_pairs.append({
                'question': current_q,
                'answer': h['content'][:500],
                'score': 0,
                'comment': ''
            })
            current_q = ''

    jj_interviews.append({
        'chapter_id': int(chapter_id),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'qa_pairs': qa_pairs,
        'final_comment': final_result.get('question', '')[:100]
    })

    # Keep max 10 sessions per user to avoid bloating users.json
    if len(jj_interviews) > 10:
        user['jj_interviews'] = jj_interviews[-10:]
        jj_interviews = user['jj_interviews']

    save_json(USERS_FILE, users)


# ── JJ老师 章节末智能体复盘 ────────────────────────────

CHAPTER_AGENT_SYSTEM_PROMPT = """你是 PyMaster 学习平台的 JJ 老师——一个幽默、耐心、善于引导的 Python 编程老师，面对的是初中生水平的初学者。你的说话风格亲切热情，偶尔带点中二冒险感，像一位引导勇者的导师。

学生刚完成了「函数」章节的所有练习，你需要根据他们的「学习黑板书」（包含该生在本平台的全部学习记录）来进行一场有温度的复盘辅导。

## 你的核心任务

1. **个性化出题**：根据学生的错题记录、提问历史、代码分数，精准定位薄弱知识点，出针对性的短答题（1-2句话可答完）
2. **评估回答**：标准适当放宽，思路对就算对，但关键概念不能含糊
3. **答错时深度教学**：
   - 先耐心解释正确做法（用生活类比、画重点）
   - 然后问：「你明白了吗，冒险者？✨」
   - 如果学生说明白了 → 出一道同类但稍微变化的题验证
   - 如果学生仍不明白 → 换一种更简单的讲解方式再解释
   - 反复直到学生真正掌握该知识点（至少连续答对2道同类题才算掌握）
4. **答对时**：简短鼓励，然后检查该知识点是否已真正掌握，掌握则进入下一知识点
5. **至少覆盖 3 个不同知识点**，优先覆盖学生做错的、问过的问题相关的知识点
6. **所有知识点通过后**：给出富有哲理性的学习鼓励和冒险启示（100字左右，结合冒险隐喻）

## 学习掌握度追踪

用黑板上的 q_history 追踪每个知识点的掌握情况：
- 每个知识点需要连续答对 2 道同类题才算掌握
- 如果某个知识点答错，归零计数器，重新出同类题
- 掌握一个知识点后再进入下一个

## 回复格式

每次回复必须使用以下严格 JSON 格式（不要包含其他文字）：
{
  "type": "question" | "correct" | "wrong" | "done",
  "content": "回复内容（correct/wrong时的评语，done时的哲理鼓励）",
  "next_question": "下一题内容（仅 correct 或 wrong 时需要）",
  "next_hint": "下一题提示",
  "topic": "当前题目知识点",
  "mastery": { "topic_name": true/false }
}

type=question: 出题考察
type=correct: 学生答对，给出鼓励。检查该知识点是否已掌握（连续答对2次），如果已掌握出下一知识点，未掌握则继续出同类题
type=wrong: 学生答错，先解释教学，问"你明白了吗，冒险者？"，再出同类题
type=done: 所有知识点通过，给出冒险哲理性的鼓励

知识点范围：函数定义与调用、参数传递(位置/默认/*args/**kwargs)、返回值、LEGB作用域、高阶函数(map/filter/reduce)、装饰器、生成器"""


@app.route('/api/agent-blackboard', methods=['GET'])
def agent_blackboard():
    """返回用户的完整学习黑板书——所有跨章节的学习数据聚合"""
    username = session.get('username', 'guest')
    users = load_json(USERS_FILE)
    user = users.get(username, {})

    # 1. All wrong answers across all chapters
    wrong_answers = user.get('wrong_answers', [])

    # 2. All JJ Q&A history across all chapters
    jj_history = user.get('jj_history', {})

    # 3. Completed KPs per chapter
    completed_kps = user.get('completed_kps', [])

    # 4. Code scores (from submit-answer records)
    exercises = user.get('completed_exercises', [])

    # 5. Game data (from progress)
    progress = user.get('progress', {})

    # 6. Format all JJ history into readable text
    all_jj = []
    for ch_id, records in jj_history.items():
        for r in records[-10:]:  # last 10 per chapter
            all_jj.append({
                'chapter': ch_id,
                'question': r.get('question', '')[:200],
                'answer': r.get('answer', '')[:200],
            })

    # 7. Group wrong answers by topic (using KP index as proxy)
    wrong_by_topic = {}
    for w in wrong_answers:
        topic = f"ch{w.get('chapter_id')}_kp{w.get('kp_index', '?')}"
        if topic not in wrong_by_topic:
            wrong_by_topic[topic] = []
        wrong_by_topic[topic].append(w)

    return jsonify({
        'success': True,
        'username': username,
        'wrong_answers': wrong_answers[-30:],  # last 30
        'jj_history': all_jj[-30:],  # last 30
        'completed_kps': completed_kps,
        'completed_count': len(completed_kps),
        'progress': {k: v.get('knowledge', 0) for k, v in progress.items()},
    })


@app.route('/api/chapter-agent', methods=['POST'])
def chapter_agent():
    data = request.get_json()
    action = data.get('action', '')
    username = session.get('username', 'guest')
    users = load_json(USERS_FILE)
    user = users.get(username, {})

    # Collect wrong answers + JJ history for context
    chapter_id = '8'
    wrong_answers = user.get('wrong_answers', [])
    chapter_wrong = [w for w in wrong_answers if str(w.get('chapter_id', '')) == chapter_id]
    jj_history = user.get('jj_history', {}).get(chapter_id, [])

    # Format context
    wrong_text = "无"
    if chapter_wrong:
        wrong_lines = [f"- 问题：{w['question'][:80]} | 你的答案：{w.get('user_answer','')[:40]} | 正确答案：{w.get('correct_answer','')[:40]}" for w in chapter_wrong]
        wrong_text = '\n'.join(wrong_lines)

    jj_text = "无"
    if jj_history:
        jj_lines = [f"- 学生问：{h['question'][:100]}" for h in jj_history[-8:]]  # last 8
        jj_text = '\n'.join(jj_lines)

    # Also include wrong answers from OTHER chapters for broader context
    other_wrong = [w for w in wrong_answers if str(w.get('chapter_id', '')) != chapter_id]
    other_wrong_text = "无"
    if other_wrong:
        other_lines = [f"- (第{w.get('chapter_id')}章) {w['question'][:80]}" for w in other_wrong[-5:]]
        other_wrong_text = '\n'.join(other_lines)

    if action == 'start':
        # Generate first question
        user_msg = f"""学生刚完成了「函数」章节的全部学习任务。

【本章错题记录】
{wrong_text}

【本章向 JJ 老师请教过的问题】
{jj_text}

【其他章节的错题(可能涉及函数知识)】
{other_wrong_text}

请根据以上信息分析学生的薄弱点，出第一道有针对性的考察题。题目要简短，适合文字回答。"""

        answer, error = _call_deepseek(CHAPTER_AGENT_SYSTEM_PROMPT, user_msg, max_tokens=800)
        if error:
            return jsonify({'success': False, 'error': error})

        # Parse JSON from response
        try:
            import re as _re
            json_match = _re.search(r'\{.*\}', answer, _re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {'type': 'question', 'content': answer}
        except json.JSONDecodeError:
            result = {'type': 'question', 'content': answer}

        return jsonify({
            'success': True,
            'type': result.get('type', 'question'),
            'content': result.get('content', answer),
            'hint': result.get('next_hint', ''),
            'topic': result.get('topic', '函数基础'),
            'total': 3
        })

    elif action == 'answer':
        q_history = data.get('q_history', [])
        current_answer = data.get('current_answer', '').strip()
        current_question = data.get('current_question', '')
        is_confirmation = data.get('is_confirmation', False)

        # Build conversation context including mastery tracking
        history_lines = []
        for i, h in enumerate(q_history, 1):
            status = '✓ 已掌握' if h.get('correct') else '✗ 待复习'
            history_lines.append(f"""第{i}题（{h.get('topic', '未知')}）：
题目：{h.get('q', '')}
学生回答：{h.get('a', '')}
评价：{h.get('feedback', '')}
结果：{status}""")

        history_text = '\n\n'.join(history_lines) if history_lines else '尚无历史记录'

        confirmation_context = ""
        if is_confirmation:
            confirmation_context = """

【注意】学生正在回应你刚才的教学讲解，请判断：
- 如果学生表示理解（如"明白了"、"懂了"、"好的"等），请回复 type=correct，并在 next_question 中给出同类验证题
- 如果学生表示不理解（如"还是不懂"、"不太明白"等），请用更简单的方式再次讲解，再次询问"你明白了吗，冒险者？"，不出新题"""

        user_msg = f"""【学习黑板书 - 学生全貌】
本章错题：{wrong_text}
本章提问：{jj_text}
其他章节相关错题：{other_wrong_text}

【当前问答进度】
{history_text}

【最新回答】
题目：{current_question}
学生回答：{current_answer}{confirmation_context}

请评价学生的回答。记住掌握规则：每个知识点需连续答对2道同类题才算掌握。如果已经覆盖至少3个不同知识点且都掌握，请 type=done。"""

        answer, error = _call_deepseek(CHAPTER_AGENT_SYSTEM_PROMPT, user_msg, max_tokens=1000)
        if error:
            return jsonify({'success': False, 'error': error})

        try:
            import re as _re
            json_match = _re.search(r'\{.*\}', answer, _re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {'type': 'correct', 'content': answer}
        except json.JSONDecodeError:
            result = {'type': 'correct', 'content': answer}

        return jsonify({
            'success': True,
            'type': result.get('type', 'correct'),
            'content': result.get('content', ''),
            'next_question': result.get('next_question', ''),
            'next_hint': result.get('next_hint', ''),
            'next_topic': result.get('topic', '函数基础'),
            'mastery': result.get('mastery', {}),
            'done': result.get('type') == 'done'
        })

    return jsonify({'success': False, 'error': '未知操作'})

def update_progress():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    item_type = data.get('type', '')  # 'knowledge' or 'exercise'
    index = data.get('index', 0)

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    progress = users[username].setdefault('progress', {}).setdefault(chapter_id, {'knowledge': 0, 'exercises': 0, 'completed_items': []})

    item_key = f"{item_type}_{index}"
    if item_key not in progress.get('completed_items', []):
        progress.setdefault('completed_items', []).append(item_key)
        if item_type == 'knowledge':
            progress['knowledge'] = progress.get('knowledge', 0) + 1
        else:
            progress['exercises'] = progress.get('exercises', 0) + 1

    save_json(USERS_FILE, users)
    return jsonify({'success': True})


def _migrate_notes(notes):
    """Ensure all notes use the new object format {content, files}."""
    migrated = {}
    for k, v in notes.items():
        if isinstance(v, str):
            migrated[k] = {'content': v, 'files': []}
        elif isinstance(v, dict):
            migrated[k] = v
        else:
            migrated[k] = {'content': '', 'files': []}
    return migrated


def _platform_open_file(filepath):
    """Open a file with the system default app. Cross-platform safe."""
    import subprocess, os
    if not os.path.isfile(filepath):
        return False
    try:
        if sys.platform == 'win32':
            subprocess.Popen(['cmd', '/c', 'start', '', filepath], shell=True)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', filepath])
        else:
            subprocess.Popen(['xdg-open', filepath])
        return True
    except Exception:
        return False


def _platform_get_doc_path():
    """Get the best path for creating user-accessible files."""
    import tempfile
    if sys.platform == 'win32':
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.isdir(desktop):
            return desktop
        documents = os.path.join(os.path.expanduser('~'), 'Documents')
        if os.path.isdir(documents):
            return documents
    # On Linux/cloud, use a 'notes' subdirectory in the app root
    notes_dir = os.path.join(WRITE_ROOT, 'user_notes')
    os.makedirs(notes_dir, exist_ok=True)
    return notes_dir


@app.route('/api/user')
def get_user():
    username = session.get('username', 'guest')
    if username == 'guest':
        # 游客模式：返回默认数据，全部解锁
        return jsonify({
            'username': 'guest',
            'mode': 'all_unlocked',
            'completed_kps': [],
            'completed_exercises': [],
            'favorites': [],
            'wrong_answers': [],
            'notes': {}
        })
    users = load_json(USERS_FILE)
    user = users.get(username, {})
    return jsonify({
        'username': username,
        'mode': user.get('mode', 'explore'),
        'completed_kps': user.get('completed_kps', []),
        'completed_exercises': user.get('completed_exercises', []),
        'favorites': user.get('favorites', []),
        'wrong_answers': user.get('wrong_answers', []),
        'notes': _migrate_notes(user.get('notes', {}))
    })


@app.route('/api/ai-quota')
def get_ai_quota():
    username = session.get('username', 'guest')
    if username == 'guest':
        # 游客模式：无限使用
        return jsonify({
            'success': True,
            'used': 0,
            'limit': -1,
            'remaining': -1,
            'is_unlimited': True
        })
    allowed, used, limit = check_daily_limit(username)
    return jsonify({
        'success': True,
        'used': used,
        'limit': limit if limit > 0 else -1,
        'remaining': (limit - used) if limit > 0 else -1,
        'is_unlimited': limit <= 0
    })


@app.route('/api/set-mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    new_mode = data.get('mode', 'explore')
    if new_mode not in ('explore', 'all_unlocked'):
        return jsonify({'success': False, 'message': '无效模式'})
    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username in users:
        users[username]['mode'] = new_mode
        save_json(USERS_FILE, users)
    return jsonify({'success': True, 'mode': new_mode})


@app.route('/api/learning-status')
def learning_status():
    courses = load_json(COURSES_FILE)
    username = session.get('username', 'guest')
    if username == 'guest':
        # 游客模式：全部解锁
        result = {}
        for c in courses:
            ch = c['id']
            kps = c.get('knowledge_points', [])
            for i in range(len(kps)):
                result[f"{ch}_{i}"] = True
        return jsonify({'success': True, 'unlocked': result, 'mode': 'all_unlocked',
                        'completed_kps': []})
    users = load_json(USERS_FILE)
    user = users.get(username, {})
    completed_kps = user.get('completed_kps', [])
    mode = user.get('mode', 'explore')
    result = {}
    if mode == 'all_unlocked':
        for c in courses:
            ch = c['id']
            kps = c.get('knowledge_points', [])
            for i in range(len(kps)):
                result[f"{ch}_{i}"] = True
    else:
        unlock = get_unlock_status(courses, completed_kps, mode)
        for c in courses:
            ch = c['id']
            kps = c.get('knowledge_points', [])
            for i in range(len(kps)):
                result[f"{ch}_{i}"] = (ch, i) in unlock
    return jsonify({'success': True, 'unlocked': result, 'mode': mode,
                    'completed_kps': completed_kps})


@app.route('/api/glossary')
def get_glossary():
    glossary_file = os.path.join(BUNDLE_DIR, 'data', 'glossary_py.json')
    if not os.path.exists(glossary_file):
        return jsonify({'success': False, 'message': '术语数据不存在'})
    terms = load_json(glossary_file)
    return jsonify({'success': True, 'terms': terms})


# ── 用户思维导图 ────────────────────────────────────────

@app.route('/api/mindmap/save', methods=['POST'])
def save_mindmap():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    content = data.get('content', '')

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False, 'message': '用户不存在'})

    user_mindmaps = users[username].setdefault('user_mindmaps', {})
    user_mindmaps[chapter_id] = {
        'content': content,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_json(USERS_FILE, users)
    return jsonify({'success': True})


@app.route('/api/mindmap/get', methods=['GET'])
def get_mindmap():
    chapter_id = request.args.get('chapter_id', '')

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False, 'content': '', 'updated_at': ''})

    user_mindmaps = users[username].get('user_mindmaps', {})
    data = user_mindmaps.get(chapter_id, {})
    return jsonify({
        'success': True,
        'content': data.get('content', ''),
        'updated_at': data.get('updated_at', '')
    })


@app.route('/api/mindmap/delete', methods=['POST'])
def delete_mindmap():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    user_mindmaps = users[username].get('user_mindmaps', {})
    if chapter_id in user_mindmaps:
        del user_mindmaps[chapter_id]
        save_json(USERS_FILE, users)
    return jsonify({'success': True})


@app.route('/api/complete-kp', methods=['POST'])
def complete_kp():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    kp_index = str(data.get('kp_index', '0'))
    key = f"{chapter_id}_{kp_index}"

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    completed = users[username].setdefault('completed_kps', [])
    if key not in completed:
        completed.append(key)
    save_json(USERS_FILE, users)

    # Also update legacy progress
    users[username].setdefault('progress', {}).setdefault(chapter_id, {}).setdefault('completed_items', [])
    item_key = f"knowledge_{kp_index}"
    if item_key not in users[username]['progress'][chapter_id]['completed_items']:
        users[username]['progress'][chapter_id]['completed_items'].append(item_key)
        users[username]['progress'][chapter_id]['knowledge'] = users[username]['progress'][chapter_id].get('knowledge', 0) + 1
    save_json(USERS_FILE, users)

    return jsonify({'success': True, 'key': key})


@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    kp_index = int(data.get('kp_index', 0))
    ex_index = int(data.get('ex_index', 0))
    is_correct = data.get('correct', False)
    question = data.get('question', '')
    user_answer = data.get('user_answer', '')
    correct_answer = data.get('correct_answer', '')

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    # Track completed exercises
    ex_key = f"{chapter_id}_{kp_index}_{ex_index}"
    completed_ex = users[username].setdefault('completed_exercises', [])
    if is_correct and ex_key not in completed_ex:
        completed_ex.append(ex_key)

    # Track wrong answers
    if not is_correct:
        wrong = users[username].setdefault('wrong_answers', [])
        wrong.append({
            'chapter_id': chapter_id,
            'kp_index': kp_index,
            'ex_index': ex_index,
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'correct': is_correct, 'ex_key': ex_key})


@app.route('/api/toggle-favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    ex_index = str(data.get('ex_index', '0'))
    question = data.get('question', '')
    key = f"{chapter_id}_{ex_index}"

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    favs = users[username].setdefault('favorites', [])
    existing = next((f for f in favs if f.get('key') == key), None)
    if existing:
        favs.remove(existing)
        is_fav = False
    else:
        favs.append({'key': key, 'question': question,
                     'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        is_fav = True

    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'is_favorite': is_fav})


@app.route('/api/save-note', methods=['POST'])
def save_note():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    kp_index = str(data.get('kp_index', '0'))
    note_content = data.get('content', '')

    key = f"{chapter_id}_{kp_index}"
    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    notes = users[username].setdefault('notes', {})

    # Migrate old string format to object format
    existing = notes.get(key)
    if isinstance(existing, str):
        existing = {'content': existing, 'files': []}
    elif not isinstance(existing, dict):
        existing = {'content': '', 'files': []}

    if note_content.strip():
        existing['content'] = note_content
        notes[key] = existing
    elif key in notes:
        if existing.get('files'):
            existing['content'] = ''
            notes[key] = existing
        else:
            del notes[key]

    save_json(USERS_FILE, users)
    return jsonify({'success': True})


def _get_note_obj(users, username, key):
    """Get note object (with content+files), migrating from old string format."""
    notes = users[username].setdefault('notes', {})
    existing = notes.get(key)
    if isinstance(existing, str):
        obj = {'content': existing, 'files': []}
        notes[key] = obj
        return obj
    if isinstance(existing, dict):
        return existing
    obj = {'content': '', 'files': []}
    notes[key] = obj
    return obj


# ---- Note Files API ----

@app.route('/api/note-files/list', methods=['POST'])
def note_files_list():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    kp_index = str(data.get('kp_index', '0'))
    key = f"{chapter_id}_{kp_index}"

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': True, 'note': {'content': '', 'files': []}})

    note = _get_note_obj(users, username, key)
    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'note': note})


@app.route('/api/note-files/create-txt', methods=['POST'])
def note_files_create_txt():
    """Create a .txt file and add to note file list. Opens in editor if desktop available."""
    try:
        import os, time
        data = request.get_json()
        chapter_id = str(data.get('chapter_id', ''))
        kp_index = str(data.get('kp_index', '0'))
        key = f"{chapter_id}_{kp_index}"

        doc_path = _platform_get_doc_path()
        filename = f"PyMaster_笔记_第{chapter_id}章_{kp_index}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(doc_path, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"PyMaster 学习笔记\n")
            f.write(f"第 {chapter_id} 章 · 知识点 {kp_index}\n")
            f.write(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 40 + "\n\n")
            f.write("")

        users = load_json(USERS_FILE)
        username = session.get('username', 'guest')
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        note = _get_note_obj(users, username, key)
        file_entry = {
            'path': filepath,
            'name': filename,
            'type': 'txt',
            'created': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        note['files'].append(file_entry)
        save_json(USERS_FILE, users)

        opened = _platform_open_file(filepath)
        is_desktop = sys.platform == 'win32'

        return jsonify({
            'success': True, 'file': file_entry,
            'opened': opened, 'is_desktop': is_desktop,
            'message': f'文件已创建: {filepath}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/note-files/add', methods=['POST'])
def note_files_add():
    """Add a local file to the note list. Desktop file dialog on Windows only."""
    try:
        import os, time

        data = request.get_json()
        chapter_id = str(data.get('chapter_id', ''))
        kp_index = str(data.get('kp_index', '0'))
        key = f"{chapter_id}_{kp_index}"

        filepath = None

        if sys.platform == 'win32':
            # Desktop file picker on Windows
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            filepath = filedialog.askopenfilename(
                title='选择要关联到笔记的文件',
                filetypes=[
                    ('所有支持的文件', '*.txt;*.py;*.md;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.pdf;*.jpg;*.png;*.gif;*.bmp'),
                    ('文本文件', '*.txt;*.md'),
                    ('Python 代码', '*.py'),
                    ('文档', '*.docx;*.doc;*.pdf'),
                    ('所有文件', '*.*')
                ]
            )
            root.destroy()
        else:
            # On Linux/cloud, this feature is not available
            return jsonify({'success': False, 'error': 'desktop_only',
                            'message': '此功能仅在桌面版可用'})

        if not filepath:
            return jsonify({'success': True, 'file': None})

        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lstrip('.').lower() or 'unknown'

        users = load_json(USERS_FILE)
        username = session.get('username', 'guest')
        if username not in users:
            return jsonify({'success': False, 'error': 'User not found'})

        note = _get_note_obj(users, username, key)
        # Avoid duplicates by path
        for f in note['files']:
            if f['path'] == filepath:
                _platform_open_file(filepath)
                return jsonify({'success': True, 'file': f})

        file_entry = {
            'path': filepath,
            'name': filename,
            'type': ext,
            'created': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        note['files'].append(file_entry)
        save_json(USERS_FILE, users)

        _platform_open_file(filepath)
        return jsonify({'success': True, 'file': file_entry})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/note-files/open', methods=['POST'])
def note_files_open():
    """Open a file with the system default application."""
    try:
        import os
        data = request.get_json()
        filepath = data.get('file_path', '')
        if not filepath or not os.path.isfile(filepath):
            return jsonify({'success': False, 'error': '文件不存在或路径无效'})

        opened = _platform_open_file(filepath)
        if opened:
            return jsonify({'success': True})
        else:
            # On non-desktop platforms, try to serve the file as a download
            return jsonify({'success': False, 'error': 'desktop_only',
                            'message': '此功能仅在桌面版可用'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/note-files/remove', methods=['POST'])
def note_files_remove():
    """Remove a file from the note's file list (does NOT delete the actual file)."""
    try:
        data = request.get_json()
        chapter_id = str(data.get('chapter_id', ''))
        kp_index = str(data.get('kp_index', '0'))
        file_path = data.get('file_path', '')
        key = f"{chapter_id}_{kp_index}"

        users = load_json(USERS_FILE)
        username = session.get('username', 'guest')
        if username not in users:
            return jsonify({'success': False})

        note = _get_note_obj(users, username, key)
        note['files'] = [f for f in note['files'] if f['path'] != file_path]
        save_json(USERS_FILE, users)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/clear-wrong', methods=['POST'])
def clear_wrong():
    data = request.get_json()
    indices = data.get('indices', [])  # list of wrong answer indices to clear

    users = load_json(USERS_FILE)
    username = session.get('username', 'guest')
    if username not in users:
        return jsonify({'success': False})

    wrong = users[username].get('wrong_answers', [])
    if indices:
        users[username]['wrong_answers'] = [w for i, w in enumerate(wrong) if i not in indices]
    else:
        users[username]['wrong_answers'] = []

    save_json(USERS_FILE, users)
    return jsonify({'success': True})


# ── Comic Engine Endpoints ─────────────────────────────────

# Load pre-generated comics (Claude-generated, high quality)
COMICS_FILE = os.path.join(BUNDLE_DIR, 'data', 'comics.json')

def load_comics():
    if not os.path.exists(COMICS_FILE):
        return {}
    with open(COMICS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/api/comic/<int:chapter_id>/<int:kp_index>')
def get_comic(chapter_id, kp_index):
    """Return a pre-generated comic script (Claude quality), or generate one."""
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if c['id'] == chapter_id), None)
    if not course:
        return jsonify({'success': False, 'message': '章节不存在'})

    kps = course.get('knowledge_points', [])
    if kp_index < 0 or kp_index >= len(kps):
        return jsonify({'success': False, 'message': '知识点不存在'})

    kp = kps[kp_index]
    comic_key = f"{chapter_id}_{kp_index}"

    # Try pre-generated comic first (Claude quality)
    pregen = load_comics()
    if comic_key in pregen:
        comic_data = pregen[comic_key]
        username = session.get('username', 'anonymous')
        comic_memory.record_view(username, chapter_id, kp_index, kp['title'])
        return jsonify({
            'success': True,
            'comic': {
                'title': comic_data['title'],
                'chapter_title': comic_data['chapter_title'],
                'kp_title': comic_data['kp_title'],
                'total_panels': len(comic_data['panels']),
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'generated_by': 'claude',
                'has_api': comic_engine.is_available(),
                'panels': comic_data['panels'],
                'characters': {
                    'teacher': {
                        'name': '蛇蛇老师',
                        'avatar': '🐍',
                        'role': 'Python 专家，耐心幽默'
                    },
                    'student': {
                        'name': '小码',
                        'avatar': '🐣',
                        'role': '好奇的学生，正在学编程'
                    }
                }
            }
        })

    # Fallback: use template engine for comics not pre-generated
    force_ai = request.args.get('ai', '0') == '1' and comic_engine.is_available()
    script = comic_engine.generate(
        chapter_title=course['title'],
        kp_title=kp['title'],
        kp_content=kp['content'],
        chapter_id=chapter_id,
        kp_index=kp_index
    )

    username = session.get('username', 'anonymous')
    comic_memory.record_view(username, chapter_id, kp_index, kp['title'])

    return jsonify({
        'success': True,
        'comic': {
            'title': script.title,
            'chapter_title': script.chapter_title,
            'kp_title': script.kp_title,
            'total_panels': script.total_panels,
            'generated_at': script.generated_at,
            'generated_by': 'template',
            'has_api': comic_engine.is_available(),
            'panels': [
                {
                    'panel_id': p.panel_id,
                    'character': p.character,
                    'character_name': p.character_name,
                    'avatar': p.avatar,
                    'dialog': p.dialog,
                    'expression': p.expression,
                    'scene': p.scene,
                    'knowledge_bite': p.knowledge_bite
                }
                for p in script.panels
            ],
            'characters': {
                'teacher': {
                    'name': ComicEngine.CHARACTERS['teacher']['name'],
                    'avatar': ComicEngine.CHARACTERS['teacher']['avatar'],
                    'role': ComicEngine.CHARACTERS['teacher']['role']
                },
                'student': {
                    'name': ComicEngine.CHARACTERS['student']['name'],
                    'avatar': ComicEngine.CHARACTERS['student']['avatar'],
                    'role': ComicEngine.CHARACTERS['student']['role']
                }
            }
        }
    })


@app.route('/api/comic/stats')
def get_comic_stats():
    """Get comic viewing statistics for the current user."""
    username = session.get('username', 'anonymous')
    stats = comic_memory.get_stats(username)
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/comic/config', methods=['POST'])
def configure_comic_engine():
    """Configure the comic engine API settings."""
    data = request.get_json()
    api_key = data.get('api_key', '').strip()
    api_base = data.get('api_base', '').strip()
    model = data.get('model', 'gpt-4o').strip()

    if api_key:
        comic_engine.api_key = api_key
    if api_base:
        comic_engine.api_base = api_base
    if model:
        comic_engine.model = model

    return jsonify({
        'success': True,
        'message': '配置已更新',
        'has_api': comic_engine.is_available()
    })


# ── TTS Voice Endpoints ────────────────────────────────────

@app.route('/api/tts/panel/<int:chapter_id>/<int:kp_index>/<int:panel_id>')
def get_panel_audio(chapter_id, kp_index, panel_id):
    """Get Doubao TTS audio for a comic panel. Returns MP3 stream."""
    comic_key = f"{chapter_id}_{kp_index}"
    pregen = load_comics()
    if comic_key not in pregen:
        return jsonify({'success': False, 'message': '漫画不存在'})

    panels = pregen[comic_key]['panels']
    panel = next((p for p in panels if p['panel_id'] == panel_id), None)
    if not panel:
        return jsonify({'success': False, 'message': '面板不存在'})

    if not tts_engine.is_available():
        return jsonify({'success': False, 'message': 'TTS 未配置', 'fallback': 'browser'})

    text = panel.get('dialog', '')
    character = panel.get('character', 'teacher')
    audio = tts_engine.synthesize(text, character)

    if audio:
        from flask import Response
        return Response(audio, mimetype='audio/mpeg',
                        headers={'Cache-Control': 'public, max-age=86400'})
    return jsonify({'success': False, 'message': '豆包 TTS 生成失败，请尝试浏览器语音', 'fallback': 'browser'})


@app.route('/api/tts/status')
def tts_status():
    """Check TTS availability."""
    return jsonify({
        'success': True,
        'edge_tts_available': tts_engine.is_available(),
        'doubao_available': doubao_tts.is_available(),
        'browser_available': True,
        'primary': 'edge-tts',
    })


@app.route('/api/tts/voices')
def get_tts_voices():
    """Get available TTS voice configurations."""
    return jsonify({
        'success': True,
        'server_tts_available': tts_engine.is_available(),
        'browser_tts_available': True,
        'primary_engine': 'edge-tts',
        'voices': {
            'teacher': {
                'browser': BrowserTTS.get_voice_config('teacher'),
                'server': EdgeTTS.VOICES.get('teacher', {}),
            },
            'student': {
                'browser': BrowserTTS.get_voice_config('student'),
                'server': EdgeTTS.VOICES.get('student', {}),
            },
            'narrator': {
                'browser': BrowserTTS.get_voice_config('narrator'),
                'server': EdgeTTS.VOICES.get('narrator', {}),
            },
        }
    })


# ── Admin Panel ────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session or session.get('username', 'guest') != ADMIN_USERNAME:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
            session['username'] = ADMIN_USERNAME
            return jsonify({'success': True}) if request.is_json else redirect(url_for('admin_dashboard'))
        return jsonify({'success': False, 'message': '管理员账号或密码错误'}) if request.is_json else ('', 403)
    return render_template('admin_login.html')


@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')


@app.route('/admin/api/whitelist', methods=['GET', 'POST'])
@admin_required
def admin_whitelist():
    wl = _load_whitelist()

    if request.method == 'GET':
        # Enrich with usage stats
        usage = _load_daily_usage()
        today = datetime.now().strftime('%Y-%m-%d')
        today_usage = usage.get(today, {})
        users = load_json(USERS_FILE)

        result = []
        for username, entry in wl.items():
            result.append({
                'username': username,
                'expiry_date': entry.get('expiry_date', ''),
                'daily_limit': entry.get('daily_limit', 0),
                'note': entry.get('note', ''),
                'created_at': entry.get('created_at', ''),
                'today_used': today_usage.get(username, 0),
                'is_registered': username in users,
                'is_active': is_whitelisted(username),
            })
        return jsonify({'success': True, 'users': result})

    # POST: add or update
    data = request.get_json()
    username = data.get('username', '').strip()
    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'})

    wl[username] = {
        'expiry_date': data.get('expiry_date', ''),
        'daily_limit': int(data.get('daily_limit', 0)),
        'note': data.get('note', ''),
        'created_at': wl.get(username, {}).get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    }
    _save_whitelist(wl)
    return jsonify({'success': True, 'message': f'用户 {username} 已添加到白名单'})


@app.route('/admin/api/whitelist/<username>', methods=['DELETE'])
@admin_required
def admin_whitelist_delete(username):
    wl = _load_whitelist()
    if username in wl:
        del wl[username]
        _save_whitelist(wl)
    return jsonify({'success': True, 'message': f'用户 {username} 已从白名单移除'})


@app.route('/admin/api/stats')
@admin_required
def admin_stats():
    usage = _load_daily_usage()
    wl = _load_whitelist()
    today = datetime.now().strftime('%Y-%m-%d')
    today_usage = usage.get(today, {})

    # Calculate total usage (last 30 days)
    from collections import Counter
    total_calls = Counter()
    for date_str, day_data in usage.items():
        for uname, count in day_data.items():
            total_calls[uname] += count

    return jsonify({
        'success': True,
        'stats': {
            'total_whitelist': len(wl),
            'total_registered': sum(1 for u in wl if u in load_json(USERS_FILE)),
            'today_total_calls': sum(today_usage.values()),
            'today_users': len(today_usage),
            'daily_breakdown': {k: v for k, v in sorted(usage.items(), reverse=True)[:30]},
        }
    })


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})
    if not os.path.exists(WHITELIST_FILE):
        _save_whitelist({})

    # Kill any existing Python process on port 5000 (old dev servers)
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 5000))
        sock.close()
        del sock
    except OSError:
        del sock
        print("[PyMaster] Port 5000 is busy; cleaning the old process...")
        try:
            import subprocess
            result = subprocess.run(
                ['netstat', '-ano'], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                if '127.0.0.1:5000' in line and 'LISTEN' in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    subprocess.run(['taskkill', '/F', '/PID', pid],
                                   capture_output=True, timeout=3)
                    print(f"[PyMaster] Terminated old process (PID: {pid})")
                    break
        except Exception:
            print("[PyMaster] Could not clean the port automatically.")

    print("[PyMaster] Started at http://127.0.0.1:5000")
    # Production: use 0.0.0.0 and PORT env var (Railway provides PORT)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
