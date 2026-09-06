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

- 9 章 Python 课程与 40 个知识点
- 每章独立的四幕 3D CG 与概念实验
- AI Master 风格的双层 3D 知识星海
- 火山方舟 SSE 流式 AI 助教与备用模型切换
- 代码练习场、练习解析、错题本和收藏
- 思维导图、章节进度和语音讲解
- 桌面端与移动端自适应

## GitHub Pages

Pages 是无需后端的静态作品展示版，展示首页、章节内容、3D CG 和知识星海。AI 问答、账号数据和代码执行需要下载源码后在本机运行。

静态站点位于 `docs/`。更新方式：

```bash
python build_static_docs.py
```

仓库 Pages 来源应设置为 `main` 分支的 `/docs` 目录。

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
