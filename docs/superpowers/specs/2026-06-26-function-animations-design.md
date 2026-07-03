# PyMaster 函数章节 Canvas 教学动画设计

## 概述

为 PyMaster 第 8 章（函数章节）新增 3 个 Canvas 驱动的教学动画演示组件，采用独立窗口弹出播放，支持自动播放 + 步进式交互。

## 架构

### 文件结构

新建 `static/js/func_demos.js`
- 复用 `func_interactive.js` 中的 `fdTheme`、`fdCanvas` 工具
- 新增 `fdEasing` 补间缓动工具函数集
- 新增 3 个动画组件对象

### 组件接口（统一模式）

```javascript
const DemoComponent = {
  scenes: [...],      // 预设场景列表
  state: { ... },     // 运行时状态（当前场景、步骤、播放状态等）
  open(),             // 打开弹窗，初始化 Canvas
  close(),            // 关闭弹窗，清理动画循环
  play(),             // 开始自动播放
  pause(),            // 暂停
  stepNext(),         // 前进到下一步
  stepPrev(),         // 回退到上一步
  reset(),            // 重置到初始状态
  render(),           // requestAnimationFrame 驱动的渲染帧
  _drawScene(ctx),    // 绘制当前场景内容
}
```

### 模板集成

- `chapter.html`: 新增 3 个 `fd-modal-overlay`（func-modal-stack / func-modal-param / func-modal-hof）、对应按钮
- `style.css`: 复用 `.fd-modal-overlay` / `.fd-modal-box` / `.fd-modal-header` 样式，新增 `.fd-demo-controls` 控制栏样式

## 组件 1: StackFrameDemo（栈帧演示）

**对应知识点：** KP0 函数的定义与文档
**Canvas 尺寸：** 700×450px

### 场景预设（3 段代码）

1. 简单两数相加：`def add(a,b): return a+b` → `x = add(3,5)`
2. 嵌套调用：`def square(x): return x*x` → `result = square(add(2,3))`
3. 递归：`def fact(n): return 1 if n<=1 else n*fact(n-1)` → `fact(4)`

### 动画步骤（每场景 5-8 步）

1. 定义函数 → 堆中创建函数对象
2. 调用 → 栈帧压栈（弹性缩放入场）
3. 形参赋值 → 参数值出现在栈帧内
4. 执行函数体 → 局部变量依次出现
5. 返回 → 返回值飞出，轨迹线标记 → 赋给调用处变量
6. 出栈 → 栈帧淡出消失

### Canvas 布局

- 顶部：代码展示区（~80px），当前执行行扫描光条高亮
- 中部三栏：全局区（左~20%）、栈区（中~35%）、堆区（右~35%）
- 底部：状态文字 + 进度

### 视觉效果

- 三栏颜色编码：全局=蓝色(#00d4ff)、栈=紫色(#a371f7)、堆=绿色(#3fb950)
- 栈帧圆角矩形，半透明填充，边框发光
- 返回值飞行弧线 + 渐变轨迹
- 代码行高亮 + 打字机效果

### 控件

▶ ⏸ ⏹ ◀ ▶ | 场景下拉选择（3段代码）| 步骤指示器 N/M

## 组件 2: ParamMatchDemo（参数匹配演示）

**对应知识点：** KP1/KP2 参数类型精讲
**Canvas 尺寸：** 700×450px

### 场景预设（5 个）

1. **位置参数：** `add(3, 5)` → 实参球按位置飞入形参槽
2. **默认参数：** `greet("小明")` → greeting 使用默认值 "你好"（灰显）
3. **关键字参数：** `describe(age=25, city="北京", name="张三")` → 参数按名字匹配
4. **可变位置 *args：** `sum_all(1,2,3,4)` → 多个小球聚合成元组槽
5. **可变关键字 **kwargs：** `info(name="A", age=18)` → 标签球飞入字典槽

### 动画步骤（每场景 4 步）

1. 显示函数签名 + 形参槽位
2. 实参小球从右侧飞入
3. 匹配动画（小球卡入/绑定到对应形参）
4. 完成状态（成功=绿色光环+✓，失败=红色闪烁+错误提示）

### Canvas 布局

- 顶部：函数签名区（~60px）
- 中部：实参区（右侧）→ 飞行动画 → 形参区（左侧），中间标注绑定关系
- 底部：匹配结果文字 + 图示

### 控件

◀ ▶ 场景切换 | ▶ 播放 ⏹ 重播 | 步骤指示器

## 组件 3: HOFDemo（高阶函数流水线）

**对应知识点：** KP4 Lambda与高阶函数
**Canvas 尺寸：** 700×450px

### 三标签页场景

#### Map 传送带
- 数字流从左向右经过 lambda 加工模块
- 传入队列 → lambda 模块（闪烁）→ 传出队列
- 每个数字经过自动转变颜色
- 预设：`map(lambda x: x*2, [1,2,3,4,5])`

#### Filter 漏斗
- 全部数据从顶部流入漏斗
- 满足条件的从底部流出（绿色路径）
- 不满足的从侧面淘汰（红色路径，淡出）
- 预设：`filter(lambda x: x%2==0, [1,2,3,4,5,6])`

#### Reduce 累加
- 多个数字从左到右两两合并
- 逐步收缩成单一最终值
- 合并过程有 + 运算符标记
- 预设：`reduce(lambda a,b: a+b, [1,2,3,4,5])`

### 控件

顶部 3 个标签页按钮 | ▶ 自动播放 ⏹ 重播 | 速度滑块 0.5×/1×/2×

## 涉及文件

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `static/js/func_demos.js` | 3 个 Canvas 动画组件 |
| 修改 | `templates/chapter.html` | 新增 3 个弹窗 + 3 个按钮 |
| 修改 | `static/css/style.css` | 新增控制栏样式 |

## 按钮映射

| KP | 按钮 | 组件 |
|----|------|------|
| KP0 | 🎬 栈帧演示 | StackFrameDemo |
| KP1/KP2 | 🎯 参数匹配演示 | ParamMatchDemo |
| KP4 | 🔄 高阶函数流水线 | HOFDemo |
