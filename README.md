# PyMaster — 3D Python 编程学习平台

PyMaster 是面向 Python 初学者的本地互动学习平台，包含 9 个章节、40 个知识点、章节 CG、AI 助教、在线练习、知识星海与学习进度追踪。

在线展示：[GitHub Pages](https://jscjscjscjscjsc.github.io/py-master/)

## 本地启动

**Windows 用户双击 `0-启动PyMaster.bat` 就够了**——这是唯一的入口。
首次启动会自动准备运行环境（约 1 分钟），之后秒开，浏览器自动打开
<http://127.0.0.1:5000>。

然后分两步完成初始化：

1. **创建本地账号**：用户名 + 密码。不需要邮箱、不联网，密码只存在
   `data/users.json`；登录一次后一年内自动记住，一台电脑可以存多个账号
   （点头像即可切换），头像可上传照片或选表情。
2. **接入大模型**：在向导第二步填 Base URL / 模型名 / API Key，点「测试连接」。
   支持任何 OpenAI 兼容接口（火山方舟、DeepSeek、硅基流动、通义千问、本地 Ollama）。
   不填也能用：课程正文、练习、刷题、判题都能离线跑，只有 AI 答疑与讲解生成需要模型。

配置写入本机 `.env`，账号数据在 `data/`，两者都已被 `.gitignore` 排除，不会上传 GitHub。
**不要把 Key 写进源码、截图、Issue 或提交记录。**

从命令行启动（开发用）：

```bash
python -m pip install -r requirements.txt
python app.py
```

需要重新配置模型时，删掉本机 `.env` 后重启，会在向导第二步重新填写。

## 主要功能

- 39 章 Python 课程（基础 → 数据分析 → Web → AI 应用）、400 个知识点
- 212 道教材练习 + 256 道刷题题库（含 86 道西科大 823 考研与操作系统专项）
- 每个知识点一节 5 分钟图文讲解（大模型写分镜、本地程序化作图、edge-tts 配音）
- 星辰教练多会话答疑、刷题中心的 Jupyter 式分块运行与在线判题
- AI Master 风格的双层 3D 知识星海、每章四幕 3D CG
- 修为等级体系、学习仪表盘、错题分类、思维导图
- 桌面端与移动端自适应，断网可用（前端库已全部本地化）

## 在线演示站

<https://jscjscjscjscjsc.github.io/py-master/>

课程正文、练习与解析、讲解样例（有图有声）、星海图、术语表都能直接看。
AI 答疑、账号进度、在线判题需要后端，演示站会给出明确提示——不会假装能用。

静态站点位于 `docs/`，由平台自身页面导出：

```bash
python build_static_docs.py            # 默认带 8 节讲解样例
python build_static_docs.py --samples 20
```

仓库 Pages 来源设置为 `main` 分支的 `/docs` 目录。
绑定自定义域名见 [上线部署方案.md](上线部署方案.md)。

## 分发给别人用（本地完整版）

```bash
python tools/make_release.py           # 产出 dist/PyMaster_教学平台.zip（约 72MB）
python tools/make_release.py --lite    # 不含 pandas/matplotlib，体积小一半
```

压缩包自带嵌入式 Python 与全部依赖 wheel，对方**不需要装 Python、不需要联网**：
解压 → 双击 `0-启动PyMaster.bat` → 浏览器自动打开。首次启动约 1 分钟，之后秒开。

第一次启动时批处理会自己解开随包 Python（用 Windows 自带的 tar / PowerShell，
不依赖系统里有没有 Python），再用 `vendor/wheels` 离线装好依赖。
所以哪怕对方电脑上一个 Python 都没有，也能跑起来。

## 部署上线

- 只上线演示站：买域名指向 GitHub Pages，¥60/年左右
- 上线完整平台（含 AI 与判题）：见 [上线部署方案.md](上线部署方案.md)，
  里面有 `deploy/` 下现成的 Dockerfile、docker-compose 与 Caddy 配置

⚠️ 判题会无沙箱执行任意代码，公网开放前请务必读该文档第二节。

## 安全说明

- `.env`、运行时用户数据、AI 用量数据和本地密钥均不会提交。
- 豆包 TTS 凭据通过可选环境变量配置，不再硬编码。
- 免费额度与计费状态以模型平台控制台为准。

## 技术要求

- Python 3.9+
- 支持 WebGL 的现代浏览器
- Flask 2.3+

## 许可证

MIT
