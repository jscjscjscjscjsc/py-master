# PyMaster — 3D Python 编程学习平台

PyMaster 是面向 Python 初学者的本地互动学习平台，包含 9 个章节、40 个知识点、章节 CG、AI 助教、在线练习、知识星海与学习进度追踪。

在线展示：[GitHub Pages](https://jscjscjscjscjsc.github.io/py-master/)

## 本地启动

Windows 用户双击 `启动PyMaster.bat`。脚本会安装依赖，并在第一次运行时依次询问：

1. 模型名称
2. API Base URL
3. API Key
4. 可选备用模型

配置只会写入本机 `.env`，该文件已被 `.gitignore` 排除，不会上传到 GitHub。默认推荐火山方舟配置：

```text
模型：doubao-seed-2-0-code-preview-260215
Base URL：https://ark.cn-beijing.volces.com/api/v3
```

API Key 需要用户在自己的火山方舟账号中创建。不要把 Key 写进源码、截图、Issue 或提交记录。

也可以从命令行启动：

```bash
python -m pip install -r requirements.txt
python setup_api.py
python app.py
```

打开 <http://127.0.0.1:5000>。

需要重新配置时，删除本机 `.env` 后再次启动，或运行：

```bash
python -c "from setup_api import prompt_setup; prompt_setup(force=True)"
```

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
python tools/make_release.py           # 产出 dist/PyMaster_教学平台.zip
```

压缩包自带嵌入式 Python 与全部依赖 wheel，对方**不需要装 Python、不需要联网**：
解压 → 双击 `启动PyMaster.bat` → 浏览器自动打开。首次启动约 1 分钟，之后秒开。

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
