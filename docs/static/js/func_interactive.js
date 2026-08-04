/**
 * func_interactive.js — 函数章节 Canvas 驱动互动可视化组件
 * 参考 mathviz 设计理念：Canvas 2D + 教学叙事 + 实时交互
 * 精简为 5 个高质量组件，每个聚焦一个核心概念
 */

// ============================================================
// 主题适配器 — 从 CSS 变量读取颜色，支持深色/浅色主题
// ============================================================
const fdTheme = {
  _cache: {},
  _timer: null,

  get(v) {
    if (fdTheme._cache[v]) return fdTheme._cache[v];
    const val = getComputedStyle(document.documentElement).getPropertyValue(v).trim();
    if (val) fdTheme._cache[v] = val;
    return val || '#ffffff';
  },

  colors: {
    cyan: '#00d4ff', purple: '#a371f7', green: '#3fb950',
    orange: '#d29922', red: '#f85149',
  },

  // Refresh cache (call on theme toggle)
  refresh() {
    fdTheme._cache = {};
    fdTheme.colors.cyan = fdTheme.get('--cyan');
    fdTheme.colors.purple = fdTheme.get('--purple');
    fdTheme.colors.green = fdTheme.get('--green');
    fdTheme.colors.orange = fdTheme.get('--orange');
    fdTheme.colors.red = fdTheme.get('--red');
  }
};

// Initial theme read
fdTheme.refresh();

// ============================================================
// Canvas 工具函数
// ============================================================
const fdCanvas = {
  // Setup canvas with device pixel ratio
  setup(canvas, width, height) {
    if (!canvas) return null;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = (width || rect.width) * dpr;
    canvas.height = (height || rect.height) * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    return ctx;
  },

  // Clear canvas
  clear(ctx, w, h) {
    if (!ctx) return;
    ctx.clearRect(0, 0, w, h);
  },

  // Draw rounded rect
  roundRect(ctx, x, y, w, h, r, fill, stroke) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = 1.5; ctx.stroke(); }
  },

  // Draw arrow line
  arrow(ctx, x1, y1, x2, y2, color, lineW) {
    const angle = Math.atan2(y2 - y1, x2 - x1);
    ctx.save();
    ctx.strokeStyle = color; ctx.fillStyle = color;
    ctx.lineWidth = lineW || 2;
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
    // Arrowhead
    const headLen = 10;
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLen * Math.cos(angle - 0.4), y2 - headLen * Math.sin(angle - 0.4));
    ctx.lineTo(x2 - headLen * Math.cos(angle + 0.4), y2 - headLen * Math.sin(angle + 0.4));
    ctx.closePath(); ctx.fill();
    ctx.restore();
  },

  // Draw text with optional background
  text(ctx, text, x, y, color, size, align, bg) {
    ctx.save();
    if (bg) {
      const m = ctx.measureText(text);
      const pad = 4;
      ctx.fillStyle = bg;
      ctx.fillRect(x - m.width / 2 - pad, y - size - pad, m.width + pad * 2, size + pad * 2);
    }
    ctx.fillStyle = color || fdTheme.get('--text-primary');
    ctx.font = `${size || 14}px "Microsoft YaHei", sans-serif`;
    ctx.textAlign = align || 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(text, x, y);
    ctx.restore();
  },

  // Animate value over time
  lerp(from, to, t) { return from + (to - from) * Math.min(t, 1); },
};

// ============================================================
// 组件 1: 函数结构拼图 (KP0)
// 拖拽式拼图游戏 — 每次打开顺序随机，拼出正确的函数结构
// ============================================================
const FuncPuzzle = {
  levels: [
    {
      title: '🌱 初识函数',
      desc: '组装一个最简单的问候函数',
      pieces: [
        { id: 0, text: 'def', hint: '函数定义从这里开始', color: '#a371f7', role: '关键字' },
        { id: 1, text: 'greet():', hint: '函数名 + 冒号', color: '#00d4ff', role: '函数头' },
        { id: 2, text: '    print("你好！")', hint: '函数体：缩进的代码块', color: '#3fb950', role: '函数体' },
      ],
      correctOrder: [0, 1, 2],
    },
    {
      title: '📦 带参数的函数',
      desc: '组装一个带参数的加倍函数',
      pieces: [
        { id: 0, text: 'def', hint: 'def 关键字', color: '#a371f7', role: '关键字' },
        { id: 1, text: 'double(x):', hint: '函数名(参数)', color: '#00d4ff', role: '函数头' },
        { id: 2, text: '    result = x * 2', hint: '计算倍数', color: '#3fb950', role: '函数体' },
        { id: 3, text: '    return result', hint: '返回计算结果', color: '#d29922', role: '返回值' },
      ],
      correctOrder: [0, 1, 2, 3],
    },
    {
      title: '🔢 多参数函数',
      desc: '组装一个两数相加的函数',
      pieces: [
        { id: 0, text: 'def', hint: 'def 起手', color: '#a371f7', role: '关键字' },
        { id: 1, text: 'add(a, b):', hint: '两个参数', color: '#00d4ff', role: '函数头' },
        { id: 2, text: '    """返回两数之和"""', hint: '文档字符串', color: '#f85149', role: '文档' },
        { id: 3, text: '    return a + b', hint: '加法运算并返回', color: '#d29922', role: '返回值' },
      ],
      correctOrder: [0, 1, 2, 3],
    },
    {
      title: '📝 带条件判断',
      desc: '组装一个判断奇偶的函数',
      pieces: [
        { id: 0, text: 'def', hint: 'def 关键字', color: '#a371f7', role: '关键字' },
        { id: 1, text: 'is_even(n):', hint: '函数名(参数)', color: '#00d4ff', role: '函数头' },
        { id: 2, text: '    if n % 2 == 0:', hint: '条件判断', color: '#3fb950', role: '条件' },
        { id: 3, text: '        return True', hint: '偶数返回 True', color: '#d29922', role: '返回值' },
        { id: 4, text: '    else:', hint: '否则分支', color: '#3fb950', role: '分支' },
        { id: 5, text: '        return False', hint: '奇数返回 False', color: '#d29922', role: '返回值' },
      ],
      correctOrder: [0, 1, 2, 3, 4, 5],
    },
    {
      title: '🏆 完整函数',
      desc: '组装一个带文档和类型提示的完整函数',
      pieces: [
        { id: 0, text: 'def', hint: 'def 关键字', color: '#a371f7', role: '关键字' },
        { id: 1, text: 'calculate_bmi(', hint: '函数名开始...', color: '#00d4ff', role: '函数头' },
        { id: 2, text: 'weight: float,', hint: '参数1：体重', color: '#ff7b72', role: '参数' },
        { id: 3, text: 'height: float', hint: '参数2：身高', color: '#ff7b72', role: '参数' },
        { id: 4, text: ') -> str:', hint: '返回值类型提示 + 冒号', color: '#00d4ff', role: '函数头' },
        { id: 5, text: '    """计算BMI并返回评估结果"""', hint: '文档字符串', color: '#f85149', role: '文档' },
        { id: 6, text: '    bmi = weight / (height ** 2)', hint: 'BMI 计算公式', color: '#3fb950', role: '计算' },
        { id: 7, text: '    return f"BMI: {bmi:.1f}"', hint: '格式化返回', color: '#d29922', role: '返回值' },
      ],
      correctOrder: [0, 1, 2, 3, 4, 5, 6, 7],
    },
  ],

  state: { levelIdx: 0, shuffled: [], placed: [], score: 0, timer: 0, timerInterval: null, completed: false },

  open() {
    this.state.levelIdx = 0;
    this.state.score = 0;
    this.state.placed = [];
    this.state.completed = false;
    this.shuffle();
    document.getElementById('func-modal-puzzle')?.classList.add('active');
    setTimeout(() => this.render(), 50);
  },

  close() {
    if (this.state.timerInterval) clearInterval(this.state.timerInterval);
    document.getElementById('func-modal-puzzle')?.classList.remove('active');
  },

  shuffle() {
    const level = this.levels[this.state.levelIdx];
    const idxs = level.correctOrder.map(i => i);
    // Fisher-Yates shuffle — guaranteed random
    for (let i = idxs.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [idxs[i], idxs[j]] = [idxs[j], idxs[i]];
    }
    this.state.shuffled = idxs;
    this.state.placed = [];
    this.state.completed = false;
    if (this.state.timerInterval) clearInterval(this.state.timerInterval);
    this.state.timer = 0;
  },

  selectLevel(idx) {
    this.state.levelIdx = idx;
    this.state.placed = [];
    this.state.completed = false;
    this.shuffle();
    this.render();
  },

  clickPiece(pieceId) {
    if (this.state.completed) return;
    const level = this.levels[this.state.levelIdx];
    // If this piece is already placed, remove it
    const placedIdx = this.state.placed.indexOf(pieceId);
    if (placedIdx !== -1) {
      this.state.placed.splice(placedIdx, 1);
      this.render();
      return;
    }
    // If piece is in shuffled pool, place it
    if (this.state.shuffled.includes(pieceId) && !this.state.placed.includes(pieceId)) {
      this.state.placed.push(pieceId);
      // Start timer on first placement
      if (this.state.placed.length === 1 && !this.state.timerInterval) {
        this.state.timerInterval = setInterval(() => {
          this.state.timer++;
          // Update timer display without full re-render
          const el = document.getElementById('func-puzzle-timer');
          if (el) el.textContent = '⏱ ' + this.state.timer + 's';
        }, 1000);
      }
      this.render();
      // Check if all placed
      if (this.state.placed.length === level.correctOrder.length) {
        this.checkAnswer();
      }
    }
  },

  clickPlacedSlot(idx) {
    if (this.state.completed) return;
    const pieceId = this.state.placed[idx];
    this.state.placed.splice(idx, 1);
    this.render();
  },

  checkAnswer() {
    const level = this.levels[this.state.levelIdx];
    const isCorrect = this.state.placed.every((id, i) => id === level.correctOrder[i]);
    if (isCorrect) {
      this.state.completed = true;
      if (this.state.timerInterval) {
        clearInterval(this.state.timerInterval);
        this.state.timerInterval = null;
      }
      this.state.score += Math.max(100 - this.state.timer * 2, 10);
      this.render();
      // Trigger confetti-like animation
      this.celebrate();
    } else {
      // Shake and reset
      this.render(true);
      setTimeout(() => {
        // Remove wrong pieces (keep matching prefix)
        let correctCount = 0;
        for (let i = 0; i < this.state.placed.length; i++) {
          if (this.state.placed[i] === level.correctOrder[i]) {
            correctCount++;
          } else {
            break;
          }
        }
        // Keep only matching prefix, remove rest
        this.state.placed = this.state.placed.slice(0, correctCount);
        this.render();
      }, 600);
    }
  },

  celebrate() {
    // Create confetti effect
    const container = document.querySelector('#func-modal-puzzle .fd-modal-box');
    if (!container) return;
    const colors = ['#a371f7', '#00d4ff', '#3fb950', '#d29922', '#f85149', '#ffd700'];
    for (let i = 0; i < 30; i++) {
      const confetti = document.createElement('div');
      confetti.style.cssText = `
        position:fixed; width:${6 + Math.random() * 6}px; height:${6 + Math.random() * 6}px;
        background:${colors[Math.floor(Math.random() * colors.length)]};
        border-radius:${Math.random() > 0.5 ? '50%' : '2px'};
        pointer-events:none; z-index:10000;
        left:${40 + Math.random() * 20}%; top:30%;
        opacity:1;
        transition:all ${1.0 + Math.random() * 0.5}s ease-out;
      `;
      document.body.appendChild(confetti);
      requestAnimationFrame(() => {
        confetti.style.transform = `translate(${(Math.random() - 0.5) * 400}px, ${200 + Math.random() * 300}px) rotate(${Math.random() * 720}deg)`;
        confetti.style.opacity = '0';
      });
      setTimeout(() => confetti.remove(), 2000);
    }
  },

  render(isWrong) {
    const panel = document.getElementById('puzzle-panel');
    if (!panel) return;
    const level = this.levels[this.state.levelIdx];
    const totalLevels = this.levels.length;

    // Build shuffled card pool (excluding placed ones)
    const available = this.state.shuffled.filter(id => !this.state.placed.includes(id));

    panel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:6px;">
        <div style="display:flex;gap:4px;flex-wrap:wrap;">
          ${this.levels.map((l, i) =>
            `<button class="fd-scene-btn ${i === this.state.levelIdx ? 'active' : ''}" onclick="FuncPuzzle.selectLevel(${i})">${l.title.replace(/^[^\s]+\s/, '')}</button>`
          ).join('')}
        </div>
        <div style="display:flex;align-items:center;gap:12px;font-size:12px;">
          <span id="func-puzzle-timer" style="color:var(--text-muted);">⏱ ${this.state.timer}s</span>
          <span style="color:var(--cyan);">⭐ ${Math.round(this.state.score)}</span>
          <span style="color:var(--text-muted);">${this.state.levelIdx + 1}/${totalLevels}</span>
        </div>
      </div>

      <div style="margin-bottom:6px;padding:4px 10px;background:var(--bg-deep);border-radius:6px;font-size:13px;color:var(--text-secondary);">
        🎯 ${level.desc}
      </div>

      <!-- Target slots -->
      <div class="puzzle-slots" style="display:flex;flex-wrap:wrap;gap:4px;min-height:54px;padding:8px;background:var(--bg-deep);border-radius:8px;margin-bottom:8px;border:1px dashed var(--border-subtle);">
        ${level.correctOrder.map((cid, i) => {
          const placed = this.state.placed[i];
          const pc = placed !== undefined ? level.pieces[placed] : null;
          const isCorrectPos = pc && i < level.correctOrder.length && placed === level.correctOrder[i];
          const isWrongPos = pc && !isCorrectPos;
          return `<div class="puzzle-slot ${pc ? 'filled' : 'empty'} ${isWrong && isWrongPos ? 'shake' : ''} ${isCorrectPos ? 'correct' : ''}"
                    onclick="FuncPuzzle.clickPlacedSlot(${i})"
                    style="flex:1;min-width:80px;min-height:42px;border:2px solid ${pc ? pc.color : 'var(--border-subtle)'};border-radius:6px;display:flex;align-items:center;justify-content:center;padding:4px 8px;cursor:${pc ? 'pointer' : 'default'};font-size:12px;font-family:var(--font-mono,monospace);background:${pc ? pc.color + '18' : 'transparent'};transition:all 0.3s;position:relative;">
            ${pc ? `<span style="color:var(--text-primary);font-weight:500;">${FuncPuzzle.escapeHtml(pc.text)}</span>
                    <span style="position:absolute;top:-8px;right:-4px;font-size:9px;color:var(--text-muted);">${pc.role}</span>`
               : `<span style="color:var(--text-muted);font-size:11px;">⬇ 第 ${i + 1} 块</span>`}
          </div>`;
        }).join('')}
      </div>

      <!-- Card pool -->
      <div style="margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:11px;color:var(--text-muted);">🧩 点击积木放入拼图槽（点击槽位可撤回）</span>
        <button class="fd-btn" onclick="FuncPuzzle.shuffle();FuncPuzzle.render();" style="font-size:11px;">🔀 重新打乱</button>
      </div>
      <div class="puzzle-pool" style="display:flex;flex-wrap:wrap;gap:4px;padding:8px;background:var(--bg-card);border-radius:8px;border:1px solid var(--border-subtle);min-height:48px;">
        ${available.length === 0
          ? '<span style="color:var(--text-muted);font-size:12px;padding:8px;">所有积木已放入拼图槽</span>'
          : available.map(id => {
              const p = level.pieces[id];
              return `<div class="puzzle-card" onclick="FuncPuzzle.clickPiece(${id})"
                        style="padding:6px 14px;border:2px solid ${p.color};border-radius:6px;cursor:pointer;font-size:12px;font-family:var(--font-mono,monospace);background:${p.color}22;color:var(--text-primary);transition:all 0.2s;white-space:nowrap;user-select:none;"
                        title="${p.hint}"
                        onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 4px 12px ${p.color}44'"
                        onmouseleave="this.style.transform='';this.style.boxShadow=''">
                ${FuncPuzzle.escapeHtml(p.text)}
              </div>`;
            }).join('')}
      </div>

      ${this.state.completed ? `
        <div style="margin-top:10px;padding:12px 16px;background:var(--green-dim);border-radius:8px;text-align:center;">
          <div style="font-size:20px;font-weight:700;color:var(--green);margin-bottom:4px;">🎉 拼图完成！</div>
          <div style="font-size:13px;color:var(--text-secondary);">得分: +${Math.max(100 - this.state.timer * 2, 10)} 分 ⭐ 用时 ${this.state.timer} 秒</div>
          <div style="margin-top:8px;display:flex;gap:8px;justify-content:center;">
            ${this.state.levelIdx < totalLevels - 1
              ? `<button class="fd-btn primary" onclick="FuncPuzzle.nextLevel()">▶ 下一关</button>`
              : `<button class="fd-btn primary" onclick="FuncPuzzle.showFinal()">🏆 查看成绩</button>`}
            <button class="fd-btn" onclick="FuncPuzzle.selectLevel(${this.state.levelIdx})">🔄 重新挑战</button>
          </div>
        </div>
      ` : ''}
    `;
  },

  nextLevel() {
    if (this.state.levelIdx < this.levels.length - 1) {
      this.state.levelIdx++;
      this.state.placed = [];
      this.state.completed = false;
      this.shuffle();
      this.render();
    }
  },

  showFinal() {
    const panel = document.getElementById('puzzle-panel');
    if (!panel) return;
    panel.innerHTML = `
      <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:48px;margin-bottom:12px;">🏆</div>
        <div style="font-size:22px;font-weight:700;color:var(--cyan);margin-bottom:8px;">恭喜通关！</div>
        <div style="font-size:14px;color:var(--text-secondary);margin-bottom:16px;">
          你已完成全部 5 关函数结构拼图
        </div>
        <div style="font-size:36px;font-weight:700;color:var(--purple);margin-bottom:20px;">⭐ ${Math.round(this.state.score)} 分</div>
        <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
          <button class="fd-btn primary" onclick="FuncPuzzle.selectLevel(0)">🔄 重新开始</button>
          <button class="fd-btn" onclick="FuncPuzzle.close()">✓ 完成</button>
        </div>
      </div>
    `;
  },

  escapeHtml(text) {
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
};

// ============================================================
// 组件 2: 参数传递显微镜 (KP1-2)
// Canvas 参数匹配动画 — 匹配游戏 + 飞入动画
// ============================================================
const ParamCanvas = {
  scenes: [
    {
      label: '位置参数',
      code: 'def add(a, b):\n    return a + b\n\nadd(3, 5)',
      params: ['a', 'b'],
      args: [3, 5],
      desc: '实参按位置顺序匹配形参：3→a, 5→b',
      detail: '这是最基本的传参方式。第一个实参 3 赋给第一个形参 a，第二个实参 5 赋给第二个形参 b。位置一一对应。'
    },
    {
      label: '默认参数',
      code: 'def greet(name, greeting="你好"):\n    return f"{greeting}，{name}！"\n\ngreet("小明")',
      params: ['name', 'greeting="你好"'],
      args: ['"小明"', 'default'],
      desc: 'greeting 使用默认值 "你好"',
      detail: 'greeting 有默认值 "你好"，调用时没有传入第二个参数，所以使用默认值。默认参数让函数更灵活——调用者可以选择是否覆盖。'
    },
    {
      label: '关键字参数',
      code: 'def describe(name, age, city):\n    return f"{name}，{age}岁，来自{city}"\n\ndescribe(city="北京", age=25, name="张三")',
      params: ['name', 'age', 'city'],
      args: ['"张三"', 25, '"北京"'],
      desc: '关键字参数可按名称匹配，不受顺序限制',
      detail: '关键字参数通过参数名匹配：city="北京", age=25, name="张三"。顺序可以任意，这提高了代码可读性。注意：位置参数必须在关键字参数之前。'
    },
    {
      label: '可变对象陷阱',
      code: 'def bad_append(item, lst=[]):\n    lst.append(item)\n    return lst\n\nprint(bad_append(1))\nprint(bad_append(2))',
      params: ['item', 'lst=[]'],
      args: [1, 'shared_list'],
      desc: '⚠️ 默认列表被共享！第二次调用 lst 仍然是 [1]！',
      detail: 'Python 的默认参数只在函数定义时计算一次。所以 lst=[] 始终指向同一个列表对象。第一次调用后 lst=[1]，第二次再调用时 lst 仍然是那个列表，变成 [1, 2]。'
    },
    {
      label: '✅ 正确做法',
      code: 'def good_append(item, lst=None):\n    if lst is None:\n        lst = []\n    lst.append(item)\n    return lst\n\nprint(good_append(1))\nprint(good_append(2))',
      params: ['item', 'lst=None'],
      args: [1, 'new_list'],
      desc: '用 None 做默认值，每次创建新列表',
      detail: '正确做法：用 None 作为默认值，函数内部判断如果是 None 就创建新列表。这样每次调用都有独立的列表，不会相互影响。'
    }
  ],

  state: {
    sceneIdx: 0, animId: null, animProgress: 0,
    gameMode: 'matching', shuffledArgs: [], selectedArg: null,
    matchedPairs: [], wrongFlash: null, gameScore: 0, attempts: 0
  },

  open() {
    this.state = {
      sceneIdx: 0, animId: null, animProgress: 0,
      gameMode: 'matching', shuffledArgs: [], selectedArg: null,
      matchedPairs: [], wrongFlash: null, gameScore: 0, attempts: 0
    };
    document.getElementById('func-modal-param')?.classList.add('active');
    setTimeout(() => { this.render(); this.draw(); }, 50);
  },

  close() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    document.getElementById('func-modal-param')?.classList.remove('active');
  },

  selectScene(idx) {
    const scene = this.scenes[idx];
    this.state.sceneIdx = idx;
    this.state.animProgress = 0;
    this.state.gameMode = 'matching';
    this.state.selectedArg = null;
    this.state.wrongFlash = null;
    this.state.matchedPairs = [];
    // Shuffle args
    this.state.shuffledArgs = scene.args.map((_, i) => i).sort(() => Math.random() - 0.5);
    this.render();
    this.draw();
  },

  clickArg(argIdx) {
    if (this.state.gameMode !== 'matching') return;
    if (this.state.matchedPairs.some(p => p.argIdx === argIdx)) return;
    this.state.selectedArg = argIdx;
    this.state.wrongFlash = null;
    this.render();
    this.draw();
  },

  clickParamSlot(paramIdx) {
    if (this.state.gameMode !== 'matching') return;
    if (this.state.selectedArg === null) return;
    if (this.state.matchedPairs.some(p => p.paramIdx === paramIdx)) return;

    const argIdx = this.state.selectedArg;
    this.state.attempts++;

    // Check if correct: in positional mode, arg index should match param index
    const scene = this.scenes[this.state.sceneIdx];
    const isCorrect = argIdx === paramIdx;

    if (isCorrect) {
      this.state.matchedPairs.push({ argIdx, paramIdx });
      this.state.gameScore += Math.max(10, 100 - this.state.attempts * 5);
      this.state.selectedArg = null;
      this.state.wrongFlash = null;

      if (this.state.matchedPairs.length === scene.params.length) {
        // All matched! Transition to animation
        this.state.gameMode = 'animation';
        this.render();
        this.draw();
        setTimeout(() => this.animateArgs(), 300);
      } else {
        this.render();
        this.draw();
      }
    } else {
      // Wrong match - flash red
      this.state.wrongFlash = { argIdx, paramIdx };
      this.render();
      this.draw();
      setTimeout(() => {
        this.state.wrongFlash = null;
        this.state.selectedArg = null;
        this.render();
        this.draw();
      }, 600);
    }
  },

  animateArgs() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    this.state.animProgress = 0;
    const animate = () => {
      this.state.animProgress += 0.03;
      this.draw();
      if (this.state.animProgress < 1) {
        this.state.animId = requestAnimationFrame(animate);
      } else {
        this.state.animId = null;
        this.state.animProgress = 1;
        this.draw();
      }
    };
    this.state.animId = requestAnimationFrame(animate);
  },

  render() {
    const panel = document.getElementById('param-panel');
    if (!panel) return;
    const s = this.state;
    const scene = this.scenes[s.sceneIdx];

    // Match mode: show parameter names on left as droppable slots, argument cards on right
    const isMatching = s.gameMode === 'matching';

    let gameArea = '';
    if (isMatching) {
      // Render parameter cards (left side) and shuffled argument cards (right side)
      const hasDefault = scene.args.some(a => a === 'default');
      const hasShared = scene.args.some(a => a === 'shared_list');
      const hasNew = scene.args.some(a => a === 'new_list');
      const hint = hasDefault ? '<span style="color:var(--orange);font-size:11px;">💡 提示：注意哪些参数有默认值，不需要匹配</span>' :
                   hasShared || hasNew ? '<span style="color:var(--orange);font-size:11px;">💡 提示：注意可变对象的行为，仔细看代码</span>' :
                   '<span style="color:var(--text-muted);font-size:11px;">💡 先点击一个实参卡片，再点击对应的形参槽位进行匹配</span>';

      const argsMatched = s.matchedPairs.length;
      const totalArgs = scene.params.length;

      gameArea = `
        <div style="display:flex;gap:8px;align-items:stretch;">
          <div style="flex:1;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
              <span class="fd-col-label">📥 形参（点击槽位放置）</span>
              <span style="font-size:11px;color:var(--text-muted);">匹配: ${argsMatched}/${totalArgs}</span>
            </div>
            ${scene.params.map((p, pIdx) => {
              const matched = s.matchedPairs.find(m => m.paramIdx === pIdx);
              const isWrong = s.wrongFlash && s.wrongFlash.paramIdx === pIdx;
              const isTarget = s.selectedArg !== null && !matched;
              return `
                <div onclick="${!matched && s.selectedArg !== null ? `ParamCanvas.clickParamSlot(${pIdx})` : ''}"
                  style="padding:10px 14px;margin:4px 0;border-radius:6px;cursor:${!matched && s.selectedArg !== null ? 'pointer' : 'default'};
                  background:${matched ? 'var(--green-dim)' : isWrong ? 'var(--red-dim)' : isTarget ? 'var(--cyan-dim)' : 'var(--bg-card)'};
                  border:2px solid ${matched ? 'var(--green)' : isWrong ? 'var(--red)' : isTarget ? 'var(--cyan)' : 'var(--border-subtle)'};
                  transition:all 0.3s;font-size:13px;color:${matched ? 'var(--green)' : isWrong ? 'var(--red)' : 'var(--text-primary)'};font-weight:${matched ? '600' : '400'};">
                  <span style="opacity:${matched ? '1' : '0.5'};font-size:11px;color:var(--text-muted);">形参 ${pIdx + 1}：</span>
                  ${p}
                  ${matched ? ' ✓' : (isTarget ? ' ⬇ 点击放入' : '')}
                </div>
              `;
            }).join('')}
          </div>
          <div style="width:2px;background:var(--border-subtle);border-radius:1px;margin:0 4px;"></div>
          <div style="flex:1;">
            <div class="fd-col-label">🔵 实参（点击选中）</div>
            ${scene.args.map((arg, aIdx) => {
              const matched = s.matchedPairs.some(m => m.argIdx === aIdx);
              const isSelected = s.selectedArg === aIdx;
              const isWrong = s.wrongFlash && s.wrongFlash.argIdx === aIdx;
              const argLabel = arg === 'default' ? '(默认值)' :
                              arg === 'shared_list' ? '[] (共享)' :
                              arg === 'new_list' ? '[] (新)' : String(arg);
              return `
                <div onclick="${!matched ? `ParamCanvas.clickArg(${aIdx})` : ''}"
                  style="padding:10px 14px;margin:4px 0;border-radius:6px;cursor:${matched ? 'default' : 'pointer'};
                  background:${matched ? 'var(--green-dim)' : isWrong ? 'var(--red-dim)' : isSelected ? 'var(--cyan-dim)' : 'var(--bg-card)'};
                  border:2px solid ${matched ? 'var(--green)' : isWrong ? 'var(--red)' : isSelected ? 'var(--cyan)' : 'var(--border-subtle)'};
                  transition:all 0.3s;font-size:13px;color:${matched ? 'var(--green)' : isWrong ? 'var(--red)' : 'var(--text-primary)'};
                  opacity:${matched ? '0.6' : '1'}">
                  <span style="font-size:11px;color:var(--text-muted);">实参：</span>${argLabel}
                  ${matched ? ' ✓' : ''}
                </div>
              `;
            }).join('')}
          </div>
        </div>
        <div style="margin-top:6px;padding:6px 10px;background:var(--bg-deep);border-radius:6px;display:flex;justify-content:space-between;align-items:center;">
          <div>${hint}</div>
          <div style="font-size:12px;color:var(--cyan);font-weight:600;">⭐ ${s.gameScore} 分</div>
        </div>
      `;
    }

    panel.innerHTML = `
      <div class="fd-scene-select">
        ${this.scenes.map((sc, i) =>
          `<button class="fd-scene-btn ${i === s.sceneIdx ? 'active' : ''}" onclick="ParamCanvas.selectScene(${i})">${sc.label}</button>`
        ).join('')}
      </div>
      ${isMatching ? gameArea : `
      <div style="display:flex;gap:12px;">
        <div class="fd-code-col" style="flex:0 0 200px;">
          <div class="fd-col-label">💻 代码</div>
          <div class="fd-code-lines" style="font-size:12px;line-height:1.5;white-space:pre;padding:8px;background:var(--bg-deep);border-radius:6px;font-family:var(--font-mono);">${scene.code}</div>
          <div style="margin-top:8px;padding:8px 10px;background:var(--bg-deep);border-radius:6px;font-size:12px;color:var(--text-secondary);line-height:1.5;">💡 ${scene.detail}</div>
        </div>
        <div class="fd-canvas-col" style="flex:1;">
          <div class="fd-col-label">📊 参数传递</div>
          <canvas id="param-canvas"></canvas>
        </div>
      </div>
      `}
      <div style="margin-top:8px;padding:8px 14px;background:${isMatching ? 'var(--green-dim)' : 'var(--bg-deep)'};border-radius:6px;font-size:13px;color:var(--green);text-align:center;font-weight:500;">
        ${isMatching
          ? (s.matchedPairs.length === scene.params.length
              ? '✅ 全部匹配正确！自动播放动画演示...'
              : scene.desc)
          : scene.desc}
      </div>
      ${!isMatching ? `
      <div style="margin-top:6px;display:flex;justify-content:space-between;align-items:center;padding:4px 8px;">
        <span style="font-size:11px;color:var(--text-muted);">匹配得分: ${s.gameScore} ⭐</span>
        <button class="fd-btn" onclick="ParamCanvas.selectScene(${s.sceneIdx})" style="font-size:11px;">↺ 重新匹配挑战</button>
      </div>` : ''}
    `;
  },

  draw() {
    if (this.state.gameMode !== 'animation') return;
    const canvas = document.getElementById('param-canvas');
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width - 4, h = rect.height - 4;
    const ctx = fdCanvas.setup(canvas, w, h);
    if (!ctx) return;
    fdCanvas.clear(ctx, w, h);

    const scene = this.scenes[this.state.sceneIdx];
    const t = this.state.animProgress;
    const paramX = 20, argX = w - 140;
    const paramW = 110;
    const startY = 40, rowH = 56;

    // Draw function name box
    fdCanvas.roundRect(ctx, paramX, 8, paramW + 20, 28, 4,
      fdTheme.get('--cyan-dim'), fdTheme.get('--cyan'));
    fdCanvas.text(ctx, 'def 函数(...)', paramX + (paramW + 20) / 2, 22, fdTheme.get('--cyan'), 12);

    // Draw parameter slots
    scene.params.forEach((p, i) => {
      const y = startY + i * rowH;
      fdCanvas.roundRect(ctx, paramX, y, paramW, 40, 4,
        fdTheme.get('--bg-card'), fdTheme.get('--border-subtle'));
      fdCanvas.text(ctx, p, paramX + paramW / 2, y + 20, fdTheme.get('--text-primary'), 12);
    });

    // Draw argument balls flying in
    scene.args.forEach((arg, i) => {
      const y = startY + i * rowH;
      const sx = argX, sy = y;
      const ex = paramX + paramW, ey = y;

      if (t > 0) {
        const cx = fdCanvas.lerp(sx, ex, Math.min(t * 1.2, 1));
        const cy = sy + Math.sin(Math.min(t * 8, Math.PI)) * (-15);

        const isDefault = arg === 'default';
        const isShared = arg === 'shared_list';
        const isNew = arg === 'new_list';
        const color = isDefault ? fdTheme.get('--orange') :
                      isShared ? fdTheme.get('--red') :
                      isNew ? fdTheme.get('--green') : fdTheme.get('--purple');
        const label = isDefault ? '(默认)' :
                      isShared ? '🔄 [] (共享)' :
                      isNew ? '✅ [] (新)' : String(arg);

        ctx.save();
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = color + '40';
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(sx + 10, sy + 20); ctx.lineTo(cx, cy + 20);
        if (t >= 0.8) ctx.lineTo(ex - 5, ey + 20);
        ctx.stroke();
        ctx.restore();

        ctx.beginPath();
        ctx.arc(cx, cy + 20, 16, 0, Math.PI * 2);
        ctx.fillStyle = color + '30';
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.stroke();

        fdCanvas.text(ctx, label + '', cx, cy + 20,
          t > 0.5 ? fdTheme.get('--text-primary') : color, 10);
      }

      fdCanvas.text(ctx, `实参 ${i + 1}`, argX + 60, y + 20, fdTheme.get('--text-muted'), 10);
    });

    fdCanvas.text(ctx, '🔵 实参 → 📥 形参', w / 2, h - 14, fdTheme.get('--text-muted'), 11);
  }
};

// ============================================================
// 组件 3: 作用域探险家 (KP3)
// Canvas LEGB 气泡搜索动画 + 猜谜游戏
// ============================================================
const ScopeCanvas = {
  scenes: [
    {
      label: '基础查找',
      code: 'x = "全局"\n\ndef outer():\n    x = "外层"\n    def inner():\n        x = "内层"\n        print(x)\n    inner()\nouter()',
      layers: {
        L: { vars: { x: '"内层"' }, color: '--red', label: 'Local 局部' },
        E: { vars: { x: '"外层"' }, color: '--orange', label: 'Enclosing 闭包' },
        G: { vars: { x: '"全局"' }, color: '--green', label: 'Global 全局' },
        B: { vars: { pi: '3.14', max: '<built-in>' }, color: '--cyan', label: 'Built-in 内置' },
      },
      lookups: [
        { var: 'x', foundIn: 'L', desc: '在 Local 局部作用域找到 x = "内层"！搜索结束。' },
      ],
      question: '代码中 print(x) 的 x 会在哪个作用域找到？',
      choices: [
        { key: 'L', label: 'Local (局部)', hint: 'inner 函数内部定义了 x' },
        { key: 'E', label: 'Enclosing (闭包)', hint: 'outer 函数内部有 x，但不是直接定义在 inner 里面' },
        { key: 'G', label: 'Global (全局)', hint: '最外层有 x，但 inner 内部也有定义' },
        { key: 'B', label: 'Built-in (内置)', hint: 'x 是变量名，不是内置函数，不可能在内置作用域' },
      ]
    },
    {
      label: '闭包查找',
      code: 'x = "全局变量"\n\ndef outer():\n    x = "外层变量"\n    def inner():\n        print(x)  # 本层没有 x！\n    inner()\nouter()',
      layers: {
        L: { vars: {}, color: '--red', label: 'Local 局部' },
        E: { vars: { x: '"外层变量"' }, color: '--orange', label: 'Enclosing 闭包' },
        G: { vars: { x: '"全局变量"' }, color: '--green', label: 'Global 全局' },
        B: { vars: { pi: '3.14', max: '<built-in>' }, color: '--cyan', label: 'Built-in 内置' },
      },
      lookups: [
        { var: 'x', foundIn: 'E', desc: 'Local 没有 x → 到 Enclosing 找到 x = "外层变量"！' },
      ],
      question: '代码中 print(x) 的 x 会在哪个作用域找到？',
      choices: [
        { key: 'L', label: 'Local (局部)', hint: 'inner 内部并没有定义 x！' },
        { key: 'E', label: 'Enclosing (闭包)', hint: 'inner 内部没有 x，但 outer 函数有定义 x' },
        { key: 'G', label: 'Global (全局)', hint: '虽然全局也有 x，但 Python 会先在 Enclosing 找' },
        { key: 'B', label: 'Built-in (内置)', hint: 'x 不是内置函数，不可能在内置作用域' },
      ]
    },
    {
      label: 'global 声明',
      code: 'x = "全局"\n\ndef change():\n    global x\n    x = "被修改了"',
      layers: {
        L: { vars: {}, color: '--red', label: 'Local 局部' },
        E: { vars: {}, color: '--orange', label: 'Enclosing 闭包' },
        G: { vars: { x: '"被修改了"' }, color: '--green', label: 'Global 全局' },
        B: { vars: { pi: '3.14', max: '<built-in>' }, color: '--cyan', label: 'Built-in 内置' },
      },
      lookups: [
        { var: 'x (global)', foundIn: 'G', desc: 'global x 直接绑定到全局作用域，修改影响全局变量。' },
      ],
      question: '代码中 global x 声明的 x 会绑定到哪个作用域？',
      choices: [
        { key: 'L', label: 'Local (局部)', hint: '使用 global 后，变量不再属于局部作用域' },
        { key: 'E', label: 'Enclosing (闭包)', hint: 'change() 没有外层嵌套函数' },
        { key: 'G', label: 'Global (全局)', hint: 'global 关键字的作用就是把变量绑定到全局作用域' },
        { key: 'B', label: 'Built-in (内置)', hint: 'x 不是内置函数' },
      ]
    }
  ],

  state: {
    sceneIdx: 0, lookupStep: -1, animId: null, searchProgress: 0,
    quizMode: true, quizAnswer: null, quizCorrect: null, quizScore: 0
  },
  searchLayer: null,

  open() {
    this.state = {
      sceneIdx: 0, lookupStep: -1, animId: null, searchProgress: 0,
      quizMode: true, quizAnswer: null, quizCorrect: null, quizScore: 0
    };
    this.searchLayer = null;
    document.getElementById('func-modal-scope')?.classList.add('active');
    setTimeout(() => { this.render(); this.draw(); }, 50);
  },

  close() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    document.getElementById('func-modal-scope')?.classList.remove('active');
  },

  selectScene(idx) {
    this.state.sceneIdx = idx;
    this.state.lookupStep = -1;
    this.state.searchProgress = 0;
    this.state.quizMode = true;
    this.state.quizAnswer = null;
    this.state.quizCorrect = null;
    this.searchLayer = null;
    this.render();
    this.draw();
  },

  guess(key) {
    const scene = this.scenes[this.state.sceneIdx];
    const correctKey = scene.lookups[0].foundIn;
    this.state.quizAnswer = key;
    this.state.quizCorrect = key === correctKey;
    if (this.state.quizCorrect) this.state.quizScore += 10;
    this.render();
    this.draw();
  },

  startSearch() {
    const scene = this.scenes[this.state.sceneIdx];
    this.state.quizMode = false;
    this.state.lookupStep = 0;
    this.state.searchProgress = 0;
    this.render();
    this.animateSearch();
  },

  search() {
    const scene = this.scenes[this.state.sceneIdx];
    if (!scene.lookups || scene.lookups.length === 0) return;
    if (this.state.lookupStep >= scene.lookups.length - 1) {
      this.state.lookupStep = -1;
      this.render();
      this.draw();
      return;
    }
    this.state.lookupStep++;
    this.state.searchProgress = 0;
    this.render();
    this.animateSearch();
  },

  animateSearch() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    this.state.searchProgress = 0;
    const layers = ['L', 'E', 'G', 'B'];
    const scene = this.scenes[this.state.sceneIdx];
    const lookup = scene.lookups[this.state.lookupStep];
    const foundLayerIdx = layers.indexOf(lookup.foundIn);
    const totalLayers = foundLayerIdx + 1;

    const animate = () => {
      this.state.searchProgress += 0.02;
      const prog = this.state.searchProgress;
      const currentLayer = Math.min(Math.floor(prog * totalLayers * 2), totalLayers - 1);
      this.searchLayer = currentLayer;
      this.draw();
      if (prog < 1) {
        this.state.animId = requestAnimationFrame(animate);
      } else {
        this.state.animId = null;
        this.searchLayer = foundLayerIdx;
        this.draw();
      }
    };
    this.state.animId = requestAnimationFrame(animate);
  },

  render() {
    const panel = document.getElementById('scope-panel');
    if (!panel) return;
    const s = this.state;
    const scene = this.scenes[s.sceneIdx];
    const lookup = s.lookupStep >= 0 && s.lookupStep < scene.lookups.length
      ? scene.lookups[s.lookupStep] : null;

    let quizHTML = '';
    if (s.quizMode) {
      quizHTML = `
        <div style="margin-top:8px;padding:12px 16px;background:var(--bg-secondary);border-radius:8px;">
          <div style="font-size:14px;font-weight:600;color:var(--text-primary);margin-bottom:8px;">🤔 猜一猜</div>
          <div style="font-size:13px;color:var(--text-secondary);margin-bottom:10px;">${scene.question}</div>
          ${!s.quizAnswer ? `
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
              ${scene.choices.map(c => `
                <div onclick="ScopeCanvas.guess('${c.key}')"
                  style="padding:10px 14px;border-radius:6px;background:var(--bg-card);border:2px solid var(--border-subtle);
                  cursor:pointer;font-size:13px;color:var(--text-primary);text-align:center;transition:all 0.2s;
                  hover:background:var(--bg-deep);">
                  <span style="font-weight:600;">${c.key}</span> — ${c.label}
                </div>
              `).join('')}
            </div>
          ` : `
            <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:6px;
              background:${s.quizCorrect ? 'var(--green-dim)' : 'var(--red-dim)'};
              border:2px solid ${s.quizCorrect ? 'var(--green)' : 'var(--red)'};">
              <span style="font-size:24px;">${s.quizCorrect ? '✅' : '❌'}</span>
              <div>
                <div style="font-size:14px;font-weight:600;color:${s.quizCorrect ? 'var(--green)' : 'var(--red)'};">
                  ${s.quizCorrect ? '回答正确！+10 ⭐' : '回答错误！'}
                </div>
                <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">
                  ${s.quizCorrect ? scene.lookups[0].desc : `正确答案是 ${scene.lookups[0].foundIn} 作用域。${scene.choices.find(c => c.key === scene.lookups[0].foundIn)?.hint || ''}`}
                </div>
              </div>
            </div>
            <button class="fd-btn primary" onclick="ScopeCanvas.startSearch()" style="margin-top:8px;width:100%;padding:8px;">
              ${s.quizCorrect ? '🎬 观看搜索动画' : '🔍 查看 LEGB 搜索过程'}
            </button>
          `}
        </div>
      `;
    }

    panel.innerHTML = `
      <div class="fd-scene-select">
        ${this.scenes.map((sc, i) =>
          `<button class="fd-scene-btn ${i === s.sceneIdx ? 'active' : ''}" onclick="ScopeCanvas.selectScene(${i})">${sc.label}</button>`
        ).join('')}
      </div>
      <div style="display:flex;gap:12px;">
        <div class="fd-code-col" style="flex:0 0 220px;">
          <div class="fd-col-label">💻 代码</div>
          <div class="fd-code-lines" style="font-size:12px;line-height:1.5;white-space:pre;padding:8px;background:var(--bg-deep);border-radius:6px;font-family:var(--font-mono);">${scene.code}</div>
          ${!s.quizMode ? `<button class="fd-btn primary" onclick="ScopeCanvas.search()" style="width:100%;margin-top:8px;">
            ${s.lookupStep >= (scene.lookups?.length || 0) - 1 ? '🔄 重新搜索' : '🔍 搜索变量'}
          </button>` : ''}
          <div style="margin-top:6px;font-size:11px;color:var(--text-muted);text-align:center;">得分: ⭐ ${s.quizScore}</div>
        </div>
        <div class="fd-canvas-col" style="flex:1;">
          <div class="fd-col-label">🌐 LEGB 作用域</div>
          <canvas id="scope-canvas"></canvas>
        </div>
      </div>
      ${!s.quizMode ? (lookup ? `<div style="margin-top:8px;padding:8px 14px;background:var(--green-dim);border-radius:6px;font-size:13px;color:var(--green);text-align:center;">🔍 ${lookup.desc}</div>` : '<div style="margin-top:8px;padding:8px 14px;background:var(--bg-deep);border-radius:6px;font-size:12px;color:var(--text-muted);text-align:center;">👆 点击「搜索变量」观察 Python 的 LEGB 查找过程</div>') : ''}
      ${s.quizMode ? quizHTML : ''}
    `;
  },

  draw() {
    const canvas = document.getElementById('scope-canvas');
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width - 4, h = rect.height - 4;
    const ctx = fdCanvas.setup(canvas, w, h);
    if (!ctx) return;
    fdCanvas.clear(ctx, w, h);

    const scene = this.scenes[this.state.sceneIdx];
    const lookup = this.state.lookupStep >= 0 && this.state.lookupStep < scene.lookups.length
      ? scene.lookups[this.state.lookupStep] : null;

    const cx = w / 2, cy = h / 2 + 10;
    const layerRadii = [50, 90, 130, 170];
    const layerKeys = ['L', 'E', 'G', 'B'];

    // Draw from outermost to innermost
    for (let li = layerKeys.length - 1; li >= 0; li--) {
      const key = layerKeys[li];
      const layer = scene.layers[key];
      const r = layerRadii[li];
      const color = fdTheme.get(layer.color);
      const isSearching = this.searchLayer !== null && li === this.searchLayer;
      const isFound = lookup && layerKeys.indexOf(lookup.foundIn) === li &&
                      this.searchLayer !== null && this.state.searchProgress >= 1;

      // Highlight correct answer in quiz mode
      const isQuizCorrectAnswer = this.state.quizAnswer && !this.state.quizMode && !isSearching &&
        lookup && layerKeys.indexOf(lookup.foundIn) === li;

      // Bubble
      ctx.save();
      ctx.globalAlpha = 0.15;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.globalAlpha = 1;
      ctx.strokeStyle = isFound ? fdTheme.get('--green') : (isSearching ? fdTheme.get('--orange') : color);
      ctx.lineWidth = isFound ? 3 : (isSearching ? 2.5 : 1.5);
      ctx.stroke();
      ctx.restore();

      // Layer label
      const labelAngle = -Math.PI / 2 + (li - 1.5) * 0.15;
      const lx = cx + (r - 16) * Math.cos(labelAngle);
      const ly = cy + (r - 16) * Math.sin(labelAngle);
      fdCanvas.text(ctx, `${layer.label} (${key})`, lx, ly, color, 11);

      // Variables
      const varEntries = Object.entries(layer.vars);
      varEntries.forEach(([vName, vVal], vi) => {
        const angle = -Math.PI / 2 + ((vi - (varEntries.length - 1) / 2) * 0.5);
        const vr = r - 28;
        const vx = cx + vr * Math.cos(angle);
        const vy = cy + vr * Math.sin(angle);
        ctx.fillStyle = isFound && lookup.var.includes(vName) ? fdTheme.get('--green') : fdTheme.get('--text-primary');
        ctx.font = '12px "Microsoft YaHei", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`${vName} = ${vVal}`, vx, vy);
      });

      // Search dot on this layer
      if (isSearching) {
        const dotAngle = Date.now() / 300;
        const dx = cx + (r - 8) * Math.cos(dotAngle);
        const dy = cy + (r - 8) * Math.sin(dotAngle);
        ctx.save();
        ctx.shadowColor = fdTheme.get('--orange');
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(dx, dy, 6, 0, Math.PI * 2);
        ctx.fillStyle = isFound ? fdTheme.get('--green') : fdTheme.get('--orange');
        ctx.fill();
        ctx.restore();
      }
    }

    // Center label
    fdCanvas.text(ctx, '🔍 LEGB', cx, cy, fdTheme.get('--text-secondary'), 12);

    // Legend
    const legendY = h - 20;
    const legends = [
      { key: 'L', color: fdTheme.get('--red'), label: 'Local' },
      { key: 'E', color: fdTheme.get('--orange'), label: 'Enclosing' },
      { key: 'G', color: fdTheme.get('--green'), label: 'Global' },
      { key: 'B', color: fdTheme.get('--cyan'), label: 'Built-in' },
    ];
    let lx = cx - 120;
    legends.forEach(l => {
      ctx.fillStyle = l.color;
      ctx.beginPath();
      ctx.arc(lx, legendY, 5, 0, Math.PI * 2);
      ctx.fill();
      fdCanvas.text(ctx, l.label, lx + 12, legendY, fdTheme.get('--text-muted'), 10, 'left');
      lx += 65;
    });
  }
};

// ============================================================
// 组件 4: 装饰器工坊 (KP5)
// Canvas 洋葱圈装饰器动画 + 排序挑战
// ============================================================
const DecoratorCanvas = {
  layers: [
    { name: '计时统计', color: '--purple', active: true, code: '@timer', orderHint: '最内层，最靠近函数' },
    { name: '日志记录', color: '--orange', active: true, code: '@log_call', orderHint: '中间层' },
    { name: '权限验证', color: '--red', active: true, code: '@auth_required', orderHint: '最外层，最先执行' },
  ],

  state: {
    phase: -1, animId: null, animProgress: 0, executing: false,
    challengeMode: false, shuffled: [], selected: [],
    challengeDone: false, challengeScore: 0
  },

  correctOrder: ['权限验证', '日志记录', '计时统计'],

  open() {
    this.state = {
      phase: -1, animId: null, animProgress: 0, executing: false,
      challengeMode: false, shuffled: [], selected: [],
      challengeDone: false, challengeScore: 0
    };
    document.getElementById('func-modal-decorator')?.classList.add('active');
    setTimeout(() => { this.render(); this.draw(); }, 50);
  },

  close() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    document.getElementById('func-modal-decorator')?.classList.remove('active');
  },

  toggleLayer(idx) {
    this.layers[idx].active = !this.layers[idx].active;
    this.state.executing = false;
    this.state.phase = -1;
    this.render();
    this.draw();
  },

  startChallenge() {
    this.state.challengeMode = true;
    this.state.challengeDone = false;
    this.state.selected = [];
    this.state.shuffled = [...this.correctOrder].sort(() => Math.random() - 0.5);
    this.state.executing = false;
    this.state.phase = -1;
    this.render();
    this.draw();
  },

  clickChallengeItem(name) {
    if (this.state.challengeDone) return;
    if (this.state.selected.includes(name)) return;

    const nextIdx = this.state.selected.length;
    const isCorrect = name === this.correctOrder[nextIdx];
    if (!isCorrect) return; // wrong order, no response

    this.state.selected.push(name);
    if (this.state.selected.length === this.correctOrder.length) {
      // All correct!
      this.state.challengeScore += 50;
      this.state.challengeDone = true;
      // Auto-enable all layers and execute
      this.layers.forEach(l => l.active = true);
      this.state.challengeMode = false;
      this.state.executing = true;
      this.state.phase = 0;
      this.state.animProgress = 0;
      this.render();
      setTimeout(() => this.animateExecution(), 200);
    } else {
      this.render();
    }
  },

  execute() {
    const activeLayers = this.layers.filter(l => l.active);
    if (activeLayers.length === 0) return;
    this.state.executing = true;
    this.state.phase = 0;
    this.state.animProgress = 0;
    this.render();
    this.animateExecution();
  },

  animateExecution() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    let speed = 0.02;
    const animate = () => {
      this.state.animProgress += speed;
      const phases = this.layers.filter(l => l.active).length * 2 + 1;
      const totalProgress = this.state.animProgress;
      const phaseLen = 1 / phases;
      this.state.phase = Math.min(Math.floor(totalProgress / phaseLen), phases - 1);

      if (this.state.animProgress >= 1) {
        this.state.animProgress = 1;
        this.state.phase = phases;
        this.state.executing = false;
        this.draw();
        this.render();
        return;
      }
      this.draw();
      this.state.animId = requestAnimationFrame(animate);
    };
    this.state.animId = requestAnimationFrame(animate);
  },

  getPhaseDescription() {
    const al = this.layers.filter(l => l.active);
    if (al.length === 0) return '请至少启用一个装饰器层';
    const phases = al.length * 2 + 1;
    const p = this.state.phase;
    if (p <= 0) return '▶ 点击「执行」开始';
    if (p <= al.length) return `⬇ 第 ${p} 层：${al[p - 1].name} 传入...`;
    if (p === al.length + 1) return '🎯 到达核心函数！执行函数体...';
    const outIdx = p - al.length - 2;
    if (outIdx < al.length) return `⬆ 第 ${al.length - outIdx} 层：${al[al.length - outIdx - 1].name} 传出...`;
    return '✅ 执行完成！';
  },

  render() {
    const panel = document.getElementById('decorator-panel');
    if (!panel) return;
    const s = this.state;

    let leftContent = '';
    if (s.challengeMode) {
      // Challenge mode: click decorators in correct order
      const done = s.selected.length;
      const total = this.correctOrder.length;
      leftContent = `
        <div class="fd-col-label">🧩 排序挑战</div>
        <div style="background:var(--bg-secondary);border-radius:6px;padding:8px;">
          <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px;">
            点击装饰器，按 <strong style="color:var(--cyan);">从外到内</strong> 的正确顺序排列：
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;">进度: ${'⬜'.repeat(done)}${'⬛'.repeat(total - done)}</div>
          <div style="display:flex;flex-direction:column;gap:4px;">
            ${s.shuffled.map(name => {
              const used = s.selected.includes(name);
              const isNext = !used && name === this.correctOrder[done];
              return `
                <div onclick="${!used ? `DecoratorCanvas.clickChallengeItem('${name}')` : ''}"
                  style="padding:10px 14px;border-radius:6px;cursor:${used ? 'default' : 'pointer'};
                  background:${used ? 'var(--green-dim)' : isNext ? 'var(--cyan-dim)' : 'var(--bg-card)'};
                  border:2px solid ${used ? 'var(--green)' : isNext ? 'var(--cyan)' : 'var(--border-subtle)'};
                  opacity:${used ? '0.7' : '1'};font-size:13px;color:var(--text-primary);
                  transition:all 0.2s;text-align:center;">
                  ${used ? '✓ ' : (isNext ? '👆 ' : '')}${name}
                </div>
              `;
            }).join('')}
          </div>
          <div style="margin-top:8px;font-size:11px;color:var(--text-muted);text-align:center;">
            💡 提示：最外层的装饰器最先执行（进入时最先处理）
          </div>
        </div>
      `;
    } else {
      leftContent = `
        <div class="fd-col-label">🧥 装饰层</div>
        <div style="background:var(--bg-secondary);border-radius:6px;padding:8px;">
          ${this.layers.map((l, i) => `
            <label style="display:flex;align-items:center;gap:8px;padding:6px 8px;margin:4px 0;background:var(--bg-card);border-radius:4px;cursor:pointer;font-size:12px;color:var(--text-primary);">
              <input type="checkbox" ${l.active ? 'checked' : ''} onchange="DecoratorCanvas.toggleLayer(${i})">
              <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${fdTheme.get(l.color)};"></span>
              ${l.code}
            </label>
          `).join('')}
        </div>
        <button class="fd-btn primary" onclick="DecoratorCanvas.execute()" style="width:100%;margin-top:6px;" ${this.layers.filter(l=>l.active).length === 0 ? 'disabled' : ''}>
          ${s.executing ? '⏳ 执行中...' : '▶ 执行调用'}
        </button>
        <button class="fd-btn" onclick="DecoratorCanvas.reset()" style="width:100%;margin-top:4px;">↺ 重置</button>
        <button class="fd-btn" onclick="DecoratorCanvas.startChallenge()" style="width:100%;margin-top:4px;background:var(--purple-dim);border-color:var(--purple);color:var(--purple);">
          🏆 排序挑战
        </button>
      `;
    }

    panel.innerHTML = `
      <div style="display:flex;gap:12px;margin-bottom:8px;">
        <div style="flex:0 0 160px;">
          ${leftContent}
          ${s.challengeScore > 0 ? `<div style="margin-top:4px;font-size:11px;color:var(--purple);text-align:center;">🏆 挑战得分: ${s.challengeScore} ⭐</div>` : ''}
        </div>
        <div class="fd-canvas-col" style="flex:1;">
          <div class="fd-col-label">🧅 装饰器洋葱圈</div>
          <canvas id="decorator-canvas"></canvas>
        </div>
      </div>
      ${!s.challengeMode ? `
      <div class="fd-narration-bar" style="margin-top:0;">
        <span class="fd-narration-text" style="font-size:13px;">${this.getPhaseDescription()}</span>
      </div>
      <div style="padding:6px 10px;background:var(--bg-deep);border-radius:6px;font-size:11px;color:var(--text-muted);line-height:1.5;">
        💡 装饰器从外到内传入（pre-processing），到达核心函数后，再从内到外传出（post-processing）。这就像剥洋葱——先剥外层，最后剥里层，出来时也是从里到外。
      </div>` : ''}
    `;
  },

  draw() {
    const canvas = document.getElementById('decorator-canvas');
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width - 4, h = rect.height - 4;
    const ctx = fdCanvas.setup(canvas, w, h);
    if (!ctx) return;
    fdCanvas.clear(ctx, w, h);

    const cx = w / 2, cy = h / 2;
    const activeLayers = this.layers.filter(l => l.active);
    const baseRadius = 22;
    const layerSpace = 24;

    // Draw core function
    ctx.save();
    ctx.shadowColor = fdTheme.get('--cyan-glow');
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(cx, cy, baseRadius, 0, Math.PI * 2);
    ctx.fillStyle = fdTheme.get('--cyan-dim');
    ctx.fill();
    ctx.strokeStyle = fdTheme.get('--cyan');
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();
    fdCanvas.text(ctx, '🎯 fn', cx, cy, fdTheme.get('--cyan'), 12);

    // Draw decorator layers (outside → inside)
    activeLayers.forEach((l, i) => {
      const r = baseRadius + (activeLayers.length - i) * layerSpace;
      const color = fdTheme.get(l.color);
      const phaseIdx = this.state.executing ? this.state.phase : -1;

      const layerNum = activeLayers.length - i;
      let isIncoming = false, isOutgoing = false;
      if (this.state.executing && this.state.animProgress < 1) {
        isIncoming = phaseIdx === layerNum;
        isOutgoing = phaseIdx === activeLayers.length + 1 + i;
      }

      ctx.save();
      if (isIncoming || isOutgoing) {
        ctx.shadowColor = color;
        ctx.shadowBlur = 18;
        ctx.globalAlpha = 0.9 + 0.1 * Math.sin(Date.now() / 150);
      } else {
        ctx.globalAlpha = 0.4;
      }
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.strokeStyle = color;
      ctx.lineWidth = isIncoming || isOutgoing ? 3 : 1.5;
      if (isIncoming || isOutgoing) ctx.setLineDash([]);
      else ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.restore();

      // Layer label
      const angle = -Math.PI / 2 + (i - (activeLayers.length - 1) / 2) * 0.4;
      const lx = cx + r * Math.cos(angle);
      const ly = cy + r * Math.sin(angle);
      ctx.save();
      ctx.fillStyle = isIncoming || isOutgoing ? color : fdTheme.get('--text-muted');
      ctx.font = `${isIncoming || isOutgoing ? 12 : 10}px "Microsoft YaHei", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(l.name, lx, ly);
      ctx.restore();

      if (isIncoming) {
        fdCanvas.arrow(ctx, cx, cy - r - 14, cx, cy - r + 10, color, 2);
        fdCanvas.text(ctx, '⬇ 传入', cx, cy - r - 22, color, 10);
      }
      if (isOutgoing) {
        fdCanvas.arrow(ctx, cx, cy + r - 10, cx, cy + r + 14, color, 2);
        fdCanvas.text(ctx, '⬆ 传出', cx, cy + r + 22, color, 10);
      }
    });

    fdCanvas.text(ctx, '🧅 洋葱圈模型：外层传入 → 核心执行 → 外层传出', w / 2, h - 14, fdTheme.get('--text-muted'), 11);
  },

  reset() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    this.state.phase = -1;
    this.state.animProgress = 0;
    this.state.executing = false;
    this.render();
    this.draw();
  }
};

// ============================================================
// 组件 5: 生成器 vs 列表对决 (KP6)
// Canvas 对比动画 + 预测游戏
// ============================================================
const GenVsListCanvas = {
  state: {
    size: 20, step: -1, animId: null,
    listItems: [], genItems: [], listDone: false, genDone: false,
    listMemory: 0, genMemory: 0, autoTimer: null,
    prediction: null, predictionCorrect: null, predictionScore: 0
  },

  open() {
    this.state = {
      size: 20, step: -1, animId: null,
      listItems: [], genItems: [], listDone: false, genDone: false,
      listMemory: 0, genMemory: 0, autoTimer: null,
      prediction: null, predictionCorrect: null, predictionScore: 0
    };
    document.getElementById('func-modal-genlist')?.classList.add('active');
    setTimeout(() => { this.render(); this.draw(); }, 50);
  },

  close() {
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    if (this.state.autoTimer) clearInterval(this.state.autoTimer);
    document.getElementById('func-modal-genlist')?.classList.remove('active');
  },

  setSize(val) {
    this.state.size = Math.max(1, Math.min(200, parseInt(val) || 10));
    this.reset();
  },

  makePrediction(choice) {
    const correct = choice === 'generator';
    this.state.prediction = choice;
    this.state.predictionCorrect = correct;
    if (correct) this.state.predictionScore += 20;
    this.render();
    this.draw();
  },

  nextStep() {
    const s = this.state;
    if (s.step >= s.size) return;

    s.step++;

    if (s.step === 1 && !s.listDone) {
      for (let i = 1; i <= s.size; i++) {
        s.listItems.push(i * i);
      }
      s.listMemory = s.size;
      s.listDone = true;
    }

    if (s.step >= 2) {
      const genIdx = s.step - 2;
      if (genIdx < s.size) {
        s.genItems.push((genIdx + 1) * (genIdx + 1));
        s.genMemory = s.genItems.length;
      }
      if (genIdx + 1 >= s.size) {
        s.genDone = true;
      }
    }

    this.render();
    this.draw();
  },

  autoPlay() {
    if (this.state.autoTimer) {
      clearInterval(this.state.autoTimer);
      this.state.autoTimer = null;
      document.getElementById('genlist-auto-btn').textContent = '▶ 自动播放';
      return;
    }
    document.getElementById('genlist-auto-btn').textContent = '⏸ 暂停';
    this.state.autoTimer = setInterval(() => {
      if (this.state.step >= this.state.size + 1 || (this.state.listDone && this.state.genDone)) {
        clearInterval(this.state.autoTimer);
        this.state.autoTimer = null;
        document.getElementById('genlist-auto-btn').textContent = '▶ 自动播放';
        return;
      }
      this.nextStep();
    }, 400);
  },

  reset() {
    if (this.state.autoTimer) {
      clearInterval(this.state.autoTimer);
      this.state.autoTimer = null;
      document.getElementById('genlist-auto-btn') &&
        (document.getElementById('genlist-auto-btn').textContent = '▶ 自动播放');
    }
    this.state.step = -1;
    this.state.listItems = [];
    this.state.genItems = [];
    this.state.listDone = false;
    this.state.genDone = false;
    this.state.listMemory = 0;
    this.state.genMemory = 0;
    this.state.prediction = null;
    this.state.predictionCorrect = null;
    this.render();
    this.draw();
  },

  render() {
    const panel = document.getElementById('genlist-panel');
    if (!panel) return;
    const s = this.state;
    const prog = s.step >= 0 ? Math.round((s.step / Math.max(s.size, 1)) * 100) : 0;

    let predictionHTML = '';
    if (s.prediction === null && s.step < 0) {
      predictionHTML = `
        <div style="margin-top:6px;padding:10px 16px;background:var(--bg-secondary);border-radius:8px;">
          <div style="font-size:13px;font-weight:600;color:var(--text-primary);margin-bottom:6px;">🤔 先猜一猜</div>
          <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px;">
            处理 <strong>${s.size}</strong> 个数的平方，哪种方式更省内存？
          </div>
          <div style="display:flex;gap:8px;">
            <div onclick="GenVsListCanvas.makePrediction('list')"
              style="flex:1;padding:10px;border-radius:6px;background:var(--bg-card);border:2px solid var(--red);cursor:pointer;
              text-align:center;font-size:13px;color:var(--red);transition:all 0.2s;">📋 列表 [ ]</div>
            <div onclick="GenVsListCanvas.makePrediction('generator')"
              style="flex:1;padding:10px;border-radius:6px;background:var(--bg-card);border:2px solid var(--green);cursor:pointer;
              text-align:center;font-size:13px;color:var(--green);transition:all 0.2s;">⚡ 生成器 ( )</div>
          </div>
        </div>
      `;
    } else if (s.prediction !== null && s.step < 0) {
      predictionHTML = `
        <div style="margin-top:6px;padding:10px 16px;border-radius:8px;
          background:${s.predictionCorrect ? 'var(--green-dim)' : 'var(--red-dim)'};
          border:2px solid ${s.predictionCorrect ? 'var(--green)' : 'var(--red)'};">
          <div style="font-size:13px;font-weight:600;color:${s.predictionCorrect ? 'var(--green)' : 'var(--red)'};">
            ${s.predictionCorrect ? '✅ 答对了！+20 ⭐' : '❌ 答错了！'}
          </div>
          <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">
            ${s.predictionCorrect
              ? '对！生成器是惰性求值，只在需要时才计算下一个值，几乎不占内存。'
              : '其实生成器是惰性求值的，只在需要时才计算，内存占用是 O(1)。点击下方按钮开始观察对比！'}
          </div>
        </div>
      `;
    }

    panel.innerHTML = `
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <span style="font-size:13px;color:var(--text-secondary);">数据量:</span>
        <input type="range" min="1" max="200" value="${s.size}" oninput="GenVsListCanvas.setSize(this.value)" style="flex:1;accent-color:var(--cyan);">
        <span style="font-size:14px;font-weight:600;color:var(--cyan);min-width:40px;">${s.size}</span>
        <span style="font-size:11px;color:var(--text-muted);">进度: ${prog}%</span>
        <span style="font-size:11px;color:var(--purple);">⭐ ${s.predictionScore}</span>
      </div>
      <div style="display:flex;gap:12px;">
        <div class="fd-canvas-col" style="flex:1;">
          <div class="fd-col-label">⚡ 生成器 vs 列表</div>
          <canvas id="genlist-canvas"></canvas>
        </div>
      </div>
      ${predictionHTML || `
      <div class="fd-narration-bar" style="margin-top:6px;">
        <span class="fd-narration-text" style="font-size:12px;">
          ${s.step < 0 ? '👆 点击「列表一步加载」或「生成器逐个 yield」开始对比' :
            s.step === 0 ? '准备就绪，点击下一步开始' :
            s.listDone && s.genDone ? '✅ 两者都生成了相同的结果，但方式完全不同！' :
            s.listDone && !s.genDone ? '📋 列表已全部加载完成，生成器还在逐个生成中...' :
            `🔄 第 ${s.step}/${s.size} 步`}
        </span>
        <div class="fd-step-btns">
          <button class="fd-btn primary" onclick="GenVsListCanvas.nextStep()" ${s.listDone && s.genDone ? 'disabled' : ''}>
            ${s.step < 0 ? '▶ 第一步：列表加载' : (s.listDone && !s.genDone ? '▶ yield 下一个' : '下一步 ▶')}
          </button>
          <button class="fd-btn" id="genlist-auto-btn" onclick="GenVsListCanvas.autoPlay()">▶ 自动播放</button>
          <button class="fd-btn" onclick="GenVsListCanvas.reset()">↺ 重置</button>
        </div>
      </div>
      `}
      <div style="padding:6px 10px;margin-top:6px;background:var(--bg-deep);border-radius:6px;font-size:11px;color:var(--text-muted);line-height:1.5;">
        💡 <strong>列表 [ ]</strong> 一次性计算并存储所有结果 → 内存 = O(n) ｜
        <strong>生成器 ( )</strong> 用的时候才计算下一个 → 内存 = O(1)
        ${s.listDone && s.genDone ? `<span style="color:var(--cyan);">结果相同，但生成器几乎不占内存！</span>` : ''}
      </div>
    `;
  },

  draw() {
    const canvas = document.getElementById('genlist-canvas');
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    const w = rect.width - 4, h = rect.height - 4;
    const ctx = fdCanvas.setup(canvas, w, h);
    if (!ctx) return;
    fdCanvas.clear(ctx, w, h);

    const s = this.state;
    const colW = (w - 24) / 2;

    // Left column: List
    const lx = 8;
    fdCanvas.roundRect(ctx, lx, 10, colW, h - 20, 6,
      fdTheme.get('--bg-secondary'), fdTheme.get('--border-subtle'));
    fdCanvas.text(ctx, '📋 列表 [x**2 for x in range(N)]', lx + colW / 2, 26,
      s.listDone ? fdTheme.get('--green') : fdTheme.get('--text-secondary'), 12);

    const memBarY = 34, memBarH = 14;
    fdCanvas.roundRect(ctx, lx + 6, memBarY, colW - 12, memBarH, 3,
      fdTheme.get('--bg-deep'));
    if (s.listMemory > 0) {
      const fillW = Math.min((colW - 12) * (s.listMemory / Math.max(s.size, 1)), colW - 12);
      fdCanvas.roundRect(ctx, lx + 6, memBarY, fillW, memBarH, 3,
        fdTheme.get('--red-dim'), fdTheme.get('--red'));
    }
    fdCanvas.text(ctx, `内存: ${s.listMemory}/${s.size} 项`, lx + colW / 2, memBarY + memBarH / 2,
      fdTheme.get('--text-muted'), 10);

    const itemStartY = 56, itemH = 18, itemGap = 2;
    const maxVisible = Math.min(s.listItems.length, Math.floor((h - itemStartY - 10) / (itemH + itemGap)));
    for (let i = 0; i < maxVisible; i++) {
      const iy = itemStartY + i * (itemH + itemGap);
      fdCanvas.roundRect(ctx, lx + 8, iy, colW - 16, itemH, 3,
        fdTheme.get('--red-dim'));
      fdCanvas.text(ctx, `[${i}] = ${s.listItems[i]}`, lx + colW / 2, iy + itemH / 2,
        fdTheme.get('--text-primary'), 9);
    }
    if (s.listItems.length > maxVisible) {
      fdCanvas.text(ctx, `... 还有 ${s.listItems.length - maxVisible} 项`, lx + colW / 2,
        itemStartY + maxVisible * (itemH + itemGap) + 6, fdTheme.get('--text-muted'), 10);
    }

    // Right column: Generator
    const rx = w / 2 + 4;
    fdCanvas.roundRect(ctx, rx, 10, colW, h - 20, 6,
      fdTheme.get('--bg-secondary'), fdTheme.get('--border-subtle'));
    fdCanvas.text(ctx, '⚡ 生成器 (x**2 for x in range(N))', rx + colW / 2, 26,
      s.genDone ? fdTheme.get('--green') : fdTheme.get('--text-secondary'), 12);

    fdCanvas.roundRect(ctx, rx + 6, memBarY, colW - 12, memBarH, 3,
      fdTheme.get('--bg-deep'));
    if (s.genMemory > 0) {
      const fillW = Math.min((colW - 12) * (s.genMemory / Math.max(s.size, 1)), colW - 12);
      fdCanvas.roundRect(ctx, rx + 6, memBarY, fillW, memBarH, 3,
        fdTheme.get('--green-dim'), fdTheme.get('--green'));
    }
    fdCanvas.text(ctx, `内存: ${s.genMemory}（只有当前项）`, rx + colW / 2, memBarY + memBarH / 2,
      fdTheme.get('--text-muted'), 10);

    for (let i = 0; i < Math.min(s.genItems.length, maxVisible); i++) {
      const iy = itemStartY + i * (itemH + itemGap);
      const isLast = i === s.genItems.length - 1 && !s.genDone;
      fdCanvas.roundRect(ctx, rx + 8, iy, colW - 16, itemH, 3,
        isLast ? fdTheme.get('--orange-dim') : fdTheme.get('--green-dim'));
      fdCanvas.text(ctx, isLast ? `▶ yielding: ${s.genItems[i]}` : `✓ ${s.genItems[i]}`, rx + colW / 2, iy + itemH / 2,
        isLast ? fdTheme.get('--orange') : fdTheme.get('--text-primary'), 9);
    }
    if (!s.genDone) {
      const nextY = itemStartY + Math.min(s.genItems.length, maxVisible) * (itemH + itemGap);
      if (nextY + 20 < h - 10) {
        fdCanvas.roundRect(ctx, rx + 8, nextY, colW - 16, itemH, 3,
          fdTheme.get('--bg-deep'), fdTheme.get('--border-subtle'));
        fdCanvas.text(ctx, '⏳ 等待 yield...', rx + colW / 2, nextY + itemH / 2,
          fdTheme.get('--text-muted'), 9);
      }
    }

    if (s.listDone && s.genDone) {
      ctx.save();
      ctx.fillStyle = fdTheme.get('--green-dim');
      ctx.fillRect(0, h - 24, w, 24);
      ctx.restore();
      fdCanvas.text(ctx, `✅ 结果相同！但列表占用 ${s.size} 个内存单元，生成器仅占用 1 个。`, w / 2, h - 12,
        fdTheme.get('--green'), 12);
    }
  }
};

// ============================================================
// CSS 注入
// ============================================================
(function() {
  const style = document.createElement('style');
  style.textContent = `
    .fd-modal-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); z-index:9999; align-items:center; justify-content:center; }
    .fd-modal-overlay.active { display:flex; }
    .fd-modal-box { background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:var(--radius-lg); padding:16px; width:92%; max-width:960px; max-height:88vh; overflow-y:auto; }
    .fd-modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
    .fd-modal-header h3 { margin:0; font-size:16px; }
    .fd-modal-close { background:none; border:none; color:var(--text-muted); font-size:20px; cursor:pointer; padding:4px 8px; border-radius:4px; }
    .fd-modal-close:hover { background:var(--bg-secondary); color:var(--text-primary); }

    .fd-scene-select { display:flex; gap:6px; margin-bottom:8px; flex-wrap:wrap; }
    .fd-scene-btn { padding:5px 12px; font-size:12px; border:1px solid var(--border-subtle); border-radius:5px; background:var(--bg-secondary); color:var(--text-secondary); cursor:pointer; transition:all 0.2s; }
    .fd-scene-btn.active { background:var(--cyan-dim); border-color:var(--cyan); color:var(--cyan); }
    .fd-scene-btn:hover { border-color:var(--border-glow); color:var(--text-primary); }

    .fd-code-col, .fd-canvas-col { display:flex; flex-direction:column; }
    .fd-col-label { font-size:11px; color:var(--text-muted); margin-bottom:4px; font-weight:600; letter-spacing:0.5px; }
    .fd-code-lines { font-family:var(--font-mono); font-size:12px; line-height:1.7; background:var(--bg-deep); border-radius:6px; padding:8px; overflow:auto; max-height:320px; }
    .fd-codeline { padding:1px 8px; border-radius:3px; transition:all 0.3s; white-space:pre; }
    .fd-codeline.hl { background:rgba(0,212,255,0.2); border-left:3px solid var(--cyan); color:var(--cyan); font-weight:600; }
    .fd-codeline.dim { opacity:0.35; }
    .fd-code-col { flex:0 0 200px; max-height:340px; }

    .fd-narration-bar { display:flex; align-items:center; gap:8px; margin-top:8px; padding:8px 12px; background:var(--bg-secondary); border-radius:8px; flex-wrap:wrap; }
    .fd-narration-text { flex:1; font-size:13px; color:var(--text-primary); line-height:1.4; min-height:20px; }
    .fd-step-indicator { font-size:11px; color:var(--text-muted); min-width:50px; }
    .fd-step-btns { display:flex; gap:4px; flex-wrap:wrap; }
    .fd-btn { padding:5px 12px; font-size:12px; border:1px solid var(--border-subtle); border-radius:5px; background:var(--bg-card); color:var(--text-secondary); cursor:pointer; transition:all 0.2s; white-space:nowrap; }
    .fd-btn:hover { border-color:var(--border-glow); color:var(--text-primary); }
    .fd-btn.primary { background:var(--cyan-dim); border-color:var(--cyan); color:var(--cyan); }
    .fd-btn.primary:hover { box-shadow:0 0 8px var(--cyan-glow); }
    .fd-btn:disabled { opacity:0.4; cursor:default; }

    canvas { width:100%; height:280px; border-radius:6px; background:var(--bg-deep); }

    @media (max-width:768px) {
      .fd-modal-box { padding:10px; width:95%; }
      .fd-code-col { flex:0 0 140px !important; }
      canvas { height:200px; }
      .fd-narration-bar { flex-direction:column; align-items:stretch; }
      .fd-step-btns { justify-content:center; }
    }
  `;
  document.head.appendChild(style);
})();
