import json
import os
import sys
import hashlib
import secrets
import subprocess
import tempfile
import time
import urllib.request
import urllib.error
import webbrowser
import threading
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask import Response

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
app.secret_key = secrets.token_hex(32)
app.template_folder = os.path.join(BUNDLE_DIR, 'templates')
app.static_folder = os.path.join(BUNDLE_DIR, 'static')

# Writable data: next to exe (or project root for dev)
DATA_DIR = os.path.join(WRITE_ROOT, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
# Read-only course data: bundled with exe
COURSES_FILE = os.path.join(BUNDLE_DIR, 'data', 'courses.json')

# Initialize Comic Engine and Memory
comic_engine = ComicEngine()
comic_memory = ComicMemory(DATA_DIR)

# Initialize TTS Engines
tts_engine = EdgeTTS()

doubao_tts = DoubaoTTS(
    app_id="3689913526",
    access_token="G7D1NW8dhQzW7PeS9RVjRNfoZZjbqYiB",
    secret_key="F4_uv5468Y5mh2xK2WeWmZWY0G_jGVp4"
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


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))


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

    users = load_json(USERS_FILE)
    if username in users:
        return jsonify({'success': False, 'message': '用户名已存在'})

    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'progress': {}
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

    session['username'] = username
    return jsonify({'success': True, 'message': '登录成功'})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


@app.route('/dashboard')
@login_required
def dashboard():
    users = load_json(USERS_FILE)
    username = session['username']
    progress = users.get(username, {}).get('progress', {})
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

    return render_template('dashboard.html', username=username, chapters=chapters)


@app.route('/chapter/<int:chapter_id>')
@login_required
def chapter(chapter_id):
    courses = load_json(COURSES_FILE)
    course = next((c for c in courses if c['id'] == chapter_id), None)
    if not course:
        return redirect(url_for('dashboard'))

    users = load_json(USERS_FILE)
    username = session['username']
    progress = users.get(username, {}).get('progress', {}).get(str(chapter_id), {})
    return render_template('chapter.html', chapter=course, progress=progress)


# ── Python Code Playground ─────────────────────────────────

@app.route('/playground')
@login_required
def playground():
    return render_template('playground.html')


@app.route('/api/run-code', methods=['POST'])
@login_required
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


# ── JJ老师 AI 助手 (DeepSeek) ──────────────────────────────

DEEPSEEK_API_KEY = "sk-24a09b5f48774c67965b71a9339aa6c4"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1/chat/completions"

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


@app.route('/api/ask-jj', methods=['POST'])
@login_required
def ask_jj():
    data = request.get_json()
    question = data.get('question', '').strip()
    context = data.get('context', '')  # optional: code or exercise context

    if not question:
        return jsonify({'success': False, 'answer': '', 'error': '问题不能为空'})

    # Build messages
    messages = [{"role": "system", "content": JJ_SYSTEM_PROMPT}]

    if context:
        messages.append({
            "role": "user",
            "content": f"【上下文/代码】\n{context}\n\n【学生提问】\n{question}"
        })
    else:
        messages.append({"role": "user", "content": question})

    # DeepSeek API call
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
        "stream": False,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    try:
        req = urllib.request.Request(DEEPSEEK_BASE_URL, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        answer = result["choices"][0]["message"]["content"]
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


@app.route('/api/progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    chapter_id = str(data.get('chapter_id', ''))
    item_type = data.get('type', '')  # 'knowledge' or 'exercise'
    index = data.get('index', 0)

    users = load_json(USERS_FILE)
    username = session['username']
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


@app.route('/api/user')
@login_required
def get_user():
    return jsonify({'username': session['username']})


# ── Comic Engine Endpoints ─────────────────────────────────

# Load pre-generated comics (Claude-generated, high quality)
COMICS_FILE = os.path.join(BUNDLE_DIR, 'data', 'comics.json')

def load_comics():
    if not os.path.exists(COMICS_FILE):
        return {}
    with open(COMICS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/api/comic/<int:chapter_id>/<int:kp_index>')
@login_required
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
@login_required
def get_comic_stats():
    """Get comic viewing statistics for the current user."""
    username = session.get('username', 'anonymous')
    stats = comic_memory.get_stats(username)
    return jsonify({'success': True, 'stats': stats})


@app.route('/api/comic/config', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})
    threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    print("🐍 PyMaster 已启动 → http://127.0.0.1:5000")
    app.run(debug=False, host='127.0.0.1', port=5000)
