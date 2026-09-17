# 接手指南（当前状态速查）

> 本文只写"接手继续干活需要知道的事"，历史演进看 `PROGRESS.md`。
> 最后更新：2026-09-17

## 一、这是什么

`PyMaster 教学平台`：把 Python 基础到 AI 应用开发做成一套可自学的平台。
课程 39 章 / 400 个知识点 / 212 道教材练习 / **256 道刷题题库**（含 181 道算法题，
其中 86 道是西科大 823《数据结构与算法》与操作系统的考研专项），
每个知识点配一节 5 分钟图文讲解，另有星辰教练、刷题中心、修为等级与学习仪表盘。

```
桌面/Vibe oding/PyMaster 教学平台/
├── 启动 PyMaster.bat        ← 双击启动（顶层，最省事）
├── 发布版/                  ← 新版，所有开发都在这里
│   ├── 启动PyMaster.bat
│   ├── app.py              Flask 主程序（约 4000 行）
│   ├── training_engine.py  刷题引擎：题库 / 判题沙箱 / 积分 / 等级曲线
│   ├── coach_engine.py     星辰教练：会话存储与提示词
│   ├── PROGRESS.md         演进记录（历史）
│   ├── HANDOFF.md          本文件（当前状态）
│   ├── data/question_bank.json   256 道题库（编译产物）
│   └── tools/render/       程序化作图引擎
└── 原版总包/                ← 旧版 9 章，仅备份，别启动
```

## 二、当前在跑什么

**讲解批量生产**（全量 400 节，进行中）

```bash
bash tools/batch_stage.sh              # 全部章节，直到做完（并发 4）
bash tools/batch_stage.sh "AI 篇"       # 只做某一篇
python build_narrations.py --list       # 看进度（不会打断生产）
```

去看 `logs/nohup_all.out` 和 `logs/batch_*.log` 能读到实时进度。
跑批进程带互斥锁，重复启动会被拒绝（提示已有进程在跑）。

## 三、讲解是怎么生产的（关键：零外部生图/语音成本）

```
知识点原文
  ↓ ① 分镜脚本 —— 由大模型写（当前用 opencode go 的 deepseek-v4.1-flash）
  ↓    16 个镜头：口播稿 / 字幕 / 代码 / 结构化作图规格
  ↓ ② 口播 —— edge-tts（微软，免费）
  ↓ ③ 配图 —— 本地程序化渲染（tools/render，7 种版式，8–14 张/秒）
5 分钟图文讲解
```

**除了写稿，其余全部免费且本地完成。**

### 配置（`.env`）

```
PYMASTER_AI_BASE_URL=https://opencode.ai/zen/go/v1
PYMASTER_AI_MODEL=deepseek-v4.1-flash
ARK_API_KEY=sk-5ju...（用户提供）
PYMASTER_AI_FALLBACK_MODELS=glm-5.3-flash
```

### 接这个通道踩过的三个坑（换供应商时会再遇到）

1. **必须带浏览器 User-Agent**。opencode.ai 前面是 Cloudflare，Python 默认 UA
   会被判成机器人，直接 403（error code 1010）。
2. **必须带 `x-opencode-session`**（随便一个 UUID 即可）。不带会返回
   400 MissingSessionID。这两点在 `narration_engine.request_headers()` 里统一处理。
3. **推理模型吃 token 预算**。deepseek-v4.1-flash 是推理模型，实测
   `max_tokens=8000` 时 8000 个 token **全部用于推理、正文一个字都没有**，
   表现为"模型返回空内容"。现已把它设为 `SCRIPT_MAX_TOKENS = 48000`。

## 四、手工撰稿通路（不依赖任何外部模型）

除了让大模型写，也支持**人工/编码助手直接撰稿**：

```bash
# 稿件放 tools/authored/<章号>_<知识点序号>.json
python tools/author_scripts.py --check     # 校验（字数、镜头数、代码是否齐）
python tools/author_scripts.py             # 合成口播 + 渲染配图
```

稿件只需写：镜头类型 `t`、口播稿 `nar`、字幕 `cap`，以及少量作图规格
（`vt` 标题 / `vb` 要点 / `vs` 步骤 / `vh` 结论条 / `vq` 提问）。
作图规格里结构化字段由程序从口播稿自动推导。

已交付样板：第 7 章 7.1 / 7.6 / 7.7 三节。

> 写作要点：5 分钟对应约 1600–1750 字口播稿（edge-tts 中文约 5.3 字/秒）。
> 校验会拦住写太短或太长，别绕过它。

## 五、其他常用命令

```bash
# 课程数据（教材 Markdown → 平台课程数据）
python tools/migrate_courseware.py --check
python tools/migrate_courseware.py --write

# 练习题全量体检（渲染 / 代码运行 / AI 评分三条链路）
python tools/test_exercises.py
python tools/test_exercises.py --ai 24

# 导出 GitHub Pages 静态站
python build_static_docs.py --samples 10

# 本地假模型（无额度时验证生产链路）
python tools/mock_llm.py 8899

# 题库自测（170 道的参考答案必须全部通过自己的断言）
python tools/verify_qbank.py --quiet
python tools/verify_qbank.py --module 408      # 只验 408 那批
python tools/build_question_bank.py            # 编译 + 体检

# 平台端到端自测（98 项：接口 / 积分数学 / 页面可访问 / 音乐资源）
python tools/test_platform.py

# 背景音乐（首次部署或换曲时跑；--check 只检查文件在不在）
python tools/fetch_music.py --check
```

## 六、已知的坑与约定

- **端口 5000 会被旧版抢占**。旧版 `原版总包/Pymaster` 也监听 5000，
  启动脚本会先清理占用再启动（判据按端口而非按地址匹配，中文 Windows 上
  netstat 输出是 GBK，解码要用 `errors='ignore'`）。
- **CDN 已全部本地化**。CodeMirror / d3 / markmap 都放在 `static/vendor/`，
  教室断网也能用。新加前端库请照做，不要引 CDN。
- **配图与音频不入库**（`static/narrations/`、`data/audio_cache/` 已 gitignore）。
  讲解脚本 `data/narrations.json` 入库——它只有几百 KB，别人克隆后本地跑一次
  渲染就能重建全部配图，不需要任何外部接口。
- **`.env.*` 一律不入库**。曾经因为把一份 `.env` 备份提交进仓库，
  被 GitHub 密钥扫描拦下推送。
- **GitHub 推送**：直连经常不通；`ghfast.top` 有时会被分支保护拦；
  可用 `ghproxy.net`。推送时若报 "repository rule violations"，
  先查有没有密钥被扫出来，再查分支保护。

## 七、学习系统（2026-09 新增）

四个新页面 + 两个引擎，详细设计见 `PROGRESS.md` 第十节。

| 入口 | 说明 |
|---|---|
| `/coach` | 星辰教练：多会话聊天（最多 10 个）、哲思追问、一键复制、练习答疑自动沉淀 |
| `/training` | 刷题中心：Jupyter 式分块运行、练习/实战双模式、实战中锁答案、交卷后 AI 批卷 |
| `/progress` | 学习仪表盘：分章节知识点/刷题进度、错题分类、实战记录、修为流水 |
| 全局浮窗 | 修为等级条（10 大境界 30 级）+ 背景音乐播放器 |

**关键维护点**：

- 加题只改 `tools/qbank_*.py`，然后 `python tools/verify_qbank.py` → `python tools/build_question_bank.py`。
  新专题号要登记进 `build_question_bank.py` 的 `ALGO_TOPICS`，新文件名加进 `build_question_bank.py`
  与 `verify_qbank.py` **两处**的 `MODULES`。
- **`verify_qbank.py` 是必须过的门禁**：它拿每道题的参考答案去跑自己的断言。
  手写断言一定会算错几道期望值，上线后表现是「学生写对了却判错」。
  实测教训：一次加 86 道题，跑出来 5 道红——**全部是断言的期望值算错，参考答案反而是对的**
  （2^14 被当成 4096、RR 完成顺序、SRTF 打平却按交替算……）。所以红灯先怀疑断言，别急着改答案。
- 考研专项的模块分工：
  `qbank_xust823a`（823 第 1–4 章）/ `qbank_xust823b`（第 5–8 章）/ `qbank_xust823c`（线性表·栈队列加练）
  / `qbank_xust823d`（图算法强化，含 Dijkstra 三个变体）/ `qbank_os_exam`（操作系统主套）
  / `qbank_osa`、`qbank_osb`（操作系统进阶）。
  加题前先看 `qbank_408.py`，它是全部题目的写法样板。
- **操作系统题都是「概念→可执行模拟」**：调度类返回 `(顺序, 完成时刻, 周转)`，置换类返回缺页次数，
  分配类返回起始地址（失败 -1），银行家算法返回安全序列（不安全 `False`）。
  别用真 `threading` 出题，判题会不稳。
- 等级曲线是 `training_engine.LEVEL_THRESHOLDS` 这张 30 个数的表（前松后紧），
  单题基础分在同文件的 `QUESTION_BASE`（简单/中等/较难 = 10/28/70，差 7 倍）。
- 每用户数据在 `data/training/<user>.json` 与 `data/coach/<user>.json`（已 gitignore）。
- 判题与代码运行都是**子进程无沙箱**执行（20–25 秒超时），别把服务暴露到公网。
- **「▶运行」现在也是结算入口**：跑的是最后一块代码时，`/api/training/run-cell` 会顺带执行题目断言，
  通过了当场结算（等同点一次「提交判题」）。只有本题**尚未通关**时才自动发分，
  否则连点运行就能刷递减分；已通关的题想再练仍走「提交判题」，那里的递减系数是有意设计的。
- **游客判题是真的判**（对错准），但没有账本可写。所以 `/judge` 与 `/run-cell` 都会回一个 `guest` 字段，
  前端据此把通关面板换成「做对了，但游客模式不记分」——**别再退回成「0 星 +0」**，
  那看起来就像平台坏了（这个 bug 真实发生过：学生没登录，做题一路 0 星，以为坏了）。
  刷题页也有 `.wb-guest-banner` 横幅，登录状态要在页面上看得见。

## 八、在线演示站与分发包（2026-09-18）

### 在线演示站（GitHub Pages）

`docs/` 由 `python build_static_docs.py --samples N` 导出，Pages 源是 `main` 分支 `/docs`。

静态站没有后端，靠 `static/js/static_mode.js` 兜住：

- 所有 `/api/*` 请求被 fetch 钩子接住，返回人话提示（AI 类、判题类、数据类分别有不同文案），
  页面不会停在"加载中"，也不会满屏 404
- 指向后端路由的 `<a href="/coach">` 之类在捕获阶段被拦下并弹提示
- 术语表走导出的 `data/glossary.json`，在线可查
- 页尾说明条写清"在线能看什么、什么要本地部署"

**踩过的两个坑**（改静态站时容易再犯）：

1. **判断"是不是静态站"不能猜 URL 后缀**。首页在 Pages 上是 `/py-master/`，
   既不以 `.html` 结尾也不是后端路由，原来的 `location.pathname.endsWith('.html')`
   会跳到不存在的 `/chapter/1`——这正是"子页面全打不开"的根因。
   现在认 `window.PYMASTER_STATIC` 或路径里有没有 `docs`。
2. **图片、音频不能写绝对路径**。`/static/...` 在 Pages 上 404，
   讲解样例会变成一片白框。统一走 `assetUrl()` / `staticAsset()` 按模式拼前缀。

导出的静态资源：`docs/static/narrations/`（样例配图）与 `docs/static/narration-audio/`
（样例口播）要入库，否则线上样例没声音没图。

### 分发包（发给学生本地跑）

```bash
python tools/make_release.py            # → dist/PyMaster_教学平台.zip（约 72MB）
python tools/make_release.py --lite     # 不含 pandas/matplotlib，体积小一半
```

包里有嵌入式 Python（`runtime/python-embed.zip`）与 `vendor/wheels/`，
用户解压后**只需要双击 `启动PyMaster.bat`**（唯一入口，别再引入第二个）：

- `tools/bootstrap_runtime.py` 首次运行解压随包 Python、补 pip、离线装依赖
- 嵌入式发行版有两个坑，都在这个脚本里处理了：
  1. 默认禁用 `site`、不带 pip → 装不了库；
  2. 有 `._pth` 时进入隔离模式，**不会**把脚本目录加进 `sys.path`
     → `python app.py` 报 `ModuleNotFoundError: comic_engine`。
     所以脚本每次启动都按当前路径重写 `._pth`，文件夹被搬走也能自愈。
- 代码运行器必须用 `sys.executable`（已修）：写死 `'python'` 在随包环境下
  找不到解释器，或悄悄跑到系统里另一个 Python 上。

实测：全新解压 → 自举 79 秒（全程不联网）→ 随包 Python 起服务 → 学生代码跑通。

### 推到 GitHub

直连不通时走镜像（已验证可用，`ghproxy.net` 与 `ghfast.top` 都能读能推）：

```bash
git -c http.https://github.com.proxy= \
  push "https://ghproxy.net/https://github.com/jscjscjscjscjsc/py-master.git" main
```

报 "Bypassed rule violations ... must be made through a pull request" 是仓库
开了分支保护，owner 账号能直接推，忽略即可。

### 上线

见 `上线部署方案.md`；`deploy/` 里有现成的 Dockerfile、docker-compose 与 Caddyfile。
**判题无沙箱，公网开放前必须读那篇的第二节。**

## 九、待办

- [ ] 讲解全量生产（进行中）
- [ ] 章节开场 3D 动画目前只有 9 套分镜
- [ ] 微信扫码登录需要微信开放平台资质与公网回调域名（代码已就绪）
- [ ] LangFlow 教学编排（调研已完成，暂缓落地）
- [ ] 题库还可继续扩：第 31、34–36、39–40 章暂无配套题
- [ ] 823/操作系统专项可以继续加：目前 823 八章共 26 题、操作系统 18 题，
      按考研复习的正常密度每章至少能铺到 15–20 题（KMP 完整实现、AVL 旋转、
      关键路径、多级反馈队列、成组链接法、死锁检测算法等还没覆盖）
