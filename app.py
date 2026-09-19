import json
import os
import sys
import ast
import base64
import binascii
import hashlib
import secrets
import subprocess
import shutil
import tempfile
import time
import re
import urllib.request
import urllib.error
import urllib.parse
import threading
import socket
import uuid
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import quote
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask import Response, send_file

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

# 可写数据目录：账号、进度、笔记、讲解音频缓存都落在这里。
#   本地版：项目根下的 data/，与以前完全一致。
#   容器版：用 PYMASTER_DATA_DIR 指向挂载卷。这样做而不是"把整个 data/ 挂上去"，
#          是因为一挂上去就会把镜像里 data/ 的课程与题库一起盖掉，
#          表现是首页直接报错、刷题页空白 —— 一个很贵的坑。
DATA_DIR = os.environ.get('PYMASTER_DATA_DIR', '').strip() or os.path.join(WRITE_ROOT, 'data')

# 可写目录里缺了"随包数据"就补一份进来。空卷挂载时靠这一步做到开箱即用；
# 也顺带让"老师换了课程数据"这种场景可以直接替换可写目录里的那份。
SEED_FILES = ('courses.json', 'question_bank.json', 'narrations.json',
              'glossary_py.json', 'comics.json', 'courses_legacy_9ch.json')


def _seed_data_dir():
    src_dir = Path(BUNDLE_DIR) / 'data'
    dst_dir = Path(DATA_DIR)
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f'[data] 无法创建数据目录 {dst_dir}：{exc}')
        return
    for name in SEED_FILES:
        src, dst = src_dir / name, dst_dir / name
        if src.exists() and not dst.exists():
            try:
                shutil.copy2(src, dst)
                print(f'[data] 已初始化 {name}')
            except OSError as exc:
                print(f'[data] 初始化 {name} 失败：{exc}')


from comic_engine import ComicEngine, ComicMemory
from tts_engine import EdgeTTS, DoubaoTTS, BrowserTTS
import narration_engine
import training_engine as training
import game_engine as game          # 修行阁：修为的成长系统（纯推导，不持有状态）
import coach_engine as coach
from pathlib import Path

_seed_data_dir()

# 讲解产物的读写位置跟随 PyInstaller 的 BUNDLE/WRITE 约定：
# 生成的 json/音频要写到可写目录，静态插画随包分发。
narration_engine.ROOT = Path(WRITE_ROOT)
narration_engine.DATA_DIR = Path(DATA_DIR)
narration_engine.AUDIO_CACHE = narration_engine.DATA_DIR / 'audio_cache'
narration_engine.STATIC_NARR_DIR = Path(BUNDLE_DIR) / 'static' / 'narrations'
for _candidate in (Path(DATA_DIR) / 'narrations.json',
                   Path(BUNDLE_DIR) / 'data' / 'narrations.json'):
    if _candidate.exists():
        narration_engine.NARRATIONS_FILE = _candidate
        break
else:
    narration_engine.NARRATIONS_FILE = Path(DATA_DIR) / 'narrations.json'
narration_engine.AUDIO_CACHE.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
# 持久化 secret key：存到 data 目录，重启后 session 不失效（否则每次重启所有用户被登出，
# 所有需登录的 API 都会 302 重定向，前端表现为"接口报错/转圈"）
SECRET_KEY_FILE = os.path.join(DATA_DIR, '.secret_key')
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

# 单机版没有"登录页"这一步的耐心：注册一次之后，下次打开就应该还是自己。
# 会话 Cookie 默认随浏览器关闭就失效，这里改成一年，实现"记住我"的效果。
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Writable data: next to exe (or project root for dev)
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
WHITELIST_FILE = os.path.join(DATA_DIR, 'whitelist.json')
DAILY_USAGE_FILE = os.path.join(DATA_DIR, 'daily_usage.json')
# Read-only course data: bundled with exe（可写目录里有就用可写目录那份）
COURSES_FILE = os.path.join(DATA_DIR, 'courses.json')
if not os.path.exists(COURSES_FILE):
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
    """旧格式：裸 sha256。仅用于兼容老账号，新密码一律走下面的 PBKDF2。"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def hash_password_new(password, salt=None):
    """加盐慢哈希。本地版账号密码就存在用户自己电脑上，但也别明文等价保存。

    返回 (算法标记, 盐, 摘要)；老账号没有这些字段时按 hash_password 校验。
    """
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 120_000)
    return 'pbkdf2', salt, digest.hex()


def verify_password(record, password):
    """兼容两种存法：新的 PBKDF2 与老账号的裸 sha256。"""
    if not isinstance(record, dict):
        return False
    stored = record.get('password') or ''
    if record.get('password_salt'):
        _, _, digest = hash_password_new(password, record['password_salt'])
        return secrets.compare_digest(digest, stored)
    return secrets.compare_digest(hash_password(password), stored)


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


# ── 在线运行代码的安全开关 ─────────────────────────────────
# 判题与"运行代码"是把学生提交的 Python 在子进程里真跑一遍，没有沙箱
# （详见 上线操作手册.md 第三节）。本地版这样最省事，但一旦有公网地址，
# 等于把机器借给任何人执行代码。所以线上部署时设：
#
#   PYMASTER_ALLOW_CODE_EXEC=0
#
# 生效后这几条链路会返回一句人话，其余功能（课程正文、练习解析、AI 答疑、
# 星海图、术语表）完全不受影响。语法检查走 ast.parse，不执行代码，保持可用。

CODE_EXEC_OFF_MESSAGE = (
    '这台服务器没有开启「在线运行代码」：它会把提交的 Python 真实跑一遍，'
    '没有沙箱隔离，所以公网部署默认关闭。课程正文、练习解析、AI 答疑都能照常用；'
    '要动手写代码，请下载本地完整版，解压后双击启动脚本即可。'
)


def code_exec_enabled():
    return os.environ.get('PYMASTER_ALLOW_CODE_EXEC', '1').strip().lower() \
        not in ('0', 'false', 'no', 'off')


@app.route('/')
def index():
    # 第一次打开（含从旧版本更新上来的用户）先走一遍开场 CG。
    # 看过的标记放在 Cookie 里：换浏览器会再看一遍，这在单机版是可接受的，
    # 而"每次启动都重放"才是真正会被嫌弃的行为。
    if not request.cookies.get(INTRO_COOKIE):
        return redirect(url_for('intro_page'))
    # 未登录也直接进入仪表盘（游客模式），保证GitHub页面可完整访问
    return redirect(url_for('dashboard'))


# ── 开场引导 CG ────────────────────────────────────────────
# 用户的第一次接触不是登录框，而是一部分钟左右的短片：Python 的来历、
# Python 之禅、Guido 本人、以及 AI 时代它为什么是第一语言。
# 放在此处还有一个作用：把"配置密钥"这类枯燥的第一次被推后到情绪被点燃之后。

INTRO_COOKIE = 'pymaster_intro'


@app.route('/intro')
def intro_page():
    return render_template('intro_cg.html',
                           next_url=url_for('intro_done'),
                           static_mode=False)


@app.route('/intro/done')
def intro_done():
    """片尾出口：按当前状态决定去哪儿，并记下"开场已看过"。"""
    if not ai_config_status()['configured']:
        target = url_for('setup_wizard')
    elif 'username' not in session:
        target = url_for('login_page')
    else:
        target = url_for('dashboard')
    resp = redirect(target)
    resp.set_cookie(INTRO_COOKIE, '1', max_age=365 * 24 * 3600,
                    samesite='Lax', httponly=True)
    return resp


@app.route('/login')
def login_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


# ── 首次运行配置向导 ───────────────────────────────────────
# 用户下载压缩包后第一次打开，要先注册账号并填自己的模型配置。
# 这些以前只能在终端里靠 setup_api.py 问答完成，现在改成网页向导。

SETUP_EXEMPT_PREFIXES = ('/setup', '/api/setup', '/static', '/login', '/api/login',
                         '/api/register', '/logout', '/favicon.ico', '/oauth',
                         # 开场 CG 要在配置向导之前播，否则新用户见到的是
                         # 一张要填密钥的表单，短片就没机会放了
                         '/intro',
                         # 配置向导第一步要列出本机账号、第二步要设置头像，
                         # 这两个接口被重定向到 /setup 的话，向导自己就先坏了
                         '/api/accounts', '/api/avatar', '/avatar')


@app.before_request
def require_ai_config():
    """AI 没配置好就把用户引到配置向导，避免进去之后处处报错。"""
    path = request.path or '/'
    if path.startswith(SETUP_EXEMPT_PREFIXES):
        return None
    # 会话里记着的账号可能已经不存在了（用户按使用说明清过 users.json、
    # 或换了 data 目录）。这种"幽灵登录"要退回游客，否则界面显示着一个
    # 已经不存在的账号，进度却怎么都不保存
    username = session.get('username')
    if username and username != 'guest' and username not in load_json(USERS_FILE):
        session.pop('username', None)
    if ai_config_status()['configured']:
        return None
    return redirect(url_for('setup_wizard'))


@app.route('/setup')
def setup_wizard():
    status = ai_config_status()
    return render_template('setup.html',
                           configured=status['configured'],
                           base_url=status['base_url'],
                           model=status['model'],
                           key_tail=status['key_tail'],
                           fallback=status['fallback'],
                           logged_in='username' in session,
                           username=session.get('username', ''),
                           open_registration=registration_is_open(),
                           wechat_ready=wechat_login_ready())


@app.route('/api/setup/test', methods=['POST'])
def setup_test_connection():
    """测试用户填的模型配置是否真的能用。"""
    data = request.get_json(silent=True) or {}
    base_url = (data.get('base_url') or '').strip()
    model = (data.get('model') or '').strip()
    api_key = (data.get('api_key') or '').strip()

    if not base_url or not model:
        return jsonify({'success': False, 'message': '接口地址和模型名称都要填'})
    if not base_url.startswith(('http://', 'https://')):
        return jsonify({'success': False, 'message': '地址要以 http:// 或 https:// 开头'})

    # 密钥那栏留空（或带着 **** 掩码）都表示"不改密钥"：界面上就是这么写的，
    # 所以这里必须沿用已保存的那把，不能反过来要求用户重输一遍
    if not api_key or api_key.startswith('****'):
        api_key = read_env_file().get('ARK_API_KEY', '')
        if not api_key:
            return jsonify({'success': False, 'message': '请填写 API Key'})

    ok, message = test_ai_connection(base_url, model, api_key)
    return jsonify({'success': ok, 'message': message})


@app.route('/api/setup/save', methods=['POST'])
def setup_save_config():
    """保存配置并立即生效，不需要重启。"""
    data = request.get_json(silent=True) or {}
    base_url = (data.get('base_url') or '').strip()
    model = (data.get('model') or '').strip()
    api_key = (data.get('api_key') or '').strip()
    fallback = (data.get('fallback') or '').strip()

    if not base_url or not model:
        return jsonify({'success': False, 'message': '接口地址和模型名称都要填'})
    # 同上：密钥留空表示沿用已保存的，只有一次都没配过才要求填
    if not api_key or api_key.startswith('****'):
        api_key = read_env_file().get('ARK_API_KEY', '')
        if not api_key:
            return jsonify({'success': False, 'message': '请填写 API Key'})

    status = apply_ai_config(base_url, model, api_key, fallback)
    return jsonify({
        'success': True,
        'message': '配置已保存并生效',
        'warnings': [],
        'status': {'base_url': status['base_url'], 'model': status['model'],
                   'key_tail': status['key_tail']},
    })


def wechat_login_ready():
    """微信扫码登录需要微信开放平台网站应用的 AppID/Secret 与公网回调地址。"""
    env = read_env_file()
    return bool(env.get('WECHAT_APP_ID') and env.get('WECHAT_APP_SECRET')
                and env.get('OAUTH_CALLBACK_BASE'))


# ── 微信扫码登录（OAuth2）────────────────────────────────
# 说明：微信扫码的整个流程都要由微信服务器回调到你的公网地址，
# 所以只在自己电脑上跑（127.0.0.1）是跑不通的。
# 这里的实现是完整的，配置好下面三项即可启用：
#   WECHAT_APP_ID / WECHAT_APP_SECRET   微信开放平台「网站应用」的凭证
#   OAUTH_CALLBACK_BASE                 公网可访问的地址，例如 https://your.domain

WECHAT_AUTHORIZE = 'https://open.weixin.qq.com/connect/qrconnect'
WECHAT_TOKEN_API = 'https://api.weixin.qq.com/sns/oauth2/access_token'
WECHAT_USERINFO_API = 'https://api.weixin.qq.com/sns/userinfo'


def _oauth_callback_url(provider):
    base = read_env_file().get('OAUTH_CALLBACK_BASE', '').rstrip('/')
    return f'{base}/oauth/{provider}/callback' if base else ''


@app.route('/oauth/wechat/start')
def oauth_wechat_start():
    env = read_env_file()
    app_id = env.get('WECHAT_APP_ID', '')
    callback = _oauth_callback_url('wechat')
    if not (app_id and callback):
        return redirect(url_for('setup_wizard'))

    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    params = urllib.parse.urlencode({
        'appid': app_id,
        'redirect_uri': callback,
        'response_type': 'code',
        'scope': 'snsapi_login',
        'state': state,
    })
    return redirect(f'{WECHAT_AUTHORIZE}?{params}#wechat_redirect')


@app.route('/oauth/wechat/callback')
def oauth_wechat_callback():
    env = read_env_file()
    code = request.args.get('code', '')
    state = request.args.get('state', '')
    if not code:
        return redirect(url_for('setup_wizard'))
    if not state or state != session.pop('oauth_state', None):
        return '登录校验失败（state 不匹配），请重新发起扫码。', 400

    token_params = urllib.parse.urlencode({
        'appid': env.get('WECHAT_APP_ID', ''),
        'secret': env.get('WECHAT_APP_SECRET', ''),
        'code': code,
        'grant_type': 'authorization_code',
    })
    try:
        with urllib.request.urlopen(f'{WECHAT_TOKEN_API}?{token_params}', timeout=15) as resp:
            token = json.loads(resp.read().decode('utf-8'))
        if 'openid' not in token:
            return f"微信授权失败：{token.get('errmsg', '未知错误')}", 400
        info_params = urllib.parse.urlencode({
            'access_token': token['access_token'],
            'openid': token['openid'],
            'lang': 'zh_CN',
        })
        with urllib.request.urlopen(f'{WECHAT_USERINFO_API}?{info_params}', timeout=15) as resp:
            profile = json.loads(resp.read().decode('utf-8'))
    except Exception as exc:
        return f'与微信服务器通信失败：{type(exc).__name__}', 502

    openid = token['openid']
    account = f'wx_{openid[:16]}'
    users = load_json(USERS_FILE)
    if account not in users:
        users[account] = {
            'password': '',
            'wechat_openid': openid,
            'nickname': profile.get('nickname', ''),
            'email': '',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mode': 'explore',
            'progress': {},
            'completed_kps': [],
            'completed_exercises': [],
            'favorites': [],
            'wrong_answers': [],
            'notes': {},
        }
        save_json(USERS_FILE, users)

    session.permanent = True
    session['username'] = account
    return redirect(url_for('dashboard'))


def registration_is_open():
    """白名单为空时视为不限制注册。

    白名单本来是给老师控制课堂上谁能注册用的，但打包发出去以后
    默认空表会把所有新用户挡在门外（注册和登录都会失败），
    所以这里把"空"解释成"不限制"，填了名单才生效。
    """
    return len(_load_whitelist()) == 0


def _account_allowed(username):
    return registration_is_open() or is_whitelisted(username)


EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    email = (data.get('email') or '').strip()

    # 没填邮箱时，账号本身可以是邮箱
    if not email and EMAIL_RE.match(username):
        email = username

    if not username or not password:
        return jsonify({'success': False, 'message': '账号和密码不能为空'})
    if len(username) < 2:
        return jsonify({'success': False, 'message': '用户名至少 2 个字符'})
    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少 6 个字符'})
    if email and not EMAIL_RE.match(email):
        return jsonify({'success': False, 'message': '邮箱格式不对，例如 123456@qq.com'})

    if not _account_allowed(username):
        return jsonify({'success': False, 'message': '注册失败：该账号不在白名单中，请联系管理员'})

    users = load_json(USERS_FILE)
    if username in users and users[username].get('password'):
        return jsonify({'success': False, 'message': '该账号已注册，直接登录即可'})
    if email and any(u.get('email') == email for u in users.values()):
        return jsonify({'success': False, 'message': '该邮箱已注册，直接登录即可'})

    _, salt, digest = hash_password_new(password)
    if username in users:
        # 密码被清空的旧账号：允许用同一个用户名重新设密码，学习记录原样保留。
        # 单机版没有"找回密码"通道，这是留给忘记密码的人的唯一出口（见使用说明）。
        users[username].update({'password': digest, 'password_salt': salt,
                                'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        save_json(USERS_FILE, users)
        session.permanent = True
        session['username'] = username
        return jsonify({'success': True, 'message': '已为这个账号重设密码并登录', 'username': username})

    users[username] = {
        'password': digest,
        'password_salt': salt,
        'email': email,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'avatar': '',
        'mode': 'explore',
        'progress': {},
        'completed_kps': [],
        'completed_exercises': [],
        'favorites': [],
        'wrong_answers': [],
        'notes': {}
    }
    save_json(USERS_FILE, users)
    session.permanent = True           # 自己电脑上不用每次登录
    session['username'] = username
    return jsonify({'success': True, 'message': '注册成功，已自动登录', 'username': username})


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'success': False, 'message': '账号和密码不能为空'})

    users = load_json(USERS_FILE)
    # 允许用邮箱登录
    if username not in users:
        hit = next((u for u, info in users.items() if info.get('email') == username), '')
        if hit:
            username = hit

    if username not in users:
        return jsonify({'success': False, 'message': '账号不存在，请先注册'})

    if not users[username].get('password'):
        return jsonify({'success': False, 'message': '这个账号还没有密码，请到注册页用同一个用户名设置一个新密码'})
    if not verify_password(users[username], password):
        return jsonify({'success': False, 'message': '密码错误'})

    if not _account_allowed(username):
        return jsonify({'success': False, 'message': '登录失败：账号未在白名单中或已过期，请联系管理员'})

    # 老账号第一次成功登录后顺手升级成加盐哈希
    if not users[username].get('password_salt'):
        _, salt, digest = hash_password_new(password)
        users[username]['password'] = digest
        users[username]['password_salt'] = salt
    users[username]['last_login'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_json(USERS_FILE, users)

    session.permanent = True           # 下次打开自动还是这个账号
    session['username'] = username
    return jsonify({'success': True, 'message': '登录成功', 'username': username})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('dashboard'))


# ── 本地账号：多账号切换与头像 ────────────────────────────
# 单机版的数据都在用户自己电脑上，所以"这台机器上有哪些账号"可以放心列出来，
# 让登录页直接点头像切换，而不是每次手打用户名。

AVATAR_DIR = os.path.join(DATA_DIR, 'avatars')
AVATAR_MAX_BYTES = 2 * 1024 * 1024
AVATAR_EXT = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/jpg': 'jpg',
              'image/webp': 'webp', 'image/gif': 'gif'}


def _avatar_filename(username):
    """头像文件名用用户名哈希：避开中文名在 Windows 上的编码坑，也防止路径穿越。"""
    return hashlib.sha1(username.encode('utf-8')).hexdigest()


def _public_account(username, info):
    """给前端用的账号摘要，绝不带密码字段。"""
    has_file = bool(info.get('avatar')) and os.path.exists(
        os.path.join(AVATAR_DIR, info['avatar']))
    return {
        'username': username,
        'avatar_url': f'/avatar/{quote(username)}' if has_file else '',
        'emoji': info.get('avatar_emoji', ''),
        'created_at': info.get('created_at', ''),
        'last_login': info.get('last_login', ''),
    }


@app.route('/api/accounts')
def api_accounts():
    """本机已有的账号列表，按最近登录排序，供登录页/切换账号使用。"""
    users = load_json(USERS_FILE)
    accounts = [_public_account(name, info) for name, info in users.items()]
    accounts.sort(key=lambda item: item.get('last_login') or '', reverse=True)
    current = session.get('username', '')
    if current and current not in users:
        current = ''          # 账号已被删掉，别再当成"当前账号"回给前端
    return jsonify({'success': True, 'accounts': accounts, 'current': current})


@app.route('/avatar/<path:username>')
def avatar_file(username):
    """头像文件。没有就 404，前端会退回到"首字母 + 颜色"的头像。"""
    users = load_json(USERS_FILE)
    info = users.get(username) or {}
    name = info.get('avatar') or ''
    path = os.path.join(AVATAR_DIR, name) if name else ''
    if not path or not os.path.exists(path):
        return ('', 404)
    response = send_file(path, max_age=3600)
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response


@app.route('/api/avatar', methods=['POST'])
def api_set_avatar():
    """换头像：支持上传图片（data URL）或选一个 emoji。"""
    data = request.get_json(silent=True) or {}
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': '请先登录再设置头像'})

    users = load_json(USERS_FILE)
    if username not in users:
        return jsonify({'success': False, 'message': '账号不存在'})

    emoji = (data.get('emoji') or '').strip()
    data_url = data.get('image') or ''

    if emoji:
        users[username]['avatar_emoji'] = emoji[:8]
        users[username]['avatar'] = ''
        save_json(USERS_FILE, users)
        return jsonify({'success': True, 'emoji': users[username]['avatar_emoji'], 'avatar_url': ''})

    match = re.match(r'^data:(image/[a-z+]+);base64,(.+)$', data_url, flags=re.S | re.I)
    if not match:
        return jsonify({'success': False, 'message': '图片格式不对，请换一张'})
    mime, payload = match.group(1).lower(), match.group(2)
    ext = AVATAR_EXT.get(mime)
    if not ext:
        return jsonify({'success': False, 'message': '只支持 PNG / JPG / WEBP / GIF'})
    try:
        blob = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error):
        return jsonify({'success': False, 'message': '图片数据损坏，请重新选择'})
    if len(blob) > AVATAR_MAX_BYTES:
        return jsonify({'success': False, 'message': '图片太大了，请选 2MB 以内的'})

    os.makedirs(AVATAR_DIR, exist_ok=True)
    filename = f'{_avatar_filename(username)}.{ext}'
    # 换了格式就把旧文件删掉，免得同一账号留两份
    for old in os.listdir(AVATAR_DIR):
        if old.startswith(_avatar_filename(username) + '.'):
            try:
                os.remove(os.path.join(AVATAR_DIR, old))
            except OSError:
                pass
    with open(os.path.join(AVATAR_DIR, filename), 'wb') as f:
        f.write(blob)

    users[username]['avatar'] = filename
    users[username]['avatar_emoji'] = ''
    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'avatar_url': f'/avatar/{quote(username)}',
                    'emoji': ''})


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
        # 只给"真的含代码"的知识点追加编程练习：
        # 纯概念、流程、协作类知识点硬塞代码题会让学生无从下手。
        if 'md-codeblock' in kps[i].get('content', '') and (
                not exercises or exercises[0].get('type') != 'code'):
            hint = f'用代码把「{kp_title}」的核心用法演示一遍，并打印出结果。'
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
                          chapter_wrong=chapter_wrong,
                          username=username,
                          total_chapters=len(courses))


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
    # 喂给 input() 的内容。不传就按空处理：空 stdin 会让 input() 立刻
    # 撞到 EOF，这正是"代码里有 input() 就报执行失败"的原因 ——
    # 以前子进程继承的是服务端的 stdin（可能是 /dev/null 或已关闭），
    # 报错还很难懂。现在改成显式传入，没填就给一句人话提示。
    stdin_text = data.get('stdin', '')
    if not isinstance(stdin_text, str):
        stdin_text = ''

    if not code:
        return jsonify({'success': False, 'output': '', 'error': '代码不能为空'})

    if len(code) > 50000:
        return jsonify({'success': False, 'output': '', 'error': '代码过长（最大50000字符）'})

    if not code_exec_enabled():
        return jsonify({'success': False, 'output': '', 'error': CODE_EXEC_OFF_MESSAGE})

    needs_input = bool(re.search(r'(?<![\w.])input\s*\(', code))

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
            # 必须用 sys.executable：随包 Python 不在 PATH 上，写死 'python' 会
            # 找不到解释器，或者悄悄跑到系统里另一个 Python 上（装没装库全看运气）
            [sys.executable, '-X', 'utf8', tmp_path],
            # 显式给 stdin：不传的话子进程会继承服务端的输入流，
            # 在服务器上那是空的，input() 直接 EOFError
            input=stdin_text.encode('utf-8'),
            capture_output=True,
            # 超时放宽到 20 秒：导入 pandas/matplotlib 在忙的机器上会明显变慢
            timeout=20,
            cwd=os.path.dirname(tmp_path),
            env={**os.environ,
                 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1',
                 # 必须指定无界面后端：默认后端会去初始化 GUI，
                 # 在服务端子进程里会直接阻塞到超时（第 26 章绘图题全军覆没就是这么来的）
                 'MPLBACKEND': 'Agg'}
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

        # input() 撞到 EOF 时，报错原文是 "EOFError: EOF when reading a line"，
        # 对初学者等于没说。换成"怎么填测试输入"的指路。
        hint = ''
        if proc.returncode != 0 and ('EOFError' in stderr or 'EOF when reading' in stderr):
            hint = ('这段程序在等键盘输入（用了 input），但没有输入数据可读。\n'
                    '把要输入的内容填到下面的「测试输入」框里（每行一个），再点运行。')
        elif needs_input and not stdin_text and proc.returncode == 0:
            hint = '提示：这段程序用了 input()。换几组测试输入再跑一遍，才算真的验证过。'

        return jsonify({
            'success': True,
            'output': output,
            'error': '',
            'hint': hint,
            'needs_input': needs_input,
            'exit_code': proc.returncode,
            'elapsed': f'{elapsed}s'
        })

    except subprocess.TimeoutExpired:
        # 等输入也可能表现为超时（比如程序里连着好几个 input）
        err = '⏱ 代码执行超时（20秒限制）\n可能原因：死循环、阻塞操作或计算量过大'
        if needs_input:
            err += '\n如果程序里有 input()，请确认「测试输入」框里填了足够行数的数据。'
        return jsonify({
            'success': False,
            'output': '',
            'error': err,
            'needs_input': needs_input,
            'exit_code': -1,
            'elapsed': '10s+'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'output': '',
            'error': f'执行异常: {str(e)}',
            'needs_input': needs_input,
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
from ark_client import ArkClient, ArkError, BROWSER_UA
ark = ArkClient()
AI_API_KEY = ark.key
AI_MODEL = ark.models[0]
AI_CACHE = {}
AI_CACHE_TTL = 300

# ── 课程知识 RAG ─────────────────────────────────────────
# 全套教材有 39 章 / 400 个知识点，整本塞进提示词又慢又贵。
# 这里开机后建一次内存索引，按问题检索最相关的几节，只把这部分喂给模型，
# 回答就会落在本课程讲过的知识范围内，而不是泛泛的互联网答案。

_COURSE_DOCS = None
_COURSE_DOCS_LOCK = threading.Lock()
_RAG_CACHE = {}
_RAG_CACHE_TTL = 600


def _html_to_text(html):
    """教材正文是 HTML，检索只需要纯文字。"""
    text = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html or '', flags=re.S | re.I)
    text = re.sub(r'<br\s*/?>|</p>|</li>|</div>|</h[1-6]>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"')
    return re.sub(r'\n{2,}', '\n', re.sub(r'[ \t]{2,}', ' ', text)).strip()


def _rag_terms(text):
    """中文按二元组切、英文数字按词切，够用且不需要分词依赖。"""
    terms = {}
    for word in re.findall(r'[a-zA-Z_][a-zA-Z0-9_\.]{1,}', text.lower()):
        terms[word] = terms.get(word, 0) + 1
    for run in re.findall(r'[\u4e00-\u9fff]+', text):
        if len(run) == 1:
            terms[run] = terms.get(run, 0) + 1
        for i in range(len(run) - 1):
            bigram = run[i:i + 2]
            terms[bigram] = terms.get(bigram, 0) + 1
    return terms


def _build_course_docs():
    """把每个知识点、每道练习压成一条可检索文档（只做一次）。"""
    docs = []
    try:
        courses = load_json(COURSES_FILE)
    except Exception as exc:
        print(f'[RAG] 课程索引构建失败：{exc}')
        return docs
    for course in courses:
        chapter_id = course.get('id')
        chapter_title = course.get('title', '')
        for kp_index, kp in enumerate(course.get('knowledge_points', [])):
            body = _html_to_text(kp.get('content', ''))
            docs.append({
                'kind': 'kp',
                'chapter_id': chapter_id,
                'chapter_title': chapter_title,
                'title': f'第 {chapter_id} 章 {chapter_title} · {kp.get("title", "")}',
                'index': kp_index,
                'text': body,
                'terms': _rag_terms(kp.get('title', '') + ' ' + chapter_title + ' ' + body),
            })
        for ex in course.get('exercises', []):
            question = ex.get('question_plain') or _html_to_text(ex.get('question', ''))
            reference = _html_to_text(ex.get('reference', ''))[:600]
            docs.append({
                'kind': 'exercise',
                'chapter_id': chapter_id,
                'chapter_title': chapter_title,
                'title': f'第 {chapter_id} 章练习 · 第 {ex.get("no", "?")} 题',
                'index': ex.get('no', 0),
                'text': question + ('\n参考答案：' + reference if reference else ''),
                'terms': _rag_terms(question + ' ' + reference),
            })
    print(f'[RAG] 课程索引就绪：{len(docs)} 条文档')
    return docs


def retrieve_course_context(query, chapter_id=None, top_k=4, budget=2600):
    """检索与问题最相关的课程片段，拼成一小段可直接进提示词的资料。"""
    global _COURSE_DOCS
    query = (query or '').strip()
    if not query:
        return ''
    cache_key = (query[:200], str(chapter_id))
    hit = _RAG_CACHE.get(cache_key)
    if hit and time.time() - hit[0] < _RAG_CACHE_TTL:
        return hit[1]

    if _COURSE_DOCS is None:
        with _COURSE_DOCS_LOCK:
            if _COURSE_DOCS is None:
                _COURSE_DOCS = _build_course_docs()
    docs = _COURSE_DOCS
    if not docs:
        return ''

    q_terms = _rag_terms(query)
    if not q_terms:
        return ''
    try:
        want_chapter = int(chapter_id)
    except (TypeError, ValueError):
        want_chapter = None

    scored = []
    for doc in docs:
        score = 0
        for term, count in q_terms.items():
            weight = doc['terms'].get(term)
            if weight:
                # 长词更有区分度（"列表推导" 比 "列表" 值钱），出现次数封顶避免刷分
                score += (1.6 if len(term) > 1 else 0.8) * min(weight, 3) * (1 + 0.2 * min(count, 3))
        if not score:
            continue
        if want_chapter is not None and doc['chapter_id'] == want_chapter:
            score *= 1.45  # 学生正在学的这一章优先
        if doc['kind'] == 'exercise':
            score *= 1.1
        scored.append((score, doc))

    scored.sort(key=lambda item: -item[0])
    picked, used = [], 0
    for score, doc in scored[:top_k]:
        body = doc['text'][:900]
        if not body:
            continue
        block = f'【{doc["title"]}】\n{body}'
        if used + len(block) > budget:
            break
        picked.append(block)
        used += len(block)
    result = '\n\n'.join(picked)
    if len(_RAG_CACHE) > 512:
        _RAG_CACHE.clear()
    _RAG_CACHE[cache_key] = (time.time(), result)
    return result


# ── 学生页面作答情况 ─────────────────────────────────────

def build_student_state(data, username):
    """把学生当前页面的作答情况整理成一段说明，让 AI 知道自己在给谁讲。"""
    page = data.get('page') or {}
    lines = []
    chapter_id = str(page.get('chapter_id') or data.get('chapter_id') or '')
    chapter_title = str(page.get('chapter_title') or '')[:60]
    kp_title = str(page.get('kp_title') or '')[:80]

    where = '第 %s 章 %s' % (chapter_id, chapter_title) if chapter_id else ''
    if where and kp_title:
        where += f' · 正在看「{kp_title}」'
    if where.strip():
        lines.append('位置：' + where.strip())

    total, done = page.get('kp_total'), page.get('kp_done')
    if isinstance(total, int) and isinstance(done, int) and total:
        lines.append(f'本章进度：{done}/{total} 个知识点已完成')

    if page.get('exercise'):
        lines.append('当前这道练习：' + str(page['exercise'])[:400])
    if page.get('code'):
        lines.append('学生当前写的代码：\n```python\n' + str(page['code'])[:1200] + '\n```')
    if page.get('output'):
        lines.append('最近一次运行输出：\n' + str(page['output'])[:400])

    wrong = page.get('wrong')
    if isinstance(wrong, list) and wrong:
        items = []
        for item in wrong[-5:]:
            if isinstance(item, dict):
                q = str(item.get('question') or item.get('q') or '')[:120]
                if q:
                    items.append('- ' + q)
            elif item:
                items.append('- ' + str(item)[:120])
        if items:
            lines.append('他这一章最近答错的题：\n' + '\n'.join(items))
    elif username and username != 'guest':
        # 页面上没带，就从服务端记录里补，保证 AI 一定看得到答题情况
        users = load_json(USERS_FILE)
        records = (users.get(username, {}).get('wrong_answers') or [])[-5:]
        items = ['- ' + str(r.get('question', ''))[:120] for r in records if r.get('question')]
        if items:
            lines.append('他最近答错的题：\n' + '\n'.join(items))

    if not lines:
        return ''
    return '【学生当前情况】\n' + '\n'.join(lines)
AI_CONNECT_TIMEOUT = 4
# Keep interactive tutoring bounded: one stalled relay should not make the
# chat feel frozen, while the browser's 12s abort remains a final guard.
AI_READ_TIMEOUT = 8

# ── AI 配置的读取 / 校验 / 热更新 ─────────────────────────
# 用户下载压缩包后要做的第一件事就是填自己的模型地址与密钥。
# 这些值原先只在启动时从 .env 读一次，填完必须重启才生效——
# 首次配置向导要求保存后立刻可用，所以这里做成可热更新。

ENV_FILE = os.path.join(WRITE_ROOT, '.env')
AI_CONFIG_KEYS = ('PYMASTER_AI_BASE_URL', 'PYMASTER_AI_MODEL', 'ARK_API_KEY')


def read_env_file():
    values = {}
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        values[key.strip()] = value.strip().strip('"\'')
        except OSError:
            pass
    return values


def ai_config_status():
    """AI 是否配置完整；顺带返回脱敏后的回显信息。"""
    env = read_env_file()
    # 进程环境优先（容器/CI 场景常用环境变量注入）
    base_url = os.environ.get('PYMASTER_AI_BASE_URL') or env.get('PYMASTER_AI_BASE_URL', '')
    model = os.environ.get('PYMASTER_AI_MODEL') or env.get('PYMASTER_AI_MODEL', '')
    key = os.environ.get('ARK_API_KEY') or env.get('ARK_API_KEY', '')
    return {
        'configured': bool(base_url and model and key),
        'base_url': base_url,
        'model': model,
        'fallback': env.get('PYMASTER_AI_FALLBACK_MODELS', ''),
        'key_tail': ('****' + key[-4:]) if len(key) >= 4 else '',
    }


def apply_ai_config(base_url, model, api_key, fallback=''):
    """写入 .env 并让配置立即生效（不需要重启）。"""
    global AI_BASE_URL, AI_API_KEY, AI_MODEL, ark

    lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for raw in f:
                line = raw.rstrip('\n')
                key = line.split('=', 1)[0].strip() if '=' in line else ''
                if key in AI_CONFIG_KEYS or key == 'PYMASTER_AI_FALLBACK_MODELS':
                    continue
                if line.strip():
                    lines.append(line)
    lines.insert(0, f'PYMASTER_AI_BASE_URL={base_url}')
    lines.insert(1, f'PYMASTER_AI_MODEL={model}')
    lines.insert(2, f'ARK_API_KEY={api_key}')
    if fallback:
        lines.insert(3, f'PYMASTER_AI_FALLBACK_MODELS={fallback}')

    tmp = ENV_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    os.replace(tmp, ENV_FILE)

    os.environ['PYMASTER_AI_BASE_URL'] = base_url
    os.environ['PYMASTER_AI_MODEL'] = model
    os.environ['ARK_API_KEY'] = api_key
    if fallback:
        os.environ['PYMASTER_AI_FALLBACK_MODELS'] = fallback

    AI_BASE_URL = _normalize_ai_endpoint(base_url)
    ark = ArkClient()
    AI_API_KEY = ark.key
    AI_MODEL = ark.models[0]
    AI_CACHE.clear()
    return ai_config_status()


def test_ai_connection(base_url, model, api_key, timeout=20):
    """拿用户填的配置真发一次最小请求，确认能用。"""
    url = _normalize_ai_endpoint(base_url)
    payload = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': '请只回复两个字：可用'}],
        # 给足 64 个 token：推理模型会把预算先花在思考上，
        # 只给 16 的话正文是空的，用户会以为"测试成功但没回复"是坏的
        'max_tokens': 64,
        'temperature': 0,
        'thinking': {'type': 'disabled'},
    }).encode('utf-8')
    # 头和 ArkClient 保持一致：部分网关会对非浏览器 UA 直接返回 403
    request = urllib.request.Request(url, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'User-Agent': BROWSER_UA,
        'x-opencode-session': str(uuid.uuid4()),
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
        content = (result['choices'][0]['message'].get('content') or '').strip()
        if not content:
            # 接口通了但模型没给正文（推理模型常见）：也算通过，别让人以为失败了
            return True, '调用成功（接口通、鉴权对；模型这次没返回正文，不影响使用）'
        return True, f'调用成功，模型回复：{content[:30]}'
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'ignore')[:160]
        hints = {
            401: 'API Key 不正确或已失效',
            403: '没有该模型的权限，或 Key 被限制',
            404: '模型名称或接口地址不对',
            429: '请求过于频繁，或额度已用尽',
        }
        hint = hints.get(exc.code, '接口返回错误')
        # 服务商把"模型不存在"也报成 401，照着 401 的提示去查 Key 会白折腾，
        # 所以这里看一眼原文，能认出是模型名的问题就直接说
        low = detail.lower()
        if 'model' in low and any(word in low for word in ('not supported', 'not found', 'invalid', 'no permission')):
            hint = '模型名称不对（服务商说这个模型不存在或没开通）'
        return False, f'{hint}（HTTP {exc.code}）{detail}'
    except urllib.error.URLError as exc:
        return False, f'连不上这个地址：{exc.reason}。请检查 Base URL 和网络。'
    except (KeyError, IndexError, ValueError):
        return False, '接口返回的格式不是 OpenAI 兼容格式，请确认 Base URL'
    except Exception as exc:
        return False, f'测试失败：{type(exc).__name__}: {str(exc)[:120]}'


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
        'quota_note': '额度以所用服务商控制台为准',
        'endpoint_ready': AI_BASE_URL.endswith('/chat/completions'),
    })


def _compose_ai_messages(question, context, chapter_id, page_state=''):
    """系统提示 + 学生贴的内容 + 页面作答情况 + 检索到的讲义 + 提问。

    只有系统提示是固定前缀，其余都放在 user 侧，
    这样服务商的前缀缓存能命中，提问的往返时间也更短。
    """
    parts = []
    if context:
        parts.append('【学生贴出的内容】\n' + context)
    if page_state:
        parts.append(page_state)
    rag = retrieve_course_context((question + ' ' + context)[:1200], chapter_id)
    if rag:
        parts.append('【本课程相关讲义（优先按这里讲过的来解释，不要跑题）】\n' + rag)
    parts.append('【学生提问】\n' + question)
    return [
        {'role': 'system', 'content': JJ_SYSTEM_PROMPT},
        {'role': 'user', 'content': '\n\n'.join(parts)},
    ]


def _ai_cache_key(messages):
    return hashlib.sha256(json.dumps([ark.active_model, messages], ensure_ascii=False).encode()).hexdigest()


def _ai_cache_get(key):
    hit = AI_CACHE.get(key)
    if hit and time.time() - hit[0] < AI_CACHE_TTL:
        return hit[1]
    return None


def _ai_cache_put(key, answer):
    if len(AI_CACHE) > 400:
        AI_CACHE.clear()
    AI_CACHE[key] = (time.time(), answer)


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
    # 学生的页面作答情况随人随页面变，必须进缓存键，不能把别人的答案复用给他
    messages = _compose_ai_messages(question, context, chapter_id, build_student_state(data, username))
    cache_key = _ai_cache_key(messages)
    cached = _ai_cache_get(cache_key)

    def generate():
        def encode(event):
            return 'data: ' + json.dumps(event, ensure_ascii=False) + '\n\n'
        yield encode({'type': 'status', 'message': '正在连接模型…'})
        if cached:
            yield encode({'type': 'delta', 'text': cached})
            yield encode({'type': 'done', 'model': ark.active_model, 'cached': True})
            return
        answer = ''
        try:
            for event in ark.events(messages):
                if event['type'] == 'delta':
                    answer += event['text']
                yield encode(event)
            if not answer:
                raise ArkError('模型没有返回正文，请重试。')
            _ai_cache_put(cache_key, answer)
            if username != 'guest':
                increment_daily_usage(username)
                if chapter_id:
                    users = load_json(USERS_FILE)
                    if username in users:
                        history = users[username].setdefault('jj_history', {}).setdefault(chapter_id, [])
                        history.append({'question': question, 'answer': answer, 'timestamp': datetime.now().isoformat()})
                        save_json(USERS_FILE, users)
                # 练习里的答疑也沉淀到星辰教练，形成可回看的「答疑对话」
                try:
                    coach.record_exchange(username, question, answer,
                                          chapter_id=chapter_id, source='exercise')
                except Exception as exc:      # 会话写失败不能影响这次回答
                    print(f'[coach] 记录练习答疑失败：{exc}')
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
    chapter_id = str(data.get('chapter_id', ''))
    messages = _compose_ai_messages(question, context, chapter_id, build_student_state(data, username))
    cache_key = _ai_cache_key(messages)
    cached = _ai_cache_get(cache_key)
    if cached:
        return jsonify({"success": True, "answer": cached, "error": "", "cached": True})
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
        _ai_cache_put(cache_key, answer)
        if username != 'guest':
            increment_daily_usage(username)

        # Store JJ chat history per chapter (游客不保存)
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
    # On Linux/cloud, use a 'notes' subdirectory in the writable data dir
    # （放可写目录而不是应用目录：容器重建后笔记还在）
    notes_dir = os.path.join(DATA_DIR, 'user_notes')
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
        'notes': _migrate_notes(user.get('notes', {})),
        **_public_account(username, user),
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

    # 修为结算：完成知识点 + 整章通关额外奖励
    settlement = _award_cultivation(username, 'kp', key, training.KP_POINTS, note='完成知识点')
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if str(c['id']) == chapter_id), None)
    if course:
        total_kps = len(course.get('knowledge_points', []))
        keys = {f'{chapter_id}_{i}' for i in range(total_kps)}
        if keys and keys.issubset(set(completed)):
            chapter_bonus = _award_cultivation(username, 'chapter', chapter_id,
                                               training.CHAPTER_POINTS, note='整章通关')
            settlement['chapter'] = chapter_bonus
            if chapter_bonus.get('awarded'):
                settlement['points'] = settlement.get('awarded', 0) + chapter_bonus['awarded']

    return jsonify({'success': True, 'key': key, **settlement})


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


# ── 五分钟图文讲解（narration）────────────────────────────
# 每个知识点配一节 5 分钟带配图的口播讲解：
# 分镜脚本由大模型撰写，配图由 tools/render 的程序化作图引擎产出（不依赖任何生图接口），
# 口播由 edge-tts 合成。产物落盘于 data/narrations.json + static/narrations/ + data/audio_cache/。

_narration_jobs = {}
_narration_job_lock = threading.Lock()


def _renderer_available():
    """程序化作图需要 node（编译版面）+ Playwright（截图）。"""
    return bool(shutil.which('node'))


def _narration_capabilities():
    builder = narration_engine.NarrationBuilder()
    return builder.text.available, _renderer_available()


def _render_narration_images(chapter_id, kp_index):
    """渲染这一节的配图；失败不抛错，脚本和口播已经产出，配图可以后补。"""
    node = shutil.which('node')
    if not node:
        return False
    key = f'{chapter_id}_{kp_index}'
    plan = subprocess.run([node, str(Path(BUNDLE_DIR) / 'tools' / 'render' / 'build-plan.mjs'),
                           '--key', key],
                          cwd=BUNDLE_DIR, capture_output=True, text=True, timeout=180)
    if plan.returncode != 0:
        return False
    shot = subprocess.run([sys.executable,
                           str(Path(BUNDLE_DIR) / 'tools' / 'render' / 'render_plan.py')],
                          cwd=BUNDLE_DIR, capture_output=True, text=True, timeout=900)
    return shot.returncode == 0


def _run_narration_job(job_id, chapter_id, kp_index, scenes, with_images):
    """后台线程：生成一节讲解，把进度写回登记表供前端轮询。"""

    def note(_stage, message):
        with _narration_job_lock:
            job = _narration_jobs.get(job_id)
            if job:
                job['message'] = message.strip()
                job['updated_at'] = time.time()

    try:
        courses = load_json(COURSES_FILE)
        course = next((c for c in courses if c['id'] == chapter_id), None)
        if not course:
            raise RuntimeError('章节不存在')
        kps = course.get('knowledge_points', [])
        if kp_index < 0 or kp_index >= len(kps):
            raise RuntimeError('知识点不存在')

        note('script', '正在撰写分镜脚本…')
        builder = narration_engine.NarrationBuilder(on_log=lambda m: note('build', m))
        payload = builder.build(
            chapter_id=chapter_id, kp_index=kp_index,
            chapter_title=course['title'], kp_title=kps[kp_index]['title'],
            kp_text=narration_engine.kp_text(kps[kp_index]['content']),
            scenes=scenes,
        )
        narration_engine.save_narration(
            narration_engine.narration_key(chapter_id, kp_index), payload)

        if with_images:
            note('images', '正在绘制配图…')
            _render_narration_images(chapter_id, kp_index)

        with _narration_job_lock:
            job = _narration_jobs.get(job_id)
            if job:
                job['status'] = 'done'
                job['message'] = (f"完成：{payload['scene_count']} 个镜头，"
                                  f"{payload['total_seconds'] / 60:.1f} 分钟")
                job['finished_at'] = time.time()
    except Exception as exc:
        with _narration_job_lock:
            job = _narration_jobs.get(job_id)
            if job:
                job['status'] = 'error'
                job['message'] = f'{type(exc).__name__}: {exc}'
                job['finished_at'] = time.time()


# ── 教材原题的文字作答批改 ─────────────────────────────────
# 教材练习题大量是"用自己的话说出/解释/列举"这类主观题，
# 不适合丢进代码编辑器，所以单独给一条文字作答 + AI 对照参考答案批改的通道。

ANSWER_SCORE_PROMPT = """你是职业院校的 Python 与 AI 应用开发课程助教，正在批改学生的书面作答。
你会拿到【题目】【参考答案】【解析】【学生作答】四部分。

批改要求：
1. 以参考答案为基准判断对错，但不要要求学生逐字一致——意思对、关键点齐就是好答案。
2. 学生答对关键点就给高分；漏掉关键点要指出漏了什么；出现事实性错误要明确指出。
3. 如果学生提交的是代码，按"代码是否能实现题目要求"来评，不要纠结风格。
4. 评分尺度：准确且完整 85-100；方向对但有遗漏 60-84；明显错误或答非所问 0-59。
5. 语气像老师，直接指出问题，不要空泛地夸奖。

只输出 JSON，不要输出其他内容：
{"score": 0-100 的整数, "feedback": "一句话总评，40 字以内",
 "strengths": "答得好的地方，30 字以内，没有就留空",
 "weaknesses": "需要补充或纠正的地方，50 字以内"}"""


@app.route('/api/score-answer', methods=['POST'])
def score_answer():
    """批改教材原题的文字作答。"""
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()[:3000]
    answer = (data.get('answer') or '').strip()[:4000]
    reference = (data.get('reference') or '').strip()[:3000]
    explanation = (data.get('explanation') or '').strip()[:2000]

    if not answer:
        return jsonify({'success': False, 'message': '作答内容为空'})
    if len(answer) < 4:
        return jsonify({'success': False, 'message': '作答太短，请再写详细一点'})

    # 游客也允许批改，但登录用户受每日额度限制，避免被刷
    username = session.get('username', 'guest')
    if username != 'guest':
        allowed, used, limit = check_daily_limit(username)
        if not allowed:
            return jsonify({'success': False, 'message': '今日 AI 批改次数已用完，明天再来'})

    user_message = (f'【题目】\n{question}\n\n【参考答案】\n{reference or "（教材未提供）"}\n\n'
                    f'【解析】\n{explanation or "（无）"}\n\n【学生作答】\n{answer}')

    reply, error = _call_deepseek(ANSWER_SCORE_PROMPT, user_message, max_tokens=600)
    if error:
        return jsonify({'success': False, 'message': f'AI 批改暂不可用：{error}'})

    if username != 'guest':
        increment_daily_usage(username)

    try:
        match = re.search(r'\{.*\}', reply, re.DOTALL)
        result = json.loads(match.group() if match else reply)
    except Exception as exc:
        print(f'[文字批改] JSON 解析失败: {exc} - raw: {reply[:200]}')
        return jsonify({'success': False, 'message': 'AI 返回格式异常，请重试'})

    return jsonify({
        'success': True,
        'score': max(0, min(100, int(result.get('score', 60)))),
        'feedback': result.get('feedback', ''),
        'strengths': result.get('strengths', ''),
        'weaknesses': result.get('weaknesses', ''),
    })


@app.route('/api/narration/<int:chapter_id>/<int:kp_index>')
def get_narration_api(chapter_id, kp_index):
    """取一个知识点的图文讲解分镜；还没生成时返回 available=false。"""
    narration = narration_engine.get_narration(chapter_id, kp_index)
    if not narration:
        return jsonify({
            'success': True,
            'available': False,
            'reason': '这个知识点的 5 分钟图文讲解还没生成',
        })
    scenes = []
    for scene in narration['scenes']:
        scenes.append({
            'id': scene['id'],
            'type': scene.get('type', 'concept'),
            'title': scene.get('title', ''),
            'narration': scene.get('narration', ''),
            'caption': scene.get('caption', ''),
            'code': scene.get('code', ''),
            'image': scene.get('image', ''),
            'audio_url': (f"/api/narration/audio/{chapter_id}/{kp_index}/{scene['id']}"
                          if scene.get('audio') else ''),
            'audio_seconds': scene.get('audio_seconds', 0),
            'voice_label': narration_engine.VOICE_LABELS.get(scene.get('voice', ''), ''),
        })
    return jsonify({
        'success': True,
        'available': True,
        'narration': {
            'chapter_id': chapter_id,
            'kp_index': kp_index,
            'chapter_title': narration.get('chapter_title', ''),
            'kp_title': narration.get('kp_title', ''),
            'title': narration.get('title', ''),
            'hook_line': narration.get('hook_line', ''),
            'scene_count': narration.get('scene_count', len(scenes)),
            'total_seconds': narration.get('total_seconds', 0),
            'narration_chars': narration.get('narration_chars', 0),
            'created_at': narration.get('created_at', ''),
            'scenes': scenes,
        },
    })


@app.route('/api/narration/audio/<int:chapter_id>/<int:kp_index>/<int:scene_id>')
def get_narration_audio(chapter_id, kp_index, scene_id):
    """返回某个镜头的口播音频（读本地缓存，不重复合成）。"""
    narration = narration_engine.get_narration(chapter_id, kp_index)
    if not narration:
        return jsonify({'success': False, 'message': '讲解不存在'}), 404
    scene = next((s for s in narration['scenes'] if s['id'] == scene_id), None)
    if not scene or not scene.get('audio'):
        return jsonify({'success': False, 'message': '该镜头没有音频'}), 404
    path = narration_engine.AUDIO_CACHE / os.path.basename(scene['audio'])
    if not path.exists():
        return jsonify({'success': False, 'message': '音频文件缺失，请重新生成'}), 404
    return Response(path.read_bytes(), mimetype='audio/mpeg',
                    headers={'Cache-Control': 'public, max-age=604800'})


@app.route('/api/narration/stats')
def narration_stats_api():
    """讲解覆盖率总览，教师端与学习端都用它展示制作进度。"""
    summary = narration_engine.stats()
    courses = load_json(COURSES_FILE)
    total_kp = sum(len(c.get('knowledge_points', [])) for c in courses)
    chapters = []
    for course in courses:
        kps = course.get('knowledge_points', [])
        ready = sum(1 for i in range(len(kps))
                    if narration_engine.narration_key(course['id'], i) in summary['ready'])
        chapters.append({
            'id': course['id'], 'title': course['title'], 'icon': course.get('icon', '📘'),
            'stage': course.get('stage', ''), 'ready': ready, 'total': len(kps),
        })
    return jsonify({
        'success': True,
        'total_kp': total_kp,
        'ready': summary['count'],
        'coverage': round(summary['count'] / total_kp * 100, 1) if total_kp else 0,
        'scenes': summary['scenes'],
        'minutes': round(summary['seconds'] / 60, 1),
        'narration_chars': summary['chars'],
        'chapters': chapters,
    })


@app.route('/api/narration/status')
def narration_status_api():
    text_ok, render_ok = _narration_capabilities()
    with _narration_job_lock:
        running = [dict(j) for j in _narration_jobs.values() if j['status'] == 'running']
    return jsonify({
        'success': True,
        'text_model_available': text_ok,
        'renderer_available': render_ok,
        'voice_available': narration_engine.VoiceOver.available(),
        'running_jobs': len(running),
        'current': running[0] if running else None,
    })


@app.route('/api/narration/request', methods=['POST'])
def request_narration():
    """现场为一节知识点生成讲解。耗时 3–5 分钟，走后台线程 + 轮询。"""
    data = request.get_json(silent=True) or {}
    chapter_id = int(data.get('chapter_id', 0))
    kp_index = int(data.get('kp_index', 0))
    scenes = max(8, min(24, int(data.get('scenes', narration_engine.DEFAULT_SCENES))))
    with_images = bool(data.get('with_images', True))

    if narration_engine.get_narration(chapter_id, kp_index):
        return jsonify({'success': True, 'status': 'already', 'message': '这节讲解已经生成好了'})

    text_ok, render_ok = _narration_capabilities()
    if not text_ok:
        return jsonify({'success': False,
                        'message': '未配置 ARK_API_KEY，无法生成讲解，请在 .env 里补上密钥。'})
    if not render_ok:
        return jsonify({'success': False,
                        'message': '未找到 node，无法渲染配图；可关闭配图后重试。'})
    if not narration_engine.VoiceOver.available():
        return jsonify({'success': False, 'message': '未安装 edge-tts，请先 pip install edge-tts。'})

    with _narration_job_lock:
        for job in _narration_jobs.values():
            if job['status'] == 'running':
                return jsonify({'success': False,
                                'message': '已有讲解正在生成，请等它完成后再发起。'})
        job_id = hashlib.md5(f'{chapter_id}_{kp_index}_{time.time()}'.encode()).hexdigest()[:12]
        _narration_jobs[job_id] = {
            'job_id': job_id, 'chapter_id': chapter_id, 'kp_index': kp_index,
            'status': 'running', 'message': '排队中…', 'started_at': time.time(),
        }
    threading.Thread(target=_run_narration_job,
                     args=(job_id, chapter_id, kp_index, scenes, with_images),
                     daemon=True).start()
    return jsonify({'success': True, 'status': 'running', 'job_id': job_id,
                    'message': '已开始生成，大约需要 3–5 分钟'})


@app.route('/api/narration/job/<job_id>')
def narration_job_status(job_id):
    with _narration_job_lock:
        job = _narration_jobs.get(job_id)
        job = dict(job) if job else None
    if not job:
        return jsonify({'success': False, 'message': '任务不存在'}), 404
    job['success'] = True
    return jsonify(job)


# ═══════════════════════════════════════════════════════════
# 星辰教练 · 刷题中心 · 修为系统
# ═══════════════════════════════════════════════════════════
# 三个模块共用同一套「用户数据目录 + 原子写」的实现，都在 training_engine 里；
# 教练会话单独一份文件（对话太长，混进 users.json 会让每次答题都要序列化几 MB 文本）。

training.configure(WRITE_ROOT, DATA_DIR)
coach.configure(WRITE_ROOT, DATA_DIR)


def _who():
    return session.get('username', 'guest')


def _sse(event):
    return 'data: ' + json.dumps(event, ensure_ascii=False) + '\n\n'


def _stream(generator):
    return Response(generator, mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


def _award_cultivation(username, reason, ref, amount, note=''):
    """加分并返回结算信息。游客不积分，避免污染数据。"""
    if not username or username == 'guest':
        return {'awarded': 0, 'profile': training.level_from_points(0)}
    box = {}

    def mutate(state):
        awarded, before, after = training.award(state, reason, ref, amount, note)
        box.update({'awarded': awarded, 'before': before, 'after': after})

    training.mutate_state(username, mutate)
    settlement = {
        'awarded': box.get('awarded', 0),
        'profile': box.get('after') or training.level_from_points(0),
        'level_up': bool(box.get('after') and box.get('before') and box['after']['level'] > box['before']['level']),
    }
    return _attach_game(settlement, username)


def _profile(username):
    if not username or username == 'guest':
        return training.level_from_points(0)
    state = training.load_state(username)
    return training.level_from_points(state.get('points', 0))


# ── 星辰教练：页面与接口 ────────────────────────────────────

@app.route('/coach')
def coach_page():
    username = _who()
    return render_template('coach.html', username=username,
                          is_guest=username == 'guest',
                          max_sessions=coach.MAX_SESSIONS)


@app.route('/api/coach/sessions', methods=['GET'])
def coach_sessions():
    username = _who()
    if username == 'guest':
        return jsonify({'success': True, 'sessions': [], 'limit': coach.MAX_SESSIONS,
                        'guest': True})
    return jsonify({'success': True, 'sessions': coach.list_sessions(username),
                    'limit': coach.MAX_SESSIONS})


@app.route('/api/coach/sessions', methods=['POST'])
def coach_create_session():
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '登录后对话才会保存，游客模式可以聊但记录不留。'}), 200
    data = request.get_json(silent=True) or {}
    created = coach.create_session(username, title=data.get('title'),
                                   source='manual', first_message=data.get('title') or '')
    if isinstance(created, dict) and created.get('error'):
        return jsonify({'success': False, 'message': created.get('message', '会话数量已达上限'),
                        'limit': coach.MAX_SESSIONS})
    return jsonify({'success': True, 'session': created,
                    'sessions': coach.list_sessions(username)})


@app.route('/api/coach/sessions/<session_id>', methods=['GET'])
def coach_get_session(session_id):
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '游客模式不保存对话'}), 200
    session_data = coach.get_session(username, session_id)
    if not session_data:
        return jsonify({'success': False, 'message': '对话不存在或已被删除'}), 404
    return jsonify({'success': True, 'session': session_data,
                    'transcript': coach.transcript(session_data)})


@app.route('/api/coach/sessions/<session_id>', methods=['DELETE'])
def coach_delete_session(session_id):
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '游客模式没有可删除的对话'}), 200
    deleted = coach.delete_session(username, session_id)
    return jsonify({'success': deleted, 'sessions': coach.list_sessions(username),
                    'message': '已删除' if deleted else '对话不存在'})


@app.route('/api/coach/sessions/<session_id>/rename', methods=['POST'])
def coach_rename_session(session_id):
    username = _who()
    data = request.get_json(silent=True) or {}
    if username == 'guest':
        return jsonify({'success': False, 'message': '游客模式不保存对话'}), 200
    ok = coach.rename_session(username, session_id, data.get('title', ''))
    return jsonify({'success': ok, 'sessions': coach.list_sessions(username)})


@app.route('/api/coach/sessions/<session_id>/transcript', methods=['GET'])
def coach_transcript(session_id):
    """一键复制用：返回一段纯文本 Markdown。"""
    username = _who()
    session_data = coach.get_session(username, session_id) if username != 'guest' else None
    if not session_data:
        return jsonify({'success': False, 'message': '对话不存在'}), 404
    return jsonify({'success': True, 'text': coach.transcript(session_data),
                    'title': session_data.get('title', '星辰教练对话')})


@app.route('/api/coach/sessions/<session_id>/clear', methods=['POST'])
def coach_clear_session(session_id):
    """清空消息但保留对话本身（相当于「重开一轮」）。"""
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '游客模式不保存对话'}), 200
    ok = coach.clear_messages(username, session_id)
    return jsonify({'success': ok, 'session': coach.get_session(username, session_id),
                    'sessions': coach.list_sessions(username)})


@app.route('/api/coach/chat', methods=['POST'])
def coach_chat():
    """星辰教练的多轮对话（SSE 流式）。"""
    data = request.get_json(silent=True) or {}
    question = str(data.get('question', '')).strip()
    if not question or len(question) > 6000:
        return jsonify({'success': False, 'message': '问题不能为空，且不要超过 6000 字。'}), 400
    username = _who()
    session_id = str(data.get('session_id', '') or '')
    chapter_id = str(data.get('chapter_id', '') or '')

    if username != 'guest' and not check_daily_limit(username)[0]:
        return jsonify({'success': False, 'message': '今日 AI 问答次数已用完，明天再来吧。'}), 429

    # 没有开会话就先开一个（游客只聊不存）
    if username != 'guest' and not session_id:
        created = coach.create_session(username, source='manual', chapter_id=chapter_id,
                                       first_message=question)
        if isinstance(created, dict) and created.get('error'):
            return jsonify({'success': False, 'message': created.get('message'),
                            'limit': coach.MAX_SESSIONS}), 200
        session_id = created['id']
    elif username != 'guest':
        if not coach.get_session(username, session_id, full=False):
            return jsonify({'success': False, 'message': '对话不存在或已被删除'}), 404

    history = []
    if username != 'guest' and session_id:
        saved = coach.get_session(username, session_id) or {}
        history = [{'role': m['role'], 'content': m['content']}
                   for m in saved.get('messages', []) if m.get('content')]
        coach.append_message(username, session_id, 'user', question,
                             {'chapter_id': chapter_id, 'source': 'coach'})
    else:
        for item in (data.get('history') or [])[-8:]:
            role = str(item.get('role', ''))
            content = str(item.get('content', ''))
            if role in ('user', 'assistant') and content:
                history.append({'role': role, 'content': content})

    page_state = build_student_state(data, username)
    rag = retrieve_course_context(question[:600], chapter_id)
    parts = []
    if page_state:
        parts.append(page_state)
    if rag:
        parts.append('【本课程相关讲义（优先按这里讲过的解释，不要跑题）】\n' + rag)
    parts.append('【学生提问】\n' + question)
    messages = [{'role': 'system', 'content': coach.COACH_SYSTEM_PROMPT}]
    messages.extend(history[-10:])
    messages.append({'role': 'user', 'content': '\n\n'.join(parts)})

    def generate():
        yield _sse({'type': 'session', 'session_id': session_id})
        yield _sse({'type': 'status', 'message': 'JJ老师正在想…'})
        answer = ''
        try:
            for event in ark.events(messages, max_tokens=1200):
                if event['type'] == 'delta':
                    answer += event['text']
                yield _sse(event)
            if not answer:
                raise ArkError('模型没有返回正文，请重试。')
            if username != 'guest':
                increment_daily_usage(username)
                coach.append_message(username, session_id, 'assistant', answer,
                                     {'chapter_id': chapter_id, 'source': 'coach'})
            yield _sse({'type': 'done', 'model': ark.active_model,
                        'title': coach.make_title(question)})
        except ArkError as exc:
            yield _sse({'type': 'error', 'message': str(exc)})

    return _stream(generate())


@app.route('/api/coach/record', methods=['POST'])
def coach_record():
    """把练习 / 刷题里的一次问答存进星辰教练（供前端在 AI 答疑结束后调用）。"""
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '游客模式不保存对话'}), 200
    data = request.get_json(silent=True) or {}
    result = coach.record_exchange(
        username,
        str(data.get('question', ''))[:4000],
        str(data.get('answer', ''))[:20000],
        chapter_id=str(data.get('chapter_id', '') or ''),
        source=str(data.get('source', 'exercise') or 'exercise'),
        meta={'question_id': data.get('question_id', ''), 'mode': data.get('mode', '')},
    )
    return jsonify({'success': bool(result.get('saved')), **result,
                    'sessions': coach.list_sessions(username)})


# ── 刷题中心：页面与接口 ────────────────────────────────────

def _exam_of(state, exam_id):
    for exam in state.get('exams', []):
        if exam.get('id') == exam_id:
            return exam
    return None


def _mark_exam_answer(state, exam_id, question_id, status, stars=0, passed=False, error=''):
    """把一次作答写进卷子；所有题都落定后自动交卷并结算实战奖励。

    判题与「跳过」两条路径共用这里。之前两边各写一遍，
    跳过那条路忘了写卷子，表现就是「跳过的题在卷子里还是待作答，永远交不了卷」。
    """
    exam = _exam_of(state, exam_id)
    if exam is None:
        return None
    answer = exam.setdefault('answers', {}).setdefault(question_id, {})
    answer['status'] = status
    answer['stars'] = max(0, int(stars or 0))
    answer['passed'] = bool(passed)
    if error:
        answer['error'] = str(error)[:400]
    elif status == 'done':
        answer['error'] = ''

    total = len(exam.get('questions', []))
    settled = sum(1 for qid in exam.get('questions', [])
                  if (exam['answers'].get(qid) or {}).get('status') in ('done', 'skipped', 'failed'))
    if total and settled >= total and exam.get('status') != 'finished':
        exam['status'] = 'finished'
        exam['finished_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        star_sum = sum((exam['answers'].get(q) or {}).get('stars', 0) for q in exam['questions'])
        exam['score'] = round(star_sum / (total * 3) * 100)
        exam['stars_total'] = star_sum
        training.award(state, 'exam', exam_id,
                       training.EXAM_FINISH_BASE + training.EXAM_FINISH_PER_Q * total,
                       note='完成实战组卷')
    return exam


@app.route('/training')
def training_page():
    username = _who()
    return render_template('training.html', username=username,
                          is_guest=username == 'guest')


@app.route('/api/training/catalog')
def training_catalog():
    """题库目录：课程章节 + 算法专题，各带用户进度。"""
    username = _who()
    courses = load_json(COURSES_FILE)
    state = training.load_state(username) if username != 'guest' else {}
    attempts = (state.get('attempts') or {})
    chapters = training.bank_chapters(courses)

    catalog = []
    for info in chapters:
        items = training.filter_questions(chapters=[info['id']])
        solved = sum(1 for q in items if attempts.get(q['id'], {}).get('solved'))
        attempted = sum(1 for q in items if attempts.get(q['id'], {}).get('attempts'))
        wrong = sum(1 for q in items if attempts.get(q['id'], {}).get('wrong'))
        catalog.append({
            **info,
            'solved': solved,
            'attempted': attempted,
            'wrong': wrong,
            'progress': round(solved / len(items) * 100) if items else 0,
        })
    by_track = {
        'course': [c for c in catalog if c['track'] == 'course'],
        'algorithm': [c for c in catalog if c['track'] == 'algorithm'],
    }
    return jsonify({'success': True, 'chapters': catalog, 'by_track': by_track,
                    'total': len(training.load_bank())})


@app.route('/api/training/questions')
def training_questions():
    """题目列表（不含答案，答案要按模式单独取）。"""
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    args = request.args
    chapters = [c for c in (args.get('chapters') or '').replace('，', ',').split(',') if c.strip()]
    try:
        limit = min(300, max(1, int(args.get('limit', 200))))
    except (TypeError, ValueError):
        limit = 200
    items = training.filter_questions(
        chapters=chapters or None,
        track=args.get('track') or None,
        difficulty=int(args['difficulty']) if str(args.get('difficulty', '')).isdigit() else None,
        keyword=(args.get('q') or '').strip() or None,
        only=args.get('only') or None,
        state=state,
        limit=limit,
    )
    return jsonify({'success': True,
                    'questions': [training.question_brief(q, state) for q in items],
                    'count': len(items)})


@app.route('/api/training/question/<question_id>')
def training_question(question_id):
    """取单题。实战模式在做卷过程中不下发答案，交卷后才解锁。

    注意：只要这道题还躺在**任意一份未交卷的卷子**里，就一律锁答案。
    早期实现只看 URL 上带没带 exam_id，学生把参数去掉就能拿到答案——
    锁答案必须是「按题判定」，不能指望调用方老实传参。
    """
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    question = training.bank_index().get(question_id)
    if not question:
        return jsonify({'success': False, 'message': '题目不存在'}), 404

    reveal = True
    blocked_reason = ''
    for exam in (state.get('exams') or []):
        # 只有「进行中」的卷子锁答案。已交卷（finished）与已作废（abandoned）
        # 都要放行，否则一份被放弃的旧卷子会把题目永久锁住。
        if exam.get('status') in ('finished', 'abandoned'):
            continue
        if question_id in (exam.get('questions') or []):
            reveal = False
            blocked_reason = '实战模式下交卷后才能看解析，先自己试试。'
            break
    detail = training.public_question(question, state, reveal=reveal)
    detail['blocked_reason'] = blocked_reason
    detail['draft'] = (state.get('drafts') or {}).get(question_id, [])
    detail['record'] = (state.get('attempts') or {}).get(question_id, {})
    return jsonify({'success': True, 'question': detail})


@app.route('/api/training/run-cell', methods=['POST'])
def training_run_cell():
    """运行某一个代码块（Jupyter 那种独立运行）。

    带上 question_id 且跑的是最后一块时，会顺手执行题目断言：**跑通了当场结算
    积分**（等同于点一次「提交判题」），不用让学生再点一次才发现自己已经做对了。
    """
    data = request.get_json(silent=True) or {}
    cells = data.get('cells') or []
    if not isinstance(cells, list) or not cells:
        return jsonify({'success': False, 'error': '还没有代码可以运行。'})
    if sum(len(str(c)) for c in cells) > 60000:
        return jsonify({'success': False, 'error': '代码太长了（合计上限 60000 字符）。'})
    if not code_exec_enabled():
        return jsonify({'success': False, 'error': CODE_EXEC_OFF_MESSAGE})

    active = max(0, min(int(data.get('active', 0) or 0), len(cells) - 1))
    username = _who()
    question = training.bank_index().get(str(data.get('question_id', '') or ''))
    # 只有「跑的是最后一块」才顺带判题：只跑了半截代码时断言必然不过，
    # 白白回一个「没通过」的结论只会误导学生。
    checks = (question or {}).get('checks') or []
    if not (question and active == len(cells) - 1):
        checks = []

    result = training.run_cells(cells, active=active,
                                stdin_text=str(data.get('stdin', ''))[:4000],
                                timeout=20, checks=checks)
    settle = None
    if question and result.get('checks_passed'):
        settle = _settle_successful_run(username, question, cells,
                                        used_ai=bool(data.get('used_ai')))
    return jsonify({'success': result.get('ok', False), **result, 'settle': settle,
                    'guest': username == 'guest'})


def _settle_successful_run(username, question, cells, used_ai=False):
    """「运行就跑通了」的结算。

    只有这道题**还没通关**时才自动发分：否则反复点运行就能一次次拿递减分，
    把账本刷花。已经通关的题想再练，仍然走「提交判题」——那里的递减系数是
    有意设计的，不是漏洞。
    """
    if username == 'guest':
        return None
    state = training.load_state(username)
    if ((state.get('attempts') or {}).get(question['id']) or {}).get('solved'):
        return None

    box = {}

    def mutate(state):
        settle_result = training.record_attempt(
            state, question, cells, {'passed': True},
            mode='practice', used_ai=used_ai)
        state.setdefault('drafts', {})[question['id']] = [str(c) for c in cells]
        box['settle'] = settle_result
        return True
    training.mutate_state(username, mutate)
    settle = box.get('settle')
    _attach_game(settle, username)
    return settle


def _attach_game(settlement, username):
    """给结算单补上修行阁的轻量字段（战力 / 新神功 / 装备数 / 试炼进度）。

    这几十毫秒换来的是闭环的收口：刷完一道较难题，提示里能直接说出
    「装备解锁 +1」「突破·得《栈帧筑基术》」，而不是只报一个分数。
    """
    if not settlement or username == 'guest':
        return settlement
    profile = settlement.get('profile') if isinstance(settlement, dict) else None
    if isinstance(profile, dict):
        profile.update(game.light_profile(training.load_state(username)))
    return settlement


@app.route('/api/training/draft', methods=['POST'])
def training_save_draft():
    """把当前代码块存成草稿，换设备 / 刷新页面还能接着写。"""
    username = _who()
    data = request.get_json(silent=True) or {}
    qid = str(data.get('question_id', ''))
    cells = [str(c)[:20000] for c in (data.get('cells') or [])][:12]
    if username == 'guest' or not qid or qid not in training.bank_index():
        return jsonify({'success': False, 'message': '游客模式不保存草稿'}), 200

    def mutate(state):
        state.setdefault('drafts', {})[qid] = cells
        return True
    training.mutate_state(username, mutate)
    return jsonify({'success': True, 'saved_at': datetime.now().strftime('%H:%M:%S')})


@app.route('/api/training/judge', methods=['POST'])
def training_judge():
    """判题：跑断言，结算星级与积分。"""
    username = _who()
    data = request.get_json(silent=True) or {}
    question = training.bank_index().get(str(data.get('question_id', '')))
    if not question:
        return jsonify({'success': False, 'error': '题目不存在'}), 404
    cells = [str(c) for c in (data.get('cells') or [])]
    if not cells or sum(len(c) for c in cells) > 60000:
        return jsonify({'success': False, 'error': '还没有写代码，或代码过长（上限 60000 字符）。'})
    if not code_exec_enabled():
        return jsonify({'success': False, 'error': CODE_EXEC_OFF_MESSAGE})

    exam_id = str(data.get('exam_id', '') or '')
    used_ai = bool(data.get('used_ai'))
    skipped = bool(data.get('skipped'))
    result = training.judge(question, cells, stdin_text=str(data.get('stdin', '')),
                            timeout=25)

    settle = None
    if username != 'guest':
        box = {}

        def mutate(state):
            settle_result = training.record_attempt(
                state, question, cells, result,
                mode='exam' if exam_id else 'practice',
                exam_id=exam_id, used_ai=used_ai, skipped=skipped)
            box['settle'] = settle_result
            state.setdefault('drafts', {})[question['id']] = cells
            if exam_id:
                _mark_exam_answer(
                    state, exam_id, question['id'],
                    'skipped' if skipped else ('done' if result.get('passed') else 'failed'),
                    stars=settle_result['stars'], passed=bool(result.get('passed')),
                    error=str(result.get('error', '')))
            return True
        training.mutate_state(username, mutate)
        settle = box.get('settle')
        _attach_game(settle, username)

    return jsonify({'success': True, 'passed': bool(result.get('passed')),
                    'error': result.get('error', ''), 'stdout': result.get('detail', ''),
                    'figures': result.get('figures', []),
                    'check_failed': result.get('check_failed', False),
                    'settle': settle,
                    # 游客判题是真判（对错是准的），但没有账本可写。把身份显式回给
                    # 前端，前端才能说清「做得对，只是不记分」，而不是显示 0 星 +0。
                    'guest': username == 'guest'})


@app.route('/api/training/exam', methods=['POST'])
def training_create_exam():
    """实战模式组卷。"""
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '实战组卷需要登录，这样成绩才能保存。'}), 200
    data = request.get_json(silent=True) or {}
    chapters = data.get('chapters') or []
    try:
        count = max(1, min(20, int(data.get('count', 5))))
    except (TypeError, ValueError):
        count = 5
    difficulty = data.get('difficulty')
    if str(difficulty) not in ('1', '2', '3'):
        difficulty = None
    track = data.get('track') if data.get('track') in ('course', 'algorithm') else None

    created = {}

    def mutate(state):
        question_ids = training.build_exam(state, chapters=chapters, count=count,
                                           difficulty=difficulty, track=track)
        if not question_ids:
            created['error'] = '这个范围内的题目不够，换个章节或减少题量试试。'
            return False
        # 同时只保留一份「进行中」的卷子：旧卷子自动作废。
        # 否则旧的活跃卷子会一直把题目锁着，学生在练习模式里连解析都看不到。
        for old in state.get('exams', []):
            if old.get('status') == 'active':
                old['status'] = 'abandoned'
                old['finished_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exam = {
            'id': training.new_exam_id(),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'chapters': chapters, 'track': track or '',
            'difficulty': int(difficulty) if difficulty else None,
            'questions': question_ids, 'answers': {}, 'status': 'active',
            'score': None, 'review': '',
        }
        state.setdefault('exams', []).insert(0, exam)
        # 只留最近 20 份卷子，避免文件无限长
        del state['exams'][20:]
        state['active_exam'] = exam['id']
        created['exam'] = exam
        return True

    training.mutate_state(username, mutate)
    if created.get('error'):
        return jsonify({'success': False, 'message': created['error']})
    exam = created['exam']
    state = training.load_state(username)
    return jsonify({'success': True, 'exam': training.exam_summary(state, exam),
                    'detail': training.exam_summary(state, exam)})


@app.route('/api/training/exam/<exam_id>')
def training_get_exam(exam_id):
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    exam = _exam_of(state, exam_id)
    if not exam:
        return jsonify({'success': False, 'message': '试卷不存在'}), 404
    return jsonify({'success': True, 'exam': training.exam_summary(state, exam)})


@app.route('/api/training/exam/<exam_id>/finish', methods=['POST'])
def training_finish_exam(exam_id):
    """提前交卷：没做的题按跳过处理。"""
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '需要登录'}), 200
    box = {}

    def mutate(state):
        exam = None
        for item in state.get('exams', []):
            if item.get('id') == exam_id:
                exam = item
                break
        if exam is None:
            box['error'] = '试卷不存在'
            return False
        for qid in exam.get('questions', []):
            answer = exam.setdefault('answers', {}).setdefault(qid, {})
            if answer.get('status') not in ('done', 'skipped', 'failed'):
                answer['status'] = 'skipped'
                answer['stars'] = answer.get('stars', 0)
        exam['status'] = 'finished'
        exam['finished_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total = len(exam.get('questions', []))
        stars = sum((exam['answers'].get(q) or {}).get('stars', 0) for q in exam.get('questions', []))
        exam['score'] = round(stars / (total * 3) * 100) if total else 0
        exam['stars_total'] = stars
        training.award(state, 'exam', exam_id,
                       training.EXAM_FINISH_BASE + training.EXAM_FINISH_PER_Q * total,
                       note='完成实战组卷（提前交卷）')
        box['exam'] = exam
        return True

    training.mutate_state(username, mutate)
    if box.get('error'):
        return jsonify({'success': False, 'message': box['error']}), 404
    state = training.load_state(username)
    return jsonify({'success': True, 'exam': training.exam_summary(state, box['exam'])})


@app.route('/api/training/exam/<exam_id>/review', methods=['POST'])
def training_review_exam(exam_id):
    """AI 批卷：逐题点评 + 薄弱点 + 下一步建议（SSE 流式）。"""
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    exam = _exam_of(state, exam_id)
    if not exam:
        return jsonify({'success': False, 'message': '试卷不存在'}), 404
    if exam.get('status') != 'finished':
        return jsonify({'success': False, 'message': '先交卷，再让 AI 批卷。'}), 200

    index = training.bank_index()
    lines = [f'这是一次实战组卷（共 {len(exam.get("questions", []))} 题），'
             f'学生得分 {exam.get("score", 0)}（满分 100）。逐题情况如下：']
    for qid in exam.get('questions', []):
        question = index.get(qid)
        if not question:
            continue
        answer = (exam.get('answers') or {}).get(qid, {})
        status = {'done': '通过', 'skipped': '跳过', 'failed': '未通过'}.get(answer.get('status'), '未完成')
        lines.append(
            f'\n【{question["title"]}】（难度 {question.get("difficulty")}，{status}，'
            f'星级 {answer.get("stars", 0)}/3）\n'
            f'题目要求：{str(question.get("statement", ""))[:400]}\n'
            f'学生代码：{(answer.get("code") or "(未提交)")[:600]}\n'
            f'报错信息：{str(answer.get("error") or "无")[:300]}'
        )
    lines.append(
        '\n请按这个结构点评（用 Markdown，控制在 700 字内）：\n'
        '1. **整体表现**：一句话总结，语气鼓励但要指出问题。\n'
        '2. **逐题点评**：每题的思路对在哪、错在哪，给出关键的那一行改动（不要贴完整答案）。\n'
        '3. **薄弱知识点**：把错误归到 2–3 个具体知识点上。\n'
        '4. **下一步练什么**：给出具体的练习建议（可以推荐题型或章节）。\n'
        '5. 最后用一行「🤔 想一想：」提出一个能引发学生反思的问题。'
    )

    messages = [
        {'role': 'system', 'content': coach.COACH_SYSTEM_PROMPT},
        {'role': 'user', 'content': '\n'.join(lines)},
    ]

    def generate():
        yield _sse({'type': 'status', 'message': 'JJ老师正在批卷…'})
        answer = ''
        try:
            for event in ark.events(messages, max_tokens=1800):
                if event['type'] == 'delta':
                    answer += event['text']
                yield _sse(event)
            if not answer:
                raise ArkError('模型没有返回正文，请重试。')
            if username != 'guest':
                def mutate(state_obj):
                    for item in state_obj.get('exams', []):
                        if item.get('id') == exam_id:
                            item['review'] = answer
                            return True
                    return False
                training.mutate_state(username, mutate)
                coach.record_exchange(
                    username,
                    f'实战组卷批卷（{len(exam.get("questions", []))} 题，得分 {exam.get("score", 0)}）',
                    answer,
                    chapter_id=str((exam.get('chapters') or [''])[0]),
                    source='exam', meta={'exam_id': exam_id})
            yield _sse({'type': 'done', 'model': ark.active_model})
        except ArkError as exc:
            yield _sse({'type': 'error', 'message': str(exc)})

    return _stream(generate())


@app.route('/api/training/ai-help', methods=['POST'])
def training_ai_help():
    """单题求助：让 JJ老师讲思路（不直接给完整答案），对话会存进星辰教练。"""
    username = _who()
    data = request.get_json(silent=True) or {}
    question = training.bank_index().get(str(data.get('question_id', '')))
    title = question['title'] if question else str(data.get('title', '这道题'))
    statement = str(data.get('statement') or (question or {}).get('statement', ''))[:2000]
    code = str(data.get('code', ''))[:3000]
    error = str(data.get('error', ''))[:800]
    ask = str(data.get('ask', '')).strip() or '这道题我卡住了，帮我理一下思路。'
    if username != 'guest' and not check_daily_limit(username)[0]:
        return jsonify({'success': False, 'message': '今日 AI 问答次数已用完。'}), 429

    messages = [{'role': 'system', 'content': coach.COACH_SYSTEM_PROMPT}]
    messages.append({'role': 'user', 'content': (
        f'我在做这道题：{title}\n题目要求：{statement}\n\n'
        f'我写的代码：\n{code or "(还没写)"}\n\n'
        f'报错/现象：{error or "运行没通过"}\n\n'
        f'我的问题：{ask}\n\n'
        '请先帮我定位问题在哪一步，再给提示（不要直接贴完整答案），最后提一个追问。'
    )})

    def generate():
        yield _sse({'type': 'status', 'message': 'JJ老师在看你的代码…'})
        answer = ''
        try:
            for event in ark.events(messages, max_tokens=1200):
                if event['type'] == 'delta':
                    answer += event['text']
                yield _sse(event)
            if not answer:
                raise ArkError('模型没有返回正文，请重试。')
            if username != 'guest':
                increment_daily_usage(username)
                saved = coach.record_exchange(
                    username, f'【{title}】{ask}', answer,
                    chapter_id=str((question or {}).get('chapter_id', '')),
                    source='training',
                    meta={'question_id': (question or {}).get('id', ''), 'code': code[:400]})
                yield _sse({'type': 'saved', **saved})
            yield _sse({'type': 'done', 'model': ark.active_model})
        except ArkError as exc:
            yield _sse({'type': 'error', 'message': str(exc)})

    return _stream(generate())


@app.route('/api/training/attempt', methods=['POST'])
def training_attempt_log():
    """单独补记一次作答（比如实战模式下「跳过」按钮）。"""
    username = _who()
    if username == 'guest':
        return jsonify({'success': False, 'message': '需要登录'}), 200
    data = request.get_json(silent=True) or {}
    question = training.bank_index().get(str(data.get('question_id', '')))
    if not question:
        return jsonify({'success': False, 'message': '题目不存在'}), 404
    settle = {}
    exam_id = str(data.get('exam_id', '') or '')

    def mutate(state):
        settle.update(training.record_attempt(
            state, question, [], {'passed': False},
            mode='exam' if exam_id else 'practice',
            exam_id=exam_id, skipped=True))
        if exam_id:
            _mark_exam_answer(state, exam_id, question['id'], 'skipped', stars=0)
        return True
    training.mutate_state(username, mutate)
    return jsonify({'success': True, 'settle': settle})


# ── 修为系统与学习仪表盘 ───────────────────────────────────

@app.route('/progress')
def progress_page():
    username = _who()
    return render_template('progress.html', username=username,
                          is_guest=username == 'guest')


# ── 修行阁：用户画像子系统 ─────────────────────────────────
# 界面上的「修为等级」在这里长成一个完整的闭环：
# 刷题/看讲解 → 修为 → 境界 → 神功与法相；较难题 → 装备；试炼全通 → 突破奖励。
# 全部推导都写在 game_engine 里，app.py 只做三件事：取数、发奖、下发。

@app.route('/cultivation')
def cultivation_page():
    username = _who()
    return render_template('cultivation.html', username=username,
                           is_guest=username == 'guest')


@app.route('/api/game/state')
def game_state():
    """修行阁的全部数据。

    顺手结算「已达成的境界试炼」——试炼是加分项，必须真发下去，
    而发放走的是 training.award 的防重复账本，所以这个 GET 是幂等的：
    刷新一百次也只发一次，符合条件的那一刻就会到账。
    """
    username = _who()
    granted = []
    if username != 'guest':
        granted, _profile = game.claim_trials(username)
    state = training.load_state(username) if username != 'guest' else {}
    snap = game.snapshot(username, state)
    snap['success'] = True
    snap['is_guest'] = username == 'guest'
    snap['granted_trials'] = [{'realm': realm, 'reward': reward} for realm, reward in granted]
    return jsonify(snap)


@app.route('/api/coach/forms')
def coach_forms():
    """星辰教练的形象谱系：当前显化的是哪一尊、下一尊差多少、十一尊各是什么样。

    这个接口只读，不结算任何东西——聊天页每次打开时拉一次，
    顺带把「刚解锁新形象」播报所需要的信息给全（current / next / forms）。
    游客按 0 级算（凡尘的星尘童儿），照样能看到完整的谱系。
    """
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    profile = training.level_from_points(state.get('points', 0))
    level = profile['level']
    forms = game.coach_form_table(level)
    current = next((f for f in forms if f['current']), forms[0])
    nxt = next((f for f in forms if not f['reached']), None)
    return jsonify({
        'success': True,
        'is_guest': username == 'guest',
        'user': username,
        'level': level,
        'realm': profile['realm'],
        'profile': profile,
        'art': game.coach_form_for(level),
        'current': current,
        'next': nxt,
        'forms': forms,
    })


@app.route('/api/cultivation/profile')
def cultivation_profile():
    username = _who()
    state = training.load_state(username) if username != 'guest' else {}
    profile = training.level_from_points(state.get('points', 0))
    attempts = state.get('attempts') or {}
    solved = sum(1 for item in attempts.values() if item.get('solved'))
    profile.update({
        'is_guest': username == 'guest',
        'solved': solved,
        'attempted': len(attempts),
        'recent': list(reversed(state.get('log', [])))[:8],
    })
    # 等级条上同时要显示战力与「这一境还差什么」——这两样由 game_engine 推导，
    # 但它只算轻量部分（不算攻略选题），因为悬浮条在每个页面都会挂。
    if username != 'guest':
        profile.update(game.light_profile(state))
    return jsonify({'success': True, 'profile': profile})


@app.route('/api/cultivation/award', methods=['POST'])
def cultivation_award():
    """给「看完讲解 / 看完漫画 / 完成章节」这类行为加分（同一目标只加一次）。"""
    username = _who()
    data = request.get_json(silent=True) or {}
    reason = str(data.get('reason', ''))
    ref = str(data.get('ref', ''))
    table = {
        'narration': (training.NARRATION_POINTS, '看完图文讲解'),
        'comic': (training.COMIC_POINTS, '看完章节漫画'),
        'chapter': (training.CHAPTER_POINTS, '完成整章知识点'),
    }
    if reason not in table or not ref:
        return jsonify({'success': False, 'message': '未知的加分类型'}), 400
    amount, note = table[reason]
    result = _award_cultivation(username, reason, ref, amount, note)
    return jsonify({'success': True, **result})


@app.route('/api/progress/overview')
def progress_overview():
    """刷题仪表盘的全部数据：分章节进度 + 错题分类 + 刷题进度。"""
    username = _who()
    courses = load_json(COURSES_FILE)
    users = load_json(USERS_FILE)
    user = {} if username == 'guest' else users.get(username, {})
    state = training.load_state(username) if username != 'guest' else {}
    attempts = state.get('attempts') or {}
    index = training.bank_index()

    completed_kps = set(user.get('completed_kps', []))
    course_wrong = user.get('wrong_answers', [])

    chapters = []
    total_q = total_solved = total_attempted = total_wrong = 0
    total_stars = total_max_stars = 0

    for info in training.bank_chapters(courses):
        items = training.filter_questions(chapters=[info['id']])
        solved = sum(1 for q in items if attempts.get(q['id'], {}).get('solved'))
        attempted = sum(1 for q in items if attempts.get(q['id'], {}).get('attempts'))
        wrong = sum(1 for q in items if attempts.get(q['id'], {}).get('wrong'))
        stars = sum(attempts.get(q['id'], {}).get('best_stars', 0) for q in items)
        wrong_ids = [q['id'] for q in items if attempts.get(q['id'], {}).get('wrong')]

        if info['track'] == 'course':
            course = next((c for c in courses if c['id'] == info['id']), None)
            kp_total = len(course.get('knowledge_points', [])) if course else 0
            kp_done = sum(1 for i in range(kp_total) if f"{info['id']}_{i}" in completed_kps)
        else:
            kp_total = kp_done = 0

        entry = {
            **info,
            'kp_total': kp_total,
            'kp_done': kp_done,
            'kp_progress': round(kp_done / kp_total * 100) if kp_total else 0,
            'q_total': len(items),
            'q_attempted': attempted,
            'q_solved': solved,
            'q_wrong': wrong,
            'q_progress': round(solved / len(items) * 100) if items else 0,
            'stars': stars,
            'max_stars': len(items) * 3,
            'wrong_ids': wrong_ids[:30],
            'learn_progress': round((kp_done + solved) / (kp_total + len(items)) * 100)
                              if (kp_total + len(items)) else 0,
        }
        chapters.append(entry)
        total_q += len(items)
        total_solved += solved
        total_attempted += attempted
        total_wrong += wrong
        total_stars += stars
        total_max_stars += len(items) * 3

    # 错题分类：刷题错题按章节归并，教材练习错题也按章节归并
    wrong_groups = []
    for entry in chapters:
        items = []
        for qid in entry['wrong_ids']:
            question = index.get(qid)
            if not question:
                continue
            record = attempts.get(qid, {})
            items.append({
                'question_id': qid,
                'title': question['title'],
                'difficulty': question.get('difficulty', 1),
                'wrong': record.get('wrong', 0),
                'last_error': str(record.get('last_error', ''))[:200],
                'solved': bool(record.get('solved')),
            })
        if items:
            wrong_groups.append({'chapter_id': entry['id'], 'title': entry['title'],
                                 'track': entry['track'], 'items': items})

    textbook_wrong = {}
    for record in course_wrong:
        cid = str(record.get('chapter_id', ''))
        textbook_wrong.setdefault(cid, []).append({
            'question': str(record.get('question', ''))[:200],
            'user_answer': str(record.get('user_answer', ''))[:200],
            'timestamp': record.get('timestamp', ''),
        })

    profile = training.level_from_points(state.get('points', 0))
    if username != 'guest':
        # 仪表盘上的画像卡要用战力/试炼/法印，一并带上（轻量，不含攻略选题）
        profile.update(game.light_profile(state))
    return jsonify({
        'success': True,
        'user': username,          # 前端用它做画像的随机种子：同一个账号永远同一张脸
        'profile': profile,
        'totals': {
            'chapters': len(chapters),
            'questions': total_q,
            'attempted': total_attempted,
            'solved': total_solved,
            'wrong': total_wrong,
            'stars': total_stars,
            'max_stars': total_max_stars,
            'mastery': round(total_solved / total_q * 100) if total_q else 0,
            'accuracy': round(total_solved / total_attempted * 100) if total_attempted else 0,
            'exams': len(state.get('exams', [])),
        },
        'chapters': chapters,
        'course_chapters': [c for c in chapters if c['track'] == 'course'],
        'algo_chapters': [c for c in chapters if c['track'] == 'algorithm'],
        'wrong_groups': wrong_groups,
        'textbook_wrong': textbook_wrong,
        'exams': [training.exam_summary(state, e) for e in (state.get('exams') or [])[:6]],
        'recent_points': list(reversed(state.get('log', [])))[:12],
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

    # 端口清理：把占着 5000 的旧实例踢掉再启动。
    # 注意判据必须按"端口"匹配而不是按"127.0.0.1:5000"匹配：
    # app.run 绑的是 0.0.0.0，netstat 里显示成 0.0.0.0:5000，
    # 之前的字符串判据永远匹配不上，于是清理静默失效，
    # 两个版本同时监听（Windows 允许），浏览器看到的还是旧版内容。
    port_to_use = int(os.environ.get('PORT', 5000))

    def _port_busy(port):
        # 必须探测 0.0.0.0：Windows 下别的进程占着 0.0.0.0:5000 时，
        # 再绑 127.0.0.1:5000 仍会成功，只测回环地址会误判成"空闲"。
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind(('0.0.0.0', port))
            return False
        except OSError:
            return True
        finally:
            probe.close()

    if _port_busy(port_to_use):
        print(f'[PyMaster] 端口 {port_to_use} 被占用，正在清理旧实例...')
        try:
            # 中文 Windows 的 netstat 输出是 GBK，用 text=True 会按 UTF-8 解码抛错，
            # 异常一旦被吞掉清理就静默失效——所以这里自己按 gbk 解码，解码失败也不崩。
            raw = subprocess.run(['netstat', '-ano'], capture_output=True, timeout=8).stdout
            listing = raw.decode('gbk', errors='ignore')
            victims = set()
            for line in listing.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[0].upper().startswith('TCP') \
                        and parts[1].endswith(f':{port_to_use}') and 'LISTEN' in parts[3].upper():
                    try:
                        pid = int(parts[4])
                    except ValueError:
                        continue
                    if pid != os.getpid():
                        victims.add(pid)
            for pid in victims:
                subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                               capture_output=True, timeout=5)
                print(f'[PyMaster] 已结束占用端口的旧进程 PID {pid}')
            for _ in range(10):
                if not _port_busy(port_to_use):
                    print(f'[PyMaster] 端口 {port_to_use} 已释放')
                    break
                time.sleep(0.5)
            else:
                print(f'[PyMaster] 端口 {port_to_use} 仍未释放，'
                      f'请手动结束占用进程后重试。')
        except Exception as exc:
            print(f'[PyMaster] 端口清理失败：{exc}')

    print(f'[PyMaster] Started at http://127.0.0.1:{port_to_use}')
    # 一键启动脚本靠这个开关让服务自己开浏览器：比在 bat 里盲等几秒再 open 可靠，
    # 至少能确定端口已经在监听
    if os.environ.get('PYMASTER_OPEN_BROWSER') == '1':
        import webbrowser
        threading.Timer(1.2, lambda: webbrowser.open(f'http://127.0.0.1:{port_to_use}')).start()
    app.run(debug=False, host='0.0.0.0', port=port_to_use)
