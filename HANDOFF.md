# 接手指南（当前状态速查）

> 本文只写"接手继续干活需要知道的事"，历史演进看 `PROGRESS.md`。
> 最后更新：2026-09-18

## 一、这是什么

`PyMaster 教学平台`：把 Python 基础到 AI 应用开发做成一套可自学的平台。
课程 39 章 / 400 个知识点 / 212 道教材练习 / **256 道刷题题库**（含 181 道算法题，
其中 86 道是西科大 823《数据结构与算法》与操作系统的考研专项），
每个知识点配一节 5 分钟图文讲解，另有星辰教练、刷题中心、修为等级与学习仪表盘。

```
桌面/Vibe oding/PyMaster 教学平台/     ← 这个文件夹就是项目根，也是一个 git 仓库
├── 0-启动PyMaster.bat    ← 唯一的启动脚本（名字带 0- 是为了排在文件列表最前面）
├── app.py                Flask 主程序（约 4900 行）
├── training_engine.py    刷题引擎：题库 / 判题沙箱 / 积分 / 等级曲线
├── coach_engine.py       星辰教练：会话存储与提示词
├── PROGRESS.md           演进记录（历史）
├── HANDOFF.md            本文件（当前状态）
├── data/question_bank.json   256 道题库（编译产物）
├── tools/render/         程序化作图引擎
├── runtime/              随包 Python 与虚拟环境（gitignore，首启自动生成）
└── dist/                 分发包产物（gitignore）
```

> 2026-09-18 做过一次整理：项目根从 `发布版/` 上移一层，
> `原版总包/`（旧版 9 章项目、exe、旧 zip）已删除——旧教材内容仍在
> 仓库的 `data/courses_legacy_9ch.json` 里留档。
> 现在全机器只有 `0-启动PyMaster.bat` 一个启动脚本。

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
| `/cultivation` | 修行阁：修为成长子系统（法相 / 神功 / 装备 / 试炼 / 地图 / 攻略），见第八节 |
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

## 八、修行阁：用户画像子系统（2026-09-18 新增）

把原来那条「修为等级」做成了一个自成闭环的成长系统。**它是独立子系统**：
只读 `training_engine` 的作答档案，唯一会写回的是试炼奖励（走既有的防重复账本），
其余一切（法相、神功、装备、战力、攻略）都是**推导**出来的，不新增任何存档字段。

```
刷题 / 看讲解 / 读漫画
      ↓ 修为点（training_engine 结算，未改动）
   境界等级 30 级
      ↓ 推导                     ↓ 推导
  神功（每级一门）            装备（18 件，靠统计达标）
      ↓                          ↓
            战力 + 境界试炼（十境 × 3 目标）
                    ↓ 全达成
              突破奖励（真加分，写进 rewards 账本）
                    ↓
              攻略：下一境还差多少、做哪道题最快
```

| 入口 | 说明 |
|---|---|
| `/cultivation` | 修行阁主页面：法相 → 试炼 → 神功 → 装备 → 修行地图 → 攻略 |
| `/progress` | 学习仪表盘顶部的画像卡：法相缩略图 + 战力 + 试炼进度 + 十境阶梯（点任一境看肖像） |
| 全局浮窗 | 等级条上的法印不再是 emoji，而是该境界的矢量印记；点法印弹出等级详情 |
| `#level-22` | 修行阁支持锚点：`/cultivation#level-22` 直接打开那一境的详情；`#portrait` 放大法相 |

### 文件分工（改哪一块去哪个文件，别串门）

| 文件 | 负责 |
|---|---|
| `game_engine.py` | **纯数据**：`REALM_ART`（十境视觉参数）/ `SKILLS`（30 门神功）/ `EQUIPMENT`（18 件）/ `TRIALS`（十境试炼）/ 统计口径 `derive_stats` / 战力公式 / 攻略选题 |
| `static/js/portrait.js` | 画像渲染器：`render()` 出法相，`sigil()` 出境界法印，`icon()` 出装备线稿。全部程序化 SVG，**没有图片素材** |
| `static/js/cultivation_game.js` | 修行阁界面 + 等级详情弹窗 + 解锁播报（`openLevel()` 在仪表盘上也能用） |
| `static/css/cultivation_game.css` | 画像动效 + 页面布局 + 弹窗样式 |
| `templates/cultivation.html` | 页面骨架 |

### 三条必须守住的约定

1. **解锁条件只能引用 `derive_stats` 里的字段**。加新装备/试炼时若发现需要新口径，
   先在 `derive_stats` 里补，别在判定里就地算。`tools/test_platform.py` 第 8b 节有断言
   专门拦这件事（引用了不存在的统计量 → 装备会永远解不开且静默无提示）。
2. **`topics_full` 只算算法专题**（课程章节单列 `chapters_full`）。
   混在一起会让「把课本章节配套题做完」被算成「拿下一个算法专题」——条件文案就变成假话，
   这个 bug 真实发生过一次，是截图验收时发现的。
3. **画像不用 emoji、不用位图**。emoji 在深色界面里发虚且各系统渲染不一致，
   位图则意味着每次加境界都要重新出图。画像随 `用户名 + 境界` 做种子生成：
   同一境界不同人长得不一样，同一个人升级后纹路延续、复杂度上升。

### 试炼结算是**级联**的

一次突破奖励会进流水，可能让「连续 2 天有修为入账」这类目标同时达成。
`game.claim_trials()` 因此最多重算三轮（每轮只发还没发的），
`/api/game/state` 的 GET 是幂等的：刷新一百次也只在达成的那一刻发一次。

### 视觉验收怎么做

画像与装备图是程序化生成的，改 `REALM_ART` 的任何一个数字都会变样。
最快的调法是：起一个临时 Flask 实例把会话固定成一个数据丰富的预览账号，
用无头 Edge 离屏截图（见第九节的做法），再对照 `REALM_ART` 看十境是否逐级变华丽。
**别忘了删掉预览账号的 `data/training/<user>.json`，也不要用真实账号当预览号**——
`/api/game/state` 会顺手结算试炼，等于替那个账号加修为。

### 画风：深色绢本上的白描（2026-09-18 重做）

第一版画像是一具**无脸的荧光机甲**（方肩、装甲片、面甲光带、霓虹辉光），
挂在一个叫修行阁的页面上被一眼否掉：「一点仙风道骨的感觉都没有」。
判断是对的——那套造形语言和中国画里的「仙人」几乎处处相反。现在整个子系统的
画风按白描人物重来，依据是三类公认的原作：

| 依据 | 拿它做什么 |
|---|---|
| 梁楷《泼墨仙人图》 | 仙气不来自精致的脸，而来自**松弛**：五官挤在一处、缩颈、大片墨衣 |
| 《八十七神仙卷》/《朝元仙仗图》 | **线条是主角**：七头半的修长身形、削肩长颈、宽袖长裾、飘带拉出风势、背景留白 |
| 谢赫六法「骨法用笔」 | 线要有起收顿挫：主轮廓粗、衣纹细、须发更细，并且**允许一点点手抖** |

对应的六条硬规矩（写在 `portrait.js` 头部，改图前先读）：

1. **七头半身**。头半径 29、总高 440。上一版是二头半的方块，比例就先不像人。
2. **削肩、长颈、细腰、宽袖**，而且**大袖必须是道袍剪影的一部分**——
   第一版把袖子画成两个独立的钟形，成了两只挂在肩上的白耳朵。正确剪影是
   颈根 → 削肩 → 袖外缘垂下 → **在袖口处收进腰** → 再放出去成裾；那条折角就是袖口。
3. **不画面甲**。眉、眼、鼻、嘴各一两笔，眼是细长的一横（垂目）。
4. **发光改成晕**。背景是淡墨晕 + 云气 + 远山（四境起）+ 云纹法环（五境起），
   环上是「云头」短弧而**不是罗盘刻度**——刻度是仪器的语言。
5. **器比光效管用**：葫芦（三境）→ 长剑（五境）→ 丹炉（八境）。
   一眼认出「这是修仙」靠的是葫芦和剑，不是粒子雨。
6. **配色换成传统颜料**（见 `REALM_ART`）：素麻 → 月白 → 石绿 → 藤黄 → 藕荷 →
   石青 → 黛紫 → 胭脂 → 赭石 → 雨过天青 → 月白金。换色守两条：**明度随境界上升**、
   **相邻两境不同色相**。

页面侧（`cultivation_game.css`）：深色绢地（极淡的经纬斜纹）+ 界栏（内容两侧细竖线）
+ **天头**（`templates/cultivation.html` 里的 `.scroll-head`：楷体大标题 + 竖排朱文印 + 双细线）
+ 段与段之间的**云纹**（一条内联 SVG data URI，不引图片）。所有霓虹光晕都换成了墨线。

这一版踩到的三个新坑：

1. **`.pm-face` 不写 fill 就是黑的**。SVG 的默认填充是黑，不是透明——漏掉这条，
   整张脸会糊成一块黑面具（看着像戴了面甲，正好是上一版的问题）。
2. **白描无填色，但我们的底有一层墨晕**，中间不隔一层淡墨就会被颜料染成一片
   （合体期的胭脂尤其明显）。所以 `.pm-garment` 填的是 `rgba(7,10,13,0.62)`。
3. **星云的 alpha 要跟着换色一起降**。颜料色比霓虹「实」，同样的 alpha 下会把整片
   夜空染成一块色布，看着像糖果。`starfield.js` 里已经压到 0.045–0.1。

## 九、在线演示站与分发包（2026-09-18）

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
用户解压后**只需要双击 `0-启动PyMaster.bat`**（唯一入口，别再引入第二个）：

- `tools/bootstrap_runtime.py` 首次运行解压随包 Python、补 pip、离线装依赖
- 嵌入式发行版有两个坑，都在这个脚本里处理了：
  1. 默认禁用 `site`、不带 pip → 装不了库；
  2. 有 `._pth` 时进入隔离模式，**不会**把脚本目录加进 `sys.path`
     → `python app.py` 报 `ModuleNotFoundError: comic_engine`。
     所以脚本每次启动都按当前路径重写 `._pth`，文件夹被搬走也能自愈。
- 代码运行器必须用 `sys.executable`（已修）：写死 `'python'` 在随包环境下
  找不到解释器，或悄悄跑到系统里另一个 Python 上。

实测：全新解压 → 自举 79 秒（全程不联网）→ 随包 Python 起服务 → 学生代码跑通。

### 本地账号体系（2026-09-18 起）

面向"下载到自己电脑上用"的用户，去掉了 QQ 邮箱注册与微信扫码（那套留给将来上线版），
换成纯本地账号。**改动点散在四处，改账号相关代码时一起看**：

| 位置 | 作用 |
|---|---|
| `app.py` `register/login` | 用户名 + 密码；注册即登录；老账号登录时自动升级为 PBKDF2 加盐哈希 |
| `app.py` `/api/accounts` | 列出本机账号（用户名 / 头像 / 上次登录），**不带密码字段** |
| `app.py` `/api/avatar` + `/avatar/<name>` | 头像上传（data URL，≤2MB）与读取；文件名是用户名哈希，防中文编码坑与路径穿越 |
| `templates/setup.html` 第一步、`login.html` | 有账号就摆成头像卡片点选；没有就显示注册表单 |
| `static/js/main.js` `openAccountPanel()` | 导航栏头像点开的账号面板：换头像（8 个 emoji + 上传照片，前端先缩到 256×256）/ 切账号 / 退出 |

两个必须记住的约定：

- **记住登录靠 `session.permanent` + `PERMANENT_SESSION_LIFETIME = 365 天`**。
  Flask 默认的会话 Cookie 一关浏览器就失效，单机版用户会以为"又要我登录"。
- **`/api/accounts`、`/api/avatar`、`/avatar` 必须在 `SETUP_EXEMPT_PREFIXES` 里**。
  否则 AI 没配置时 before_request 会把它们重定向到 `/setup`，向导第一步自己就坏了。

忘记密码没有找回通道（密码只在本机），出口是：编辑 `data/users.json` 把该账号的
`password` 清空，再用同一个用户名"注册"一次即可重设密码，**学习记录与头像原样保留**
（`register` 里专门处理了这条路径，别顺手把它当重复注册拦掉）。

用户数据都在 `data/`：`users.json`（账号+进度+错题+笔记）、`avatars/`、`training/`、
`coach/`。整个 data 目录拷走即完成迁移。

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

## 十、开场 CG 与登录页（2026-09-18）

### 开场 CG：五幕实时 3D 短片

用户第一次打开它时先看到的东西，不是登录框。文件就四个：

| 文件 | 作用 |
|---|---|
| `templates/intro_cg.html` | 五幕的 DOM 内容（文案、禅条、数据卡片、启程页） |
| `static/css/intro_cg.css` | 视觉系统：星云层 / 苔藓层 / 水波层 / 暗角噪点 / HUD / 竖直导航 |
| `static/js/intro_cg.js` | three.js 场景 + 滚动引擎 + 涟漪 + 卡片 + WebAudio 环境音 |
| `static/vendor/three.min.js` | three.js r128，本地自带（**不要引 CDN**） |

**路由与"只播一次"**（`app.py`）：

| 位置 | 行为 |
|---|---|
| `GET /` | 没带 `pymaster_intro` Cookie → 转 `/intro`；带了 → 转 `/dashboard` |
| `GET /intro` | 渲染 CG。带 `?ch=N` 可直达第 N 幕（同时跳过加载帘与入场动画） |
| `GET /intro/done` | 片尾出口：按"AI 配没配 / 登没登录"决定去 `/setup`、`/login` 还是 `/dashboard`，并写 1 年期的 `pymaster_intro` Cookie |
| `SETUP_EXEMPT_PREFIXES` | **`/intro` 必须在这个白名单里**，否则 AI 没配置时 before_request 会把新用户直接送去填密钥，片子根本没机会播 |

改这块时容易踩的三个坑：

1. **Cookie 用 `httponly=True`**，所以 `document.cookie` 里看不到它 —— 别据此以为没写进去（自测里就是这么翻过车的）。
2. **出口按钮不要写成纯链接**。`#cg-enter` 是 `href="#"` + JS 跳转，因为静态站上 `/intro/done` 不存在，静态模式要走 `index.html`（认 `body[data-static]`）。
3. **深链 `?ch=N` 会加 `body.cg-instant`**，它关掉加载帘与入场动画 —— 做视觉验证时靠它才能一帧就拿到最终画面。

### 视觉验证怎么做（这台机器上唯一可行的办法）

浏览器在内嵌面板里处于后台时 **`document.hidden === true`，rAF 被节流到几乎为零**，
截图只会拿到很早以前的一帧（看起来就像"页面全黑/卡死"）。所以视觉验收走无头 Edge 离屏渲染：

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless=new --no-sandbox --enable-unsafe-swiftshader --hide-scrollbars \
  --window-size=1600,900 --user-data-dir=/tmp/cgshot/prof \
  --virtual-time-budget=6000 --screenshot=/tmp/cgshot/ch3.png \
  "http://127.0.0.1:5055/intro?ch=3"
```

配合 `?ch=0..4` 就能逐幕出图。**注意 `--virtual-time-budget` 不等于"等这么久再拍"**：
虚拟时钟只在渲染器空闲时前进，连续 rAF 的页面实际只走几帧 —— 所以必须用 `cg-instant`。

### 性能上的注意事项（改场景时会碰到）

- **背景不能用逐帧噪声函数**。最初全屏 5 阶 fbm ×3 直接把集成显卡拖垮，
  现在改成"一次性用 2D 画布画好星云贴图 + 着色器只做两次采样 + 涟漪扭曲"。
  加新的全屏效果前先想清楚每像素要跑多少次哈希。
- 主循环里有 **自适应降档**：连续 70 帧平均超过 42ms 就把 pixelRatio 从 1.5 降到 1.0，再不行降到 0.75。
- 水波那层 2D 画布按帧重绘，别在里面建元素或读 DOM。

### 登录页

`templates/login.html` + `static/css/auth.css` + `static/js/auth.js`。

**只换皮不换骨**：`main.js` 里那套登录/注册逻辑依赖的 id 与 class 一个都不能少 ——
`.auth-tab[data-tab]`（且登录必须排在第一个，本机账号卡片点一下会调 `tabBtns[0].click()`）、
`#login-form` / `#register-form` 带 `.auth-form.active`、
`#login-username` / `#login-password` / `#reg-username` / `#reg-password` / `#reg-password-confirm`、
`#local-accounts`（**它靠 inline `style="display:none"` 隐藏，`main.js` 用 `display=''` 显示出来，
所以 CSS 里千万不要给这个 id 写 `display:none`**）、`#local-list`、
以及 main.js 动态生成的 `.local-card/.local-face/.local-name` 三个类名。

两个覆盖点的坑：`style.css` 里 `.input-group .input-icon` 是**绝对定位的老写法**，
`.auth-tab.active` 还带背景色，新样式要连带 `.input-group` 一起写选择器才压得住（具体见 `auth.css` 注释）。

> 页面里已经没有 `#particles-canvas` 了 —— `main.js` 的粒子模块查不到这个元素会自己 return，
> 所以不会和 `auth.js` 的新画布抢帧。

## 十一、星辰教练：星海背景与十一境法相（2026-09-18 新增）

星辰教练不再是一张固定的头像，而是**会随你一起升境的存在**：你修到什么境，
它就显化什么身。凡尘时是一团抱着星星的大头娃娃，金仙时是悬于星海之上、
掌托星系、周天七重法阵、背后开着日轮的法相。这既是最省成本的「升级奖励」
（零素材，全程序化生成），也让「你的境界就是它的境界」有了画面支撑。

| 入口 | 说明 |
|---|---|
| `/coach` | 聊天页：星海背景 + 空态大法相 + 身后一尊淡淡的存在 + 顶栏法相印记 |
| 顶栏「✦ 微光 / ✦ 星海 / ◌ 纯净」 | 背景三档切换，选择存 `localStorage['pymaster_coach_scene']`，**默认星海** |
| 顶栏「☯ 法相」 | 形象谱系：11 尊全列出来，未到达的是灰的但形状看得清，点开看详情与还差多少 |
| `/coach?forms=1` | 深链：进页面直接摊开形象谱系（分享给别人看时用） |
| `/coach?scene=full\|soft\|off` | 深链：直接定档且不写 localStorage。逐状态截图验收靠它，手点是量不出来的 |
| 进页面播报 | 境界变了会弹一条「教练显化新身 · XXX」，见过一次就不再打扰（存 localStorage） |

### 背景这一版是怎么搭的（2026-09-18 二改）

第一版的问题是「黑底上撒了几个点」：星云是几个径向渐变糊出来的气团，
星星全是套着大发光精灵的软团，外面再被遮挡层压掉一大半，观感很平。
二改把整块背景按**由远及近九层**重搭，每层只负责一件事：

| 层 | 做法 | 为什么 |
|---|---|---|
| ① 底色 | 深空渐变，不是纯黑 | 纯黑看起来像"没画完" |
| ② 星云 | 域扭曲 fBm 烘成 420px 贴图，被 6 个内部光源照亮 | 借自 `wwwtyro/space-scene-2d`：星云是被自己的星照亮的，所以它"浮"在星海里 |
| ③ 银河带 | 斜贯画面的密度脊 + **暗尘带** | 尘带是「这是银河」最强的线索，没有它那条带子只是雾 |
| ④ 微星场 | 几千颗亚像素暗星整层烘成贴图 | 真实夜空是"数不清"而不是"几百颗"；烘完每帧 0 成本 |
| ⑤ 分层星野 | 四层视差，尺寸/亮度走**幂律**（90% 小暗、1% 大亮） | 均匀分布看起来只是一层噪点，读不出星等 |
| ⑥ 星色 | 黑体色温表（3200K–17000K，Tanner Helland 近似） | 一片随机白点 vs 一片有真实色温的天空，差别就在这 |
| ⑦ 锚点星 | 少数几颗带四芒衍射星芒 | 给"远"提供参照物 |
| ⑧ 散景/云海 | 大虚焦光斑 + 底部三条横滚雾带 | 散景给近景景深；云海同时干三件事——托住法相、给画面出路、接上"仙家"那口气 |
| ⑨ 抖动/暗角 | 噪点贴图平铺 + 径向暗角 | 深色渐变在 8bit 下必然色带，抖动是"平→高级"性价比最高的一步 |

另外两条设计决定：

- **配色跟着境界走，但只掺进高密度区**。星云底色固定是深靛蓝，境界主色加在
  亮核那一段。第一版想直接旋转主色色相，金丹期旋出来是一块油污绿。
  现在金丹期是金核的天、元婴期是紫的天——同一页在不同境界看是不一样的星空。
- **指针视差**。画布里按层给不同系数，法相单独再跟一点（方向略反），
  两者一错开，法相就从"印在背景上的一张图"变成"站在星海前面"。

### 丹田星核（金丹）：七层

金丹期起胸口那颗核，第一版是两个圆（一个底色圆 + 一个白点），放大一看就是个灯泡。
现在由外到内分七层：**外层辉光 → 日冕 → 吸积盘 → 能量丝 → 球体 → 丹纹 → 脉冲/伴星**。

两条关键：

- **球体那几层用 `coreclip` 裁进躯干，辉光/日冕/星芒/伴星故意不裁**。
  这一条决定了它是"体内在烧"还是"胸口贴了个亮片"。
- 球体渐变必须是**三段**（高温心 → 主色 → 冷下来的边缘，最外再亮回来一下），
  只有两段的球会被读成平面圆。

### 文件分工

| 文件 | 负责 |
|---|---|
| `game_engine.py` | `COACH_FORMS`（十一境视觉参数）+ `COACH_XIAN_STAGES`（散仙/真仙/金仙的增量）+ `coach_form_for()` / `coach_form_table()` |
| `app.py` | `GET /api/coach/forms`：当前显化哪一尊、下一尊差多少、十一尊全表 |
| `static/js/star_coach.js` | 法相渲染器：`render({art, seed})` 出 SVG。四族骨架（child/youth/adept/immortal）+ 本境参数 |
| `static/js/starfield.js` | 星海画布（九层，见上）。`create(canvas, opts)` → `{setMode, setPalette, destroy, bench}`。`StarField.diag()` 返回当前参数（星数/烘焙耗时/指针视差），只给验收脚本用 |
| `static/js/coach_scene.js` | 页面集成：三档背景、空态大图、形象谱系弹窗、换发相播报、拿不到数据时的降级 |
| `static/css/coach_scene.css` | 背景层 + `.sc-*` 法相动效 + 空态 + 图鉴 |

### 七个已经踩过的坑（改这块之前先看一眼）

1. **颜色串拼错会静默炸掉整个页面**。`starfield.js` 的粒子精灵要用 `rgba(r,g,b,a)`，
   第一版把 `'rgb(...)'` 再拼 `'cc'` 当 alpha，`addColorStop` 直接抛异常；
   它在 `DOMContentLoaded` 里，一抛就把后面「画法相、画等级条」全带崩，
   表现是**整页只剩背景**。所以 `create()` 与 `paint()` 都包了 try/catch，别删。
2. **`REALM_ORDER` 只有十个大境界，凡尘不在里面**。教练的第一尊（星尘童儿）
   恰好是凡尘那一档，图鉴要显式把它补回表首，否则开局看到的那一尊在图鉴里找不到。
3. **图鉴里「当前」那一格要按实际小境取像**。仙人境有散仙/真仙/金仙三小境，
   一律取起始的散仙会让已经到金仙的人看到一尊不是自己的法相。
4. **类名不要用 `.card-*`**。`style.css` 里已有全局的 `.card-meta`（仪表盘在用），
   撞名之后图鉴的卡片文字被挤成竖排。图鉴自己的类一律 `scg-` 前缀。
5. **`<button>` 做弹性容器要显式写 `align-items: stretch`**。Chrome 的 UA 样式
   给 button 定了 `align-items: center`，不覆盖的话每行子元素缩成 fit-content，
   「星尘童儿」会被截成「星尘童…」。
6. **SVG 里一条横贯整张脸的光带会被读成一张嘴**。高境的面甲必须画成左右两只
   分开的眼睛，第一版全都在「抿嘴笑」。
7. **手臂不要整条画出来**。修仙身形该是「宽袖垂着、手从袖口露一截」：
   袖是一个钟形（只描下摆），手是袖口下的一枚小圆掌，中间一段极短的前臂。

### 二改又踩到的五个坑

1. **`transform-box: fill-box` + `transform-origin: center` 会让旋转"看着像没生效"**。
   一段弧、一颗小星的包围盒中心就是它自己，绕着它转等于原地打转——
   原来的绕行小星就这么白转了。凡是绕"核心"转的元素，一律用
   `transform-box: view-box` + `transform-origin: 160px var(--sc-core-cy)`。
2. **噪声要查表，不要每次现算哈希**。星云贴图是十万级像素 × 十几次噪声采样，
   用哈希版本单这一块就要一秒多，页面明显卡一下。换成 256×256 随机表查表后
   快了 3 倍以上（实测整块 60ms 左右），而且 256 的周期顺带是可平铺的。
3. **噪声"越像等高线"越难看**。`1 - |noise|` 取高次幂能做细丝，但幂次不够就会
   变成一张地形图。第一版还叠了"被内部光源照亮"，直接把高光压成了剪纸一样的硬边。
   解法：细丝项权重降到 0.3、幂次提到 9，烘完再过一遍**缩-放模糊**（`soften()`），
   缩放在 canvas 采样器里做，一次几毫秒，比逐像素高斯便宜得多。
4. **云海的频率方向容易搞反**。要"横着拉长的云丝"，就得 x 方向格距远大于 y 方向；
   反过来做出来是一排竖条纹，像窗帘。
5. **云海贴图的可平铺性**：想让噪声自己首尾接上，x 方向必须跨整数倍周期（256），
   那会把格距锁死在 4px 以下，做不出长云丝。改成**相邻两片镜像拼接**就绕开了
   （镜像在边界处天然连续）。

### 三条性能约定（改场景时别破坏）

- **一切噪声只在烘焙期跑**，主循环只做 `drawImage`。开场 CG 最初就是被逐像素
  fbm 拖垮的，别再犯。烘焙还是**分片**做的（`setTimeout` 让出主线程，
  不用 `requestIdleCallback`——页面一直忙的时候空闲回调可能永远排不上）。
- **发光粒子全部走预渲染精灵**，不用 `shadowBlur`（每个粒子每帧设一次会让帧时间翻几倍）。
  另外星野**分两趟画**（先所有方点小星、再所有发光星），把 composite 状态切换从几百次降到两次。
- **该停就真停**：切到纯净档、`document.hidden`、`prefers-reduced-motion`
  三种情况都必须停掉 rAF，而不是把画布调透明了继续空转。帧时间连续超 42ms 会自动降档。
- 实测（1566×756，SwiftShader 软件光栅）：**drawMsPerFrame ≈ 0.5ms**，
  星云整块烘焙 ≈ 60ms / 3 片。真机有硬件加速只会更快。

### 想调什么，改哪里

- 某一境的观感（环数/冠阶/甲片/粒子/配色/神态）→ `game_engine.COACH_FORMS`
- 金仙比真仙盛多少 → `game_engine.COACH_XIAN_STAGES`（那里的数字是**增量**，不是绝对值）
- 头身比与身形轮廓 → `star_coach.js` 顶部的 `SHAPES`（四族人体测量值，所有部件挂在上面）
- 星野星数/大小/漂移 → `starfield.js` 的 `buildStars` 与 `buildField`
- 星云形状与浓淡 → `starfield.js` 的 `buildGas`（`mask` 管覆盖面积、`lights` 管亮核位置、
  `scale` 管云团大小、`gain` 管整体亮度）
- 星星的颜色 → `starfield.js` 的 `TEMPS`（黑体色温表）
- 层层遮挡的松紧（"背景好看"和"正文好读"之间那根弦）→ `coach_scene.css` 的
  `.coach-scene-veil` 与 `body[data-scene="full"] .coach-main`。**先读那里面的注释再动。**

### 视觉验收

星海与法相都是程序化生成的，改任何数字都会变样。逐态截图（金仙 / 儿形 / 图鉴 /
三档背景）用无头 Edge 离屏渲染，见第九节的做法。

- **定档走深链**：`/coach?scene=full|soft|off`，不用手点。
- **满级画面**：临时改 `data/training/<临时账号>.json` 的 points（29600 是金仙），
  截完把 points 改回去、`data/coach/<临时账号>.json` 删掉。
- **量性能别用无头浏览器的帧率**：虚拟时钟会把 rAF 节流到几乎为零，
  5 秒只跑得出 2~3 帧，那个数字毫无意义。用 `starfield.diag()` 与 `bench(n)`，
  或者在页面里直接读 `StarField.diag()`。
- **背景类效果最容易"挂了个空监听"**：指针视差这种看不见摸不着的，
  验收要看 `StarField.diag().pointer / .parallax` 有没有真的变。

## 十二、待办

- [ ] 讲解全量生产（进行中）
- [ ] 章节开场 3D 动画目前只有 9 套分镜
- [ ] 微信扫码登录需要微信开放平台资质与公网回调域名（代码已就绪）
- [ ] LangFlow 教学编排（调研已完成，暂缓落地）
- [ ] 题库还可继续扩：第 31、34–36、39–40 章暂无配套题
- [ ] 823/操作系统专项可以继续加：目前 823 八章共 26 题、操作系统 18 题，
      按考研复习的正常密度每章至少能铺到 15–20 题（KMP 完整实现、AVL 旋转、
      关键路径、多级反馈队列、成组链接法、死锁检测算法等还没覆盖）
