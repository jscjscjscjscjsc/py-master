"""Small OpenAI-compatible Ark transport, with bounded streaming and quota failover."""
import json
import os
import time
import uuid
import threading
import urllib.request
import urllib.error

BASE = 'https://ark.cn-beijing.volces.com/api/v3'
DEFAULT_MODEL = 'doubao-seed-2-0-code-preview-260215'

# 网关（Cloudflare）会对 urllib 默认 UA 直接返回 403 code 1010，
# 用浏览器 UA 才能过；x-opencode-session 是 opencode go 套餐的必填路由头。
BROWSER_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')


def endpoint(url):
    base = (url or BASE).strip().rstrip('/')
    if base.endswith('/chat/completions'):
        return base
    return base + ('/chat/completions' if base.endswith(('/v1', '/v3')) else '/v1/chat/completions')


class ArkError(Exception):
    pass


class ArkClient:
    def __init__(self):
        self.url = endpoint(os.getenv('PYMASTER_AI_BASE_URL', BASE))
        self.key = os.getenv('ARK_API_KEY') or os.getenv('PYMASTER_AI_API_KEY', '')
        self.models = list(dict.fromkeys([os.getenv('PYMASTER_AI_MODEL', DEFAULT_MODEL)] +
            [m.strip() for m in os.getenv('PYMASTER_AI_FALLBACK_MODELS', '').split(',') if m.strip()]))
        self.exhausted = set()
        self.lock = threading.Lock()
        self.active_model = self.models[0]
        self.session_id = str(uuid.uuid4())
        # 推理模型的思考过程会让首字延迟从 2 秒级涨到 8 秒级，
        # 面向学生的问答要的是即时感，所以默认关掉，可用环境变量打开。
        self.thinking_disabled = os.getenv('PYMASTER_AI_THINKING', 'disabled').strip().lower() != 'enabled'

    @staticmethod
    def quota_error(code):
        # Rate limits and invalid keys must never masquerade as exhausted free quota.
        return code in {'InsufficientQuota', 'QuotaExceeded', 'FreeTierQuotaExceeded',
                        'AllocationQuota.FreeTierOnly', 'QuotaExceeded.FreeTier'}

    @staticmethod
    def overdue_error(code):
        # 欠费账户返回 403 且密钥本身是有效的，提示必须指向充值而不是换 key
        return code in {'AccountOverdueError', 'AccountOverdue'}

    def _open_stream(self, model, payload):
        """发起流式请求，拿到还没读的响应对象。

        为什么要重试：实测同一句话连发 6 次，5 次稳定 2 秒返回，
        但会有一次整个卡住 47 秒（服务端偶发不响应）。原来只有一次机会，
        用户看到的就是"连接超时"；而隔几秒重试基本都能成。
        重试只做在建连阶段 —— 流一旦开始吐字就不再重试，
        否则会把已经显示给用户的半截回答重来一遍。
        """
        attempts = max(1, int(os.getenv('PYMASTER_AI_RETRY', '3')))
        connect_timeout = int(os.getenv('PYMASTER_AI_CONNECT_TIMEOUT', '20'))
        last_error = None
        for attempt in range(1, attempts + 1):
            req = urllib.request.Request(
                self.url, data=json.dumps(payload).encode(),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.key,
                    'User-Agent': BROWSER_UA,
                    'x-opencode-session': self.session_id,
                })
            try:
                return urllib.request.urlopen(req, timeout=connect_timeout)
            except urllib.error.HTTPError:
                # HTTP 类错误（鉴权、限流、额度）重试没有意义，交给上层分类处理
                raise
            except (OSError, ValueError) as exc:
                last_error = exc
                if attempt < attempts:
                    time.sleep(0.8 * attempt)
        raise ArkError(
            f'模型连接超时（已重试 {attempts} 次）。'
            '网络不稳或服务商临时无响应时会这样，稍后再试；'
            '若长期如此，可在配置页换用备用模型。') from last_error

    def events(self, messages, max_tokens=800):
        if not self.key:
            raise ArkError('请在本机 .env 中设置 ARK_API_KEY。')
        deadline = time.monotonic() + 55
        with self.lock:
            models = [m for m in self.models if m not in self.exhausted]
        for model in models:
            payload = {'model': model, 'messages': messages, 'stream': True,
                       'max_tokens': max_tokens, 'temperature': 0.35,
                       'stream_options': {'include_usage': True}}
            if self.thinking_disabled or model.startswith('doubao-seed'):
                payload['thinking'] = {'type': 'disabled'}
            try:
                with self._open_stream(model, payload) as response:
                    self.active_model = model
                    yield {'type': 'model', 'model': model}
                    ended = False
                    for raw in response:
                        if time.monotonic() > deadline:
                            raise ArkError('回答超时，请缩短问题后重试。')
                        line = raw.decode('utf-8').strip()
                        if not line.startswith('data:'):
                            continue
                        content = line[5:].strip()
                        if content == '[DONE]':
                            ended = True
                            break
                        event = json.loads(content)
                        if event.get('error'):
                            raise ArkError('模型返回错误，请稍后重试。')
                        choices = event.get('choices') or []
                        if choices:
                            delta = choices[0].get('delta', {}).get('content')
                            if delta:
                                yield {'type': 'delta', 'text': delta}
                            if choices[0].get('finish_reason'):
                                yield {'type': 'finish', 'reason': choices[0]['finish_reason']}
                        if event.get('usage'):
                            yield {'type': 'usage', 'usage': event['usage']}
                    if not ended:
                        raise ArkError('连接中断，回答可能不完整，请重试。')
                    return
            except urllib.error.HTTPError as exc:
                try:
                    code = json.loads(exc.read()).get('error', {}).get('code', '')
                except (ValueError, AttributeError):
                    code = ''
                if self.quota_error(code):
                    with self.lock:
                        self.exhausted.add(model)
                    yield {'type': 'switch', 'message': '当前模型额度已用尽，正在尝试备用模型。'}
                    continue
                if self.overdue_error(code):
                    raise ArkError('模型账号已欠费（AccountOverdueError），AI 功能全部不可用；'
                                   '请到服务商控制台充值，或在「首次运行配置」页换成其他服务商的 Key。') from None
                if exc.code in (401, 403):
                    raise ArkError(f'模型鉴权或模型权限失败（HTTP {exc.code}），请核对 API Key 和模型名是否正确。') from None
                if exc.code == 429:
                    raise ArkError('模型请求限流，请稍后再试。') from None
                raise ArkError(f'模型服务返回 HTTP {exc.code}，请检查模型配置。') from None
            except (OSError, ValueError) as exc:
                raise ArkError('模型连接超时或返回格式异常，请稍后重试。') from None
        raise ArkError('所配置模型的可用额度已耗尽，请配置仍有额度且已开通的备用模型。')

    def complete(self, messages, max_tokens=800):
        return ''.join(e['text'] for e in self.events(messages, max_tokens) if e['type'] == 'delta')
