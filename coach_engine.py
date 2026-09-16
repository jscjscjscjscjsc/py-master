"""星辰教练：多轮对话的会话存储与提示词。

为什么单独一份文件来做会话存储，而不是塞进 users.json：

- 一次对话动辄几十轮、每轮上千字，混进 users.json 后，
  用户登录、答题、加收藏这些高频小写入都要带着整包对话落盘，
  文件会迅速膨胀到几 MB，写一次就是一次全量序列化。
- 会话是「文档型」数据，天然适合一个用户一个文件，
  也方便出问题时单文件定界。

限制：每人最多 10 个会话（用户明确要求）。手动会话不会被自动清理；
练习答疑这类机器创建的会话在满额时会顶掉自己最老的一个，
保证「随手问一下」永远存得下，同时绝不删用户自己建的会话。
"""

import json
import os
import re
import threading
import uuid
from datetime import datetime

import training_engine

MAX_SESSIONS = 10
MAX_MESSAGES = 400          # 单个会话的消息上限，超出后从最早的非首条开始丢弃
TITLE_LIMIT = 24

SESSION_DIR = os.path.join(training_engine.DATA_DIR, 'coach')
_lock = threading.RLock()


def configure(root=None, data_dir=None):
    global SESSION_DIR
    base = str(data_dir) if data_dir else os.path.join(str(root), 'data')
    SESSION_DIR = os.path.join(base, 'coach')
    os.makedirs(SESSION_DIR, exist_ok=True)


if not os.path.isdir(SESSION_DIR):
    os.makedirs(SESSION_DIR, exist_ok=True)


def _safe_user(username):
    name = re.sub(r'[^0-9A-Za-z_.@\-\u4e00-\u9fff]', '_', str(username or 'guest'))
    return name[:60] or 'guest'


def _path(username):
    os.makedirs(SESSION_DIR, exist_ok=True)
    return os.path.join(SESSION_DIR, _safe_user(username) + '.json')


def _now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _load(username):
    path = _path(username)
    if not os.path.exists(path):
        return {'sessions': []}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {'sessions': []}
    if not isinstance(data, dict) or not isinstance(data.get('sessions'), list):
        return {'sessions': []}
    return data


def _save(username, data):
    path = _path(username)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _mutate(username, fn):
    with _lock:
        data = _load(username)
        result = fn(data)
        if result is not False:
            _save(username, data)
        return result


def make_title(text, fallback='新的对话'):
    clean = re.sub(r'\s+', ' ', str(text or '')).strip()
    clean = re.sub(r'^[#>*\-\s]+', '', clean)
    if not clean:
        return fallback
    return clean[:TITLE_LIMIT] + ('…' if len(clean) > TITLE_LIMIT else '')


def list_sessions(username):
    """会话列表（不含消息正文，只给标题与预览）。"""
    data = _load(username)
    out = []
    for s in data.get('sessions', []):
        messages = s.get('messages', [])
        preview = ''
        for m in reversed(messages):
            if m.get('content'):
                preview = re.sub(r'\s+', ' ', m['content'])[:70]
                break
        out.append({
            'id': s.get('id'),
            'title': s.get('title', '新的对话'),
            'source': s.get('source', 'manual'),
            'chapter_id': s.get('chapter_id', ''),
            'created_at': s.get('created_at', ''),
            'updated_at': s.get('updated_at', ''),
            'message_count': len(messages),
            'preview': preview,
        })
    out.sort(key=lambda s: s.get('updated_at', ''), reverse=True)
    return out


def get_session(username, session_id, full=True):
    data = _load(username)
    for s in data.get('sessions', []):
        if s.get('id') == session_id:
            if full:
                return s
            info = dict(s)
            info.pop('messages', None)
            return info
    return None


def count_sessions(username):
    return len(_load(username).get('sessions', []))


def create_session(username, title=None, source='manual', chapter_id='', first_message=''):
    """新建会话。超过上限时：机器会话可以顶掉最老的一个，手动会话直接拒绝。"""
    def fn(data):
        sessions = data.setdefault('sessions', [])
        if len(sessions) >= MAX_SESSIONS:
            if source != 'manual':
                bots = [s for s in sessions if s.get('source', 'manual') != 'manual']
                if bots:
                    oldest = min(bots, key=lambda s: s.get('updated_at', ''))
                    sessions.remove(oldest)
                else:
                    return {'error': 'cap', 'message':
                            f'星辰教练最多保存 {MAX_SESSIONS} 个对话，请先删除一个旧对话。'}
            else:
                return {'error': 'cap', 'message':
                        f'星辰教练最多保存 {MAX_SESSIONS} 个对话，请先删除一个旧对话再新建。'}
        session = {
            'id': 'cs' + uuid.uuid4().hex[:12],
            'title': title or make_title(first_message, '新的对话'),
            'source': source,
            'chapter_id': str(chapter_id or ''),
            'created_at': _now(),
            'updated_at': _now(),
            'messages': [],
        }
        sessions.append(session)
        return {'session': session}

    result = _mutate(username, fn)
    if result and result.get('error'):
        return result
    return result.get('session') if result else None


def delete_session(username, session_id):
    def fn(data):
        sessions = data.get('sessions', [])
        before = len(sessions)
        data['sessions'] = [s for s in sessions if s.get('id') != session_id]
        return len(data['sessions']) != before
    return bool(_mutate(username, fn))


def rename_session(username, session_id, title):
    def fn(data):
        for s in data.get('sessions', []):
            if s.get('id') == session_id:
                s['title'] = make_title(title, s.get('title', '新的对话'))
                s['updated_at'] = _now()
                return True
        return False
    return bool(_mutate(username, fn))


def clear_messages(username, session_id):
    def fn(data):
        for s in data.get('sessions', []):
            if s.get('id') == session_id:
                s['messages'] = []
                s['updated_at'] = _now()
                return True
        return False
    return bool(_mutate(username, fn))


def append_message(username, session_id, role, content, meta=None, auto_title=True):
    def fn(data):
        for s in data.get('sessions', []):
            if s.get('id') == session_id:
                messages = s.setdefault('messages', [])
                messages.append({
                    'role': role,
                    'content': str(content or ''),
                    'ts': _now(),
                    'meta': meta or {},
                })
                if len(messages) > MAX_MESSAGES:
                    del messages[:len(messages) - MAX_MESSAGES]
                s['updated_at'] = _now()
                if auto_title and role == 'user' and s.get('title') in ('', '新的对话'):
                    s['title'] = make_title(content)
                return True
        return False
    return bool(_mutate(username, fn))


def find_session_by(username, source, chapter_id=''):
    data = _load(username)
    for s in data.get('sessions', []):
        if s.get('source') == source and str(s.get('chapter_id', '')) == str(chapter_id or ''):
            return s
    return None


def record_exchange(username, question, answer, chapter_id='', source='exercise',
                    meta=None, title_hint=''):
    """把一次问答存进星辰教练。

    练习 / 刷题里问 AI 的对话要有地方沉淀，但用户不该被「会话满了」打断答题，
    所以这里的策略是：先找同章节同来源的会话追加；没有再建；
    建不了（10 个会话全是用户手建的）就把这条挂在最近更新的那个会话末尾，
    并在消息上打标记说明来源。数据不丢，也不会删用户的东西。
    """
    if not question or not answer:
        return {'saved': False, 'reason': 'empty'}

    chapter_id = str(chapter_id or '')
    session = find_session_by(username, source, chapter_id)
    if not session:
        label = {'exercise': '练习答疑', 'training': '刷题答疑', 'exam': '实战答疑'}.get(source, '答疑')
        title = f'{label} · 第 {chapter_id} 章' if chapter_id else label
        session = create_session(username, title=title, source=source, chapter_id=chapter_id)
        if isinstance(session, dict) and session.get('error'):
            sessions = list_sessions(username)
            if not sessions:
                return {'saved': False, 'reason': session.get('error', 'cap')}
            session_id = sessions[0]['id']
            payload = dict(meta or {})
            payload['source'] = source
            payload['chapter_id'] = chapter_id
            payload['unsorted'] = True
            append_message(username, session_id, 'user', question, payload, auto_title=False)
            append_message(username, session_id, 'assistant', answer, payload, auto_title=False)
            return {'saved': True, 'session_id': session_id, 'merged': True}
    payload = dict(meta or {})
    payload.setdefault('source', source)
    payload.setdefault('chapter_id', chapter_id)
    if title_hint:
        payload.setdefault('hint', title_hint)
    append_message(username, session['id'], 'user', question, payload, auto_title=False)
    append_message(username, session['id'], 'assistant', answer, payload, auto_title=False)
    return {'saved': True, 'session_id': session['id']}


def transcript(session):
    """把会话导出成一段可一键复制的 Markdown 文本。"""
    lines = [f"# {session.get('title', '星辰教练对话')}",
             f"时间：{session.get('created_at', '')}", '']
    for m in session.get('messages', []):
        who = '我' if m.get('role') == 'user' else 'JJ老师'
        meta = m.get('meta') or {}
        tag = f"（来自{meta.get('source')}）" if meta.get('source') in ('exercise', 'training', 'exam') else ''
        lines.append(f'**{who}**{tag}  `{m.get("ts", "")}`')
        lines.append('')
        lines.append(str(m.get('content', '')))
        lines.append('')
    return '\n'.join(lines)


# ── 提示词 ──────────────────────────────────────────────
COACH_SYSTEM_PROMPT = """你是「JJ老师」，PyMaster 学习平台的 Python 与 AI 教练。你的学生是中学生与编程初学者。

【回答风格】
- 先正面回答学生的问题，讲清楚「为什么」，再用具体例子落地。
- 用生活类比解释抽象概念，语气温和、有耐心，可以活泼但不要油腻。
- 代码一律用 Markdown 代码块，必须是能直接运行的 Python 3 语法。
- 学生没说清楚的地方，先基于常识做最合理的假设并说明假设，不要反复追问后什么都不答。
- 中文回答，控制在 500 字以内。

【哲思引导（这是你的核心职责，每次回答都必须做到）】
回答完问题后，你必须主动提出 1 个新的问题，引导学生往下想一层。这个追问要满足：
- 具体、可验证，学生想一想能答上来，而不是空泛的「你觉得呢」。
- 与刚才的内容直接相关，指向一个更深的原理、一个反例、或一次动手验证。
- 单独用一行以「🤔 想一想：」开头，问题只问一件事。
例如学生问完列表和元组，你答完可以追问：
「🤔 想一想：如果元组里装的是列表，那个列表里的元素还能改吗？为什么？」
学生如果只是答了上一个追问，你要先点评他的思路（对在哪里、漏在哪里），再给下一个追问。

【边界】
- 只回答 Python、编程、AI 与当前课程相关的问题；无关话题礼貌说明你只教这些。
- 不确定的版本差异、库 API 或运行结果，直说「我不确定」并建议用最小示例验证，绝不编造。
- 学生贴的是练习题时，先给思路和方向，别直接甩完整答案；他说「给我看答案」时再给。
"""
