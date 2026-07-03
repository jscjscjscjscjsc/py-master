# 笔记文件管理器设计文档

## 概述

在 PyMaster 笔记系统中增加文件管理功能，让用户可以：
1. 从笔记中创建 .txt 文件并用系统默认编辑器打开/编辑
2. 将任意本地文件（代码/文档/md/txt 等）关联到笔记，随时用系统默认软件打开

## 数据存储

在 `users.json` 中扩展 notes 结构，每个知识点下的笔记改为对象，包含 content 和 files 列表：

```json
{
  "notes": {
    "8_0": {
      "content": "函数的定义要点...",
      "files": [
        {
          "path": "C:\\Users\\Admin\\Desktop\\函数笔记.txt",
          "name": "函数笔记.txt",
          "type": "txt",
          "created": "2026-07-01 14:30:00"
        }
      ]
    }
  }
}
```

- `content` — 笔记文本内容（现有）
- `files` — 关联文件列表
  - `path` — 文件绝对路径
  - `name` — 文件名（显示用）
  - `type` — 扩展名（用于图标）
  - `created` — 添加时间

### 迁移

现有用户数据中 `notes["8_0"]` 是字符串，需要兼容：
- 读取时：如果是字符串，自动转为 `{content: 字符串, files: []}`
- 保存时：始终使用新结构

## 后端 API

### GET `/api/note-files/list`

获取某个 KP 的笔记（含文件列表）。

**请求参数：** `chapter_id`, `kp_index`

**响应：**
```json
{
  "success": true,
  "note": {
    "content": "笔记内容",
    "files": [
      {"path": "...", "name": "文件名.txt", "type": "txt", "created": "2026-07-01 14:30:00"}
    ]
  }
}
```

### POST `/api/note-files/create-txt`

在桌面上创建 .txt 文件并用记事本打开，同时加入文件列表。

**请求参数：** `chapter_id`, `kp_index`

**响应：**
```json
{
  "success": true,
  "file": {"path": "...", "name": "...", "type": "txt", "created": "..."}
}
```

### POST `/api/note-files/add`

弹出 Windows 原生文件选择框，用户选择文件后加入列表。

**请求参数：** `chapter_id`, `kp_index`

**响应：**
```json
{
  "success": true,
  "file": {"path": "...", "name": "...", "type": "py", "created": "..."}
}
```

### POST `/api/note-files/open`

用 `os.startfile()` 打开指定文件（系统默认程序）。

**请求参数：** `file_path`

**响应：** `{"success": true}` 或错误信息

### POST `/api/note-files/remove`

从文件列表中移除（不删原文件）。

**请求参数：** `chapter_id`, `kp_index`, `file_path`

**响应：** `{"success": true}`

## 前端 UI

在 `chapter.html` 每个 KP 的笔记区域新增文件列表区块：

```
┌─ 📝 我的笔记 ──────────────────────────┐
│  [textarea 笔记编辑器]                   │
│  [保存笔记]  [新建TXT]  [📂 打开文件]    │
│                                         │
│  ─── 📎 关联文件 ───                    │
│  📄 函数笔记.txt          [打开] [✕]     │
│  🐍 demo.py              [打开] [✕]     │
│  📝 notes.md             [打开] [✕]     │
│  (空列表时显示: 暂无关联文件)             │
└─────────────────────────────────────────┘
```

### 文件类型图标映射

| 扩展名 | 图标 |
|--------|------|
| .txt   | 📄  |
| .py    | 🐍  |
| .md    | 📝  |
| .docx, .doc | 📘 |
| .xlsx, .xls | 📊 |
| .pptx, .ppt | 📽️ |
| .jpg, .png, .gif, .bmp | 🖼️ |
| .pdf   | 📕  |
| 其他   | 📎  |

### 交互流程

**新建 TXT：**
1. 用户点击 [新建TXT]
2. API 在桌面创建 `PyMaster_笔记_第X章_X_时间戳.txt`
3. 自动用记事本打开
4. 文件自动加入列表并刷新

**打开文件（选择本地文件）：**
1. 用户点击 [📂 打开文件]
2. 后端弹出 Windows 原生文件选择对话框（tkinter/win32ui）
3. 选定后用 `os.startfile()` 打开
4. 文件自动加入列表并刷新

**文件列表操作：**
- 点击 [打开] → 调用 `/api/note-files/open`
- 点击 [✕] → 调用 `/api/note-files/remove`，刷新列表

### JS 函数

```javascript
async function loadNoteFiles(chapterId, kpIndex) { ... }
async function createNoteTxt(chapterId, kpIndex) { ... }
async function addLocalFile(chapterId, kpIndex) { ... }
async function openNoteFile(filePath) { ... }
async function removeNoteFile(chapterId, kpIndex, filePath) { ... }
```

## 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `app.py` | 修改 | 迁移 notes 数据结构，新增 5 个 API 端点 |
| `templates/chapter.html` | 修改 | 笔记区域增加文件列表 UI |
| `static/js/main.js` | 修改 | 新增文件管理相关 JS 函数 |
| `static/css/style.css` | 修改 | 文件列表样式 |

## 不涉及

- 文件内容不同步到服务器
- 不支持文件拖拽上传
- 不支持文件夹选择
