# PyMaster 函数教学动画实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 PyMaster 第 8 章（函数章节）新增 3 个 Canvas 驱动的教学动画演示组件，支持独立窗口弹出播放 + 自动播放 + 步进式交互

**Architecture:** 新建 `static/js/func_demos.js`，包含 fdEasing 工具函数和 3 个动画组件对象（StackFrameDemo / ParamMatchDemo / HOFDemo）。组件复用 `func_interactive.js` 中的 `fdTheme`/`fdCanvas` 工具模块。弹窗复用现有 `fd-modal-overlay` 体系。在 `chapter.html` 新增按钮和弹窗，在 `style.css` 新增控制栏样式。

**Tech Stack:** 原生 Canvas 2D + requestAnimationFrame, 零外部依赖

**Design Spec:** `docs/superpowers/specs/2026-06-26-function-animations-design.md`

---

### Task 1: 创建 func_demos.js — fdEasing 工具函数 + StackFrameDemo 组件

**Files:**
- Create: `static/js/func_demos.js`

- [ ] **Step 1: 创建文件头部 + fdEasing 工具函数**

```javascript
/**
 * func_demos.js — 函数章节 Canvas 教学动画演示
 * 3 个组件：StackFrameDemo / ParamMatchDemo / HOFDemo
 * 复用 func_interactive.js 中的 fdTheme / fdCanvas
 */

// ============================================================
// 补间/缓动工具函数
// ============================================================
const fdEasing = {
  // 线性插值
  lerp(a, b, t) { return a + (b - a) * Math.min(Math.max(t, 0), 1); },

  // 三次缓入缓出
  easeInOut(t) {
    return t < 0.5
      ? 4 * t * t * t
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  },

  // 弹性缓出（适合栈帧压入弹出）
  elasticOut(t) {
    if (t === 0 || t === 1) return t;
    const c4 = (2 * Math.PI) / 3;
    return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },

  // 弹跳缓出（适合小球入槽）
  bounceOut(t) {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  },

  // 缓入平方
  easeInQuad(t) { return t * t; },

  // 缓出平方
  easeOutQuad(t) { return t * (2 - t); },

  // 值范围映射
  mapRange(value, inMin, inMax, outMin, outMax) {
    return outMin + (value - inMin) * (outMax - outMin) / (inMax - inMin);
  },

  // 简单动画时间线 — 驱动一组动画关键帧
  // frames: [{ start, end, onUpdate(progress) }], duration: ms
  Timeline(frames, duration, onComplete) {
    const startTime = performance.now();
    const totalDuration = duration;
    let running = true;

    function tick() {
      if (!running) return;
      const elapsed = performance.now() - startTime;
      const t = Math.min(elapsed / totalDuration, 1);

      frames.forEach(f => {
        const localT = (t - f.start) / (f.end - f.start);
        if (localT >= 0 && localT <= 1) {
          f.onUpdate(fdEasing.easeInOut(localT));
        }
      });

      if (t < 1) {
        requestAnimationFrame(tick);
      } else if (onComplete) {
        onComplete();
      }
    }
    tick();
    return { cancel: () => { running = false; } };
  }
};
```

- [ ] **Step 2: 添加 StackFrameDemo 组件的场景数据和状态管理**

```javascript
// ============================================================
// 组件 1: 栈帧演示 — StackFrameDemo
// ============================================================
const StackFrameDemo = {
  scenes: [
    {
      title: '两数相加',
      code: [
        'def add(a, b):',
        '    result = a + b',
        '    return result',
        '',
        'x = add(3, 5)',
        'print(x)'
      ],
      steps: [
        { label: 'def add → 堆中创建函数对象', highlight: [0], data: { heap: { add: { type: 'function', params: 'a,b' } } } },
        { label: '调用 add(3,5) → 栈帧压入调用栈', highlight: [4], data: { stack: [{ name: 'add', vars: { a: 3, b: 5 }, active: true }] } },
        { label: '执行 a + b → result 存入栈帧', highlight: [1], data: { stack: [{ name: 'add', vars: { a: 3, b: 5, result: 8 }, active: true }] } },
        { label: 'return result → 返回值 8 飞出栈帧', highlight: [2], data: { stack: [{ name: 'add', vars: { a: 3, b: 5, result: 8 }, returning: 8 }], global: { x: null } } },
        { label: 'x = 8 → 赋值完成，栈帧销毁', highlight: [4], data: { stack: [], global: { x: 8 }, heap: { add: { type: 'function', params: 'a,b' } } } },
      ]
    },
    {
      title: '嵌套调用',
      code: [
        'def square(x):',
        '    return x * x',
        '',
        'result = square(add(2, 3))'
      ],
      steps: [
        { label: '定义 square 函数 → 堆中创建', highlight: [0], data: { heap: { square: { type: 'function' } } } },
        { label: '调用 add(2,3) → add 帧压栈', highlight: [3], data: { stack: [{ name: 'add', vars: { a: 2, b: 3 }, active: true }] } },
        { label: 'add 返回 5 → add 帧出栈', highlight: [3], data: { stack: [{ name: 'add', vars: { a: 2, b: 3 }, returning: 5 }] } },
        { label: '调用 square(5) → square 帧压栈', highlight: [3], data: { stack: [{ name: 'square', vars: { x: 5 }, active: true }] } },
        { label: 'return 5*5=25 → square 帧出栈', highlight: [1], data: { stack: [{ name: 'square', vars: { x: 5 }, returning: 25 }] } },
        { label: 'result = 25 → 完成', highlight: [3], data: { stack: [], global: { result: 25 } } },
      ]
    },
    {
      title: '递归阶乘',
      code: [
        'def fact(n):',
        '    if n <= 1: return 1',
        '    return n * fact(n-1)',
        '',
        'print(fact(4))'
      ],
      steps: [
        { label: '定义 fact → 堆中创建函数对象', highlight: [0], data: { heap: { fact: { type: 'function' } } } },
        { label: 'fact(4) → 栈帧 #1 压栈 (n=4)', highlight: [4], data: { stack: [{ name: 'fact', vars: { n: 4 }, active: true }] } },
        { label: '递归 fact(3) → 栈帧 #2 (n=3)', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 }, active: true }] } },
        { label: '递归 fact(2) → 栈帧 #3 (n=2)', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 }, active: true }] } },
        { label: '递归 fact(1) → 栈帧 #4 (n=1)', highlight: [1], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 } }, { name: 'fact', vars: { n: 1 }, active: true }] } },
        { label: 'n<=1, return 1 → 栈帧 #4 出栈', highlight: [1], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 } }], heap: { fact: { type: 'function' } }, returnVal: '1' } },
        { label: '2*1=2 → 栈帧 #3 出栈', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }], returnVal: '2' } },
        { label: '3*2=6 → 栈帧 #2 出栈', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }], returnVal: '6' } },
        { label: '4*6=24 → 栈帧 #1 出栈, fact(4)=24', highlight: [2], data: { stack: [], global: { 'fact(4)': 24 }, returnVal: '24' } },
      ]
    }
  ],

  state: {
    sceneIdx: 0,
    stepIdx: 0,
    playing: false,
    animTimer: null,
    animProgress: 0,
    canvas: null,
    ctx: null,
  },

  open() {
    this.state.sceneIdx = 0;
    this.state.stepIdx = 0;
    this.state.playing = false;
    this.state.animProgress = 0;
    const modal = document.getElementById('func-modal-stack');
    if (modal) modal.classList.add('active');
    setTimeout(() => this._setupCanvas(), 100);
    this._updateUI();
  },

  close() {
    this.state.playing = false;
    if (this.state.animTimer) { this.state.animTimer.cancel(); this.state.animTimer = null; }
    document.getElementById('func-modal-stack')?.classList.remove('active');
  },
```

- [ ] **Step 3: 实现 StackFrameDemo 的 Canvas 渲染方法**

```javascript
  _setupCanvas() {
    this.state.canvas = document.getElementById('stack-canvas');
    if (!this.state.canvas) return;
    const rect = this.state.canvas.parentElement.getBoundingClientRect();
    const w = Math.min(700, rect.width - 4);
    const h = 450;
    this.state.ctx = fdCanvas.setup(this.state.canvas, w, h);
    this.state.width = w;
    this.state.height = h;
    this.render();
  },

  render() {
    const { ctx, width, height, sceneIdx, stepIdx, animProgress } = this.state;
    if (!ctx) return;
    fdCanvas.clear(ctx, width, height);
    const scene = this.scenes[sceneIdx];
    const step = scene.steps[stepIdx];
    const t = animProgress;

    // 背景
    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, width, height);

    // 1. 顶部代码区 (0-80px)
    this._drawCodeArea(ctx, width, scene.code, step.highlight, t);

    // 2. 三栏分区 (80-400px)
    this._drawZones(ctx, width, step.data, t);

    // 3. 底部操作提示 (400-450px)
    this._drawFooter(ctx, width, step.label);
  },

  _drawCodeArea(ctx, width, codeLines, highlightLines, t) {
    const x = 10, y = 8, lineH = 20, fontSize = 13;
    ctx.font = `${fontSize}px "Consolas", "Courier New", monospace`;
    codeLines.forEach((line, i) => {
      const isHighlight = highlightLines.includes(i);
      // 行高亮背景
      if (isHighlight) {
        ctx.fillStyle = `rgba(0, 212, 255, ${0.1 + 0.15 * Math.sin(Date.now() / 300)})`;
        ctx.fillRect(0, y + i * lineH - 2, width, lineH);
      }
      // 行号
      ctx.fillStyle = fdTheme.get('--text-muted');
      ctx.textAlign = 'right';
      ctx.fillText(`${i + 1}`, 30, y + i * lineH + 12);
      // 代码
      ctx.fillStyle = isHighlight ? fdTheme.colors.cyan : fdTheme.get('--text-primary');
      ctx.textAlign = 'left';
      ctx.fillText(line, 38, y + i * lineH + 12);
    });
    // 分割线
    ctx.fillStyle = fdTheme.get('--border-subtle');
    ctx.fillRect(0, y + codeLines.length * lineH + 4, width, 1);
  },

  _drawZones(ctx, width, data, t) {
    const yStart = 90;
    const zoneH = 300;
    const zoneW = (width - 20) / 3;

    // 三个分区背景
    const zones = [
      { label: '🌐 全局区', x: 10, w: zoneW, color: fdTheme.colors.cyan },
      { label: '📚 栈区', x: 10 + zoneW, w: zoneW, color: fdTheme.colors.purple },
      { label: '🗄️ 堆区', x: 10 + zoneW * 2, w: zoneW, color: fdTheme.colors.green },
    ];

    zones.forEach(z => {
      ctx.fillStyle = z.color + '15';
      fdCanvas.roundRect(ctx, z.x, yStart, z.w - 5, zoneH, 6, ctx.fillStyle);
      ctx.fillStyle = z.color + '40';
      ctx.font = '12px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(z.label, z.x + (z.w - 5) / 2, yStart + 18);
    });

    if (!data) return;

    // 堆区绘制
    if (data.heap) {
      Object.entries(data.heap).forEach(([name, info], i) => {
        const z = zones[2];
        const fx = z.x + 15, fy = yStart + 30 + i * 50, fw = z.w - 35, fh = 40;
        // 函数对象方块
        ctx.fillStyle = fdTheme.colors.green + '30';
        fdCanvas.roundRect(ctx, fx, fy, fw, fh, 6, ctx.fillStyle, fdTheme.colors.green + '80');
        ctx.fillStyle = fdTheme.colors.green;
        ctx.font = 'bold 12px "Consolas", monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`function ${name}()`, fx + 8, fy + 17);
        ctx.font = '10px "Microsoft YaHei", sans-serif';
        ctx.fillStyle = fdTheme.get('--text-muted');
        ctx.fillText(info.params ? `参数: ${info.params}` : '', fx + 8, fy + 32);
      });
    }

    // 栈区绘制
    if (data.stack && data.stack.length > 0) {
      data.stack.forEach((frame, fi) => {
        const z = zones[1];
        const sy = yStart + 30 + fi * 70;
        const sfw = z.w - 25;
        // 帧背景
        const frameColor = frame.active ? fdTheme.colors.purple : fdTheme.colors.purple + '80';
        ctx.fillStyle = frame.active ? fdTheme.colors.purple + '25' : fdTheme.colors.purple + '15';
        fdCanvas.roundRect(ctx, z.x + 10, sy, sfw, 60, 5, ctx.fillStyle, frameColor + '60');
        // 帧标题
        ctx.fillStyle = frameColor;
        ctx.font = 'bold 12px "Consolas", monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`📦 ${frame.name}()`, z.x + 20, sy + 18);
        // 局部变量
        if (frame.vars) {
          Object.entries(frame.vars).forEach(([k, v], vi) => {
            ctx.fillStyle = fdTheme.get('--text-primary');
            ctx.font = '11px "Consolas", monospace';
            ctx.fillText(`${k} = ${v}`, z.x + 20 + vi * 45, sy + 40);
          });
        }
        // 返回值飞行动画
        if (frame.returning !== undefined && t > 0) {
          const fromX = z.x + sfw / 2, fromY = sy;
          const toX = zones[0].x + zones[0].w / 2, toY = yStart + 60;
          const cx = (fromX + toX) / 2 - 30;
          const cy = Math.min(fromY, toY) - 20;
          const progress = fdEasing.elasticOut(t);
          const rx = fdEasing.lerp(fromX, toX, progress);
          const ry = fdEasing.lerp(fromY, toY, progress) - 20 * Math.sin(progress * Math.PI);
          ctx.fillStyle = '#ffd700';
          ctx.beginPath();
          ctx.arc(rx, ry, 8, 0, Math.PI * 2);
          ctx.fill();
          ctx.font = 'bold 11px "Consolas", monospace';
          ctx.fillStyle = '#fff';
          ctx.textAlign = 'center';
          ctx.fillText(`${frame.returning}`, rx, ry + 4);
          // 轨迹线
          ctx.strokeStyle = '#ffd70040';
          ctx.lineWidth = 2;
          ctx.setLineDash([4, 4]);
          ctx.beginPath();
          for (let p = 0; p <= progress; p += 0.02) {
            const px = fdEasing.lerp(fromX, toX, p);
            const py = fdEasing.lerp(fromY, toY, p) - 20 * Math.sin(p * Math.PI);
            p === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
          }
          ctx.stroke();
          ctx.setLineDash([]);
        }
      });
    }

    // 全局区变量
    if (data.global) {
      Object.entries(data.global).forEach(([k, v], gi) => {
        if (v === null) return;
        const z = zones[0];
        ctx.fillStyle = fdTheme.colors.cyan + '30';
        fdCanvas.roundRect(ctx, z.x + 10, yStart + 30 + gi * 35, z.w - 25, 28, 4, ctx.fillStyle);
        ctx.fillStyle = fdTheme.colors.cyan;
        ctx.font = 'bold 12px "Consolas", monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`${k} = ${v}`, z.x + 18, yStart + 48 + gi * 35);
      });
    }
  },

  _drawFooter(ctx, width, label) {
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, 395, width, 55);
    ctx.fillStyle = fdTheme.colors.cyan + 'CC';
    ctx.font = '13px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`⏵ ${label}`, 16, 425);
  },

  _updateUI() {
    const scene = this.scenes[this.state.sceneIdx];
    const total = scene.steps.length;
    const cur = this.state.stepIdx + 1;
    document.getElementById('stack-step-info').textContent = `步骤 ${cur}/${total}`;
    document.getElementById('stack-scene-title').textContent = scene.title;
    document.getElementById('stack-play-btn').textContent = this.state.playing ? '⏸' : '▶';
  },
```

- [ ] **Step 4: 实现 StackFrameDemo 的播放/步进控制方法**

```javascript
  stepNext() {
    const scene = this.scenes[this.state.sceneIdx];
    if (this.state.stepIdx < scene.steps.length - 1) {
      this.state.stepIdx++;
      this.state.animProgress = 0;
      // 自动播放动画过渡
      this.state.animTimer = fdEasing.Timeline(
        [{ start: 0, end: 1, onUpdate: (p) => { this.state.animProgress = p; this.render(); } }],
        600,
        () => { this.state.animProgress = 1; this.render(); this._updateUI(); }
      );
      this._updateUI();
    }
  },

  stepPrev() {
    if (this.state.stepIdx > 0) {
      this.state.stepIdx--;
      this.state.animProgress = 1;
      this.render();
      this._updateUI();
    }
  },

  play() {
    if (this.state.playing) {
      // Pause
      this.state.playing = false;
      if (this.state.animTimer) { this.state.animTimer.cancel(); }
      this._updateUI();
      return;
    }
    this.state.playing = true;
    this._updateUI();
    this._autoAdvance();
  },

  _autoAdvance() {
    if (!this.state.playing) return;
    const scene = this.scenes[this.state.sceneIdx];
    if (this.state.stepIdx >= scene.steps.length - 1) {
      this.state.playing = false;
      this._updateUI();
      return;
    }
    this.stepNext();
    setTimeout(() => this._autoAdvance(), 1800);
  },

  reset() {
    this.state.playing = false;
    if (this.state.animTimer) { this.state.animTimer.cancel(); }
    this.state.stepIdx = 0;
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },

  changeScene(idx) {
    this.state.playing = false;
    if (this.state.animTimer) { this.state.animTimer.cancel(); }
    this.state.sceneIdx = Math.min(idx, this.scenes.length - 1);
    this.state.stepIdx = 0;
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },
};
```

- [ ] **Step 5: 保存文件并验证语法**

```bash
node -e "const fs=require('fs'); const code=fs.readFileSync('static/js/func_demos.js','utf8'); try { new Function(code); console.log('✅ 语法检查通过'); } catch(e) { console.error('❌', e.message); }"
```

---

### Task 2: 添加 ParamMatchDemo 组件

**Files:**
- Modify: `static/js/func_demos.js` (append)

- [ ] **Step 1: 添加 ParamMatchDemo 场景数据**

```javascript
// ============================================================
// 组件 2: 参数匹配演示 — ParamMatchDemo
// ============================================================
const ParamMatchDemo = {
  scenes: [
    {
      title: '位置参数',
      code: 'add(3, 5)  # 位置一一对应',
      signature: 'def add(a, b):',
      params: [
        { name: 'a', type: 'pos', default: null, x: 220, y: 180 },
        { name: 'b', type: 'pos', default: null, x: 220, y: 240 },
      ],
      args: [
        { value: '3', target: 0, x: 480, y: 180, color: '#00d4ff' },
        { value: '5', target: 1, x: 480, y: 240, color: '#3fb950' },
      ],
      resultLabel: '✅ a=3, b=5',
      error: false,
    },
    {
      title: '默认参数',
      code: 'greet("小明")  # greeting 使用默认值',
      signature: 'def greet(name, greeting="你好"):',
      params: [
        { name: 'name', type: 'pos', default: null, x: 200, y: 170 },
        { name: 'greeting', type: 'default', default: '"你好"', x: 200, y: 250 },
      ],
      args: [
        { value: '"小明"', target: 0, x: 480, y: 170, color: '#00d4ff' },
      ],
      resultLabel: '✅ name="小明", greeting="你好" (默认值)',
      error: false,
    },
    {
      title: '关键字参数',
      code: 'describe(age=25, city="北京", name="张三")',
      signature: 'def describe(name, age, city):',
      params: [
        { name: 'name', type: 'keyword', default: null, x: 200, y: 130 },
        { name: 'age', type: 'keyword', default: null, x: 200, y: 210 },
        { name: 'city', type: 'keyword', default: null, x: 200, y: 290 },
      ],
      args: [
        { value: '"张三"', target: 0, x: 500, y: 130, color: '#a371f7', label: 'name=' },
        { value: '25', target: 1, x: 500, y: 210, color: '#00d4ff', label: 'age=' },
        { value: '"北京"', target: 2, x: 500, y: 290, color: '#3fb950', label: 'city=' },
      ],
      resultLabel: '✅ name="张三", age=25, city="北京"',
      error: false,
    },
    {
      title: '可变位置参数 *args',
      code: 'sum_all(1, 2, 3, 4)  # *args 打包成元组',
      signature: 'def sum_all(*args):',
      params: [
        { name: '*args', type: 'var_pos', default: null, x: 200, y: 210 },
      ],
      args: [
        { value: '1', target: 0, x: 400, y: 140, color: '#00d4ff' },
        { value: '2', target: 0, x: 440, y: 160, color: '#3fb950' },
        { value: '3', target: 0, x: 480, y: 180, color: '#a371f7' },
        { value: '4', target: 0, x: 520, y: 200, color: '#ffd700' },
      ],
      resultLabel: '✅ args = (1, 2, 3, 4)',
      error: false,
    },
    {
      title: '可变关键字参数 **kwargs',
      code: 'info(name="A", age=18)  # **kwargs 打包成字典',
      signature: 'def info(**kwargs):',
      params: [
        { name: '**kwargs', type: 'var_kw', default: null, x: 200, y: 210 },
      ],
      args: [
        { value: '"A"', target: 0, x: 450, y: 150, color: '#00d4ff', label: 'name=' },
        { value: '18', target: 0, x: 450, y: 250, color: '#3fb950', label: 'age=' },
      ],
      resultLabel: '✅ kwargs = {"name": "A", "age": 18}',
      error: false,
    },
  ],
```

- [ ] **Step 2: 添加 ParamMatchDemo 状态和开放方法**

```javascript
  state: {
    sceneIdx: 0,
    stepIdx: 0,    // 0=初始, 1=飞入中, 2=匹配完成
    playing: false,
    animTimeline: null,
    animProgress: 0,
    matched: false,
    canvas: null,
    ctx: null,
    width: 700,
    height: 450,
  },

  open() {
    this.state.sceneIdx = 0;
    this.state.stepIdx = 0;
    this.state.matched = false;
    this.state.playing = false;
    document.getElementById('func-modal-param-demo')?.classList.add('active');
    setTimeout(() => this._setupCanvas(), 100);
    this._updateUI();
  },

  close() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    document.getElementById('func-modal-param-demo')?.classList.remove('active');
  },

  _setupCanvas() {
    this.state.canvas = document.getElementById('param-demo-canvas');
    if (!this.state.canvas) return;
    const rect = this.state.canvas.parentElement.getBoundingClientRect();
    const w = Math.min(700, rect.width - 4);
    const h = 450;
    this.state.ctx = fdCanvas.setup(this.state.canvas, w, h);
    this.state.width = w;
    this.state.height = h;
    this.render();
  },
```

- [ ] **Step 3: 实现 ParamMatchDemo 渲染方法**

```javascript
  render() {
    const { ctx, width, height, sceneIdx, stepIdx, animProgress } = this.state;
    if (!ctx) return;
    fdCanvas.clear(ctx, width, height);
    const scene = this.scenes[sceneIdx];

    // 背景
    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, width, height);

    // 顶部 — 函数签名和调用代码
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, 0, width, 60);
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = 'bold 14px "Consolas", "Courier New", monospace';
    ctx.textAlign = 'left';
    ctx.fillText(scene.signature, 16, 26);
    ctx.fillStyle = fdTheme.get('--text-secondary');
    ctx.font = '13px "Consolas", monospace';
    ctx.fillText(scene.code, 16, 48);

    // 分割线
    ctx.fillStyle = fdTheme.get('--border-subtle');
    ctx.fillRect(0, 60, width, 1);

    // 形参区（左侧）
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📥 形参', 200, 90);

    // 绘制形参槽位
    scene.params.forEach((p, i) => {
      const sy = p.y;
      const slotW = p.type === 'var_pos' || p.type === 'var_kw' ? 120 : 80;
      ctx.fillStyle = fdTheme.colors.purple + '20';
      fdCanvas.roundRect(ctx, p.x - slotW / 2, sy - 15, slotW, 30, 8, ctx.fillStyle, fdTheme.colors.purple + '60');
      ctx.fillStyle = fdTheme.colors.purple;
      ctx.font = 'bold 12px "Consolas", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(p.name, p.x, sy + 5);
      if (p.default) {
        ctx.fillStyle = fdTheme.get('--text-muted');
        ctx.font = '10px sans-serif';
        ctx.fillText(`=${p.default}`, p.x + 10, sy + 20);
      }
    });

    // 实参区（右侧）
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📤 实参', width - 100, 90);

    // 绘制实参球
    scene.args.forEach((arg, i) => {
      if (stepIdx === 0) {
        // 初始状态：实参在右侧
        const ax = arg.x;
        const ay = arg.y;
        const radius = 14;
        ctx.fillStyle = arg.color;
        ctx.shadowColor = arg.color + '60';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(ax, ay, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        // 参数标签
        if (arg.label) {
          ctx.fillStyle = fdTheme.get('--text-secondary');
          ctx.font = '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(arg.label, ax, ay - 22);
        }
        // 值
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 11px "Consolas", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(arg.value, ax, ay + 4);
      } else if (stepIdx >= 1 && animProgress > 0) {
        // 飞行动画中或已完成
        const target = scene.params[arg.target];
        const startX = arg.x, startY = arg.y;
        const endX = target.x, endY = target.y;
        const progress = stepIdx >= 2 ? 1 : Math.min(animProgress, 1);
        const eased = fdEasing.bounceOut(progress);
        const ax = fdEasing.lerp(startX, endX, eased);
        const ay = fdEasing.lerp(startY, endY, eased) - 20 * Math.sin(eased * Math.PI) * (1 - eased);
        const radius = 14;
        ctx.fillStyle = arg.color;
        ctx.shadowColor = arg.color + '60';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(ax, ay, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 11px "Consolas", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(arg.value, ax, ay + 4);

        // 匹配完成时绿光
        if (progress >= 1) {
          ctx.strokeStyle = fdTheme.colors.green + '60';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.arc(ax, ay, radius + 8, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
    });

    // 匹配结果
    if (stepIdx >= 2) {
      ctx.fillStyle = scene.error ? fdTheme.colors.red + '20' : fdTheme.colors.green + '20';
      fdCanvas.roundRect(ctx, width / 2 - 150, 370, 300, 36, 8, ctx.fillStyle);
      ctx.fillStyle = scene.error ? fdTheme.colors.red : fdTheme.colors.green;
      ctx.font = 'bold 14px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(scene.resultLabel, width / 2, 393);
    }
  },
```

- [ ] **Step 4: 实现 ParamMatchDemo 控制方法**

```javascript
  stepNext() {
    if (this.state.stepIdx < 2) {
      this.state.stepIdx++;
      this.state.animProgress = 0;
      // 飞入动画
      if (this.state.stepIdx === 1) {
        this.state.animTimeline = fdEasing.Timeline(
          [{ start: 0, end: 1, onUpdate: (p) => { this.state.animProgress = p; this.render(); } }],
          800,
          () => {
            this.state.animProgress = 1;
            this.state.stepIdx = 2;
            this.render();
            this._updateUI();
          }
        );
      }
      this._updateUI();
    }
  },

  stepPrev() {
    if (this.state.stepIdx > 0) {
      this.state.stepIdx--;
      this.state.animProgress = 0;
      this.render();
      this._updateUI();
    }
  },

  play() {
    if (this.state.playing) {
      this.state.playing = false;
      if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
      this._updateUI();
      return;
    }
    this.state.playing = true;
    this._updateUI();
    this._autoAdvance();
  },

  _autoAdvance() {
    if (!this.state.playing) return;
    if (this.state.stepIdx >= 2) {
      // 循环回第一场景
      this.state.playing = false;
      this._updateUI();
      return;
    }
    this.stepNext();
    setTimeout(() => this._autoAdvance(), 1500);
  },

  reset() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    this.state.stepIdx = 0;
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },

  changeScene(idx) {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    this.state.sceneIdx = Math.min(idx, this.scenes.length - 1);
    this.state.stepIdx = 0;
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },

  _updateUI() {
    const scene = this.scenes[this.state.sceneIdx];
    document.getElementById('param-scene-title').textContent = scene.title;
    document.getElementById('param-play-btn').textContent = this.state.playing ? '⏸' : '▶';
  },
};
```

- [ ] **Step 5: 验证语法**

```bash
node -e "const fs=require('fs'); const code=fs.readFileSync('static/js/func_demos.js','utf8'); try { new Function(code); console.log('✅ 语法检查通过'); } catch(e) { console.error('❌', e.message); }"
```

---

### Task 3: 添加 HOFDemo 组件（高阶函数流水线）

**Files:**
- Modify: `static/js/func_demos.js` (append)

- [ ] **Step 1: 添加 HOFDemo 组件代码**

```javascript
// ============================================================
// 组件 3: 高阶函数流水线 — HOFDemo
// ============================================================
const HOFDemo = {
  tabs: ['map', 'filter', 'reduce'],
  tabLabels: { map: '🔄 Map 传送带', filter: '🔍 Filter 漏斗', reduce: '📉 Reduce 累加' },

  scenes: {
    map: {
      title: 'map — 批量转换',
      code: "map(lambda x: x*2, [1, 2, 3, 4, 5])",
      items: [1, 2, 3, 4, 5],
      transform: 'x → x*2',
      results: [2, 4, 6, 8, 10],
      color: '#00d4ff',
      description: '每个数字经过 lambda 自动 ×2，批量转换输出',
    },
    filter: {
      title: 'filter — 条件筛选',
      code: "filter(lambda x: x%2==0, [1, 2, 3, 4, 5, 6])",
      items: [1, 2, 3, 4, 5, 6],
      transform: 'x%2==0 ?',
      results: [2, 4, 6],
      color: '#3fb950',
      description: '符合条件的数字通过漏斗，不符合的从侧边淘汰',
    },
    reduce: {
      title: 'reduce — 累加聚合',
      code: "reduce(lambda a,b: a+b, [1, 2, 3, 4, 5])",
      items: [1, 2, 3, 4, 5],
      transform: 'a+b →',
      results: [15],
      color: '#a371f7',
      description: '数字从左到右两两合并，逐步收缩成单一值',
    },
  },

  state: {
    activeTab: 'map',
    playing: false,
    animProgress: 0,
    stepIdx: 0,
    animTimeline: null,
    canvas: null,
    ctx: null,
    width: 700,
    height: 450,
  },

  open() {
    this.state.activeTab = 'map';
    this.state.playing = false;
    this.state.animProgress = 0;
    this.state.stepIdx = 0;
    document.getElementById('func-modal-hof')?.classList.add('active');
    setTimeout(() => this._setupCanvas(), 100);
    this._updateUI();
  },

  close() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    document.getElementById('func-modal-hof')?.classList.remove('active');
  },

  _setupCanvas() {
    this.state.canvas = document.getElementById('hof-canvas');
    if (!this.state.canvas) return;
    const rect = this.state.canvas.parentElement.getBoundingClientRect();
    const w = Math.min(700, rect.width - 4);
    const h = 450;
    this.state.ctx = fdCanvas.setup(this.state.canvas, w, h);
    this.state.width = w;
    this.state.height = h;
    this.render();
  },

  render() {
    const { ctx, width, height, activeTab, animProgress } = this.state;
    if (!ctx) return;
    fdCanvas.clear(ctx, width, height);
    const scene = this.scenes[activeTab];

    // 背景
    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, width, height);

    // 顶部代码区
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, 0, width, 50);
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = '13px "Consolas", monospace';
    ctx.textAlign = 'left';
    ctx.fillText(scene.code, 16, 32);

    // 代码区分割线
    ctx.fillStyle = fdTheme.get('--border-subtle');
    ctx.fillRect(0, 50, width, 1);

    if (activeTab === 'map') {
      this._drawMapScene(ctx, width, height, scene, animProgress);
    } else if (activeTab === 'filter') {
      this._drawFilterScene(ctx, width, height, scene, animProgress);
    } else if (activeTab === 'reduce') {
      this._drawReduceScene(ctx, width, height, scene, animProgress);
    }

    // 底部描述
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, height - 40, width, 40);
    ctx.fillStyle = fdTheme.get('--text-secondary');
    ctx.font = '13px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('💡 ' + scene.description, width / 2, height - 14);
  },

  _drawMapScene(ctx, width, height, scene, t) {
    const cy = 200;
    const boxW = 36, boxH = 30;
    const startX = 60, endX = width - 80;
    const totalItems = scene.items.length;
    const spacing = (endX - startX) / (totalItems + 1);

    // 绘制 lambda 加工模块（中间）
    const modX = width / 2 - 60, modY = cy - 35, modW = 120, modH = 70;
    ctx.fillStyle = scene.color + '20';
    ctx.shadowColor = scene.color + '40';
    ctx.shadowBlur = 15;
    fdCanvas.roundRect(ctx, modX, modY, modW, modH, 8, ctx.fillStyle, scene.color + '80');
    ctx.shadowBlur = 0;
    ctx.fillStyle = scene.color;
    ctx.font = 'bold 13px "Consolas", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('λ', modX + modW / 2, modY + 20);
    ctx.font = '11px sans-serif';
    ctx.fillText(scene.transform, modX + modW / 2, modY + 48);

    // 处理进度
    const processedCount = t * totalItems;

    for (let i = 0; i < totalItems; i++) {
      const isProcessed = i < processedCount;
      const x = startX + (i + 1) * spacing;

      if (isProcessed) {
        // 已处理 — 在右侧显示结果
        const outX = modX + modW + 30 + (i - Math.floor(processedCount - 1)) * (spacing - 10);
        if (outX < width - 40) {
          ctx.fillStyle = scene.color + '40';
          fdCanvas.roundRect(ctx, outX - boxW / 2, cy - boxH / 2, boxW, boxH, 4, ctx.fillStyle);
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 13px "Consolas", monospace';
          ctx.textAlign = 'center';
          ctx.fillText(String(scene.results[i]), outX, cy + 5);
          // 连接线
          ctx.strokeStyle = scene.color + '40';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(modX + modW, cy);
          ctx.lineTo(outX - boxW / 2, cy);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      } else {
        // 未处理 — 在左侧显示
        const inX = x;
        ctx.fillStyle = fdTheme.get('--text-secondary');
        fdCanvas.roundRect(ctx, inX - boxW / 2, cy - boxH / 2, boxW, boxH, 4, ctx.fillStyle, fdTheme.get('--border-subtle'));
        ctx.fillStyle = fdTheme.get('--text-primary');
        ctx.font = 'bold 13px "Consolas", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(String(scene.items[i]), inX, cy + 5);
        // 输入箭头
        ctx.strokeStyle = fdTheme.get('--text-muted');
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(inX + boxW / 2, cy);
        ctx.lineTo(modX, cy);
        ctx.stroke();
        fdCanvas.arrow(ctx, inX + boxW / 2, cy, modX, cy, fdTheme.get('--text-muted'), 1.5);
      }
    }

    // 标签
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('输入', startX + (modX - startX) / 2, height - 90);
    ctx.fillText('输出', modX + modW + (width - 40 - modX - modW) / 2, height - 90);
  },

  _drawFilterScene(ctx, width, height, scene, t) {
    const funnelX = width / 2 - 30, funnelTopY = 80, funnelBottomY = 260;
    const totalItems = scene.items.length;
    const processedCount = t * totalItems;

    // 漏斗图形
    ctx.fillStyle = scene.color + '15';
    ctx.beginPath();
    ctx.moveTo(funnelX - 50, funnelTopY);
    ctx.lineTo(funnelX + 50, funnelTopY);
    ctx.lineTo(funnelX + 35, funnelBottomY);
    ctx.lineTo(funnelX - 35, funnelBottomY);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = scene.color + '40';
    ctx.lineWidth = 2;
    ctx.stroke();

    // 漏斗标签
    ctx.fillStyle = scene.color;
    ctx.font = '13px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('🔍 filter: ' + scene.transform, width / 2, funnelTopY + 55);

    // 元素动画
    for (let i = 0; i < totalItems; i++) {
      const item = scene.items[i];
      const startX = 60 + i * ((width - 120) / (totalItems - 1));
      const isFiltered = scene.results.includes(item);
      const isProcessed = i < processedCount;

      if (isProcessed) {
        if (isFiltered) {
          // 通过 — 从漏斗底部流出
          const outY = funnelBottomY + 20 + i * 5;
          ctx.fillStyle = scene.color + '40';
          fdCanvas.roundRect(ctx, funnelX - 14, outY, 28, 24, 4, ctx.fillStyle);
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 12px "Consolas"';
          ctx.textAlign = 'center';
          ctx.fillText(String(item), funnelX, outY + 16);
          // 路径
          ctx.strokeStyle = scene.color + '30';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(startX, 90);
          ctx.lineTo(funnelX, funnelBottomY);
          ctx.lineTo(funnelX, outY);
          ctx.stroke();
        } else {
          // 淘汰 — 从侧面出去
          const sideX = i % 2 === 0 ? 30 : width - 30;
          ctx.fillStyle = fdTheme.colors.red + '40';
          ctx.beginPath();
          ctx.arc(sideX, 90 + i * 20, 10, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = '#fff';
          ctx.font = '10px "Consolas"';
          ctx.textAlign = 'center';
          ctx.fillText('✗', sideX, 95 + i * 20);
          // 路径
          ctx.strokeStyle = fdTheme.colors.red + '20';
          ctx.lineWidth = 1;
          ctx.setLineDash([3, 3]);
          ctx.beginPath();
          ctx.moveTo(startX, 90);
          ctx.lineTo(sideX, 90 + i * 20);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      } else {
        // 未处理 — 顶部排队
        ctx.fillStyle = fdTheme.get('--text-secondary');
        ctx.beginPath();
        ctx.arc(startX, 90, 16, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px "Consolas"';
        ctx.textAlign = 'center';
        ctx.fillText(String(item), startX, 95);
      }
    }
  },

  _drawReduceScene(ctx, width, height, scene, t) {
    const values = [...scene.items];
    const totalSteps = values.length - 1;
    const steps = [];
    let current = [...values];
    for (let i = 0; i < totalSteps; i++) {
      const newVal = current[0] + current[1];
      current = [newVal, ...current.slice(2)];
      steps.push({ before: [...current], merged: newVal, left: current[0], rest: current.slice(1) });
    }

    const currentStep = Math.min(Math.floor(t * totalSteps), totalSteps - 1);
    const stepProgress = (t * totalSteps) - currentStep;

    // 显示初始数组
    const boxW = 36, boxH = 30;
    const startX = 60;
    const spacing = 50;
    const cy = 150;

    // 标题
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = 'bold 13px "Consolas", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('初始: ' + values.join(' + '), width / 2, 90);

    if (t === 0) {
      // 初始状态：所有数字
      values.forEach((v, i) => {
        const x = startX + i * spacing;
        ctx.fillStyle = scene.color + '30';
        fdCanvas.roundRect(ctx, x - boxW / 2, cy - boxH / 2, boxW, boxH, 4, ctx.fillStyle);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px "Consolas"';
        ctx.textAlign = 'center';
        ctx.fillText(String(v), x, cy + 5);
      });
      return;
    }

    // 画步骤
    const progressStep = Math.min(currentStep + 1, totalSteps);
    const remaining = [steps[progressStep - 1]?.left || values[0]];

    // 已合并的项
    let xPos = startX;
    for (let i = 0; i < progressStep; i++) {
      const step = steps[i];
      // 括号/合并标记
      const pairX = startX + i * spacing;
      ctx.strokeStyle = scene.color + '60';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(pairX + spacing / 2, cy + boxH / 2 + 10, 10, 0, Math.PI);
      ctx.stroke();
      ctx.fillStyle = scene.color;
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${values[i]}+${values[i+1]}`, pairX + spacing / 2, cy + boxH / 2 + 35);
      // 合并结果
      if (i === currentStep && stepProgress < 1) {
        // 正在合并中 — 动画
        const mergeProgress = fdEasing.bounceOut(stepProgress);
        const mx = pairX + spacing / 2;
        const my = cy - 30 - 40 * (1 - mergeProgress);
        ctx.fillStyle = scene.color + '50';
        ctx.beginPath();
        ctx.arc(mx, my, 16 * (0.5 + 0.5 * mergeProgress), 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px "Consolas"';
        ctx.textAlign = 'center';
        ctx.fillText(String(step.merged), mx, my + 4);
        // 从下方上来的箭头
        ctx.strokeStyle = scene.color + '40';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(pairX + spacing / 2, cy + boxH / 2 + 15);
        ctx.lineTo(mx, my + 16);
        ctx.stroke();
      } else if (i < currentStep || (i === currentStep && stepProgress >= 1)) {
        // 已合并完成
        xPos = startX + (i + 1) * spacing - boxW;
        const mx = xPos;
        ctx.fillStyle = scene.color + '40';
        fdCanvas.roundRect(ctx, mx - boxW / 2, cy - boxH / 2 - 40, boxW, boxH, 4, ctx.fillStyle);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px "Consolas"';
        ctx.textAlign = 'center';
        ctx.fillText(String(step.merged), mx, cy + 5 - 40);
      }
    }

    // 最终结果
    if (t >= 1) {
      const finalVal = scene.results[0];
      ctx.fillStyle = '#ffd70040';
      ctx.shadowColor = '#ffd70060';
      ctx.shadowBlur = 20;
      const fx = width / 2;
      fdCanvas.roundRect(ctx, fx - 30, cy + 100, 60, 36, 8, ctx.fillStyle);
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#ffd700';
      ctx.font = 'bold 18px "Consolas", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`= ${finalVal}`, fx, cy + 123);
      ctx.fillStyle = fdTheme.get('--text-secondary');
      ctx.font = '12px sans-serif';
      ctx.fillText('最终结果', fx, cy + 165);
    }
  },
```

- [ ] **Step 2: 添加 HOFDemo 控制方法**

```javascript
  setTab(tab) {
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    this.state.activeTab = tab;
    this.state.playing = false;
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },

  play() {
    if (this.state.playing) {
      this.state.playing = false;
      if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
      this._updateUI();
      return;
    }
    this.state.playing = true;
    this.state.animProgress = 0;
    this._updateUI();

    this.state.animTimeline = fdEasing.Timeline(
      [{ start: 0, end: 1, onUpdate: (p) => { this.state.animProgress = p; this.render(); } }],
      3000,
      () => {
        this.state.playing = false;
        this.state.animProgress = 1;
        this.render();
        this._updateUI();
      }
    );
  },

  reset() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    this.state.animProgress = 0;
    this.render();
    this._updateUI();
  },

  _updateUI() {
    const tab = this.state.activeTab;
    document.getElementById('hof-play-btn').textContent = this.state.playing ? '⏸' : '▶';
    // 更新标签按钮状态
    document.querySelectorAll('.hof-tab-btn').forEach(btn => {
      const isActive = btn.dataset.tab === tab;
      btn.style.opacity = isActive ? '1' : '0.5';
      btn.style.borderColor = isActive ? 'var(--cyan)' : 'var(--border-subtle)';
    });
  },
};
```

- [ ] **Step 3: 验证语法**

```bash
node -e "const fs=require('fs'); const code=fs.readFileSync('static/js/func_demos.js','utf8'); try { new Function(code); console.log('✅ 语法检查通过'); } catch(e) { console.error('❌', e.message); }"
```

---

### Task 4: 修改 chapter.html — 新增弹窗和按钮

**Files:**
- Modify: `templates/chapter.html`

- [ ] **Step 1: 在 KP0 按钮区添加栈帧演示按钮**

```html
<!-- 在现有 FuncPuzzle 按钮旁 -->
<button class="btn-interactive" onclick="FuncPuzzle.open()" style="...">🧩 函数结构拼图</button>
<button class="btn-interactive" onclick="StackFrameDemo.open()" style="background:var(--cyan-dim);color:var(--cyan);border:1px solid var(--cyan);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;transition:all 0.2s;">🎬 栈帧演示</button>
```

- [ ] **Step 2: 在 KP1/KP2 按钮区添加参数匹配按钮**

```html
<!-- 修改现有行，在 ParamCanvas 按钮旁 -->
<button class="btn-interactive" onclick="ParamCanvas.open()" style="...">🔬 参数传递显微镜</button>
<button class="btn-interactive" onclick="ParamMatchDemo.open()" style="background:var(--green-dim);color:var(--green);border:1px solid var(--green);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;transition:all 0.2s;">🎯 参数匹配演示</button>
```

- [ ] **Step 3: 在 KP4 按钮区添加高阶函数流水线按钮**

```html
{% elif kp_loop_idx == 4 %}
<button class="btn-interactive" onclick="HOFDemo.open()" style="background:var(--orange-dim);color:var(--orange);border:1px solid var(--orange);padding:6px 14px;border-radius:6px;cursor:pointer;font-size:13px;transition:all 0.2s;">🔄 高阶函数流水线</button>
```

- [ ] **Step 4: 在弹窗区末尾（</body> 前）添加 3 个弹窗**

```html
<!-- StackFrameDemo Modal -->
<div class="fd-modal-overlay" id="func-modal-stack">
  <div class="fd-modal-box fd-modal-box-wide">
    <div class="fd-modal-header">
      <h3>🎬 栈帧演示 — <span id="stack-scene-title">两数相加</span></h3>
      <button class="fd-modal-close" onclick="StackFrameDemo.close()">✕</button>
    </div>
    <div style="position:relative;">
      <canvas id="stack-canvas" style="width:100%;height:450px;display:block;"></canvas>
      <div class="fd-demo-controls">
        <select id="stack-scene-select" class="fd-scene-select" onchange="StackFrameDemo.changeScene(parseInt(this.value))">
          <option value="0">两数相加</option>
          <option value="1">嵌套调用</option>
          <option value="2">递归阶乘</option>
        </select>
        <div class="fd-control-group">
          <button id="stack-play-btn" class="fd-ctrl-btn" onclick="StackFrameDemo.play()">▶</button>
          <button class="fd-ctrl-btn" onclick="StackFrameDemo.reset()">⏹</button>
          <button class="fd-ctrl-btn" onclick="StackFrameDemo.stepPrev()">◀</button>
          <button class="fd-ctrl-btn" onclick="StackFrameDemo.stepNext()">▶</button>
          <span id="stack-step-info" class="fd-step-info">步骤 1/5</span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ParamMatchDemo Modal -->
<div class="fd-modal-overlay" id="func-modal-param-demo">
  <div class="fd-modal-box fd-modal-box-wide">
    <div class="fd-modal-header">
      <h3>🎯 参数匹配演示 — <span id="param-scene-title">位置参数</span></h3>
      <button class="fd-modal-close" onclick="ParamMatchDemo.close()">✕</button>
    </div>
    <div style="position:relative;">
      <canvas id="param-demo-canvas" style="width:100%;height:450px;display:block;"></canvas>
      <div class="fd-demo-controls">
        <select id="param-scene-select" class="fd-scene-select" onchange="ParamMatchDemo.changeScene(parseInt(this.value))">
          <option value="0">位置参数</option>
          <option value="1">默认参数</option>
          <option value="2">关键字参数</option>
          <option value="3">*args 可变位置</option>
          <option value="4">**kwargs 可变关键字</option>
        </select>
        <div class="fd-control-group">
          <button id="param-play-btn" class="fd-ctrl-btn" onclick="ParamMatchDemo.play()">▶</button>
          <button class="fd-ctrl-btn" onclick="ParamMatchDemo.reset()">⏹</button>
          <button class="fd-ctrl-btn" onclick="ParamMatchDemo.stepPrev()">◀</button>
          <button class="fd-ctrl-btn" onclick="ParamMatchDemo.stepNext()">▶</button>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- HOFDemo Modal -->
<div class="fd-modal-overlay" id="func-modal-hof">
  <div class="fd-modal-box fd-modal-box-wide">
    <div class="fd-modal-header">
      <h3>🔄 高阶函数流水线</h3>
      <button class="fd-modal-close" onclick="HOFDemo.close()">✕</button>
    </div>
    <div style="position:relative;">
      <!-- 标签切换 -->
      <div class="hof-tabs">
        <button class="hof-tab-btn" data-tab="map" onclick="HOFDemo.setTab('map')">🔄 Map 传送带</button>
        <button class="hof-tab-btn" data-tab="filter" onclick="HOFDemo.setTab('filter')">🔍 Filter 漏斗</button>
        <button class="hof-tab-btn" data-tab="reduce" onclick="HOFDemo.setTab('reduce')">📉 Reduce 累加</button>
      </div>
      <canvas id="hof-canvas" style="width:100%;height:450px;display:block;"></canvas>
      <div class="fd-demo-controls">
        <div class="fd-control-group">
          <button id="hof-play-btn" class="fd-ctrl-btn" onclick="HOFDemo.play()">▶</button>
          <button class="fd-ctrl-btn" onclick="HOFDemo.reset()">⏹</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 5: 在 chapter.html `<head>` 中添加 `<script src>` 引用 func_demos.js**

```html
<script src="{{ url_for('static', filename='js/func_interactive.js') }}"></script>
<script src="{{ url_for('static', filename='js/func_demos.js') }}"></script>  <!-- 新增这行 -->
```

---

### Task 5: 修改 style.css — 新增控制栏样式

**Files:**
- Modify: `static/css/style.css`

- [ ] **Step 1: 在 fd-modal 样式区追加宽版弹窗、控制栏、标签页样式**

```css
/* Wide modal box for demo animations */
.fd-modal-box-wide {
  max-width: 760px;
}

/* Demo Controls Bar */
.fd-demo-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  gap: 12px;
  flex-shrink: 0;
}

.fd-scene-select {
  padding: 4px 10px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
  max-width: 160px;
}

.fd-control-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fd-ctrl-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-primary);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.fd-ctrl-btn:hover {
  border-color: var(--cyan);
  color: var(--cyan);
  background: rgba(0, 212, 255, 0.1);
}

.fd-step-info {
  font-size: 12px;
  color: var(--text-muted);
  margin-left: 8px;
  white-space: nowrap;
}

/* HOF Tab Buttons */
.hof-tabs {
  display: flex;
  gap: 0;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.hof-tab-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.hof-tab-btn:hover {
  color: var(--text-primary);
  background: rgba(0, 212, 255, 0.05);
}

.hof-tab-btn[data-tab="map"] { border-bottom-color: var(--cyan); }
.hof-tab-btn[data-tab="filter"] { border-bottom-color: var(--green); }
.hof-tab-btn[data-tab="reduce"] { border-bottom-color: var(--purple); }
```

- [ ] **Step 2: 验证 CSS 无冲突**

```bash
grep -n "fd-demo-controls\|hof-tabs\|fd-modal-box-wide" static/css/style.css | head -10
```

---

### Task 6: 整合测试

- [ ] **Step 1: 启动服务器**

```bash
python app.py
```

- [ ] **Step 2: 打开浏览器访问 http://127.0.0.1:5000**
  - 登录后进入第 8 章
  - 验证 KP0 出现 "🎬 栈帧演示" 按钮
  - 验证 KP1/KP2 出现 "🎯 参数匹配演示" 按钮
  - 验证 KP4 出现 "🔄 高阶函数流水线" 按钮

- [ ] **Step 3: 测试栈帧演示**
  - 点击按钮 → 弹窗出现
  - Canvas 正常渲染，显示代码区 + 三栏分区
  - 点击 ▶ 自动播放，步骤自动推进
  - 点击 ◀▶ 手动步进
  - 切换场景（嵌套调用/递归），数据正确更新
  - 点击 ✕ 关闭弹窗，动画清理

- [ ] **Step 4: 测试参数匹配演示**
  - 5 个场景全部可切换
  - 实参小球飞入动画流畅（bounceOut 缓动）
  - 匹配完成显示绿色 ✓ 和结果文字

- [ ] **Step 5: 测试高阶函数流水线**
  - 3 个标签页（Map/Filter/Reduce）可切换
  - 每个标签播放动画正常
  - Map：数字经过 lambda 转换
  - Filter：通过/淘汰路径正确
  - Reduce：数字逐步合并到最终值

- [ ] **Step 6: 验证深色/浅色主题兼容**
  - 切换主题 → fdTheme 自动刷新颜色
  - Canvas 文字可读，颜色适配

