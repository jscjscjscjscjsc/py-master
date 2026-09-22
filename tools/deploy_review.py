#!/usr/bin/env python3
"""把 PyMaster 与 AI Master 一起部署到一台服务器，供评审在线试用。

为什么单独一个脚本（而不是复用 tools/deploy_server.py）
----------------------------------------------------
比赛要求"提供可供评审使用的测试链接"，评审会真的去点、去用、去问 AI。
所以这条链路和"发给学生自用"不一样，它多了三件事：

  1. **两个平台要一起上线**，并在同一个域名下开两个子站
     （pymaster.域名 / aimaster.域名，或 /path 形式）
  2. **要有评审能直接登录的演示账号**，且他的操作不能污染真实数据
     （见 demo_mode.py：档案只在内存里）
  3. **自动生成随机口令**，并把链接、账号、二维码、使用说明打包成一份
     `评审访问说明.md`，可以直接贴进申报表"测试链接"那一栏

用法
----
    # 先看看会打包什么（不动服务器）
    python tools/deploy_review.py --host root@1.2.3.4 --domain learn.example.com --dry-run

    # 正式部署
    python tools/deploy_review.py --host root@1.2.3.4 --domain learn.example.com

    # 只重新生成说明与二维码（服务器已就绪时）
    python tools/deploy_review.py --host root@1.2.3.4 --domain learn.example.com --docs-only

前提：本机能 ssh/scp 免密登录那台服务器。Windows 用 Git Bash 或 PowerShell
都自带 OpenSSH，不需要额外装东西。
"""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYMASTER_DIR = HERE.parent
AIMASTER_DIR = Path(os.environ.get('AIMASTER_DIR')
                    or r'C:\Users\Admin（无密码）\Desktop\Vibe oding\AI Master 学习宇宙\AI Master 学习平台')
OUT_DIR = PYMASTER_DIR / 'dist' / 'review'

# 不进包的目录（运行环境、产物、缓存、版本库）
EXCLUDE_DIRS = {
    '.git', '__pycache__', '.pytest_cache', 'node_modules', 'runtime', 'dist',
    'docs', 'logs', '.video-build', '.workbuddy', 'tests', 'preview',
    'vendor/wheels', 'data/music_cache', 'static/audio', 'static/narration-audio',
}
EXCLUDE_SUFFIX = {'.pyc', '.pyo', '.zip', '.log', '.bak', '.mp4', '.docx'}

# 演示账号要用的种子档案（预置学习痕迹，评审看到的不是空壳）
DEMO_SEED = {
    'profile': {'nickname': '评审演示'},
    'training': {},
}


ACCOUNT_FILE = OUT_DIR / '账号.json'


def load_or_create_accounts():
    """演示账号口令：首次生成后固定，重跑不换（否则会和已交出去的说明对不上）。"""
    if ACCOUNT_FILE.exists():
        try:
            data = json.loads(ACCOUNT_FILE.read_text(encoding='utf-8'))
            if data.get('pymaster_pass') and data.get('aimaster_pass'):
                print(f'  沿用已有口令：{ACCOUNT_FILE}')
                return data
        except (OSError, ValueError):
            pass
    accounts = {
        'pymaster_user': 'reviewer',
        'pymaster_pass': secrets.token_urlsafe(9),
        'aimaster_user': 'reviewer',
        'aimaster_pass': secrets.token_urlsafe(9),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ACCOUNT_FILE.write_text(json.dumps(accounts, ensure_ascii=False, indent=2),
                            encoding='utf-8')
    print(f'  已生成新口令并保存到 {ACCOUNT_FILE}')
    return accounts


def human(n):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f'{n:.1f} {unit}'
        n /= 1024


def is_excluded(rel: Path):
    parts = rel.parts
    for i in range(len(parts) - 1):
        for depth in (1, 2):
            if i + depth <= len(parts) - 1 and '/'.join(parts[i:i + depth]) in EXCLUDE_DIRS:
                return True
        if parts[i] in EXCLUDE_DIRS:
            return True
    return rel.suffix.lower() in EXCLUDE_SUFFIX


def collect(root: Path, with_media=True):
    files = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if is_excluded(rel):
            continue
        if not with_media and rel.as_posix().startswith(('static/narrations', 'data/audio_cache')):
            continue
        files.append(rel)
    return files


def build_tarball(root: Path, files, out_path: Path, arc_root: str):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(out_path, 'w') as tar:
        for rel in files:
            tar.add(root / rel, arcname=f'{arc_root}/{rel.as_posix()}')
    return out_path


def run(cmd, **kw):
    print('  $', ' '.join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    return subprocess.run(cmd, **kw)


def remote(host, script, check=True):
    return run(['ssh', '-o', 'StrictHostKeyChecking=accept-new', host, script], check=check)


def _add_quiet_zone(out_png: Path, modules_guess=8):
    """给二维码补白边（quiet zone）。

    很多扫码器要求四周至少有 4 个模块宽的空白，少了会识别不了 ——
    在线二维码服务生成出来的图常常是"紧贴边缘、一点白边都没有"，
    打印或截图后扫码失败，而这是最容易被忽略又最影响体验的一点。
    """
    try:
        from PIL import Image
    except ImportError:
        return False
    img = Image.open(out_png).convert('RGB')
    w, h = img.size
    # 按 4 个模块估白边：常见二维码版本下，边长/模块数 ≈ 每模块像素
    pad = max(16, int(w / 45 * 4))
    canvas = Image.new('RGB', (w + pad * 2, h + pad * 2), 'white')
    canvas.paste(img, (pad, pad))
    canvas.save(out_png)
    return True


def make_qr(text, out_png: Path):
    """生成二维码。优先用本机已装的东西，都不行就跳过（不阻塞部署）。"""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    made = False
    made_by_lib = False
    # 1) Python 的 qrcode（可指定 border，它自带白边）
    try:
        import qrcode  # type: ignore
        qr = qrcode.QRCode(border=4, box_size=12)
        qr.add_data(text)
        qr.make(fit=True)
        qr.make_image(fill_color='black', back_color='white').save(str(out_png))
        made = made_by_lib = True
    except Exception:
        pass
    # 2) 网页版服务（需联网）；它默认没有白边，要自己补
    if not made:
        try:
            import urllib.request
            import urllib.parse
            url = ('https://api.qrserver.com/v1/create-qr-code/?size=520x520&margin=24&data='
                   + urllib.parse.quote(text, safe=''))
            with urllib.request.urlopen(url, timeout=20) as resp:
                out_png.write_bytes(resp.read())
            made = True
        except Exception:
            return False
    # 网页服务那条路生成出来没有白边，补一次；qrcode 库已经带 border=4，
    # 别再叠（叠两层会让白边宽窄不一，反而显得随意）
    if not made_by_lib:
        _add_quiet_zone(out_png)
    return True


def write_review_doc(path: Path, domain, pymaster_url, aimaster_url, accounts, qr_ok):
    body = f'''# 教学智能体大赛 · 在线试用说明

> 本文件用于填写申报表「测试链接 / 二维码」栏，也是给评审的使用指南。
> 生成时间：{time.strftime('%Y-%m-%d %H:%M')}

---

## 一、访问地址

| 教学智能体 | 访问链接 |
|---|---|
| **PyMaster 教学平台** | {pymaster_url} |
| **AI Master 星辰学习系统** | {aimaster_url} |

两个平台部署在同一台服务器上，链接可直接点开，无需安装任何软件。

## 二、测试账号

两个平台都提供了**评审专用演示账号**，点击登录后即可使用全部功能：

| 平台 | 用户名 | 密码 |
|---|---|---|
| PyMaster | `{accounts['pymaster_user']}` | `{accounts['pymaster_pass']}` |
| AI Master | `{accounts['aimaster_user']}` | `{accounts['aimaster_pass']}` |

> 演示账号已预置一段学习记录（进度、积分、错题、修为等级），
> 便于直接看到"用起来之后"的样子，不必从零开始点。
>
> **评审期间的任何操作都不会被保存**，请放心试用：做题、改代码、
> 问 AI 老师都可以随便试。下次重新登录即回到初始状态。

## 三、建议的试用路径（约 10 分钟）

### PyMaster 教学平台
1. **开场动画**：打开链接先是一部分钟的五幕 3D 短片（Python 的来历 →
   Python 之禅 → 龟叔 → AI 大时代 → 启程）。鼠标划过画面会有水波，
   右侧章节导航可点击跳转；不想看可点右上角「跳过片头」。
2. **看一节图文讲解**：进入任意章节 → 点「🎬 5 分钟图文讲解」，
   有配图、字幕、语音，可倍速与逐句跳转。
3. **动手做题**：左侧切到「刷题中心」→ 随便点一道题 → 左侧写代码 →
   点「▶ 运行」，代码会真的执行并给出结果；点「提交判题」看评分。
   需要键盘输入的题目，代码区下方会出现「测试输入」框，每行填一个值。
4. **问 AI 老师**：右下角浮标打开「星辰教练」，
   例如问"递归和循环有什么区别，用我能听懂的话讲"。
5. **看成长体系**：右上角「修行阁」是按你的学习数据推导的角色画像
   （法相、神功、装备、试炼），以及基于作答档案的修为等级。

### AI Master 星辰学习系统
1. **学习路线**：首页按目标生成个性化学习路线，可点开每一站看任务。
2. **星辰教练**：多轮对话答疑，回答会追问"你觉得为什么"，
   把"讲出来"当作掌握标准（费曼式门禁）。
3. **知识星海**：拖拽旋转、滚轮缩放的三维知识图谱，点击星球看关联。
4. **动手实验**：BPE 分词、Transformer 注意力等小实验，调参数即时看输出变化。

## 四、数据与合规说明

- **本系统不含任何真实学生数据。** 两个平台的仓库里只有课程内容与题库；
  演示账号是专门为评审生成的虚拟档案，与任何真实学生无关。
- **演示账号的操作不落盘**：所有改动只存在服务器内存中，重启即还原，
  不存在"评审操作污染教学数据"的风险。
- **在线代码执行已加安全限制**：只允许课程范围内的 Python 代码，
  系统级操作（起进程、网络请求、文件写入）会被拦截并给出说明；
  单次执行有人 CPU 时间与内存上限。教师本地部署的完整版不受此限制。
- **姓名、学校、院系等个人信息未出现在平台任何界面中**，
  已按大赛要求做匿名化处理。

## 五、技术说明（供评委参考）

- 部署形态：Docker 容器 + Caddy 自动 HTTPS，一条命令完成部署与更新
- 两个平台均为 Flask 应用，前端零 CDN 依赖（断网教室内网可用）
- PyMaster 判题在子进程沙箱外运行，因此公网版启用了
  静态代码检查 + 资源限制双层防护；本地版可直接运行任意 Python

'''
    path.write_text(body, encoding='utf-8')
    return path


def main():
    ap = argparse.ArgumentParser(description='双平台评审部署（PyMaster + AI Master）')
    ap.add_argument('--host', required=True, help='SSH 目标，例如 root@1.2.3.4')
    ap.add_argument('--domain', default='', help='主域名，例如 learn.example.com')
    ap.add_argument('--dir', default='/opt/review', help='服务器上的安装目录')
    ap.add_argument('--skip-media', action='store_true',
                    help='不传讲解配图与口播（快很多，但讲解页会是空的）')
    ap.add_argument('--docs-only', action='store_true',
                    help='只重新生成说明与二维码，不重新部署')
    ap.add_argument('--dry-run', action='store_true', help='只打包并报告，不连服务器')
    args = ap.parse_args()

    domain = args.domain.strip()
    if domain:
        pymaster_url = f'https://pymaster.{domain}'
        aimaster_url = f'https://aimaster.{domain}'
    else:
        pymaster_url = 'https://<域名>/（尚未配置域名）'
        aimaster_url = 'https://<域名>/（尚未配置域名）'

    # 演示账号口令：**首次生成后固定下来**（存 dist/review/账号.json）。
    # 每次重跑都换口令的话，会把服务器上的口令和已交给评审的说明改得对不上——
    # 而申报材料一旦提交就改不了，这种不一致是致命的。
    accounts = load_or_create_accounts()

    if args.docs_only:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        qr_ok = make_qr(pymaster_url, OUT_DIR / 'PyMaster_二维码.png')
        make_qr(aimaster_url, OUT_DIR / 'AIMaster_二维码.png')
        doc = write_review_doc(OUT_DIR / '评审访问说明.md', domain,
                               pymaster_url, aimaster_url, accounts, qr_ok)
        print(f'已生成：{doc}')
        print(f'二维码：{"已生成" if qr_ok else "生成失败（可手动用在线工具转）"}')
        print(f'口令沿用首次生成的那一份（{ACCOUNT_FILE.name}），与服务器保持一致。')
        return

    # ── 打包 ──
    print('=' * 62)
    print('  打包清单')
    print('=' * 62)
    pm_files = collect(PYMASTER_DIR, with_media=not args.skip_media)
    pm_size = sum((PYMASTER_DIR / f).stat().st_size for f in pm_files)
    print(f'  PyMaster : {len(pm_files):>6} 个文件  {human(pm_size)}'
          f'{"（不含讲解产物）" if args.skip_media else ""}')

    if not AIMASTER_DIR.exists():
        sys.exit(f'找不到 AI Master 目录：{AIMASTER_DIR}\n'
                 '可用环境变量 AIMASTER_DIR 指定。')
    am_files = collect(AIMASTER_DIR)
    am_size = sum((AIMASTER_DIR / f).stat().st_size for f in am_files)
    print(f'  AI Master: {len(am_files):>6} 个文件  {human(am_size)}')
    print(f'  合计     : {human(pm_size + am_size)}')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print('\n[1/5] 打包…')
    t0 = time.time()
    build_tarball(PYMASTER_DIR, pm_files, OUT_DIR / 'pymaster.tar', 'pymaster')
    build_tarball(AIMASTER_DIR, am_files, OUT_DIR / 'aimaster.tar', 'aimaster')
    print(f'      用时 {time.time() - t0:.0f}s')

    # 生成评审说明与二维码（本地一份，稍后随包上传）
    qr_ok = make_qr(pymaster_url, OUT_DIR / 'PyMaster_二维码.png')
    make_qr(aimaster_url, OUT_DIR / 'AIMaster_二维码.png')
    doc = write_review_doc(OUT_DIR / '评审访问说明.md', domain,
                           pymaster_url, aimaster_url, accounts, qr_ok)
    print(f'      评审说明：{doc.name}')

    if args.dry_run:
        print('\n--dry-run：已生成 tar 与说明，未连接服务器。')
        return

    for tool in ('ssh', 'scp'):
        if not shutil.which(tool):
            sys.exit(f'找不到 {tool}。Windows 请确认已启用 OpenSSH 客户端，'
                     '或用 Git Bash 打开本脚本。')

    print('\n[2/5] 准备服务器…')
    remote(args.host, f'mkdir -p {args.dir}/pymaster-data {args.dir}/aimaster-data '
                      f'{args.dir}/logs {args.dir}/narrations')
    remote(args.host, 'command -v docker >/dev/null 2>&1 || '
                      '(curl -fsSL https://get.docker.com | sh)', check=False)
    # compose 插件（部分镜像只带了 docker 没带 compose）
    remote(args.host, 'docker compose version >/dev/null 2>&1 || '
                      '(apt-get update -qq && apt-get install -y -qq docker-compose-plugin) '
                      '|| true', check=False)

    print('\n[3/5] 上传…')
    remote(args.host, f'cd {args.dir} && rm -rf pymaster aimaster')
    for name in ('pymaster.tar', 'aimaster.tar', '评审访问说明.md',
                 'PyMaster_二维码.png', 'AIMaster_二维码.png'):
        src = OUT_DIR / name
        if src.exists():
            run(['scp', '-C', str(src), f'{args.host}:{args.dir}/'])
    remote(args.host, f'cd {args.dir} && '
                      f'tar -xf pymaster.tar && tar -xf aimaster.tar && '
                      f'rm -f pymaster.tar aimaster.tar')

    print('\n[4/5] 写入演示账号环境…')
    env_pm = (f'PYMASTER_DEMO_USER={accounts["pymaster_user"]}\n'
              f'PYMASTER_DEMO_PASSWORD={accounts["pymaster_pass"]}\n'
              'PYMASTER_SAFE_MODE=1\n'
              'PYMASTER_ALLOW_CODE_EXEC=1\n')
    env_am = (f'STARLAB_DEMO_USER={accounts["aimaster_user"]}\n'
              f'STARLAB_DEMO_PASSWORD={accounts["aimaster_pass"]}\n')
    # 用 base64 传，避免脚本引号/换行在远端的转义问题
    import base64
    b64_pm = base64.b64encode(env_pm.encode()).decode()
    b64_am = base64.b64encode(env_am.encode()).decode()
    remote(args.host,
           f'cd {args.dir} && echo {b64_pm} | base64 -d > pymaster.env && '
           f'echo {b64_am} | base64 -d > aimaster.env && chmod 600 *.env')

    print('\n[5/5] 构建并启动（首次约 5–10 分钟）…')
    remote(args.host, f'cd {args.dir} && docker compose up -d --build', check=False)

    print('\n' + '=' * 62)
    print('  部署完成。还差两步：')
    print('=' * 62)
    print(f'''
  1) 域名解析（把两条 A 记录都指向 {args.host.split("@")[-1]}）
       pymaster.{domain or '你的域名'}   →  服务器 IP
       aimaster.{domain or '你的域名'}   →  服务器 IP

  2) 填模型密钥（不填也能用，只是没有 AI 答疑）
       ssh {args.host} "vi {args.dir}/pymaster.env"
         追加三行：
           PYMASTER_AI_BASE_URL=https://opencode.ai/zen/go/v1
           PYMASTER_AI_MODEL=deepseek-v4.1-flash
           ARK_API_KEY=你的密钥
       同理 aimaster.env 里加 STARLAB_AI_BASE_URL / STARLAB_AI_MODEL / ARK_API_KEY
       然后 cd {args.dir} && docker compose up -d

  评审访问说明（含账号、链接、二维码、使用路径）已生成：
    {OUT_DIR / '评审访问说明.md'}
  服务器上也放了一份：{args.dir}/评审访问说明.md

  健康检查：cd {args.dir} && docker compose logs -f
''')


if __name__ == '__main__':
    main()
