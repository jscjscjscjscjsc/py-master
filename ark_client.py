"""Small OpenAI-compatible Ark transport, with bounded streaming and quota failover."""
import json
import os
import time
import threading
import urllib.request
import urllib.error

BASE = 'https://ark.cn-beijing.volces.com/api/v3'
DEFAULT_MODEL = 'doubao-seed-2-0-code-preview-260215'


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

    @staticmethod
    def quota_error(code):
        # Rate limits and invalid keys must never masquerade as exhausted free quota.
        return code in {'InsufficientQuota', 'QuotaExceeded', 'FreeTierQuotaExceeded',
                        'AllocationQuota.FreeTierOnly', 'QuotaExceeded.FreeTier'}

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
            if model.startswith('doubao-seed'):
                payload['thinking'] = {'type': 'disabled'}
            req = urllib.request.Request(self.url, data=json.dumps(payload).encode(),
                headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.key})
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
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
                if exc.code in (401, 403):
                    raise ArkError(f'火山鉴权或模型权限失败（HTTP {exc.code}），请核对 API Key 和模型开通状态。') from None
                if exc.code == 429:
                    raise ArkError('火山请求限流，请稍后再试。') from None
                raise ArkError(f'火山服务返回 HTTP {exc.code}，请检查模型配置。') from None
            except (OSError, ValueError) as exc:
                raise ArkError('火山连接超时或返回格式异常，请稍后重试。') from None
        raise ArkError('所配置模型的可用额度已耗尽，请配置仍有额度且已开通的备用模型。')

    def complete(self, messages, max_tokens=800):
        return ''.join(e['text'] for e in self.events(messages, max_tokens) if e['type'] == 'delta')
