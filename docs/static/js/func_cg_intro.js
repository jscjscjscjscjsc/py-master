/**
 * func_cg_intro.js — 函数章节 CG 开场动画
 * 神秘星空 + 流式代码 + 哲理性提示 + 函数定义
 */

const FuncCGIntro = {
  state: {
    active: false,
    stage: -1,      // -1=hidden, 0=stars, 1=code, 2=philosophy, 3=definition, 4=cta, 5=done
    charIdx: 0,
    lineIdx: 0,
    fadeAlpha: 0,
    stars: [],
    shootingStars: [],
    animId: null,
    autoTimer: null
  },

  stages: {
    code: {
      lines: [
        { text: 'def mystery(*args, **kwargs):', color: '#00d4ff', delay: 40 },
        { text: '    """Unlock the secrets of the universe."""', color: '#6c5ce7', delay: 30 },
        { text: '    return lambda x: sum(x) / len(x) if x else None', color: '#00e676', delay: 50 },
        { text: '', color: '#666', delay: 20 },
        { text: '@decorator', color: '#ff6b6b', delay: 30 },
        { text: 'def transform(data):', color: '#00d4ff', delay: 40 },
        { text: '    return [f(x) for x in data if predicate(x)]', color: '#ffd93d', delay: 50 },
        { text: '', color: '#666', delay: 20 },
        { text: 'result = map(lambda n: n**2, filter(lambda n: n%2==0, range(42)))', color: '#6c5ce7', delay: 50 },
        { text: '', color: '#666', delay: 20 },
        { text: 'with open("wisdom.txt") as f:', color: '#00d4ff', delay: 35 },
        { text: '    secrets = [line.strip() for line in f]', color: '#00e676', delay: 40 },
        { text: '', color: '#666', delay: 30 },
        { text: 'class Enigma:', color: '#ff6b6b', delay: 35 },
        { text: '    def __call__(self, x):', color: '#ffd93d', delay: 35 },
        { text: '        return x if x in self else self.guess(x)', color: '#6c5ce7', delay: 45 },
      ]
    },
    philosophy: [
      '函数不是代码，而是思维的容器。',
      '每一段函数，都是对混沌的一次优雅封装。',
      '真正的编程智慧，在于理解抽象的力量。',
      '把复杂藏起来，把简单露出来——这就是函数的哲学。'
    ],
    definition: '封装好的具有某项功能的代码块',
    cta: '准备好探索 Python 函数了吗，冒险者？'
  },

  open() {
    if (this.state.active) return;
    // Auto-start ambient music
    if (typeof AmbientMusic !== 'undefined') AmbientMusic.play();
    // Check if already shown this session
    if (sessionStorage.getItem('func_cg_shown')) {
      this._scrollToContent();
      return;
    }

    this.state.active = true;
    this.state.stage = -1;
    this.state.charIdx = 0;
    this.state.lineIdx = 0;
    this.state.fadeAlpha = 0;
    this.state.stars = [];
    this.state.shootingStars = [];

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'func-cg-overlay';
    overlay.innerHTML = `
      <canvas id="func-cg-canvas"></canvas>
      <div id="func-cg-content">
        <div id="func-cg-code"></div>
        <div id="func-cg-philosophy"></div>
        <div id="func-cg-definition"></div>
        <div id="func-cg-cta"></div>
      </div>
      <button id="func-cg-skip" onclick="FuncCGIntro.skip()">跳过 ›</button>
    `;
    document.body.appendChild(overlay);

    this._initStars();
    this._startAnim();
    this.state.stage = 0;

    // Auto-progress through stages
    setTimeout(() => this._nextStage(), 500); // → code
  },

  close() {
    this.state.active = false;
    if (this.state.animId) cancelAnimationFrame(this.state.animId);
    if (this.state.autoTimer) clearTimeout(this.state.autoTimer);
    const overlay = document.getElementById('func-cg-overlay');
    if (overlay) {
      overlay.style.transition = 'opacity 0.8s';
      overlay.style.opacity = '0';
      setTimeout(() => overlay.remove(), 800);
    }
    sessionStorage.setItem('func_cg_shown', 'true');
  },

  skip() {
    if (this.state.autoTimer) clearTimeout(this.state.autoTimer);
    this.close();
  },

  _scrollToContent() {
    const kp = document.querySelector('.kp-item');
    if (kp) {
      kp.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setTimeout(() => {
        const header = kp.querySelector('.kp-header');
        if (header) header.click();
      }, 500);
    }
  },

  _initStars() {
    const canvas = document.getElementById('func-cg-canvas');
    if (!canvas) return;
    const w = window.innerWidth, h = window.innerHeight;
    canvas.width = w; canvas.height = h;
    canvas.style.width = w + 'px'; canvas.style.height = h + 'px';

    this.state.stars = [];
    for (let i = 0; i < 200; i++) {
      this.state.stars.push({
        x: Math.random() * w, y: Math.random() * h,
        r: 0.5 + Math.random() * 1.5,
        alpha: 0.3 + Math.random() * 0.7,
        speed: 0.2 + Math.random() * 0.5,
        twinkle: Math.random() * Math.PI * 2
      });
    }
  },

  _nextStage() {
    if (!this.state.active) return;
    this.state.stage++;
    this.state.fadeAlpha = 0;
    this.state.charIdx = 0;
    this.state.lineIdx = 0;

    switch (this.state.stage) {
      case 1: // Code streaming
        this._streamCode();
        break;
      case 2: // Philosophy
        this._streamPhilosophy();
        break;
      case 3: // Definition
        this._showDefinition();
        break;
      case 4: // CTA
        this._showCTA();
        break;
      case 5: // Done
        setTimeout(() => this.close(), 3000);
        break;
    }
  },

  _streamCode() {
    if (!this.state.active) return;
    const container = document.getElementById('func-cg-code');
    if (!container) return;
    container.style.display = 'block';
    container.innerHTML = '';
    this.state.lineIdx = 0;
    this.state.charIdx = 0;

    const typeNextLine = () => {
      if (!this.state.active || this.state.stage !== 1) return;

      const lines = this.stages.code.lines;
      if (this.state.lineIdx >= lines.length) {
        // All lines done, move to next stage
        this.state.autoTimer = setTimeout(() => this._nextStage(), 2000);
        return;
      }

      const line = lines[this.state.lineIdx];
      if (line.text === '') {
        container.innerHTML += '<br>';
        this.state.lineIdx++;
        this.state.charIdx = 0;
        this.state.autoTimer = setTimeout(typeNextLine, line.delay);
        return;
      }

      if (this.state.charIdx === 0) {
        const el = document.createElement('div');
        el.className = 'cg-code-line';
        el.style.color = line.color;
        el.dataset.lineIdx = this.state.lineIdx;
        container.appendChild(el);
      }

      const currentEl = container.lastElementChild;
      if (currentEl && currentEl.dataset.lineIdx == this.state.lineIdx) {
        currentEl.textContent = line.text.substring(0, this.state.charIdx + 1) + '▌';
        this.state.charIdx++;

        if (this.state.charIdx >= line.text.length) {
          currentEl.textContent = line.text;
          this.state.lineIdx++;
          this.state.charIdx = 0;
          // Scroll to keep latest code visible
          container.scrollTop = container.scrollHeight;
          this.state.autoTimer = setTimeout(typeNextLine, line.delay);
        } else {
          this.state.autoTimer = setTimeout(typeNextLine, line.delay - 15 + Math.random() * 15);
        }
      }
    };

    typeNextLine();
  },

  _streamPhilosophy() {
    if (!this.state.active) return;
    const container = document.getElementById('func-cg-philosophy');
    if (!container) return;
    container.style.display = 'block';

    const lines = this.stages.philosophy;
    let idx = 0;
    let charPos = 0;

    const typeLine = () => {
      if (!this.state.active || this.state.stage !== 2) return;
      if (idx >= lines.length) {
        this.state.autoTimer = setTimeout(() => this._nextStage(), 2500);
        return;
      }

      if (charPos === 0) {
        const el = document.createElement('div');
        el.className = 'cg-philosophy-line';
        container.appendChild(el);
        // Fade in
        requestAnimationFrame(() => { el.style.opacity = '1'; });
      }

      const currentEl = container.lastElementChild;
      if (currentEl) {
        currentEl.textContent = lines[idx].substring(0, charPos + 1) + '▌';
        charPos++;

        if (charPos >= lines[idx].length) {
          currentEl.textContent = lines[idx];
          idx++;
          charPos = 0;
          this.state.autoTimer = setTimeout(typeLine, 1200);
        } else {
          this.state.autoTimer = setTimeout(typeLine, 50 + Math.random() * 30);
        }
      }
    };

    typeLine();
  },

  _showDefinition() {
    if (!this.state.active) return;
    const container = document.getElementById('func-cg-definition');
    if (!container) return;
    container.style.display = 'block';

    const text = this.stages.definition;
    let pos = 0;

    // Add decorative elements
    container.innerHTML = '<div class="cg-def-label">◈ 函数的定义 ◈</div><div class="cg-def-text"></div>';

    const typeDef = () => {
      if (!this.state.active || this.state.stage !== 3) return;
      const textEl = container.querySelector('.cg-def-text');
      if (!textEl) return;

      if (pos <= text.length) {
        textEl.textContent = text.substring(0, pos) + (pos < text.length ? '▌' : '');
        pos++;
        this.state.autoTimer = setTimeout(typeDef, 40 + Math.random() * 20);
      } else {
        // Flash cursor a few times then advance
        let flashCount = 0;
        const flash = () => {
          if (!this.state.active) return;
          textEl.textContent = text + (flashCount % 2 === 0 ? '▌' : '');
          flashCount++;
          if (flashCount < 6) {
            this.state.autoTimer = setTimeout(flash, 400);
          } else {
            textEl.textContent = text;
            this.state.autoTimer = setTimeout(() => this._nextStage(), 1500);
          }
        };
        this.state.autoTimer = setTimeout(flash, 300);
      }
    };

    typeDef();
  },

  _showCTA() {
    if (!this.state.active) return;
    const container = document.getElementById('func-cg-cta');
    if (!container) return;
    container.style.display = 'block';

    const text = this.stages.cta;
    let pos = 0;

    const typeCTA = () => {
      if (!this.state.active || this.state.stage !== 4) return;
      const el = container;
      if (pos <= text.length) {
        el.textContent = text.substring(0, pos) + (pos < text.length ? '▌' : '');
        pos++;
        this.state.autoTimer = setTimeout(typeCTA, 60 + Math.random() * 30);
      } else {
        this.state.autoTimer = setTimeout(() => this._nextStage(), 800);
      }
    };

    // Fade in
    container.style.opacity = '0';
    container.style.transition = 'opacity 1s';
    requestAnimationFrame(() => { container.style.opacity = '1'; });

    this.state.autoTimer = setTimeout(typeCTA, 1000);
  },

  _startAnim() {
    const tick = () => {
      if (!this.state.active) return;
      this._draw();
      this.state.animId = requestAnimationFrame(tick);
    };
    this.state.animId = requestAnimationFrame(tick);
  },

  _draw() {
    const canvas = document.getElementById('func-cg-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width, h = canvas.height;

    // Dark starry background with slight gradient
    const grad = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w * 0.7);
    grad.addColorStop(0, '#0a0e2a');
    grad.addColorStop(0.5, '#06081a');
    grad.addColorStop(1, '#020108');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Draw stars
    const now = Date.now() / 1000;
    this.state.stars.forEach(star => {
      const twinkle = Math.sin(now * star.speed + star.twinkle) * 0.3 + 0.7;
      const alpha = star.alpha * twinkle;
      ctx.beginPath();
      ctx.arc(star.x, star.y, star.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
      ctx.fill();
    });

    // Draw shooting stars
    if (Math.random() < 0.005) {
      this.state.shootingStars.push({
        x: Math.random() * w * 0.8, y: Math.random() * h * 0.3,
        dx: 4 + Math.random() * 3, dy: 3 + Math.random() * 2,
        life: 1, len: 60 + Math.random() * 40
      });
    }
    this.state.shootingStars = this.state.shootingStars.filter(s => {
      ctx.save();
      ctx.globalAlpha = s.life;
      ctx.strokeStyle = 'rgba(200, 220, 255, ' + s.life + ')';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(s.x - s.dx * 2, s.y - s.dy * 2);
      ctx.stroke();

      // Glow at head
      ctx.beginPath();
      ctx.arc(s.x, s.y, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 255, ${s.life * 0.8})`;
      ctx.fill();
      ctx.restore();

      s.x += s.dx;
      s.y += s.dy;
      s.life -= 0.008;
      return s.life > 0;
    });

    // Subtle nebula effect
    const nebulaAlpha = 0.03 + Math.sin(now * 0.1) * 0.01;
    ctx.save();
    ctx.globalAlpha = nebulaAlpha;
    const nebGrad = ctx.createRadialGradient(
      w * 0.3 + Math.sin(now * 0.05) * w * 0.1, h * 0.4, 0,
      w * 0.3, h * 0.4, w * 0.4
    );
    nebGrad.addColorStop(0, '#6c5ce7');
    nebGrad.addColorStop(1, 'transparent');
    ctx.fillStyle = nebGrad;
    ctx.fillRect(0, 0, w, h);

    const nebGrad2 = ctx.createRadialGradient(
      w * 0.7 + Math.sin(now * 0.07 + 2) * w * 0.1, h * 0.6, 0,
      w * 0.7, h * 0.6, w * 0.35
    );
    nebGrad2.addColorStop(0, '#00d4ff');
    nebGrad2.addColorStop(1, 'transparent');
    ctx.fillStyle = nebGrad2;
    ctx.fillRect(0, 0, w, h);
    ctx.restore();
  }
};
