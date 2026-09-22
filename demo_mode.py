"""评审演示账号：能真操作，但改动不落盘。

为什么需要
----------
比赛要求"提供可供评审使用的测试账号"。评审会真的去点、去做题、去问 AI，
如果给他一个真实教师的账号，他的操作会污染真实学习数据；如果给访客模式，
进度、修行阁、错题本全是空的，"智能体"看起来像个空壳。

折中做法：**演示账号有一个预置好的、有学习痕迹的档案**（有进度、有积分、
有错题、修行阁已解锁若干境界），评审看到的是一个"用过一阵子的学生"；
但他的一切改动都**只存在内存里，不写任何文件**，
容器重启或重新登录就回到初始状态。真实数据一个字节都不会被碰到。

启用方式
--------
    PYMASTER_DEMO_USER=demo            # 演示账号用户名（默认 demo）
    PYMASTER_DEMO_PASSWORD=demo2026    # 登录口令（部署脚本会生成一个随机的）
    PYMASTER_DEMO_SEED=/path/demo.json # 预置档案（可选，没有就用内置模板）

不设 PYMASTER_DEMO_USER 时本模块完全不生效，本地版行为与以前一致。
"""
import copy
import os
import threading

_LOCK = threading.Lock()

# 演示账号的默认画像：一个"学了一阵子"的学生。
# 数值刻意选得不夸张（不是满分大神），这样评审看到的是可信的学习轨迹。
_SEED_TEMPLATE = {
    'profile': {
        'nickname': '演示同学',
        'note': '评审演示账号：可以任意操作，所有改动都不会保存',
        'mode': 'all_unlocked',
        'progress': {},
        'completed_kps': ['1_0', '1_1', '1_2', '1_3', '1_4', '2_0', '2_1', '3_0'],
        'completed_exercises': [],
        'favorites': [],
        'wrong_answers': [
            {'chapter_id': 4, 'question': '偶数下标字符怎么取？',
             'user_answer': 's[1::2]', 'correct_answer': 's[::2]'},
        ],
        'notes': {},
        'points': 186,
    },
    'training': {
        'points': 186,
        'attempts': {
            'ch01-01': {'attempts': 1, 'runs': 2, 'solved': True, 'best_stars': 3,
                        'clears': 1, 'points': 10, 'history': []},
            'ch02-01': {'attempts': 2, 'runs': 3, 'solved': True, 'best_stars': 2,
                        'clears': 1, 'points': 18, 'history': []},
            'ch03-01': {'attempts': 1, 'runs': 1, 'solved': True, 'best_stars': 3,
                        'clears': 1, 'points': 10, 'history': []},
            'ch04-01': {'attempts': 3, 'runs': 4, 'solved': False, 'best_stars': 0,
                        'clears': 0, 'wrong': 2, 'points': 0, 'history': []},
        },
        'rewards': {},
        'drafts': {},
    },
}

# 内存里的当前副本（按用户名缓存，进程内共享）
_memo = {}


def demo_user():
    return (os.environ.get('PYMASTER_DEMO_USER') or '').strip()


def demo_password():
    return (os.environ.get('PYMASTER_DEMO_PASSWORD') or 'demo2026').strip()


def is_enabled():
    return bool(demo_user())


def is_demo(username):
    return is_enabled() and (username or '').strip() == demo_user()


def _load_seed():
    """预置档案：优先读外部文件，没有就用内置模板。"""
    template = copy.deepcopy(_SEED_TEMPLATE)
    path = (os.environ.get('PYMASTER_DEMO_SEED') or '').strip()
    if path and os.path.exists(path):
        try:
            import json
            with open(path, 'r', encoding='utf-8') as f:
                extra = json.load(f)
            profile = extra.get('profile') or {}
            training = extra.get('training') or {}
            template['profile'].update(profile)
            template['training'].update(training)
        except (OSError, ValueError):
            pass
    return template


def get_profile():
    """演示账号的用户档案（内存副本）。"""
    with _LOCK:
        if 'profile' not in _memo:
            _memo['profile'] = _load_seed()['profile']
        return copy.deepcopy(_memo['profile'])


def set_profile(data):
    """写档案 —— 只进内存，不落盘。"""
    with _LOCK:
        _memo['profile'] = copy.deepcopy(data)


def get_training_state():
    with _LOCK:
        if 'training' not in _memo:
            _memo['training'] = _load_seed()['training']
        return copy.deepcopy(_memo['training'])


def set_training_state(state):
    with _LOCK:
        _memo['training'] = copy.deepcopy(state)


def reset():
    """把演示账号恢复到初始状态（评审想重来一遍时用）。"""
    with _LOCK:
        _memo.clear()


def banner():
    """启动时打印一行，提醒这是演示模式。"""
    if not is_enabled():
        return ''
    return (f'[demo] 评审演示账号已启用：{demo_user()} / {demo_password()}'
            '（所有改动只在内存里，不写入磁盘）')
