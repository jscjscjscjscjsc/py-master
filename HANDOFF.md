# 接手指南（当前状态速查）

> 本文只写"接手继续干活需要知道的事"，历史演进看 `PROGRESS.md`。
> 最后更新：2026-09-16

## 一、这是什么

`PyMaster 教学平台`：把 Python 基础到 AI 应用开发做成一套可自学的平台。
课程 39 章 / 400 个知识点 / 212 道教材练习 / **170 道刷题题库**（含 95 道算法题），
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
│   ├── data/question_bank.json   170 道题库（编译产物）
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
  新专题号要登记进 `build_question_bank.py` 的 `ALGO_TOPICS`，新文件名加进两个脚本的 `MODULES`。
- 等级曲线是 `training_engine.LEVEL_THRESHOLDS` 这张 30 个数的表（前松后紧），
  单题基础分在同文件的 `QUESTION_BASE`（简单/中等/较难 = 10/28/70，差 7 倍）。
- 每用户数据在 `data/training/<user>.json` 与 `data/coach/<user>.json`（已 gitignore）。
- 判题与代码运行都是**子进程无沙箱**执行（20–25 秒超时），别把服务暴露到公网。

## 八、待办

- [ ] 讲解全量生产（进行中）
- [ ] 章节开场 3D 动画目前只有 9 套分镜
- [ ] 微信扫码登录需要微信开放平台资质与公网回调域名（代码已就绪）
- [ ] LangFlow 教学编排（调研已完成，暂缓落地）
- [ ] 题库还可继续扩：第 31、34–36、39–40 章暂无配套题
