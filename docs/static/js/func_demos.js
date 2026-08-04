/**
 * func_demos.js -- Canvas function call stack frame animation demos
 * Depends on func_interactive.js (fdTheme, fdCanvas) and fdEasing (defined herein)
 * Used for Chapter 8 interactive function visualization
 */

// ============================================================
// fdEasing -- Easing utility functions + timeline manager
// ============================================================
const fdEasing = {
  lerp(a, b, t) { return a + (b - a) * Math.min(Math.max(t, 0), 1); },
  easeInOut(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; },
  elasticOut(t) { if (t === 0 || t === 1) return t; const c4 = (2 * Math.PI) / 3; return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1; },
  bounceOut(t) { const n1 = 7.5625, d1 = 2.75; if (t < 1/d1) return n1*t*t; if (t < 2/d1) return n1*(t-=1.5/d1)*t+0.75; if (t < 2.5/d1) return n1*(t-=2.25/d1)*t+0.9375; return n1*(t-=2.625/d1)*t+0.984375; },
  Timeline(frames, duration, onComplete) {
    const startTime = performance.now(); let running = true;
    function tick() {
      if (!running) return;
      const elapsed = performance.now() - startTime;
      const t = Math.min(elapsed / duration, 1);
      frames.forEach(function(f) {
        const lt = (t - f.start) / (f.end - f.start);
        if (lt >= 0 && lt <= 1) f.onUpdate(fdEasing.easeInOut(lt));
      });
      if (t < 1) requestAnimationFrame(tick); else if (onComplete) onComplete();
    }
    tick();
    return { cancel: function() { running = false; } };
  }
};

// ============================================================
// StackFrameDemo -- Call stack frame visualization component
// ============================================================
const StackFrameDemo = {
  scenes: [
    {
      label: '两数相加',
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
        { label: '执行 a+b → result 存入栈帧', highlight: [1], data: { stack: [{ name: 'add', vars: { a: 3, b: 5, result: 8 }, active: true }] } },
        { label: 'return result → 返回值 8 飞出栈帧', highlight: [2], data: { stack: [{ name: 'add', vars: { a: 3, b: 5, result: 8 }, returning: 8 }], global: { x: null } } },
        { label: 'x = 8 → 赋值完成，栈帧销毁', highlight: [4], data: { stack: [], global: { x: 8 }, heap: { add: { type: 'function', params: 'a,b' } } } }
      ]
    },
    {
      label: '嵌套调用',
      code: [
        'def square(x):',
        '    return x * x',
        '',
        'result = square(add(2, 3))'
      ],
      steps: [
        { label: '堆中创建 square 函数对象', highlight: [0], data: { heap: { square: { type: 'function', params: 'x' } } } },
        { label: '调用 add(2,3) → 栈帧压入', highlight: [3], data: { stack: [{ name: 'add', vars: { a: 2, b: 3 }, active: true }] } },
        { label: 'add 返回 5 → 返回值飞出', highlight: [1], data: { stack: [{ name: 'add', vars: { a: 2, b: 3 }, returning: 5 }] } },
        { label: '调用 square(5) → 栈帧压入', highlight: [3], data: { stack: [{ name: 'square', vars: { x: 5 }, active: true }] } },
        { label: 'square 返回 25 → 返回值飞出', highlight: [1], data: { stack: [{ name: 'square', vars: { x: 5 }, returning: 25 }] } },
        { label: 'result = 25 → 赋值完成', highlight: [3], data: { stack: [], global: { result: 25 } } }
      ]
    },
    {
      label: '递归阶乘',
      code: [
        'def fact(n):',
        '    if n <= 1: return 1',
        '    return n * fact(n-1)',
        '',
        'print(fact(4))'
      ],
      steps: [
        { label: '堆中创建 fact 函数对象', highlight: [0], data: { heap: { fact: { type: 'function', params: 'n' } } } },
        { label: 'fact(4) 调用 → 栈帧压入', highlight: [4], data: { stack: [{ name: 'fact', vars: { n: 4 }, active: true }] } },
        { label: 'fact(3) 递归 → 新栈帧压入', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 }, active: true }] } },
        { label: 'fact(2) 递归 → 新栈帧压入', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 }, active: true }] } },
        { label: 'fact(1) → n<=1, 返回 1', highlight: [1], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 } }, { name: 'fact', vars: { n: 1 }, active: true }] } },
        { label: 'fact(1) = 1 → 返回值飞出', highlight: [1], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2 } }, { name: 'fact', vars: { n: 1, result: 1 }, returning: 1 }] } },
        { label: 'fact(2) = 2*1 = 2 → 返回值飞出', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3 } }, { name: 'fact', vars: { n: 2, result: 2 }, returning: 2 }] } },
        { label: 'fact(3) = 3*2 = 6 → 返回值飞出', highlight: [2], data: { stack: [{ name: 'fact', vars: { n: 4 } }, { name: 'fact', vars: { n: 3, result: 6 }, returning: 6 }] } },
        { label: 'fact(4) = 4*6 = 24 → 完成', highlight: [4], data: { stack: [], global: { result: 24 }, heap: { fact: { type: 'function', params: 'n' } } } }
      ]
    }
  ],

  state: {
    sceneIdx: 0,
    stepIdx: 0,
    playing: false,
    animTimer: null,
    transitionProgress: 0,
    transitionStart: 0,
    transitionDuration: 600,
    canvas: null,
    ctx: null,
    width: 700,
    height: 450,
    animFrameId: null
  },

  open: function() {
    this.state.sceneIdx = 0;
    this.state.stepIdx = 0;
    this.state.playing = false;
    this.state.transitionProgress = 0;
    this.state.animTimer = null;
    this.state.animFrameId = null;
    this._setupCanvas();
    let modal = document.getElementById('func-modal-stack');
    if (modal) modal.classList.add('active');
    let self = this;
    setTimeout(function() {
      self._setupCanvas();
      self.render();
      self._updateUI();
    }, 50);
  },

  close: function() {
    this.state.playing = false;
    if (this.state.animTimer) {
      clearTimeout(this.state.animTimer);
      this.state.animTimer = null;
    }
    if (this.state.animFrameId) {
      cancelAnimationFrame(this.state.animFrameId);
      this.state.animFrameId = null;
    }
    let modal = document.getElementById('func-modal-stack');
    if (modal) modal.classList.remove('active');
  },

  _setupCanvas: function() {
    let canvas = document.getElementById('stack-canvas');
    if (!canvas) return;
    canvas.style.width = this.state.width + 'px';
    canvas.style.height = this.state.height + 'px';
    this.state.canvas = canvas;
    this.state.ctx = fdCanvas.setup(canvas, this.state.width, this.state.height);
  },

  render: function() {
    let ctx = this.state.ctx;
    if (!ctx) return;
    let w = this.state.width;
    let h = this.state.height;
    let scene = this.scenes[this.state.sceneIdx];
    let step = scene && scene.steps[this.state.stepIdx];
    if (!scene || !step) return;
    let t = this.state.transitionProgress;

    fdCanvas.clear(ctx, w, h);
    this._drawBackground(ctx, w, h);
    this._drawCodeArea(ctx, w, scene.code, step.highlight, t);
    this._drawZones(ctx, w, step.data, t);
    this._drawFooter(ctx, w, step.label);
  },

  _drawBackground: function(ctx, w, h) {
    // Full background
    ctx.save();
    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  },

  _drawCodeArea: function(ctx, w, codeLines, highlightLines, t) {
    let codeH = 124;
    let lineH = 19;
    let padLeft = 36;
    let padTop = 8;

    // Background
    fdCanvas.roundRect(ctx, 4, 4, w - 8, codeH - 4, 6,
      fdTheme.get('--bg-deep'), fdTheme.get('--border-subtle'));

    // Title label
    ctx.save();
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '9px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('▶ Code Execution', 12, 6);
    ctx.restore();

    // Code rendering
    ctx.save();
    ctx.font = '12px Consolas, "Microsoft YaHei", monospace';
    ctx.textBaseline = 'middle';

    let now = Date.now() / 1000;

    for (let i = 0; i < codeLines.length; i++) {
      let line = codeLines[i];
      let y = padTop + 6 + i * lineH;
      let isHighlighted = highlightLines && highlightLines.indexOf(i) !== -1;

      if (isHighlighted) {
        // Pulse effect using sin wave
        let pulse = 0.5 + 0.5 * Math.sin(now * 4);
        let alpha = 0.12 + pulse * 0.12;

        // Highlight background
        ctx.fillStyle = 'rgba(0, 212, 255, ' + alpha + ')';
        ctx.fillRect(padLeft - 4, y - lineH / 2, w - padLeft - 14, lineH);

        // Left accent bar
        ctx.fillStyle = 'rgba(0, 212, 255, ' + (0.5 + pulse * 0.5) + ')';
        ctx.fillRect(padLeft - 4, y - lineH / 2, 3, lineH);
      }

      // Line number
      ctx.textAlign = 'right';
      ctx.fillStyle = isHighlighted ? 'rgba(0, 212, 255, 0.7)' : fdTheme.get('--text-muted');
      ctx.globalAlpha = isHighlighted ? 1 : 0.4;
      ctx.fillText(String(i + 1), padLeft - 8, y);
      ctx.globalAlpha = 1;

      // Code text
      ctx.textAlign = 'left';
      ctx.fillStyle = isHighlighted ? fdTheme.colors.cyan : fdTheme.get('--text-primary');
      ctx.globalAlpha = isHighlighted ? 1 : 0.6;
      ctx.fillText(line, padLeft + 6, y);
      ctx.globalAlpha = 1;
    }

    ctx.restore();
  },

  _drawZones: function(ctx, w, data, t) {
    let zoneY = 132;
    let zoneH = 260;
    let zoneBottom = zoneY + zoneH;

    let globalX = 6, globalW = 178;
    let stackX = 194, stackW = 300;
    let heapX = 504, heapW = 190;

    // Draw zone backgrounds with labels
    this._drawSingleZoneBg(ctx, 'Global (全局)', globalX, zoneY, globalW, zoneH, fdTheme.colors.cyan);
    this._drawSingleZoneBg(ctx, 'Call Stack (调用栈', stackX, zoneY, stackW, zoneH, fdTheme.colors.purple);
    this._drawSingleZoneBg(ctx, 'Heap (堆)', heapX, zoneY, heapW, zoneH, fdTheme.colors.green);

    // Vertical zone separators
    ctx.save();
    ctx.strokeStyle = fdTheme.get('--border-subtle');
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);
    ctx.globalAlpha = 0.4;
    ctx.beginPath();
    ctx.moveTo(stackX, zoneY + 24);
    ctx.lineTo(stackX, zoneBottom - 4);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(heapX, zoneY + 24);
    ctx.lineTo(heapX, zoneBottom - 4);
    ctx.stroke();
    ctx.restore();

    // --- Global Zone ---
    this._drawGlobalZone(ctx, globalX, zoneY, globalW, zoneH, data);

    // --- Stack Zone ---
    this._drawStackZone(ctx, stackX, zoneY, stackW, zoneH, data, t);

    // --- Heap Zone ---
    this._drawHeapZone(ctx, heapX, zoneY, heapW, zoneH, data);

    // --- Return value flying arc (during transition) ---
    if (t > 0 && t < 1 && data.stack) {
      this._drawReturnArc(ctx, w, zoneY, zoneH, globalX, globalW, stackX, stackW, data, t);
    }
  },

  _drawSingleZoneBg: function(ctx, label, x, y, w, h, accentColor) {
    fdCanvas.roundRect(ctx, x, y, w, h, 6,
      fdTheme.get('--bg-secondary'), fdTheme.get('--border-subtle'));

    ctx.save();
    ctx.fillStyle = accentColor;
    ctx.font = 'bold 11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, x + w / 2, y + 13);
    ctx.restore();
  },

  _drawGlobalZone: function(ctx, gx, gy, gw, gh, data) {
    if (data.global && Object.keys(data.global).length > 0) {
      let entries = Object.entries(data.global);
      entries.forEach(function(kv, i) {
        let name = kv[0];
        let val = kv[1];
        let boxY = gy + 32 + i * 32;
        fdCanvas.roundRect(ctx, gx + 8, boxY, gw - 16, 26, 4,
          fdTheme.get('--bg-card'), fdTheme.get('--border-subtle'));
        fdCanvas.text(ctx, name + ' = ' + String(val),
          gx + gw / 2, boxY + 13,
          val === null ? fdTheme.get('--text-muted') : fdTheme.colors.cyan, 11);
      });
    } else {
      ctx.save();
      ctx.fillStyle = fdTheme.get('--text-muted');
      ctx.globalAlpha = 0.25;
      ctx.font = '11px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('📦 暂无全局变量', gx + gw / 2, gy + gh / 2);
      ctx.restore();
    }
  },

  _drawStackZone: function(ctx, sx, sy, sw, sh, data, t) {
    let zoneBottom = sy + sh;

    if (data.stack && data.stack.length > 0) {
      let frameW = sw - 24;
      let frameH = 58;
      let frameGap = 4;
      let totalFramesH = data.stack.length * (frameH + frameGap) - frameGap;
      let frameY = zoneBottom - 10 - totalFramesH;

      let self = this;

      ctx.save();
      data.stack.forEach(function(frame, fi) {
        let isReturning = frame.returning !== undefined;
        let isActive = frame.active;

        // Elastic slide-in during transition for non-returning frames
        let offset = 0;
        if (t > 0 && t < 1 && !isReturning) {
          let frameT = Math.max((t - fi * 0.08) * 1.2, 0);
          if (frameT < 1) {
            offset = (1 - fdEasing.elasticOut(Math.min(frameT, 1))) * 100;
          }
        }

        let fx = sx + 12 + offset;
        let fillColor = isActive
          ? fdTheme.get('--purple-dim')
          : isReturning
            ? fdTheme.get('--orange-dim')
            : fdTheme.get('--bg-card');
        let borderColor = isActive
          ? fdTheme.colors.purple
          : isReturning
            ? fdTheme.colors.orange
            : fdTheme.get('--border-subtle');

        fdCanvas.roundRect(ctx, fx, frameY, frameW, frameH, 6, fillColor, borderColor);

        // Frame name label
        ctx.fillStyle = isActive ? fdTheme.colors.purple : (isReturning ? fdTheme.colors.orange : fdTheme.get('--text-secondary'));
        ctx.font = 'bold 11px "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        let prefix = isReturning ? '→ ' : '';
        ctx.fillText(prefix + frame.name + '()', fx + 8, frameY + 14);

        // Local variables
        if (frame.vars) {
          let vx = fx + 10;
          let entries = Object.entries(frame.vars);
          entries.forEach(function(kv, vi) {
            if (vi < 4) {
              let vy = frameY + 32 + (vi % 2) * 16;
              ctx.fillStyle = fdTheme.get('--text-primary');
              ctx.font = '10px Consolas, "Microsoft YaHei", monospace';
              ctx.textAlign = 'left';
              ctx.textBaseline = 'middle';
              ctx.fillText(kv[0] + ' = ' + String(kv[1]), vx, vy);
              if (vi % 2 === 1 || vi === entries.length - 1) {
                vx = fx + 10;
              } else {
                vx += frameW / 2;
              }
            }
          });
        }

        // Returning value badge (visible after transition completes)
        if (isReturning && t >= 1) {
          fdCanvas.roundRect(ctx, fx + frameW - 46, frameY + 4, 40, 20, 4,
            fdTheme.get('--green-dim'), fdTheme.colors.green);
          fdCanvas.text(ctx, String(frame.returning) + ' →', fx + frameW - 26, frameY + 14,
            fdTheme.colors.green, 10);
        }

        frameY += frameH + frameGap;
      });
      ctx.restore();
    } else {
      ctx.save();
      ctx.fillStyle = fdTheme.get('--text-muted');
      ctx.globalAlpha = 0.25;
      ctx.font = '11px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('📭 调用栈为空', sx + sw / 2, sy + sh / 2);
      ctx.restore();
    }
  },

  _drawHeapZone: function(ctx, hx, hy, hw, hh, data) {
    if (data.heap && Object.keys(data.heap).length > 0) {
      let entries = Object.entries(data.heap);
      let self = this;
      entries.forEach(function(kv, i) {
        let name = kv[0];
        let obj = kv[1];
        let boxY = hy + 32 + i * 68;
        fdCanvas.roundRect(ctx, hx + 8, boxY, hw - 16, 60, 6,
          fdTheme.get('--green-dim'), fdTheme.colors.green);

        ctx.save();
        ctx.fillStyle = fdTheme.colors.green;
        ctx.font = 'bold 12px "Microsoft YaHei", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('📦 ' + name, hx + hw / 2, boxY + 18);
        ctx.fillStyle = fdTheme.get('--text-muted');
        ctx.font = '10px Consolas, "Microsoft YaHei", monospace';
        ctx.fillText('fn(' + obj.params + ')', hx + hw / 2, boxY + 36);
        ctx.fillStyle = fdTheme.get('--text-muted');
        ctx.font = '9px sans-serif';
        ctx.globalAlpha = 0.6;
        ctx.fillText('type: ' + obj.type, hx + hw / 2, boxY + 52);
        ctx.restore();
      });
    } else {
      ctx.save();
      ctx.fillStyle = fdTheme.get('--text-muted');
      ctx.globalAlpha = 0.25;
      ctx.font = '11px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('📦 暂无对象', hx + hw / 2, hy + hh / 2);
      ctx.restore();
    }
  },

  _drawReturnArc: function(ctx, w, zoneY, zoneH, globalX, globalW, stackX, stackW, data, t) {
    let zoneBottom = zoneY + zoneH;

    // Find the returning frame
    let returningFrame = null;
    let frameIdx = -1;
    if (data.stack) {
      for (let i = 0; i < data.stack.length; i++) {
        if (data.stack[i].returning !== undefined) {
          returningFrame = data.stack[i];
          frameIdx = i;
          break;
        }
      }
    }

    if (!returningFrame) return;

    // Calculate start position (center of returning stack frame)
    let frameW = stackW - 24;
    let frameH = 58;
    let frameGap = 4;
    let totalFramesH = data.stack.length * (frameH + frameGap) - frameGap;
    let frameY = zoneBottom - 10 - totalFramesH;
    // Add offset for this specific frame
    for (let j = 0; j < frameIdx; j++) {
      frameY += frameH + frameGap;
    }

    let sx = stackX + 12 + frameW / 2;
    let sy = frameY + frameH / 2;

    // End position (fly toward global zone or right side)
    let ex = globalX + globalW / 2;
    let ey = zoneY + 50;

    // Arc parameters
    let arcH = -70;
    let ct = fdEasing.easeInOut(t);

    // Current position along arc
    let cx = fdEasing.lerp(sx, ex, ct);
    let cy = sy + (ey - sy) * ct + Math.sin(ct * Math.PI) * arcH;

    // Draw trail dots
    let trailSteps = 10;
    for (let k = 0; k < trailSteps; k++) {
      let trailT = Math.max(ct - (k + 1) * 0.03, 0);
      if (trailT <= 0) continue;
      let tx = fdEasing.lerp(sx, ex, trailT);
      let ty = sy + (ey - sy) * trailT + Math.sin(trailT * Math.PI) * arcH;
      let trailAlpha = (1 - k / trailSteps) * 0.35;
      let trailRadius = (1 - k / trailSteps) * 2.5 + 1;

      ctx.save();
      ctx.globalAlpha = trailAlpha;
      ctx.fillStyle = fdTheme.colors.orange;
      ctx.beginPath();
      ctx.arc(tx, ty, trailRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Main fly dot
    ctx.save();
    ctx.shadowColor = fdTheme.colors.orange;
    ctx.shadowBlur = 14;
    ctx.fillStyle = fdTheme.colors.orange;
    ctx.beginPath();
    ctx.arc(cx, cy, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Value label on dot
    ctx.save();
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,0,0,0.6)';
    ctx.shadowBlur = 4;
    ctx.fillText(String(returningFrame.returning), cx, cy);
    ctx.restore();

    // Flying arrow trail line
    ctx.save();
    ctx.strokeStyle = fdTheme.colors.orange;
    ctx.globalAlpha = 0.15;
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 6]);
    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(cx, cy);
    ctx.stroke();
    ctx.restore();
  },

  _drawFooter: function(ctx, w, label) {
    let fy = 398;
    let fh = 48;

    fdCanvas.roundRect(ctx, 4, fy, w - 8, fh - 4, 6,
      fdTheme.get('--bg-deep'), fdTheme.get('--border-subtle'));

    // Step label
    ctx.save();
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = '13px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('▶ ' + label, w / 2 - 40, fy + fh / 2);
    ctx.restore();

    // Scene + step counter on the right
    let scene = this.scenes[this.state.sceneIdx];
    let step = scene && scene.steps[this.state.stepIdx];
    if (!scene || !step) return;
    ctx.save();
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.fillText(scene.label + '  |  Step ' + (this.state.stepIdx + 1) + '/' + scene.steps.length,
      w - 16, fy + fh / 2);
    ctx.restore();

    // Progress dots on the left
    let totalSteps = scene.steps.length;
    let dotStartX = 20;
    ctx.save();
    for (let i = 0; i < totalSteps; i++) {
      let dx = dotStartX + i * 16;
      let dy = fy + fh / 2;
      let isActive = i === this.state.stepIdx;
      ctx.fillStyle = isActive ? fdTheme.colors.cyan : fdTheme.get('--border-subtle');
      ctx.globalAlpha = isActive ? 1 : 0.35;
      ctx.beginPath();
      ctx.arc(dx, dy, isActive ? 5 : 3, 0, Math.PI * 2);
      ctx.fill();

      if (isActive) {
        // Glow ring around active dot
        ctx.globalAlpha = 0.2;
        ctx.strokeStyle = fdTheme.colors.cyan;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(dx, dy, 8, 0, Math.PI * 2);
        ctx.stroke();
      }
    }
    ctx.restore();
  },

  _updateUI: function() {
    let stepLabel = document.getElementById('stack-step-label');
    let stepCounter = document.getElementById('stack-step-counter');
    let btnPrev = document.getElementById('stack-btn-prev');
    let btnNext = document.getElementById('stack-btn-next');
    let btnPlay = document.getElementById('stack-btn-play');
    let scene = this.scenes[this.state.sceneIdx];
    let step = scene && scene.steps[this.state.stepIdx];
    if (!scene || !step) return;

    if (stepLabel) stepLabel.textContent = step.label;
    if (stepCounter) stepCounter.textContent = 'Step ' + (this.state.stepIdx + 1) + ' / ' + scene.steps.length;
    if (btnPrev) btnPrev.disabled = this.state.stepIdx <= 0;
    if (btnNext) btnNext.disabled = this.state.stepIdx >= scene.steps.length - 1;
    if (btnPlay) btnPlay.textContent = this.state.playing ? '⏸ 暂停' : '▶ 播放';
  },

  stepNext: function() {
    let scene = this.scenes[this.state.sceneIdx];
    if (this.state.stepIdx >= scene.steps.length - 1) return;

    this.state.stepIdx++;
    this.state.transitionProgress = 0.001;
    this.state.transitionStart = performance.now();

    let self = this;

    function animate() {
      let elapsed = performance.now() - self.state.transitionStart;
      let progress = Math.min(elapsed / self.state.transitionDuration, 1);
      self.state.transitionProgress = progress;
      self.render();
      if (progress < 1) {
        self.state.animFrameId = requestAnimationFrame(animate);
      } else {
        self.state.transitionProgress = 0;
        self.state.animFrameId = null;
        self.render();
        self._updateUI();
      }
    }

    if (this.state.animFrameId) {
      cancelAnimationFrame(this.state.animFrameId);
    }
    this.state.animFrameId = requestAnimationFrame(animate);
    this._updateUI();
  },

  stepPrev: function() {
    if (this.state.stepIdx <= 0) return;

    if (this.state.animFrameId) {
      cancelAnimationFrame(this.state.animFrameId);
      this.state.animFrameId = null;
    }
    this.state.transitionProgress = 0;

    this.state.stepIdx--;
    this.render();
    this._updateUI();
  },

  play: function() {
    if (this.state.playing) {
      this.state.playing = false;
      if (this.state.animTimer) {
        clearTimeout(this.state.animTimer);
        this.state.animTimer = null;
      }
      this._updateUI();
      return;
    }

    let scene = this.scenes[this.state.sceneIdx];
    if (this.state.stepIdx >= scene.steps.length - 1) {
      this.state.stepIdx = 0;
      this.state.animProgress = 0;
      this.render();
      this._updateUI();
      return;
    }
    this.state.playing = true;
    this._updateUI();
    this._autoAdvance();
  },

  _autoAdvance: function() {
    if (!this.state.playing) return;

    let self = this;
    let scene = this.scenes[this.state.sceneIdx];

    this.stepNext();

    this.state.animTimer = setTimeout(function() {
      if (!self.state.playing) return;
      if (self.state.stepIdx >= scene.steps.length - 1) {
        self.state.playing = false;
        self._updateUI();
        return;
      }
      self._autoAdvance();
    }, 1800);
  },

  reset: function() {
    if (this.state.animFrameId) {
      cancelAnimationFrame(this.state.animFrameId);
      this.state.animFrameId = null;
    }
    if (this.state.animTimer) {
      clearTimeout(this.state.animTimer);
      this.state.animTimer = null;
    }
    this.state.playing = false;
    this.state.transitionProgress = 0;
    this.state.stepIdx = 0;
    this.render();
    this._updateUI();
  },

  changeScene: function(idx) {
    if (idx < 0 || idx >= this.scenes.length) return;
    if (this.state.animFrameId) {
      cancelAnimationFrame(this.state.animFrameId);
      this.state.animFrameId = null;
    }
    if (this.state.animTimer) {
      clearTimeout(this.state.animTimer);
      this.state.animTimer = null;
    }
    this.state.playing = false;
    this.state.transitionProgress = 0;
    this.state.stepIdx = 0;
    this.state.sceneIdx = idx;
    this.render();
    this._updateUI();
  }
};

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

  state: {
    sceneIdx: 0,
    stepIdx: 0,
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
    const modal = document.getElementById('func-modal-param');
    if (modal) modal.classList.add('active');
    setTimeout(() => this._setupCanvas(), 100);
    this._updateUI();
  },

  close() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    const modal = document.getElementById('func-modal-param');
    if (modal) modal.classList.remove('active');
  },

  _setupCanvas() {
    this.state.canvas = document.getElementById('param-canvas');
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

    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, width, height);

    // Top: function signature and call code
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, 0, width, 60);
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = 'bold 14px "Consolas", "Courier New", monospace';
    ctx.textAlign = 'left';
    ctx.fillText(scene.signature, 16, 26);
    ctx.fillStyle = fdTheme.get('--text-secondary');
    ctx.font = '13px "Consolas", monospace';
    ctx.fillText(scene.code, 16, 48);

    ctx.fillStyle = fdTheme.get('--border-subtle');
    ctx.fillRect(0, 60, width, 1);

    // Left: parameter slots
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📥 形参', 200, 90);

    scene.params.forEach((p) => {
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
        ctx.fillText('=' + p.default, p.x + 10, sy + 20);
      }
    });

    // Right: argument balls
    ctx.fillStyle = fdTheme.get('--text-muted');
    ctx.font = '11px "Microsoft YaHei", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('📤 实参', width - 100, 90);

    scene.args.forEach((arg) => {
      const target = scene.params[arg.target];
      const startX = arg.x, startY = arg.y;
      const endX = target.x, endY = target.y;
      const radius = 14;

      let ax, ay, progress;
      if (stepIdx === 0) {
        ax = startX; ay = startY; progress = 0;
      } else if (stepIdx >= 1 && animProgress > 0) {
        progress = stepIdx >= 2 ? 1 : Math.min(animProgress, 1);
        const eased = fdEasing.bounceOut(progress);
        ax = fdEasing.lerp(startX, endX, eased);
        ay = fdEasing.lerp(startY, endY, eased) - 20 * Math.sin(eased * Math.PI) * (1 - eased);
      } else {
        return;
      }

      ctx.fillStyle = arg.color;
      ctx.shadowColor = arg.color + '60';
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.arc(ax, ay, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      if (arg.label && progress < 1) {
        ctx.fillStyle = fdTheme.get('--text-secondary');
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(arg.label, ax, ay - 22);
      }

      ctx.fillStyle = '#fff';
      ctx.font = 'bold 11px "Consolas", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(arg.value, ax, ay + 4);

      if (progress >= 1) {
        ctx.strokeStyle = fdTheme.colors.green + '60';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(ax, ay, radius + 8, 0, Math.PI * 2);
        ctx.stroke();
      }
    });

    // Result label
    if (stepIdx >= 2) {
      ctx.fillStyle = scene.error ? fdTheme.colors.red + '20' : fdTheme.colors.green + '20';
      fdCanvas.roundRect(ctx, width / 2 - 150, 370, 300, 36, 8, ctx.fillStyle);
      ctx.fillStyle = scene.error ? fdTheme.colors.red : fdTheme.colors.green;
      ctx.font = 'bold 14px "Microsoft YaHei", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(scene.resultLabel, width / 2, 393);
    }
  },

  stepNext() {
    if (this.state.stepIdx < 2) {
      this.state.stepIdx++;
      this.state.animProgress = 0;
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
    const el = document.getElementById('param-scene-title');
    if (el) el.textContent = scene.title;
    const btn = document.getElementById('param-play-btn');
    if (btn) btn.textContent = this.state.playing ? '⏸' : '▶';
  },
};

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
    const modal = document.getElementById('func-modal-hof');
    if (modal) modal.classList.add('active');
    setTimeout(() => this._setupCanvas(), 100);
    this._updateUI();
  },

  close() {
    this.state.playing = false;
    if (this.state.animTimeline) { this.state.animTimeline.cancel(); }
    const modal = document.getElementById('func-modal-hof');
    if (modal) modal.classList.remove('active');
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

    ctx.fillStyle = fdTheme.get('--bg-primary');
    ctx.fillRect(0, 0, width, height);

    // Top code area
    ctx.fillStyle = fdTheme.get('--bg-secondary');
    ctx.fillRect(0, 0, width, 50);
    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = '13px "Consolas", monospace';
    ctx.textAlign = 'left';
    ctx.fillText(scene.code, 16, 32);

    ctx.fillStyle = fdTheme.get('--border-subtle');
    ctx.fillRect(0, 50, width, 1);

    if (activeTab === 'map') {
      this._drawMapScene(ctx, width, height, scene, animProgress);
    } else if (activeTab === 'filter') {
      this._drawFilterScene(ctx, width, height, scene, animProgress);
    } else if (activeTab === 'reduce') {
      this._drawReduceScene(ctx, width, height, scene, animProgress);
    }

    // Bottom description
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

    // Lambda module
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

    const processedCount = t * totalItems;

    for (let i = 0; i < totalItems; i++) {
      const isProcessed = i < processedCount;
      const x = startX + (i + 1) * spacing;

      if (isProcessed) {
        const outX = modX + modW + 30 + (i - Math.floor(processedCount - 1)) * (spacing - 10);
        if (outX < width - 40) {
          ctx.fillStyle = scene.color + '40';
          fdCanvas.roundRect(ctx, outX - boxW / 2, cy - boxH / 2, boxW, boxH, 4, ctx.fillStyle);
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 13px "Consolas", monospace';
          ctx.textAlign = 'center';
          ctx.fillText(String(scene.results[i]), outX, cy + 5);
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
        const inX = x;
        ctx.fillStyle = fdTheme.get('--text-secondary');
        fdCanvas.roundRect(ctx, inX - boxW / 2, cy - boxH / 2, boxW, boxH, 4, ctx.fillStyle, fdTheme.get('--border-subtle'));
        ctx.fillStyle = fdTheme.get('--text-primary');
        ctx.font = 'bold 13px "Consolas", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(String(scene.items[i]), inX, cy + 5);
        ctx.strokeStyle = fdTheme.get('--text-muted');
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(inX + boxW / 2, cy);
        ctx.lineTo(modX, cy);
        ctx.stroke();
        fdCanvas.arrow(ctx, inX + boxW / 2, cy, modX, cy, fdTheme.get('--text-muted'), 1.5);
      }
    }

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

    // Funnel shape
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

    ctx.fillStyle = scene.color;
    ctx.font = '13px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('🔍 filter: ' + scene.transform, width / 2, funnelTopY + 55);

    for (let i = 0; i < totalItems; i++) {
      const item = scene.items[i];
      const startX = 60 + i * ((width - 120) / (totalItems - 1));
      const isFiltered = scene.results.includes(item);
      const isProcessed = i < processedCount;

      if (isProcessed) {
        if (isFiltered) {
          const outY = funnelBottomY + 20 + i * 5;
          ctx.fillStyle = scene.color + '40';
          fdCanvas.roundRect(ctx, funnelX - 14, outY, 28, 24, 4, ctx.fillStyle);
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 12px "Consolas"';
          ctx.textAlign = 'center';
          ctx.fillText(String(item), funnelX, outY + 16);
          ctx.strokeStyle = scene.color + '30';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.moveTo(startX, 90);
          ctx.lineTo(funnelX, funnelBottomY);
          ctx.lineTo(funnelX, outY);
          ctx.stroke();
        } else {
          const sideX = i % 2 === 0 ? 30 : width - 30;
          ctx.fillStyle = fdTheme.colors.red + '40';
          ctx.beginPath();
          ctx.arc(sideX, 90 + i * 20, 10, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = '#fff';
          ctx.font = '10px "Consolas"';
          ctx.textAlign = 'center';
          ctx.fillText('✗', sideX, 95 + i * 20);
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
      steps.push({ merged: newVal });
    }

    const currentStep = Math.min(Math.floor(t * totalSteps), totalSteps - 1);
    const stepProgress = (t * totalSteps) - currentStep;
    const boxW = 36, boxH = 30;
    const startX = 60;
    const spacing = 50;
    const cy = 150;

    ctx.fillStyle = fdTheme.get('--text-primary');
    ctx.font = 'bold 13px "Consolas", monospace';
    ctx.textAlign = 'center';
    ctx.fillText('初始: ' + values.join(' + '), width / 2, 90);

    if (t === 0) {
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

    for (let i = 0; i < currentStep + 1; i++) {
      const step = steps[i];
      const pairX = startX + i * spacing;
      ctx.strokeStyle = scene.color + '60';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(pairX + spacing / 2, cy + boxH / 2 + 10, 10, 0, Math.PI);
      ctx.stroke();
      ctx.fillStyle = scene.color;
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(values[i] + '+' + values[i+1], pairX + spacing / 2, cy + boxH / 2 + 35);

      if (i === currentStep && stepProgress < 1) {
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
        ctx.strokeStyle = scene.color + '40';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(pairX + spacing / 2, cy + boxH / 2 + 15);
        ctx.lineTo(mx, my + 16);
        ctx.stroke();
      } else if (i < currentStep || (i === currentStep && stepProgress >= 1)) {
        const mx = startX + (i + 1) * spacing - boxW;
        ctx.fillStyle = scene.color + '40';
        fdCanvas.roundRect(ctx, mx - boxW / 2, cy - boxH / 2 - 40, boxW, boxH, 4, ctx.fillStyle);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 12px "Consolas"';
        ctx.textAlign = 'center';
        ctx.fillText(String(step.merged), mx, cy + 5 - 40);
      }
    }

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
      ctx.fillText('= ' + String(finalVal), fx, cy + 123);
      ctx.fillStyle = fdTheme.get('--text-secondary');
      ctx.font = '12px sans-serif';
      ctx.fillText('最终结果', fx, cy + 165);
    }
  },

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
    const btn = document.getElementById('hof-play-btn');
    if (btn) btn.textContent = this.state.playing ? '⏸' : '▶';
    document.querySelectorAll('.hof-tab-btn').forEach(btn => {
      const isActive = btn.dataset.tab === tab;
      btn.style.opacity = isActive ? '1' : '0.5';
      btn.style.borderColor = isActive ? 'var(--cyan)' : 'var(--border-subtle)';
    });
  },
};
