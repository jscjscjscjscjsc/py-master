"""PyMaster 图文讲解引擎 —— 把知识点变成 5 分钟带画面的口播讲解。

三级流水线（每级都落盘缓存，重跑不重复烧钱）
---------------------------------------------
1. 分镜脚本：火山方舟大模型把知识点改写成 N 个镜头，
   每个镜头含 口播稿 / 画面说明 / 字幕要点 / 可选代码。
2. 画面：Seedream 生图，全课程统一的漫画风格与固定主角（蛇蛇老师 + 小码），
   保证一节讲解视觉连贯。
3. 口播：微软 edge-tts 免费合成，按镜头切分成独立音频，方便图文同步与跳转。

产物
----
- data/narrations.json                     分镜脚本索引（key: "<章号>_<知识点序号>"）
- static/narrations/<ch>_<kp>/s01.jpg…     镜头配图
- data/audio_cache/narr_<hash>.mp3         镜头口播
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
STATIC_NARR_DIR = ROOT / 'static' / 'narrations'
AUDIO_CACHE = DATA_DIR / 'audio_cache'
NARRATIONS_FILE = DATA_DIR / 'narrations.json'

ARK_BASE = 'https://ark.cn-beijing.volces.com/api/v3'
DEFAULT_TEXT_MODEL = 'doubao-seed-2-0-code-preview-260215'
DEFAULT_IMAGE_MODEL = 'doubao-seedream-4-0-250828'

# 一节讲解的目标规模：16 镜头 × 约 100 字 ≈ 300 秒
# 实测 edge-tts 云希声线 +6% 语速下中文约 5.3 字/秒
DEFAULT_SCENES = 16
TARGET_SECONDS = 300
CHARS_PER_SECOND = 5.3

# 统一画风：和平台既有的蛇蛇老师 / 小码 形象保持一致。
# 明确排除像素风——否则模型会随机给出 8-bit 马赛克质感，破坏一节讲解内的视觉连贯。
STYLE_PROMPT = (
    '风格要求（必须严格遵守）：现代化扁平矢量插画，干净的色块与平滑曲线，'
    '均匀的浅色描边，柔和阴影，明快配色（青绿、橙黄、米白背景），'
    '构图居中、留白充足，适合作为课件大图。'
    '绝对不要像素风、不要 8-bit 马赛克、不要写实照片、不要 3D 渲染。'
    '画面里的屏幕、纸张、面板、标签等界面元素只用纯色块与简单图标示意，'
    '不要绘制任何文字、字母、数字或伪文字。'
    '主角形象固定：一条戴圆框眼镜的友善绿色小蛇（蛇蛇老师），'
    '偶尔出现一只黄色小鸡（学生小码），角色造型每一张都要保持一致。'
)

VOICE_BY_TYPE = {
    'hook': 'zh-CN-YunxiNeural',
    'concept': 'zh-CN-YunxiNeural',
    'code': 'zh-CN-YunxiNeural',
    'compare': 'zh-CN-XiaoxiaoNeural',
    'pitfall': 'zh-CN-XiaoxiaoNeural',
    'summary': 'zh-CN-YunyangNeural',
}
VOICE_LABELS = {
    'zh-CN-YunxiNeural': '云希 · 清亮男声',
    'zh-CN-XiaoxiaoNeural': '晓晓 · 温暖女声',
    'zh-CN-YunyangNeural': '云扬 · 沉稳旁白',
}

_SCRIPT_SYSTEM = (
    '你是一位职业院校的 Python 与 AI 应用开发讲师，擅长把技术知识点讲成'
    '有画面感、有节奏、口语化但信息密度极高的短视频课程。'
    '你的讲解必须严格基于给定教材内容，不得编造教材里没有的 API、数字或结论。'
    '输出必须是合法的 JSON，不要输出任何解释文字或 Markdown 代码围栏。'
)


def _env(name, default=''):
    value = os.environ.get(name)
    if value:
        return value.strip()
    env_file = ROOT / '.env'
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if key.strip() == name:
                    return val.strip()
    return default


class ArkText:
    """火山方舟文本模型：流式读取，避免长输出被单次超时截断。"""

    def __init__(self, model=None, api_key=None, base=None):
        self.model = model or _env('PYMASTER_AI_MODEL', DEFAULT_TEXT_MODEL)
        self.api_key = api_key or _env('ARK_API_KEY') or _env('PYMASTER_AI_API_KEY')
        self.url = (base or _env('PYMASTER_AI_BASE_URL', ARK_BASE)).rstrip('/')
        if not self.url.endswith('/chat/completions'):
            self.url += '/chat/completions'

    @property
    def available(self):
        return bool(self.api_key)

    def complete(self, system, user, max_tokens=8000, temperature=0.6, timeout=240,
                 attempts=4):
        if not self.api_key:
            raise RuntimeError('未配置 ARK_API_KEY，无法生成讲解稿。')
        payload = {
            'model': self.model,
            'messages': [{'role': 'system', 'content': system},
                         {'role': 'user', 'content': user}],
            'stream': True,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }
        body = json.dumps(payload).encode('utf-8')
        last_error = None
        for attempt in range(attempts):
            request = urllib.request.Request(
                self.url, data=body,
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + self.api_key})
            try:
                return self._read_stream(request, timeout)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode('utf-8', 'ignore')[:180]
                last_error = RuntimeError(f'HTTP {exc.code} {detail}')
                # 鉴权/额度类错误重试没有意义，直接抛出
                if exc.code in (400, 401, 403, 404):
                    raise last_error from None
            except Exception as exc:
                last_error = exc
            if attempt < attempts - 1:
                time.sleep(min(2 ** attempt, 20) + random.uniform(0, 2))
        raise RuntimeError(f'分镜脚本生成失败（已重试 {attempts} 次）：{last_error}')

    def _read_stream(self, request, timeout):
        chunks = []
        deadline = time.monotonic() + timeout
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw in response:
                if time.monotonic() > deadline:
                    raise TimeoutError('讲解稿生成超时')
                line = raw.decode('utf-8').strip()
                if not line.startswith('data:'):
                    continue
                body = line[5:].strip()
                if body == '[DONE]':
                    break
                try:
                    event = json.loads(body)
                except ValueError:
                    continue
                if event.get('error'):
                    raise RuntimeError(event['error'].get('message', '模型返回错误'))
                for choice in event.get('choices') or []:
                    piece = (choice.get('delta') or {}).get('content')
                    if piece:
                        chunks.append(piece)
        text = ''.join(chunks)
        if not text.strip():
            raise RuntimeError('模型返回空内容')
        return text


class SeedreamImages:
    """Seedream 文生图：返回图片字节，调用方负责落盘。"""

    def __init__(self, model=None, api_key=None, base=None):
        self.model = model or _env('PYMASTER_IMAGE_MODEL', DEFAULT_IMAGE_MODEL)
        self.api_key = api_key or _env('ARK_API_KEY') or _env('PYMASTER_AI_API_KEY')
        self.base = (base or _env('PYMASTER_AI_BASE_URL', ARK_BASE)).rstrip('/')
        if self.base.endswith('/chat/completions'):
            self.base = self.base[:-len('/chat/completions')]
        self.url = self.base + '/images/generations'
        self.last_error = ''

    @property
    def available(self):
        return bool(self.api_key)

    def generate(self, prompt, size='1024x1024', retries=3):
        if not self.api_key:
            raise RuntimeError('未配置 ARK_API_KEY，无法生成配图。')
        payload = {
            'model': self.model,
            'prompt': prompt,
            'size': size,
            'response_format': 'url',
            'watermark': False,
        }
        for attempt in range(retries):
            request = urllib.request.Request(
                self.url, data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + self.api_key})
            try:
                with urllib.request.urlopen(request, timeout=150) as response:
                    result = json.loads(response.read().decode('utf-8'))
                items = result.get('data') or []
                if not items:
                    raise RuntimeError('生图返回为空')
                image_url = items[0].get('url') or items[0].get('b64_json')
                if not image_url:
                    raise RuntimeError('生图未返回图片地址')
                if image_url.startswith('http'):
                    with urllib.request.urlopen(image_url, timeout=120) as remote:
                        return remote.read()
                import base64
                return base64.b64decode(image_url)
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode('utf-8', 'ignore')[:200]
                self.last_error = f'HTTP {exc.code} {detail}'
                if exc.code in (429, 500, 502, 503) and attempt < retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
                raise RuntimeError(f'生图失败：{self.last_error}') from None
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                self.last_error = str(exc)[:160]
                if attempt < retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
                raise RuntimeError(f'生图网络异常：{self.last_error}') from None
        raise RuntimeError(f'生图失败：{self.last_error}')


class VoiceOver:
    """edge-tts 免费口播；按文本+音色缓存，时长由 MP3 采样信息精确得出。

    全进程只保留**一个**常驻事件循环：早期版本每段口播都调一次 asyncio.run()
    并在多线程里并发，反复创建/销毁 Proactor 事件循环会耗尽进程的 socket 资源，
    表现为跑完一节之后所有网络请求都被拒绝（WinError 10061）。
    """

    _loop = None
    _loop_thread = None
    _loop_lock = threading.Lock()

    # 同一段文本只允许一个线程在合成，其余线程等它写完直接读缓存。
    # 并发生产时不同小节会出现相同文本（命中同一缓存文件），
    # 两个线程同时写同一个 mp3 会撞出 WinError 32 文件占用。
    _synth_locks = {}
    _synth_locks_guard = threading.Lock()

    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir or AUDIO_CACHE)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _lock_for(cls, path):
        with cls._synth_locks_guard:
            return cls._synth_locks.setdefault(str(path), threading.Lock())

    @classmethod
    def _ensure_loop(cls):
        with cls._loop_lock:
            if cls._loop is None or cls._loop.is_closed():
                loop = asyncio.new_event_loop()
                thread = threading.Thread(target=loop.run_forever, daemon=True,
                                          name='edge-tts-loop')
                thread.start()
                cls._loop, cls._loop_thread = loop, thread
            return cls._loop

    @staticmethod
    def available():
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def _clean(text):
        text = re.sub(r'```.*?```', ' ', text, flags=re.S)
        text = re.sub(r'[`*#>|]', '', text)
        text = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def duration_of(path):
        """读音频时长。Windows 上杀毒软件扫描新文件会短暂占用句柄，所以重试几次。"""
        from mutagen.mp3 import MP3
        for attempt in range(4):
            try:
                return float(MP3(str(path)).info.length)
            except PermissionError:
                if attempt == 3:
                    break
                time.sleep(0.4 * (attempt + 1))
            except Exception:
                break
        return round(path.stat().st_size * 8 / 48000, 2)

    @staticmethod
    async def _save(text, voice, rate, pitch, path):
        import edge_tts
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(str(path))

    def synth(self, text, voice='zh-CN-YunxiNeural', rate='+6%', pitch='+0Hz', attempts=5):
        """合成一段口播。

        edge-tts 是免费公共服务，偶发 TLS 抖动与限流，实测同一句话
        可能连续失败几次再成功，所以这里退避重试并在最后换音色兜底——
        批量生产时单点抖动不应该让整节课作废。

        并发安全：同一段文本用同一把锁串行合成，并且先写临时文件再原子替换，
        保证读缓存的一方永远看不到写了一半的文件。
        """
        text = self._clean(text)
        if len(text) < 2:
            return None, 0.0
        key = hashlib.md5(f'{voice}|{rate}|{pitch}|{text}'.encode('utf-8')).hexdigest()
        path = self.cache_dir / f'narr_{key}.mp3'

        lock = self._lock_for(path)
        with lock:
            if path.exists() and path.stat().st_size > 1024:
                return path, self.duration_of(path)

            loop = self._ensure_loop()
            fallbacks = [voice] + [v for v in VOICE_BY_TYPE.values() if v != voice]
            last_error = None
            tmp = path.with_suffix(f'.{os.getpid()}.{threading.get_ident()}.tmp')

            for attempt in range(attempts):
                target_voice = fallbacks[min(attempt // 2, len(fallbacks) - 1)]
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self._save(text, target_voice, rate, pitch, tmp), loop)
                    future.result(timeout=90)
                    if tmp.exists() and tmp.stat().st_size > 1024:
                        os.replace(tmp, path)   # 原子替换，读者不会看到半个文件
                        return path, self.duration_of(path)
                    last_error = RuntimeError('返回空音频')
                except Exception as exc:
                    last_error = exc
                tmp.unlink(missing_ok=True)
                if attempt < attempts - 1:
                    time.sleep(min(2 ** attempt, 16) + random.uniform(0, 1.5))
            raise RuntimeError(f'语音合成失败（已重试 {attempts} 次）：{last_error}')


def kp_text(html_content):
    """把知识点 HTML 还原成纯文本喂给大模型（保留代码块，讲解要能引用代码）。"""
    try:
        if str(ROOT / 'tools') not in sys.path:
            sys.path.insert(0, str(ROOT / 'tools'))
        from md2html import html_to_text
        return html_to_text(html_content)
    except Exception:
        text = re.sub(r'<(script|style).*?</\1>', ' ', html_content, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()


# ---------------------------------------------------------------- 分镜脚本

_SCENE_SCHEMA = """{
  "title": "本讲标题，不超过 14 个字",
  "hook_line": "一句话点题，不超过 20 字",
  "scenes": [
    {
      "type": "hook | concept | code | compare | pitfall | summary | flow",
      "title": "镜头小标题，不超过 12 个字",
      "narration": "口播稿，纯口语中文，不要 Markdown、不要念代码符号",
      "caption": "屏幕字幕要点，不超过 30 字，允许用 → 表示关系",
      "code": "需要展示的代码片段（没有就留空字符串）",
      "visual": { "layout": "与该镜头 type 相同", "...": "见下方各 layout 的字段说明" }
    }
  ]
}"""

_VISUAL_SPEC = """【visual 字段：这是配图的作图规格，由排版程序精确渲染，务必遵守字数上限】
按镜头 type 选用对应 layout，字段如下（不用的字段留空字符串或空数组）：

- layout="hook"（开场）
  title 标题≤16字；question 一句钩子问题≤26字；mood 取 "happy" 或 "alert"；
  bullets 最多 2 条，每条 text≤18字

- layout="concept"（概念）
  title 标题≤16字；subtitle 副标题≤24字（可空）；
  bullets 3~4 条，每条 {"icon":"①","text":"≤16字"}，icon 可用 ①②③④ 或单个 emoji；
  highlight 一句话结论≤20字

- layout="code"（代码）
  title≤16字；code 代码≤8 行、每行≤42 字符（必须是教材原文里能跑的代码，不要截断成不完整的行）；
  output 运行结果≤4 行（没有就留空）；bullets 最多 1 条，text≤20字

- layout="compare"（对比）
  title≤16字；left 和 right 各为 {"label":"≤10字","lines":["≤12字", ...]}，lines 2~4 条；
  highlight 结论≤20字

- layout="pitfall"（踩坑）
  title≤16字；wrong 错误说明≤26字；wrong_code 错误代码≤4行、每行≤42字符（保持语句完整）；
  right_answer 正确说明≤26字；right_code 正确代码≤4行、每行≤42字符（保持语句完整）；
  highlight 提醒≤20字

- layout="summary"（小结）
  title≤16字；bullets 恰好 3 条，每条≤20字（会渲染成大号编号卡片，务必简短）

- layout="flow"（流程）
  title≤16字；steps 3~5 步，每步≤14字；highlight 关键点≤20字

硬性要求：
- 每条文案都必须能在一行内排下，超字数会破坏版面，必须压缩到上限之内。
- 文案里可以有中文、英文、数字，但不要出现 Markdown 符号（** # `）和换行符。
- 每张图的信息必须与同镜头的 narration 讲的是同一件事。"""


def _legacy_image_prompt_note():
    """仅在需要调用第三方生图模型时追加的说明（默认不走这条路径）。"""
    return ('6. image_prompt 描述该镜头的漫画插画，要具体（主体 + 动作 + 视觉隐喻），'
            '不要出现文字要求，不要和别的镜头重复。')


def build_script_prompt(chapter_title, kp_title, kp_text, scenes=DEFAULT_SCENES,
                        want_image_prompt=False):
    total_chars = int(TARGET_SECONDS * CHARS_PER_SECOND)
    lo, hi = total_chars // scenes - 4, total_chars // scenes + 6
    span = f'{lo * scenes}–{hi * scenes}'
    visual_note = '' if want_image_prompt else '\n' + _VISUAL_SPEC
    image_note = ('\n' + _legacy_image_prompt_note()) if want_image_prompt else ''
    return f"""请为下面这个知识点写一节 5 分钟的图文讲解分镜脚本。

【所属章节】{chapter_title}
【知识点】{kp_title}

【教材原文】
{kp_text[:7000]}

【写作要求】
1. 一共 {scenes} 个镜头，按顺序覆盖这个知识点的完整逻辑：
   - 第 1 个镜头 type=hook：用一个真实小场景或提问抓住注意力
   - 中间用 concept（概念拆解）、code（代码演示）、compare（对比辨析）、
     pitfall（常见坑）、flow（流程）交替推进
   - 至少 2 个 pitfall 镜头，写学生真实会犯的错
   - 最后 1 个镜头 type=summary：收束成 3 条必须记住的结论
2. **字数硬性要求（最重要）**：每个镜头 narration 必须写满 {lo} 到 {hi} 个汉字。
   这是 5 分钟口播课的节奏，写短了不够时长，写长了讲不完。
   - 写完后自己数一遍每个镜头的字数，凡是少于 {lo} 字的镜头，必须补充
     具体细节（为什么这样设计、和前面知识的联系、一个反例、一句易错提醒）把它补足。
   - 全篇合计 {span} 字之间（中文字符才算字数，标点不计）。
3. 讲解风格：
   - 口语化，像老师在耳边讲，允许"我们来看""注意这里""记住这句话"这类过渡
   - 信息密度高：每句话都要推进理解，不要空话套话
   - 不要出现 Markdown 符号（不要用 ** 加粗），不要朗读代码符号
     （可以说"用中括号取值"，不要念"中括号 i 中括号"）
   - 前后镜头用自然的语言衔接，像一节课而不是片段拼接
4. caption 是屏幕上显示的一句话要点，不超过 30 字，允许用箭头表达因果关系。
5. code 只有在需要展示代码时填写：必须是教材原文里的代码或由它直接改写，保持可运行、缩进正确。
   没有代码的镜头留空字符串。{image_note}
7. 严格基于教材原文，不要引入教材里没有的 API 或结论。
{visual_note}
只输出 JSON，结构如下：
{_SCENE_SCHEMA}"""


def _extract_json(text):
    """模型偶尔会包一层代码围栏或在前后加话，这里做容错提取。"""
    text = text.strip()
    fence = re.search(r'```(?:json)?\s*(.*?)```', text, flags=re.S)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('模型没有返回 JSON')
    return json.loads(text[start:end + 1])


def clean_narration(text):
    """口播稿要保持纯口语：清掉模型偶尔漏出的 Markdown 标记与括号说明。"""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = text.replace('`', '').replace('##', '').replace('#', '')
    text = re.sub(r'^\s*[-•]\s*', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


_EXPAND_SYSTEM = (
    '你是课程讲稿的润色编辑。任务是把偏短的镜头讲稿补写到目标字数，'
    '只允许增加内容，不允许改变原意、不允许删减已有信息、不允许改掉代码与字幕要点。'
    '补写内容必须来自给定教材，绝不能编造教材里没有的 API 或结论。'
    '输出必须是合法 JSON，不要输出解释文字或 Markdown 代码围栏。'
)


def _expand_prompt(chapter_title, kp_title, scenes, target_len):
    items = []
    for scene in scenes:
        items.append({
            'id': scene['id'],
            'type': scene['type'],
            'title': scene['title'],
            'caption': scene['caption'],
            'current_chars': len(scene['narration']),
            'narration': scene['narration'],
        })
    return f"""下面这节讲解《{kp_title}》（所属章节：{chapter_title}）中有几个镜头的口播稿太短，
一节课的节奏撑不起来。请把每个镜头补写到 {target_len} 字左右（中文字符计，标点不计）。

【待补写的镜头】
{json.dumps(items, ensure_ascii=False, indent=1)}

【补写要求】
1. 每个镜头补到 {target_len} 字左右，**绝对不要超过 {target_len + 10} 字**。
   全篇合计不要超过 {target_len * len(scenes)} 字——超了这节课就讲不完了。
2. 保留原有的叙述顺序和全部已有信息，只在合适位置增加：
   - 为什么这样设计的解释
   - 与前面章节知识的呼应
   - 一个反例或易错提醒
   - 一句帮助学生记忆的总结
3. 保持口语化，不要 Markdown 符号，不要朗读代码符号。
4. 不要改 type / title / caption。

只输出 JSON：{{"scenes": [{{"id": 镜头编号, "narration": "补写后的完整口播稿"}}]}}"""


def expand_short_scenes(client, chapter_title, kp_title, script, target_chars):
    """对明显偏短的镜头做一次定向补写。

    大模型对"写满 N 字"这类长度指令完成度不稳定，实测常只写到七成，
    所以这里按实际字数再补一轮，保证一节讲解真的能讲满 5 分钟。
    """
    # 实测模型会写超目标约三成，所以这里按九成下目标，落点才接近 5 分钟
    target_len = max(60, int(target_chars * 0.9 // len(script['scenes'])))
    short = [s for s in script['scenes'] if len(s['narration']) < target_len * 0.85]
    if not short:
        return script, 0
    raw = client.complete(_EXPAND_SYSTEM,
                          _expand_prompt(chapter_title, kp_title, short, target_len),
                          max_tokens=8000, temperature=0.5)
    try:
        payload = _extract_json(raw)
    except ValueError:
        return script, 0
    rewritten = {int(item['id']): clean_narration(str(item.get('narration', '')))
                 for item in payload.get('scenes') or [] if item.get('id') is not None}
    touched = 0
    for scene in script['scenes']:
        replacement = rewritten.get(scene['id'], '')
        if replacement and len(replacement) > len(scene['narration']):
            scene['narration'] = replacement
            touched += 1
    script['narration_chars'] = sum(len(s['narration']) for s in script['scenes'])
    script['estimated_seconds'] = round(script['narration_chars'] / CHARS_PER_SECOND, 1)
    return script, touched


_LAYOUTS = ('hook', 'concept', 'code', 'compare', 'pitfall', 'summary', 'flow')


def _clip(text, limit):
    """压到单行能排下的长度：去掉换行与 Markdown 残留，再截断。"""
    value = clean_narration(str(text or '')).replace('\n', ' ').strip()
    return value[:limit]


def _clip_code(code, max_lines=8, max_cols=60):
    lines = [line.rstrip()[:max_cols] for line in str(code or '').split('\n')]
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines[:max_lines])


def _clip_list(items, limit, count):
    out = []
    for item in items or []:
        if isinstance(item, dict):
            text = _clip(item.get('text') or item.get('label') or '', limit)
            if text:
                out.append({'icon': _clip(item.get('icon') or '', 2), 'text': text})
        else:
            text = _clip(item, limit)
            if text:
                out.append(text)
        if len(out) >= count:
            break
    return out


def sanitize_visual(raw, scene_type):
    """把大模型给的作图规格裁到版面能容下的长度。

    出图是精确排版，超一个字就会换行撑破卡片，所以这里逐字段硬裁，
    宁可文案略短也不让版面崩掉。
    """
    raw = raw if isinstance(raw, dict) else {}
    layout = raw.get('layout') if raw.get('layout') in _LAYOUTS else None
    layout = layout or (scene_type if scene_type in _LAYOUTS else 'concept')
    visual = {
        'layout': layout,
        'title': _clip(raw.get('title'), 16),
        'subtitle': _clip(raw.get('subtitle'), 24),
        'caption': '',
    }
    if layout == 'hook':
        visual['question'] = _clip(raw.get('question') or raw.get('subtitle'), 26)
        visual['mood'] = 'alert' if str(raw.get('mood', '')).lower() == 'alert' else 'happy'
        visual['bullets'] = _clip_list(raw.get('bullets'), 18, 2)
    elif layout == 'concept':
        visual['bullets'] = _clip_list(raw.get('bullets'), 16, 4)
        visual['highlight'] = _clip(raw.get('highlight'), 20)
    elif layout == 'code':
        visual['code'] = _clip_code(raw.get('code'), 8, 60)
        visual['output'] = _clip_code(raw.get('output'), 4, 60)
        visual['bullets'] = _clip_list(raw.get('bullets'), 20, 1)
    elif layout == 'compare':
        for key in ('left', 'right'):
            side = raw.get(key) if isinstance(raw.get(key), dict) else {}
            visual[key] = {
                'label': _clip(side.get('label'), 10),
                'lines': _clip_list(side.get('lines'), 12, 4),
            }
        visual['highlight'] = _clip(raw.get('highlight'), 20)
    elif layout == 'pitfall':
        visual['wrong'] = _clip(raw.get('wrong'), 26)
        visual['wrong_code'] = _clip_code(raw.get('wrong_code'), 4, 60)
        visual['right_answer'] = _clip(raw.get('right_answer'), 26)
        visual['right_code'] = _clip_code(raw.get('right_code'), 4, 60)
        visual['highlight'] = _clip(raw.get('highlight'), 20)
    elif layout == 'summary':
        visual['bullets'] = _clip_list(raw.get('bullets'), 20, 3)
    elif layout == 'flow':
        steps = _clip_list(raw.get('steps') or raw.get('bullets'), 14, 5)
        visual['steps'] = steps
        visual['highlight'] = _clip(raw.get('highlight'), 20)
    return visual


def build_script(chapter_title, kp_title, kp_text, scenes=DEFAULT_SCENES, client=None,
                 expand=True, want_image_prompt=False):
    client = client or ArkText()
    raw = client.complete(_SCRIPT_SYSTEM,
                          build_script_prompt(chapter_title, kp_title, kp_text, scenes,
                                              want_image_prompt))
    data = _extract_json(raw)
    cleaned = []
    for idx, scene in enumerate(data.get('scenes') or [], start=1):
        narration = clean_narration(str(scene.get('narration', '')))
        if not narration:
            continue
        scene_type = str(scene.get('type', 'concept')).strip() or 'concept'
        item = {
            'id': idx,
            'type': scene_type,
            'title': clean_narration(str(scene.get('title', '')))[:20],
            'narration': narration,
            'caption': clean_narration(str(scene.get('caption', '')))[:60],
            'code': str(scene.get('code', '')).rstrip(),
            'visual': sanitize_visual(scene.get('visual'), scene_type),
        }
        if want_image_prompt:
            item['image_prompt'] = str(scene.get('image_prompt', '')).strip()
        cleaned.append(item)
    if not cleaned:
        raise ValueError('分镜脚本为空')
    result = {
        'title': str(data.get('title', kp_title)).strip()[:40],
        'hook_line': clean_narration(str(data.get('hook_line', '')))[:40],
        'scenes': cleaned,
        'narration_chars': sum(len(s['narration']) for s in cleaned),
    }
    result['estimated_seconds'] = round(result['narration_chars'] / CHARS_PER_SECOND, 1)
    if expand and result['narration_chars'] < TARGET_SECONDS * CHARS_PER_SECOND * 0.92:
        result, touched = expand_short_scenes(
            client, chapter_title, kp_title, result,
            int(TARGET_SECONDS * CHARS_PER_SECOND))
        result['expanded_scenes'] = touched
    return result


# ---------------------------------------------------------------- 组装一节讲解

class NarrationBuilder:
    def __init__(self, text_client=None, images=None, voice=None,
                 narr_dir=None, workers=4, voice_workers=3, on_log=print):
        self.text = text_client or ArkText()
        self.images = images or SeedreamImages()
        self.voice = voice or VoiceOver()
        self.narr_dir = Path(narr_dir or STATIC_NARR_DIR)
        self.workers = workers
        # 口播并发刻意压低：edge-tts 是免费公共服务，请求太密会被限流
        self.voice_workers = voice_workers
        self.on_log = on_log

    def build(self, chapter_id, kp_index, chapter_title, kp_title, kp_text,
              scenes=DEFAULT_SCENES, image_size='1024x1024', use_image_model=False):
        """生成一节讲解的分镜与口播，并写回配图坐标。

        配图默认由 tools/render 的程序化作图引擎产出（不需要任何生图接口），
        这里只负责把 image 字段指向渲染产物；
        仅当显式 use_image_model=True 时才调用第三方生图模型。
        """
        started = time.time()
        script = build_script(chapter_title, kp_title, kp_text, scenes, self.text,
                              want_image_prompt=use_image_model)
        expand_note = (f"，补写 {script['expanded_scenes']} 个偏短镜头"
                       if script.get('expanded_scenes') else '')
        self.on_log(f"    ✓ 分镜脚本 {len(script['scenes'])} 镜头 / "
                    f"{script['narration_chars']} 字 / 预计 {script['estimated_seconds']:.0f}s"
                    f"{expand_note}")

        scene_list = script['scenes']

        if use_image_model:
            folder = self.narr_dir / f'{chapter_id}_{kp_index}'
            folder.mkdir(parents=True, exist_ok=True)

            def render(scene):
                target = folder / f"s{scene['id']:02d}.jpg"
                if target.exists() and target.stat().st_size > 2048:
                    return True
                prompt = f"{scene.get('image_prompt', '')}。{STYLE_PROMPT}"
                try:
                    target.write_bytes(self.images.generate(prompt, size=image_size))
                    return True
                except Exception as exc:
                    self.on_log(f"    ✗ 镜头 {scene['id']} 生图失败：{exc}")
                    return False

            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                results = list(pool.map(render, scene_list))
            ok = sum(1 for r in results if r)
            self.on_log(f'    ✓ 配图 {ok}/{len(scene_list)} 张')

        def speak(scene):
            voice = VOICE_BY_TYPE.get(scene['type'], 'zh-CN-YunxiNeural')
            rate = '+2%' if scene['type'] == 'summary' else '+6%'
            scene['image'] = f'narrations/{chapter_id}_{kp_index}/s{scene["id"]:02d}.jpg'
            scene['voice'] = voice
            try:
                path, duration = self.voice.synth(scene['narration'], voice=voice, rate=rate)
            except Exception as exc:
                # 单镜头失败不中断整节：记录缺口，重跑时会因为音频缓存而只补这一段
                self.on_log(f"    ⚠ 镜头 {scene['id']} 口播失败：{str(exc)[:90]}")
                scene['audio'] = ''
                scene['audio_seconds'] = 0
                return 0.0
            scene['audio'] = f'data/audio_cache/{path.name}' if path else ''
            scene['audio_seconds'] = round(duration, 2)
            return duration

        with ThreadPoolExecutor(max_workers=self.voice_workers) as pool:
            durations = list(pool.map(speak, scene_list))

        missing_voice = sum(1 for s in scene_list if not s.get('audio'))
        total = round(sum(durations), 1)
        if missing_voice:
            self.on_log(f'    ⚠ {missing_voice}/{len(scene_list)} 个镜头缺口播，建议重跑本节补齐')
        if total < TARGET_SECONDS * 0.6 and not missing_voice:
            self.on_log(f'    ⚠ 总时长 {total}s，短于 5 分钟目标，可增加镜头数重跑')
        self.on_log(f'    ✓ 口播 {total}s')

        return {
            'chapter_id': chapter_id,
            'kp_index': kp_index,
            'chapter_title': chapter_title,
            'kp_title': kp_title,
            'title': script['title'],
            'hook_line': script['hook_line'],
            'style': 'programmatic-slide' if not use_image_model else 'comic-illustration',
            'image_engine': self.images.model if use_image_model else 'tools/render (程序化作图)',
            'text_model': self.text.model,
            'total_seconds': total,
            'narration_chars': script['narration_chars'],
            'scene_count': len(scene_list),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'build_seconds': round(time.time() - started, 1),
            'scenes': scene_list,
        }


# ---------------------------------------------------------------- 存储

_store_lock = threading.Lock()


def load_narrations():
    if not NARRATIONS_FILE.exists():
        return {}
    try:
        return json.loads(NARRATIONS_FILE.read_text(encoding='utf-8'))
    except ValueError:
        return {}


def save_narration(key, payload):
    with _store_lock:
        data = load_narrations()
        data[key] = payload
        NARRATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = NARRATIONS_FILE.with_suffix('.tmp')
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        tmp.replace(NARRATIONS_FILE)
    return payload


def narration_key(chapter_id, kp_index):
    return f'{chapter_id}_{kp_index}'


def get_narration(chapter_id, kp_index):
    return load_narrations().get(narration_key(chapter_id, kp_index))


def stats():
    data = load_narrations()
    return {
        'count': len(data),
        'scenes': sum(item.get('scene_count', 0) for item in data.values()),
        'seconds': round(sum(item.get('total_seconds', 0) for item in data.values()), 1),
        'chars': sum(item.get('narration_chars', 0) for item in data.values()),
        'ready': sorted(data.keys()),
    }
