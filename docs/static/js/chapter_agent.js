/**
 * chapter_agent.js — 章节末智能体复盘系统
 * CG 星空 + 代码雨 + JJ 智能体对话
 * 根据错题和提问历史生成针对性题目
 */
const ChapterAgent = {
  state: {
    stage: 'init',        // init | intro | qa | done | closed
    chapterId: 8,
    overlay: null,
    canvas: null,
    ctx: null,
    width: 0, height: 0,
    stars: [],
    raindrops: [],
    animFrame: null,
    introTimer: null,

    // JJ avatar state
    jjVisible: false,
    jjPulse: 0,

    // Q&A state
    qHistory: [],
    currentQuestion: '',
    currentHint: '',
    currentTopic: '',
    questionCount: 0,
    totalExpected: 3,
    isSubmitting: false,
    waitingForConfirm: false,
    pendingNextQ: '',
    pendingNextHint: '',
  },

  // ── Public API ──

  open(chapterId) {
    if (this.state.stage !== 'init' && this.state.stage !== 'closed') return;
    this.state.chapterId = chapterId || 8;
    this.state.stage = 'init';
    this.state.qHistory = [];
    this.state.questionCount = 0;
    this.state.jjVisible = false;
    this.state.waitingForConfirm = false;
    this.state.pendingNextQ = '';
    this.state.pendingNextHint = '';

    // Pre-fetch blackboard data to warm context
    fetch('/api/agent-blackboard').catch(() => {});

    this._createOverlay();
    this._initCanvas();
    this._initStars();
    this._initCodeRain();
    this._startIntro();
  },

  close() {
    this.state.stage = 'closed';
    if (this.state.introTimer) { clearTimeout(this.state.introTimer); this.state.introTimer = null; }
    if (this.state.animFrame) { cancelAnimationFrame(this.state.animFrame); this.state.animFrame = null; }
    if (this.state.overlay) {
      this.state.overlay.style.opacity = '0';
      setTimeout(() => {
        if (this.state.overlay) {
          this.state.overlay.remove();
          this.state.overlay = null;
        }
      }, 500);
    }
    // Clean up key listener
    if (this._boundEscKey) {
      document.removeEventListener('keydown', this._boundEscKey);
      this._boundEscKey = null;
    }
  },

  // ── Overlay creation ──

  _createOverlay() {
    const existing = document.getElementById('chapter-agent-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.id = 'chapter-agent-overlay';
    overlay.className = 'agent-overlay';
    overlay.innerHTML = `
      <canvas id="agent-canvas"></canvas>
      <div class="agent-ui">
        <div class="agent-title" id="agent-title">
          <div class="agent-title-main">函数章节 · 复盘时刻</div>
          <div class="agent-title-sub">让 JJ 老师带你回顾本章重点</div>
        </div>
        <div class="agent-avatar" id="agent-avatar" style="opacity:0;">
          <div class="agent-avatar-ring">
            <div class="agent-avatar-inner">🧑‍🏫</div>
          </div>
          <div class="agent-avatar-name">JJ 老师</div>
        </div>
        <div class="agent-dialog" id="agent-dialog" style="opacity:0;">
          <div class="agent-dialog-content" id="agent-dialog-content">
            <div class="agent-thinking-dots" id="agent-thinking">
              <span>.</span><span>.</span><span>.</span>
            </div>
            <div class="agent-message" id="agent-message"></div>
          </div>
          <div class="agent-input-area" id="agent-input-area">
            <textarea id="agent-input" class="agent-input" placeholder="输入你的回答..." rows="2"></textarea>
            <button id="agent-submit-btn" class="agent-submit-btn" onclick="ChapterAgent._submitAnswer()">
              发送 ✦
            </button>
          </div>
          <div class="agent-progress" id="agent-progress">
            <span id="agent-progress-text"></span>
          </div>
          <div class="agent-next-btn" id="agent-next-btn" style="display:none;">
            <button onclick="ChapterAgent.close()" class="agent-cta-btn">
              🚀 进入下一章
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    this.state.overlay = overlay;

    // Enter animation + keyboard handlers
    requestAnimationFrame(() => { overlay.style.opacity = '1'; });

    // Enter to submit, Escape to close
    const input = document.getElementById('agent-input');
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this._submitAnswer();
        }
        if (e.key === 'Escape') this.close();
      });
    }
    document.addEventListener('keydown', this._boundEscKey = (e) => {
      if (e.key === 'Escape') this.close();
    });
  },

  _initCanvas() {
    this.state.canvas = document.getElementById('agent-canvas');
    if (!this.state.canvas) return;
    this.state.width = window.innerWidth;
    this.state.height = window.innerHeight;
    this.state.canvas.width = this.state.width;
    this.state.canvas.height = this.state.height;
    this.state.ctx = this.state.canvas.getContext('2d');
  },

  _initStars() {
    const stars = [];
    for (let i = 0; i < 250; i++) {
      stars.push({
        x: Math.random() * this.state.width,
        y: Math.random() * this.state.height,
        r: Math.random() * 2 + 0.5,
        alpha: Math.random() * 0.8 + 0.2,
        speed: Math.random() * 0.3 + 0.05,
        twinkleSpeed: Math.random() * 0.02 + 0.005,
        twinklePhase: Math.random() * Math.PI * 2,
      });
    }
    // Add a few shooting stars
    for (let i = 0; i < 5; i++) {
      stars.push({
        x: Math.random() * this.state.width,
        y: Math.random() * this.state.height * 0.3,
        r: 2.5,
        alpha: 0,
        speed: 3 + Math.random() * 2,
        twinkleSpeed: 0,
        twinklePhase: 0,
        shooting: true,
        shootingLife: Math.random(),
      });
    }
    this.state.stars = stars;
  },

  _initCodeRain() {
    const drops = [];
    const codeSnippets = [
      'def', 'return', 'lambda', 'map(', 'filter(', 'reduce(',
      'if', 'for', 'in', 'range(', 'print(', 'import',
      'class', 'self', 'True', 'False', 'None', 'yield',
      'global', 'nonlocal', '*args', '**kwargs',
      '->', ':=', '==', '!=', '>=', '<=',
      'a+b', 'x*2', 'n-1', 'fact()', 'square()',
      'add()', 'result', 'lambda x:', 'x%2==0',
      '[1,2,3]', '{}', '()', 'def fact(n):',
      'return n*fact(n-1)', 'map(lambda x:',
      'filter(lambda x:', 'reduce(lambda a,b:',
    ];
    const cols = Math.floor(this.state.width / 28);
    for (let i = 0; i < cols; i++) {
      drops.push({
        x: i * 28 + Math.random() * 14,
        y: Math.random() * this.state.height,
        speed: 0.8 + Math.random() * 1.5,
        length: 3 + Math.floor(Math.random() * 8),
        snippets: codeSnippets,
        alpha: 0.15 + Math.random() * 0.25,
        charOffsets: Array(8).fill(0).map(() => Math.floor(Math.random() * codeSnippets.length)),
      });
    }
    this.state.raindrops = drops;
  },

  // ── Intro Animation ──

  _startIntro() {
    this.state.stage = 'intro';
    this._animate();

    // After 1s show title
    this.state.introTimer = setTimeout(() => {
      const title = document.getElementById('agent-title');
      if (title) title.style.opacity = '1';
    }, 800);

    // After 3.5s transition to QA
    this.state.introTimer = setTimeout(() => {
      this._transitionToQA();
    }, 3500);
  },

  _transitionToQA() {
    this.state.stage = 'qa';

    // Hide title
    const title = document.getElementById('agent-title');
    if (title) title.style.opacity = '0';

    // Show JJ avatar
    this.state.jjVisible = true;
    const avatar = document.getElementById('agent-avatar');
    if (avatar) avatar.style.opacity = '1';

    // Show dialog
    const dialog = document.getElementById('agent-dialog');
    if (dialog) dialog.style.opacity = '1';

    // Start first question
    this._startFirstQuestion();
  },

  // ── Q&A Flow ──

  async _startFirstQuestion() {
    this._setThinking(true);
    try {
      const res = await fetch('/api/chapter-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'start',
          chapter_id: this.state.chapterId,
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || '请求失败');

      this.state.currentQuestion = data.content || '请解释一下什么是函数？';
      this.state.currentHint = data.hint || '想想函数的定义和用途';
      this.state.currentTopic = data.topic || '函数基础';
      this.state.totalExpected = data.total || 3;
      this.state.questionCount = 0;

      this._setThinking(false);
      this._showQuestion(this.state.currentQuestion, this.state.currentTopic);
    } catch (e) {
      this._setThinking(false);
      this._showQuestion('请解释一下什么是函数？你能用自己的话说说吗？', '函数定义');
      this.state.currentQuestion = '请解释一下什么是函数？你能用自己的话说说吗？';
      this.state.currentHint = '想想看，函数就像是一个小工具，把一些代码打包起来...';
      this.state.currentTopic = '函数定义';
    }
  },

  _submitAnswer() {
    if (this.state.isSubmitting || this.state.stage !== 'qa') return;
    const input = document.getElementById('agent-input');
    const btn = document.getElementById('agent-submit-btn');
    const answer = (input.value || '').trim();
    if (!answer) return;

    this.state.isSubmitting = true;
    input.disabled = true;
    btn.disabled = true;

    // Show user's answer in dialog
    this._appendMessage('user', answer);
    input.value = '';
    this._setThinking(true);

    this._callAgentAPI(answer);
  },

  async _callAgentAPI(answer) {
    const input = document.getElementById('agent-input');
    const btn = document.getElementById('agent-submit-btn');
    try {
      const res = await fetch('/api/chapter-agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'answer',
          chapter_id: this.state.chapterId,
          q_history: this.state.qHistory,
          current_question: this.state.currentQuestion,
          current_answer: answer,
          is_confirmation: this.state.waitingForConfirm || false,
        })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.error || '请求失败');

      this._setThinking(false);

      if (data.type === 'correct' || data.type === 'wrong') {
        const isCorrect = data.type === 'correct';
        // Record in history
        this.state.qHistory.push({
          q: this.state.currentQuestion,
          a: answer,
          correct: isCorrect,
          feedback: data.content || '',
          topic: this.state.currentTopic,
        });

        // Show feedback
        this._showFeedback(isCorrect, data.content);

        if (isCorrect) {
          // After correct, either next question or done
          if (data.next_question && !data.done) {
            setTimeout(() => {
              this.state.currentQuestion = data.next_question || '';
              this.state.currentHint = data.next_hint || '';
              this.state.currentTopic = data.next_topic || '函数基础';
              this._showQuestion(this.state.currentQuestion, this.state.currentTopic);
              this.state.isSubmitting = false;
              input.disabled = false;
              btn.disabled = false;
              input.focus();
            }, 2000);
          } else {
            // All done
            setTimeout(() => this._showDone(data.content || ''), 2000);
          }
        } else {
          // Wrong: show explanation with "你明白了吗，冒险者？"
          // Let the user respond before showing the repeat question
          this.state.isSubmitting = false;
          input.disabled = false;
          btn.disabled = false;
          input.placeholder = '输入"明白了，冒险者！"或"还是不太懂..."';
          input.focus();
          // Store the repeat question for when user confirms understanding
          this.state.pendingNextQ = data.next_question || '';
          this.state.pendingNextHint = data.next_hint || '';
          this.state.waitingForConfirm = true;
        }
      } else if (data.type === 'done') {
        // Done with all questions
        this.state.qHistory.push({
          q: this.state.currentQuestion,
          a: answer,
          correct: true,
          feedback: data.content || '',
          topic: this.state.currentTopic,
        });
        this._setThinking(false);
        setTimeout(() => this._showDone(data.content || ''), 1500);
      }
    } catch (e) {
      this._setThinking(false);
      this._showFeedback(false, '😅 网络开小差了，我们重新来一次吧！');
      setTimeout(() => {
        this.state.isSubmitting = false;
        input.disabled = false;
        btn.disabled = false;
        input.focus();
      }, 1500);
    }
  },

  _showQuestion(question, topic) {
    const msg = document.getElementById('agent-message');
    if (!msg) return;
    const topicTag = topic ? `<span class="agent-topic-tag">${topic}</span>` : '';
    msg.innerHTML = `${topicTag}<div class="agent-question-text">${this._escapeHtml(question)}</div>`;

    // Show input area, hide next btn
    const inputArea = document.getElementById('agent-input-area');
    const nextBtn = document.getElementById('agent-next-btn');
    if (inputArea) inputArea.style.display = 'flex';
    if (nextBtn) nextBtn.style.display = 'none';

    // Update progress
    this._updateProgress();

    // Reset input state
    const input = document.getElementById('agent-input');
    const btn = document.getElementById('agent-submit-btn');
    if (input) { input.disabled = false; input.placeholder = '输入你的回答...'; input.focus(); }
    if (btn) btn.disabled = false;
    this.state.isSubmitting = false;
    this.state.waitingForConfirm = false;
  },

  _showFeedback(isCorrect, text) {
    const msg = document.getElementById('agent-message');
    if (!msg) return;
    const icon = isCorrect ? '✨' : '💪';
    const color = isCorrect ? 'var(--green)' : 'var(--orange)';
    msg.innerHTML = `<div style="color:${color};font-size:18px;margin-bottom:6px;">${icon} ${isCorrect ? '回答正确！' : '再接再厉！'}</div>
      <div style="color:var(--text-secondary);line-height:1.6;">${this._escapeHtml(text)}</div>`;
  },

  _showDone(encouragement) {
    this.state.stage = 'done';
    const msg = document.getElementById('agent-message');
    if (!msg) return;
    msg.innerHTML = `
      <div class="agent-done-icon">🌟</div>
      <div class="agent-done-title">复盘完成！</div>
      <div class="agent-done-text">${this._escapeHtml(encouragement)}</div>
    `;

    const inputArea = document.getElementById('agent-input-area');
    const nextBtn = document.getElementById('agent-next-btn');
    const progress = document.getElementById('agent-progress');
    if (inputArea) inputArea.style.display = 'none';
    if (nextBtn) nextBtn.style.display = 'block';
    if (progress) progress.style.display = 'none';

    // Brighten stars
    this.state.stars.forEach(s => { s.alpha = Math.min(1, s.alpha + 0.3); });
  },

  _appendMessage(role, text) {
    const msg = document.getElementById('agent-message');
    if (!msg) return;
    const div = document.createElement('div');
    div.className = `agent-msg agent-msg-${role}`;
    div.textContent = text;
    msg.appendChild(div);
  },

  _setThinking(on) {
    const thinking = document.getElementById('agent-thinking');
    const msg = document.getElementById('agent-message');
    if (thinking) thinking.style.display = on ? 'flex' : 'none';
    if (msg && on) msg.innerHTML = '';
  },

  _updateProgress() {
    const el = document.getElementById('agent-progress-text');
    if (!el) return;
    const done = this.state.qHistory.filter(h => h.correct).length;
    el.textContent = `✨ ${'★'.repeat(done)}${'☆'.repeat(Math.max(0, this.state.totalExpected - done))}  ${done}/${this.state.totalExpected}`;
  },

  _escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  },

  // ── Render Loop ──

  _animate() {
    const { ctx, width, height, stars, raindrops } = this.state;
    if (!ctx) return;

    // Clear with trail effect
    ctx.fillStyle = 'rgba(5, 5, 20, 0.15)';
    ctx.fillRect(0, 0, width, height);

    // Draw nebula glow
    const grad = ctx.createRadialGradient(width * 0.3, height * 0.4, 0, width * 0.3, height * 0.4, width * 0.5);
    grad.addColorStop(0, 'rgba(100, 50, 180, 0.03)');
    grad.addColorStop(0.5, 'rgba(50, 30, 120, 0.02)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    const grad2 = ctx.createRadialGradient(width * 0.7, height * 0.6, 0, width * 0.7, height * 0.6, width * 0.4);
    grad2.addColorStop(0, 'rgba(0, 100, 180, 0.02)');
    grad2.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad2;
    ctx.fillRect(0, 0, width, height);

    // Draw stars
    const now = Date.now();
    stars.forEach(s => {
      if (s.shooting) {
        // Shooting star
        s.shootingLife += 0.008;
        s.x -= s.speed;
        s.y += s.speed * 0.3;
        s.alpha = Math.sin(s.shootingLife * Math.PI) * 0.8;
        if (s.shootingLife > 1 || s.x < 0 || s.y > height) {
          s.x = Math.random() * width;
          s.y = Math.random() * height * 0.3;
          s.shootingLife = 0;
        }
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(s.x + s.speed * 8, s.y - s.speed * 2);
        ctx.strokeStyle = `rgba(255,255,255,${s.alpha})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        return;
      }

      // Twinkle
      const alpha = s.alpha * (0.6 + 0.4 * Math.sin(now * s.twinkleSpeed + s.twinklePhase));
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(200, 220, 255, ${alpha})`;
      ctx.fill();
    });

    // Draw code rain
    const dimFactor = this.state.stage === 'intro' ? 1 : 0.4;
    if (this.state.stage !== 'done') {
      raindrops.forEach(d => {
        d.y += d.speed;
        if (d.y > height + 20) { d.y = -20; }
        d.alpha = (0.15 + Math.random() * 0.1) * dimFactor;

        ctx.font = '11px "Consolas", monospace';
        for (let j = 0; j < d.length; j++) {
          const sy = d.y - j * 22;
          if (sy < -10 || sy > height + 10) continue;
          const snippet = d.snippets[(d.charOffsets[j] + Math.floor(now / 3000)) % d.snippets.length];
          const fadeAlpha = d.alpha * (1 - j / d.length);
          ctx.fillStyle = `rgba(100, 200, 255, ${fadeAlpha * 0.6})`;
          ctx.fillText(snippet, d.x, sy);
        }
      });
    }

    // JJ avatar glow pulse
    if (this.state.jjVisible) {
      this.state.jjPulse += 0.03;
      const pulseAlpha = 0.3 + 0.15 * Math.sin(this.state.jjPulse);
      const avatarEl = document.getElementById('agent-avatar');
      if (avatarEl) {
        avatarEl.style.boxShadow = `0 0 ${30 + 20 * Math.sin(this.state.jjPulse)}px rgba(100, 150, 255, ${pulseAlpha})`;
      }
    }

    this.state.animFrame = requestAnimationFrame(() => this._animate());
  },
};
