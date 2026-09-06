"""First-run local API setup. Secrets are written only to the ignored .env file."""
from getpass import getpass
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / '.env'
DEFAULT_URL = 'https://ark.cn-beijing.volces.com/api/v3'
DEFAULT_MODEL = 'doubao-seed-2-0-code-preview-260215'


def read_env():
    values = {}
    if ENV_FILE.exists():
        for raw in ENV_FILE.read_text(encoding='utf-8').splitlines():
            if raw.strip() and not raw.lstrip().startswith('#') and '=' in raw:
                key, value = raw.split('=', 1)
                values[key.strip()] = value.strip()
    return values


def configured(values=None):
    values = values or read_env()
    return all(values.get(key) for key in ('PYMASTER_AI_BASE_URL', 'PYMASTER_AI_MODEL', 'ARK_API_KEY'))


def prompt_setup(force=False):
    current = read_env()
    if configured(current) and not force:
        return True
    print('\nPyMaster 首次运行 · AI 配置')
    print('配置只保存在本机 .env，不会提交到 GitHub。直接回车可采用推荐值。\n')
    default_model = current.get('PYMASTER_AI_MODEL', DEFAULT_MODEL)
    model = input(f'模型名称 [{default_model}]: ').strip() or default_model
    while True:
        default_url = current.get('PYMASTER_AI_BASE_URL', DEFAULT_URL)
        base_url = input(f'API Base URL [{default_url}]: ').strip() or default_url
        parsed = urlparse(base_url)
        if parsed.scheme == 'https' and parsed.netloc:
            break
        print('请输入完整的 HTTPS URL，例如 https://ark.cn-beijing.volces.com/api/v3')
    api_key = getpass('API Key（输入不会显示）: ').strip() or current.get('ARK_API_KEY', '')
    if not api_key:
        print('API Key 不能为空。')
        return False
    fallback = input('备用模型（可选，多个名称用英文逗号分隔）: ').strip() or current.get('PYMASTER_AI_FALLBACK_MODELS', '')
    lines = [
        f'PYMASTER_AI_BASE_URL={base_url.rstrip("/")}',
        f'PYMASTER_AI_MODEL={model}',
        f'ARK_API_KEY={api_key}',
        f'PYMASTER_AI_FALLBACK_MODELS={fallback}',
    ]
    temporary = ROOT / '.env.tmp'
    temporary.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    temporary.replace(ENV_FILE)
    print('\n配置完成，正在启动 PyMaster。')
    return True


if __name__ == '__main__':
    raise SystemExit(0 if prompt_setup() else 1)
