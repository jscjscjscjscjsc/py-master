"""公网版的访问数据库（SQLite）。

为什么单独一份 SQLite，而不是继续用 json 文件
--------------------------------------------
账号数据（users.json）留在原处不动：它被 app.py 里几十处读写，
还被刷题引擎、教练引擎各自引用，整体搬进数据库是"为了好看而冒大风险"，
而且单机版必须保持"整个平台就是一个文件夹、拷贝即迁移"的形态。

但**访问日志**是另一种负载，它天生适合数据库：
  · 只追加、按时间倒序查、要按用户/事件/日期范围筛选、要出统计；
  · 用 json 文件就得把整个文件读进内存再在 Python 里筛，
    几千条之后后台页面会明显变慢，而且没法分页；
  · 十几个人用，SQLite 绰绰有余 —— 它是进程内的库，
    没有网络往返、没有额外服务要装、不用配账号密码，
    写入是原子的，断电也不容易坏（WAL 模式）。

并发写法：每次操作开一个短连接（SQLite 打开文件很便宜），
外面套一把模块级锁。十几个人、每秒几个请求的规模下，
这比维护连接池简单得多，也不会踩 sqlite3 的"连接不能跨线程"那条线。
"""
from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
import threading
from datetime import datetime, timedelta

# 事件 → 中文标签。后台页直接用它渲染，不用在前端再维护一份映射。
EVENT_LABELS = {
    'register': '注册',
    'login': '登录',
    'login_fail': '登录失败',
    'logout': '退出',
    'password_reset': '重设密码',
    'ai_bind': '绑定模型',
    'ai_clear': '解绑模型',
    'visit': '浏览',
    'admin': '管理操作',
}

# 「有名字」的事件：会出现在日志筛选下拉里。
# visit 单独归一类，否则几千条浏览记录会把登录/注册这些关键事件淹掉。
NOTABLE_EVENTS = tuple(k for k in EVENT_LABELS if k != 'visit')

RETENTION_DAYS = 90
_VISIT_DEDUP_SECONDS = 60      # 同一用户刷同一个页面不重复记

_DB_FILE = None
_LOCK = threading.RLock()
_last_prune_day = None


def configure(data_dir):
    """由 app.py 在启动时指定数据库位置（跟随 PYMASTER_DATA_DIR）。"""
    global _DB_FILE
    _DB_FILE = os.path.join(data_dir, 'access.db')


def db_path():
    return _DB_FILE


def _connect():
    # timeout 给足：多个人同时写的时候让 SQLite 自己等一下再报 busy
    conn = sqlite3.connect(_DB_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    """建表。幂等，可以每次启动都调。"""
    if not _DB_FILE:
        return False
    with _LOCK:
        os.makedirs(os.path.dirname(_DB_FILE), exist_ok=True)
        conn = _connect()
        try:
            # WAL：读写不互相阻塞，崩了也能自动恢复
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS access_log (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts       TEXT NOT NULL,
                    epoch    INTEGER NOT NULL,
                    day      TEXT NOT NULL,
                    username TEXT NOT NULL DEFAULT '',
                    event    TEXT NOT NULL,
                    ip       TEXT DEFAULT '',
                    ua       TEXT DEFAULT '',
                    path     TEXT DEFAULT '',
                    detail   TEXT DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_log_epoch  ON access_log(epoch DESC);
                CREATE INDEX IF NOT EXISTS idx_log_user   ON access_log(username, epoch DESC);
                CREATE INDEX IF NOT EXISTS idx_log_event  ON access_log(event, epoch DESC);
                CREATE INDEX IF NOT EXISTS idx_log_day    ON access_log(day);

                -- 每个人每种事件的累计计数：后台列表直接读它，
                -- 不用对几千行做 GROUP BY（十几个人用不到，但顺手就做了）
                CREATE TABLE IF NOT EXISTS user_rollup (
                    username    TEXT NOT NULL,
                    event       TEXT NOT NULL,
                    count       INTEGER NOT NULL DEFAULT 0,
                    first_epoch INTEGER NOT NULL,
                    last_epoch  INTEGER NOT NULL,
                    last_ip     TEXT DEFAULT '',
                    PRIMARY KEY (username, event)
                );
            ''')
            conn.commit()
        finally:
            conn.close()
        _prune()
        return True


def _prune():
    """只保留最近 RETENTION_DAYS 天，每天做一次。

    公网站的日志没人会手动清理，不自动裁掉的话这个文件会一直长。
    浏览记录（visit）留 30 天就够查"最近来过没"，关键事件留满 90 天。
    """
    global _last_prune_day
    today = datetime.now().strftime('%Y-%m-%d')
    if _last_prune_day == today:
        return
    _last_prune_day = today
    cutoff = int((datetime.now() - timedelta(days=RETENTION_DAYS)).timestamp())
    visit_cutoff = int((datetime.now() - timedelta(days=30)).timestamp())
    try:
        conn = _connect()
        try:
            conn.execute('DELETE FROM access_log WHERE epoch < ? AND event != ?',
                         (cutoff, 'visit'))
            conn.execute('DELETE FROM access_log WHERE epoch < ?', (visit_cutoff,))
            conn.commit()
        finally:
            conn.close()
    except sqlite3.Error:
        pass


def _device_of(ua):
    """把 User-Agent 压成"系统 · 浏览器"，后台列表一眼能看懂。"""
    ua = ua or ''
    low = ua.lower()
    if not ua:
        return ''
    if 'android' in low:
        os_name = 'Android'
    elif 'iphone' in low or 'ipad' in low:
        os_name = 'iOS'
    elif 'windows' in low:
        os_name = 'Windows'
    elif 'mac os' in low or 'macintosh' in low:
        os_name = 'macOS'
    elif 'linux' in low:
        os_name = 'Linux'
    else:
        os_name = ''

    # 顺序有讲究：Chrome / Edge 的 UA 里都带 "Safari"，必须先判它们。
    # 反过来判的话所有 Chrome 都会被记成 Safari，后台看着就不对了。
    if 'edg/' in low:
        browser = 'Edge'
    elif 'chrome/' in low or 'crios/' in low:
        browser = 'Chrome'
    elif 'firefox/' in low:
        browser = 'Firefox'
    elif 'safari/' in low:
        browser = 'Safari'
    elif 'python' in low or 'curl' in low or 'wget' in low:
        browser = '脚本'
    else:
        browser = ''

    if os_name and browser:
        return f'{os_name} · {browser}'
    return os_name or browser


# 详情字段 → 中文名。后台列表里直接读它拼一句人话，
# 而不是把 {"action":"登录后台"} 这种原始 JSON 摊在表格里。
_DETAIL_FIELDS = {
    'action': '操作',
    'reason': '原因',
    'model': '模型',
    'base_url': '地址',
    'detail': '变更项',
}


def _format_detail(detail_text):
    """把详情 JSON 拼成一句人话：登录后台 / 模型 deepseek-v4.1-flash · 地址 …"""
    if not detail_text:
        return ''
    try:
        obj = json.loads(detail_text)
    except (ValueError, TypeError):
        return str(detail_text)[:120]
    if isinstance(obj, list):
        return '、'.join(str(x) for x in obj)[:120]
    if not isinstance(obj, dict):
        return str(obj)[:120]
    parts = []
    for key, value in obj.items():
        label = _DETAIL_FIELDS.get(key, key)
        text = ', '.join(str(x) for x in value) if isinstance(value, list) else str(value)
        # 只有"操作/原因"这类本身就读得通的字段才省略前缀，
        # 其余拼成 "模型 xxx" 更好认
        if key in ('action', 'reason'):
            parts.append(text)
        else:
            parts.append(f'{label} {text}')
    return ' · '.join(parts)[:160]


def record(username, event, ip='', ua='', path='', detail=None, dedup=False):
    """记一笔。任何失败都只打印，绝不打断正在处理的请求。

    dedup=True（浏览记录用）：同一用户、同一路径、一分钟内只记第一次，
    否则停留在某个页面上反复点按钮会刷出几百条一样的行。
    """
    if not _DB_FILE:
        return
    try:
        now = datetime.now()
        ts = now.strftime('%Y-%m-%d %H:%M:%S')
        epoch = int(now.timestamp())
        day = now.strftime('%Y-%m-%d')
        detail_text = ''
        if detail:
            detail_text = json.dumps(detail, ensure_ascii=False) if isinstance(detail, dict) \
                else str(detail)
        with _LOCK:
            conn = _connect()
            try:
                if dedup:
                    hit = conn.execute(
                        'SELECT 1 FROM access_log WHERE username=? AND path=? AND event=? '
                        'AND epoch > ? LIMIT 1',
                        (username or '', path, event, epoch - _VISIT_DEDUP_SECONDS)).fetchone()
                    if hit:
                        return
                conn.execute(
                    'INSERT INTO access_log (ts, epoch, day, username, event, ip, ua, path, detail) '
                    'VALUES (?,?,?,?,?,?,?,?,?)',
                    (ts, epoch, day, username or '', event, ip or '', (ua or '')[:300],
                     path or '', detail_text))
                conn.execute(
                    'INSERT INTO user_rollup (username, event, count, first_epoch, last_epoch, last_ip) '
                    'VALUES (?,?,1,?,?,?) '
                    'ON CONFLICT(username, event) DO UPDATE SET '
                    '  count = count + 1, last_epoch = excluded.last_epoch, last_ip = excluded.last_ip',
                    (username or '', event, epoch, epoch, ip or ''))
                conn.commit()
            finally:
                conn.close()
        _prune()
    except sqlite3.Error as exc:
        print(f'[access-db] 写日志失败（不影响使用）：{exc}')
    except Exception as exc:
        print(f'[access-db] 记日志异常（不影响使用）：{exc}')


def _build_filter(username=None, event=None, since=None, until=None, ip=None):
    where, params = [], []
    if username:
        where.append('username = ?')
        params.append(username)
    if event:
        if isinstance(event, (list, tuple)):
            where.append('event IN (%s)' % ','.join('?' * len(event)))
            params.extend(event)
        else:
            where.append('event = ?')
            params.append(event)
    if ip:
        where.append('ip LIKE ?')
        params.append(f'%{ip}%')
    if since:
        where.append('day >= ?')
        params.append(since)
    if until:
        where.append('day <= ?')
        params.append(until)
    return (' WHERE ' + ' AND '.join(where) if where else ''), params


def query(limit=100, offset=0, **filters):
    """按时间倒序取日志。返回 (行列表, 总数)。"""
    if not _DB_FILE:
        return [], 0
    clause, params = _build_filter(**filters)
    limit = max(1, min(int(limit or 100), 1000))
    offset = max(0, int(offset or 0))
    with _LOCK:
        conn = _connect()
        try:
            total = conn.execute(f'SELECT COUNT(*) AS c FROM access_log{clause}', params).fetchone()['c']
            rows = conn.execute(
                f'SELECT * FROM access_log{clause} ORDER BY epoch DESC, id DESC LIMIT ? OFFSET ?',
                (*params, limit, offset)).fetchall()
        finally:
            conn.close()
    out = []
    for row in rows:
        item = dict(row)
        item['event_label'] = EVENT_LABELS.get(item.get('event'), item.get('event', ''))
        item['device'] = _device_of(item.get('ua'))
        item['detail_text'] = _format_detail(item.get('detail'))
        out.append(item)
    return out, total


def export_csv(**filters):
    """导出筛选结果（给后台的「导出 CSV」用）。"""
    rows, _ = query(limit=1000, offset=0, **filters)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['时间', '用户', '事件', 'IP', '设备', '页面/路径', '详情'])
    for row in reversed(rows):          # CSV 按时间正序更好读
        writer.writerow([row['ts'], row['username'], row['event_label'], row['ip'],
                         row['device'], row['path'], row['detail']])
    return '\ufeff' + buf.getvalue()    # BOM：Excel 打开中文不乱码


def overview(days=7):
    """总览卡片 + 最近若干天的活跃度。"""
    if not _DB_FILE:
        return {}
    today = datetime.now().strftime('%Y-%m-%d')
    since_day = (datetime.now() - timedelta(days=int(days) - 1)).strftime('%Y-%m-%d')
    with _LOCK:
        conn = _connect()
        try:
            def one(sql, params=()):
                row = conn.execute(sql, params).fetchone()
                return row['c'] if row else 0

            today_visitors = one(
                "SELECT COUNT(DISTINCT username) AS c FROM access_log "
                "WHERE day=? AND event='visit' AND username != ''", (today,))
            today_logins = one(
                "SELECT COUNT(*) AS c FROM access_log WHERE day=? AND event='login'", (today,))
            today_registers = one(
                "SELECT COUNT(*) AS c FROM access_log WHERE day=? AND event='register'", (today,))
            total_events = one('SELECT COUNT(*) AS c FROM access_log')
            fail_logins = one(
                "SELECT COUNT(*) AS c FROM access_log WHERE event='login_fail' AND day>=?",
                (since_day,))
            series = conn.execute(
                "SELECT day, COUNT(DISTINCT CASE WHEN event='visit' THEN username END) AS visitors, "
                "       SUM(CASE WHEN event='login' THEN 1 ELSE 0 END) AS logins, "
                "       SUM(CASE WHEN event='register' THEN 1 ELSE 0 END) AS registers "
                "FROM access_log WHERE day >= ? GROUP BY day ORDER BY day", (since_day,)).fetchall()
        finally:
            conn.close()

    by_day = {row['day']: row for row in series}
    days_list = []
    for i in range(int(days) - 1, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        row = by_day.get(day)
        days_list.append({
            'day': day,
            'visitors': (row['visitors'] or 0) if row else 0,
            'logins': (row['logins'] or 0) if row else 0,
            'registers': (row['registers'] or 0) if row else 0,
        })
    return {
        'today_visitors': today_visitors,
        'today_logins': today_logins,
        'today_registers': today_registers,
        'total_events': total_events,
        'recent_login_fail': fail_logins,
        'days': days_list,
    }


def user_rollup(username):
    """某个用户的累计计数（登录次数、最后活跃时间、用过的 IP）。"""
    if not _DB_FILE:
        return {}
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                'SELECT event, count, first_epoch, last_epoch, last_ip FROM user_rollup '
                'WHERE username=?', (username,)).fetchall()
            ip_rows = conn.execute(
                'SELECT ip, COUNT(*) AS c, MAX(ts) AS last_ts FROM access_log '
                'WHERE username=? AND ip != "" GROUP BY ip ORDER BY c DESC LIMIT 5',
                (username,)).fetchall()
            last_seen = conn.execute(
                'SELECT ts, path, ip FROM access_log WHERE username=? AND event="visit" '
                'ORDER BY epoch DESC LIMIT 1', (username,)).fetchone()
        finally:
            conn.close()

    def fmt(epoch):
        try:
            return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
        except (OSError, ValueError, TypeError):
            return ''

    counters = {row['event']: row['count'] for row in rows}
    # 「登录次数」把注册也算进去：注册成功时平台会自动登录（见 app.py 的
    # register 视图），所以只统计 login 事件的话，"注册完一直在用、
    # 只是没再手动登出登入"的人会显示 0 次登录 —— 站长看着像他没来过。
    login_total = counters.get('login', 0) + counters.get('register', 0)
    result = {
        'login_count': login_total,
        'login_only_count': counters.get('login', 0),
        'visit_count': counters.get('visit', 0),
        'fail_count': counters.get('login_fail', 0),
        'register_count': counters.get('register', 0),
        'ai_bind_count': counters.get('ai_bind', 0),
        'events': {row['event']: {
            'count': row['count'],
            'first': fmt(row['first_epoch']),
            'last': fmt(row['last_epoch']),
            'last_ip': row['last_ip'] or '',
        } for row in rows},
        'ips': [{'ip': row['ip'], 'count': row['c'], 'last': row['last_ts']} for row in ip_rows],
        'last_seen': dict(last_seen) if last_seen else {},
    }
    return result


def all_user_summaries():
    """所有人的活跃摘要，一次查出来给后台列表用（避免每人一条 SQL）。"""
    if not _DB_FILE:
        return {}
    with _LOCK:
        conn = _connect()
        try:
            rows = conn.execute(
                'SELECT username, '
                '  SUM(CASE WHEN event="login" THEN 1 ELSE 0 END) AS logins, '
                '  SUM(CASE WHEN event="register" THEN 1 ELSE 0 END) AS registers, '
                '  SUM(CASE WHEN event="visit" THEN 1 ELSE 0 END) AS visits, '
                '  SUM(CASE WHEN event="login_fail" THEN 1 ELSE 0 END) AS fails, '
                '  MIN(epoch) AS first_epoch, MAX(epoch) AS last_epoch '
                'FROM access_log WHERE username != "" GROUP BY username').fetchall()
            # 最后访问的 IP / 页面：按用户取最新那条（窗口函数，SQLite 3.25+ 自带）
            latest = conn.execute(
                'SELECT username, ip, path, ts FROM ('
                '  SELECT username, ip, path, ts, ROW_NUMBER() OVER '
                '  (PARTITION BY username ORDER BY epoch DESC, id DESC) AS rn '
                '  FROM access_log WHERE username != "") WHERE rn = 1').fetchall()
        finally:
            conn.close()

    def fmt(epoch):
        try:
            return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
        except (OSError, ValueError, TypeError):
            return ''

    out = {row['username']: {
        # 同 user_rollup：注册即自动登录，所以登录次数含注册那一次
        'login_count': (row['logins'] or 0) + (row['registers'] or 0),
        'visit_count': row['visits'] or 0,
        'fail_count': row['fails'] or 0,
        'first_seen': fmt(row['first_epoch']),
        'last_seen': fmt(row['last_epoch']),
    } for row in rows}
    for row in latest:
        item = out.setdefault(row['username'], {})
        item['last_ip'] = row['ip'] or ''
        item['last_path'] = row['path'] or ''
        item['last_seen'] = row['ts'] or item.get('last_seen', '')
    return out


def user_ips(username):
    """某个用户用过的全部 IP（含次数），后台详情展开用。"""
    return user_rollup(username).get('ips', [])
