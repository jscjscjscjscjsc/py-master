/**
 * training.js — 刷题中心
 *
 * 两种模式共用一个「代码块运行器」：
 * - 练习模式：选题 → 写代码 → 随时看解析、随时问 JJ老师
 * - 实战模式：自由组卷 → 逐题作答（可跳过）→ 交卷后才解锁解析 → AI 批卷
 *
 * 三个容易翻车的地方，代码里都做了处理：
 * 1. 代码块要像 Jupyter 一样**逐块可运行**，且变量在块之间共享
 *    （后端把前面的块一起执行，只回传当前块的输出，见 /api/training/run-cell）；
 * 2. 运行/判题都是子进程，可能慢也可能超时，所以按钮必须锁住防连点；
 * 3. 实战模式下**绝对不能提前拿到答案**，题的详情由后端按模式裁剪。
 */
const Training = {
  mode: 'practice',
  track: 'course',
  chapters: new Set(),
  difficulty: '',
  only: '',
  catalog: [],
  questions: [],
  current: null,
  cells: [],
  editors: [],
  exam: null,
  examIndex: 0,
  examCursor: 0,
  usedAi: {},
  busy: false,
  draftTimer: null,

  el: {},

  async init() {
    this.el = {
      side: document.getElementById('wb-side'),
      list: document.getElementById('wb-list'),
      detail: document.getElementById('wb-detail'),
      tabs: document.querySelectorAll('.wb-tab'),
      title: document.getElementById('wb-title'),
    };
    document.querySelectorAll('.wb-tab').forEach((tab) => {
      tab.addEventListener('click', () => this.switchMode(tab.dataset.mode));
    });
    try {
      const last = localStorage.getItem('pymaster_training_track');
      if (last === 'course' || last === 'algorithm') this.track = last;
    } catch (e) {}
    // 支持从错题本 / 仪表盘深链进来：?q=题目ID 或 ?chapters=章节ID
    const params = new URLSearchParams(location.search);
    const chapterParam = params.get('chapters');
    if (chapterParam) {
      chapterParam.split(',').filter(Boolean).forEach((id) => this.chapters.add(String(id)));
    }
    await this.loadCatalog();
    this.renderSide();
    await this.loadQuestions();
    const questionParam = params.get('q');
    if (questionParam) await this.openQuestion(questionParam);
  },

  async api(url, options) {
    const response = await fetch(url, options);
    return response.json().catch(() => ({ success: false, message: '服务返回了非 JSON 内容' }));
  },

  toast(message) {
    if (window.UI && UI.toast) UI.toast(message);
    else if (window.Cultivation && Cultivation.toast) Cultivation.toast(message, '', 2400);
  },

  confirm(message, options) {
    if (window.UI && UI.confirm) return UI.confirm(message, options);
    return Promise.resolve(window.confirm(message));
  },

  async loadCatalog() {
    const data = await this.api('/api/training/catalog');
    if (data.success) this.catalog = data.chapters || [];
  },

  switchMode(mode) {
    if (this.mode === mode) return;
    this.mode = mode;
    this.current = null;
    this.exam = null;
    document.querySelectorAll('.wb-tab').forEach((tab) => {
      tab.classList.toggle('active', tab.dataset.mode === mode);
    });
    this.renderSide();
    if (mode === 'exam') this.renderExamSetup();
    else this.loadQuestions();
  },

  currentTrackChapters() {
    return this.catalog.filter((c) => c.track === this.track);
  },

  renderSide() {
    const side = this.el.side;
    if (!side) return;
    const trackChapters = this.currentTrackChapters();
    const total = trackChapters.reduce((sum, c) => sum + c.count, 0);
    const solved = trackChapters.reduce((sum, c) => sum + c.solved, 0);
    side.innerHTML = `
      <h3>题库赛道</h3>
      <div class="wb-seg">
        <button data-track="course" class="${this.track === 'course' ? 'active' : ''}">课程配套</button>
        <button data-track="algorithm" class="${this.track === 'algorithm' ? 'active' : ''}">算法与数据结构</button>
      </div>
      <h3>章节 / 专题（已通关 ${solved}/${total}）</h3>
      <div class="chapter-pick" id="chapter-pick">
        ${trackChapters.map((c) => `
          <div class="pick-row ${this.chapters.has(String(c.id)) ? 'on' : ''}" data-id="${c.id}">
            <span class="t">${c.icon ? c.icon + ' ' : ''}${this.esc(c.title)}</span>
            <span class="n ${c.solved ? 'done' : ''}">${c.solved}/${c.count}</span>
          </div>`).join('')}
      </div>
      <h3>难度</h3>
      <div class="wb-seg" id="diff-seg">
        <button data-diff="" class="${this.difficulty === '' ? 'active' : ''}">全部</button>
        <button data-diff="1" class="${this.difficulty === '1' ? 'active' : ''}">简单</button>
        <button data-diff="2" class="${this.difficulty === '2' ? 'active' : ''}">中等</button>
        <button data-diff="3" class="${this.difficulty === '3' ? 'active' : ''}">较难</button>
      </div>
      <h3>状态</h3>
      <div class="wb-seg" id="only-seg">
        <button data-only="" class="${this.only === '' ? 'active' : ''}">全部</button>
        <button data-only="unsolved" class="${this.only === 'unsolved' ? 'active' : ''}">未通关</button>
        <button data-only="wrong" class="${this.only === 'wrong' ? 'active' : ''}">错题</button>
      </div>
      <div class="wb-actions">
        <button class="wb-btn" id="pick-all">全选本章节</button>
        <button class="wb-btn" id="pick-clear">清空筛选</button>
      </div>`;

    side.querySelectorAll('[data-track]').forEach((button) => {
      button.addEventListener('click', () => {
        this.track = button.dataset.track;
        this.chapters.clear();
        try { localStorage.setItem('pymaster_training_track', this.track); } catch (e) {}
        this.renderSide();
        if (this.mode === 'exam') this.renderExamSetup();
        else this.loadQuestions();
      });
    });
    side.querySelectorAll('.pick-row').forEach((row) => {
      row.addEventListener('click', () => {
        const id = String(row.dataset.id);
        if (this.chapters.has(id)) this.chapters.delete(id);
        else this.chapters.add(id);
        row.classList.toggle('on');
        this.loadQuestions();
      });
    });
    side.querySelectorAll('[data-diff]').forEach((button) => {
      button.addEventListener('click', () => {
        this.difficulty = button.dataset.diff;
        side.querySelectorAll('[data-diff]').forEach((b) => b.classList.toggle('active', b === button));
        this.loadQuestions();
      });
    });
    side.querySelectorAll('[data-only]').forEach((button) => {
      button.addEventListener('click', () => {
        this.only = button.dataset.only;
        side.querySelectorAll('[data-only]').forEach((b) => b.classList.toggle('active', b === button));
        this.loadQuestions();
      });
    });
    const all = document.getElementById('pick-all');
    if (all) all.addEventListener('click', () => {
      this.currentTrackChapters().forEach((c) => this.chapters.add(String(c.id)));
      this.renderSide();
      this.loadQuestions();
    });
    const clear = document.getElementById('pick-clear');
    if (clear) clear.addEventListener('click', () => {
      this.chapters.clear();
      this.difficulty = '';
      this.only = '';
      this.renderSide();
      this.loadQuestions();
    });
  },

  async loadQuestions() {
    const params = new URLSearchParams();
    params.set('track', this.track);
    if (this.chapters.size) params.set('chapters', [...this.chapters].join(','));
    if (this.difficulty) params.set('difficulty', this.difficulty);
    if (this.only) params.set('only', this.only);
    const data = await this.api('/api/training/questions?' + params.toString());
    this.questions = data.questions || [];
    this.renderList();
  },

  renderList() {
    const list = this.el.list;
    if (!list) return;
    if (!this.questions.length) {
      list.innerHTML = '<div class="empty-note">这个范围里没有题目，换个章节或清空筛选试试。</div>';
      return;
    }
    list.innerHTML = this.questions.map((q, index) => {
      const stars = [1, 2, 3].map((n) => (n <= q.stars ? '★' : '<span class="off">★</span>')).join('');
      const cls = q.solved ? 'solved' : (q.wrong ? 'wrong' : '');
      return `<div class="qcard ${cls}" data-id="${q.id}">
        <div class="q-num">${String(index + 1).padStart(2, '0')}</div>
        <div class="q-body">
          <div class="q-title">${this.esc(q.title)}</div>
          <div class="q-tags">
            <span class="diff d${q.difficulty}">${q.difficulty === 1 ? '简单' : q.difficulty === 2 ? '中等' : '较难'}</span>
            <span>${this.esc(q.topic || '')}</span>
            ${q.wrong ? `<span style="color:var(--red)">错过 ${q.wrong} 次</span>` : ''}
          </div>
        </div>
        <div class="q-right"><span class="stars">${stars}</span></div>
      </div>`;
    }).join('');
    list.querySelectorAll('.qcard').forEach((card) => {
      card.addEventListener('click', () => this.openQuestion(card.dataset.id));
    });
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  },

  md(text) {
    return window.MdLite ? window.MdLite.toHtml(text) : this.esc(text);
  },

  // ── 题目详情 ────────────────────────────────────
  async openQuestion(questionId, options = {}) {
    const url = '/api/training/question/' + encodeURIComponent(questionId)
      + (options.examId ? '?exam_id=' + encodeURIComponent(options.examId) : '');
    const data = await this.api(url);
    if (!data.success) { this.toast(data.message || '打不开这道题'); return; }
    this.current = data.question;
    this.examId = options.examId || '';
    this.examCursor = options.cursor === undefined ? this.examCursor : options.cursor;
    const draft = (data.question.draft && data.question.draft.length)
      ? data.question.draft
      : [data.question.starter_code || ''];
    this.cells = draft.slice();
    this.renderDetail();
    const list = document.getElementById('wb-list');
    if (list) {
      // 列表收缩成窄栏并高亮当前题，详情就在下面，不用一路滚到底
      list.classList.add('compact');
      list.querySelectorAll('.qcard').forEach((card) => {
        const active = card.dataset.id === questionId;
        card.style.borderColor = active ? 'rgba(0,212,255,0.7)' : '';
        if (active) card.scrollIntoView({ block: 'nearest' });
      });
    }
    const detail = document.getElementById('wb-detail');
    if (detail && !options.keepScroll) detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },

  renderDetail() {
    const q = this.current;
    const detail = this.el.detail;
    if (!q || !detail) return;
    const blocked = !!q.blocked_reason;
    const stars = [1, 2, 3].map((n) => (n <= (q.stars || 0) ? '★' : '<span class="off">★</span>')).join('');
    detail.innerHTML = `
      <div class="qdetail">
        <div class="qdetail-head">
          <h2>${this.esc(q.title)}</h2>
          <div class="qdetail-meta">
            <span class="diff d${q.difficulty}">${q.difficulty_label}</span>
            <span class="q-pill">${this.esc(q.chapter_title || '')}</span>
            ${q.topic ? `<span class="q-pill">${this.esc(q.topic)}</span>` : ''}
            <span class="stars">${stars}</span>
            <span>已作答 ${q.attempts || 0} 次 · 通关 ${q.attempts && q.solved ? '是' : '否'}</span>
          </div>
        </div>
        <div class="q-statement">${this.md(q.statement)}</div>
        <div id="stdin-wrap" ${q.needs_input ? '' : 'hidden'}>
          <div class="stdin-head"><span>⌨ 测试输入</span><span class="stdin-tip">每行一个值，按顺序喂给 input()</span></div>
          <textarea class="stdin-box" id="stdin-box" placeholder="例如：&#10;83.5&#10;100"></textarea>
        </div>
        <div class="cells" id="cells"></div>
        <div class="q-toolbar">
          <button class="wb-btn tiny" id="cell-add">＋ 代码块</button>
          <button class="wb-btn tiny" id="run-all">▶ 全部运行</button>
          <button class="wb-btn tiny good" id="judge">✅ 提交判题</button>
          <button class="wb-btn tiny" id="hint">💡 提示</button>
          ${blocked
            ? '<span class="q-pill" style="border-color:rgba(210,153,34,0.5);color:var(--orange)">实战中：交卷后解锁解析</span>'
            : `<button class="wb-btn tiny" id="solution">📖 看解析</button>`}
          <span class="grow"></span>
          <button class="wb-btn tiny warn" id="ask-ai">🤖 问 JJ老师</button>
          ${this.examId ? '<button class="wb-btn tiny" id="skip">⏭ 跳过这题</button>' : ''}
          ${this.examId ? '<button class="wb-btn tiny primary" id="next-q">下一题 →</button>' : ''}
        </div>
        <div id="panels"></div>
      </div>`;
    this.mountCells();
    this.bindToolbar();
  },

  mountCells() {
    const box = document.getElementById('cells');
    if (!box) return;
    box.innerHTML = this.cells.map((code, index) => `
      <div class="cell" data-index="${index}">
        <div class="cell-head">
          <span class="c-label">In [${index + 1}]</span>
          <span class="c-spacer"></span>
          <button class="run" data-run="${index}">▶ 运行</button>
          ${this.cells.length > 1 ? `<button class="del" data-del="${index}">删除</button>` : ''}
        </div>
        <textarea class="cell-src" data-src="${index}"></textarea>
        <div class="cell-out" data-out="${index}"></div>
      </div>`).join('');

    this.editors = [];
    box.querySelectorAll('.cell').forEach((cellNode) => {
      const index = Number(cellNode.dataset.index);
      const textarea = cellNode.querySelector('textarea');
      const editor = CodeMirror.fromTextArea(textarea, {
        mode: 'python',
        theme: 'material-darker',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        autoCloseBrackets: true,
        styleActiveLine: true,
      });
      editor.setValue(this.cells[index] || '');
      editor.on('change', () => {
        this.cells[index] = editor.getValue();
        this.queueDraft();
      });
      // Ctrl/Cmd + Enter 跑当前块，这是 Jupyter 的手感
      editor.setOption('extraKeys', {
        'Ctrl-Enter': () => this.runCell(index),
        'Cmd-Enter': () => this.runCell(index),
      });
      this.editors[index] = editor;
    });

    box.querySelectorAll('[data-run]').forEach((button) => {
      button.addEventListener('click', () => this.runCell(Number(button.dataset.run)));
    });
    box.querySelectorAll('[data-del]').forEach((button) => {
      button.addEventListener('click', () => {
        const index = Number(button.dataset.del);
        this.cells.splice(index, 1);
        if (!this.cells.length) this.cells = [''];
        this.renderCells();
      });
    });
    setTimeout(() => this.editors.forEach((editor) => editor && editor.refresh()), 30);
  },

  renderCells() {
    this.mountCells();
    this.queueDraft();
  },

  bindToolbar() {
    const bind = (id, handler) => {
      const node = document.getElementById(id);
      if (node) node.addEventListener('click', handler);
    };
    bind('cell-add', () => { this.cells.push(''); this.renderCells(); });
    bind('run-all', () => this.runAll());
    bind('judge', () => this.submit());
    bind('hint', () => this.showHints());
    bind('solution', () => this.showSolution());
    bind('ask-ai', () => this.askAI());
    bind('skip', () => this.skipQuestion());
    bind('next-q', () => this.nextExamQuestion());
  },

  syncCells() {
    this.editors.forEach((editor, index) => {
      if (editor) this.cells[index] = editor.getValue();
    });
    return this.cells.slice();
  },

  setBusy(busy, label) {
    this.busy = busy;
    ['judge', 'run-all', 'ask-ai', 'skip'].forEach((id) => {
      const node = document.getElementById(id);
      if (node) {
        node.disabled = busy;
        if (busy && label && node.id === 'judge') node.textContent = label;
        if (!busy && node.id === 'judge') node.textContent = '✅ 提交判题';
      }
    });
  },

  // 草稿每 1.5 秒落一次盘，避免每敲一个字就发请求
  queueDraft() {
    clearTimeout(this.draftTimer);
    this.draftTimer = setTimeout(() => this.saveDraft(), 1500);
  },

  async saveDraft() {
    if (!this.current) return;
    await this.api('/api/training/draft', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: this.current.id, cells: this.syncCells() }),
    });
  },

  showOutput(index, html, cls) {
    const box = document.querySelector(`[data-out="${index}"]`);
    if (!box) return;
    box.className = 'cell-out show ' + (cls || '');
    box.innerHTML = html;
  },

  renderRunResult(index, result) {
    const parts = [];
    if (result.stdout) parts.push(this.esc(result.stdout));
    if (result.error) parts.push('<span style="color:#ff9c94">' + this.esc(result.error) + '</span>');
    (result.figures || []).forEach((src) => parts.push(`<img src="${src}" alt="运行产生的图">`));
    if (!parts.length) parts.push('<span class="meta">（没有输出）</span>');
    if (result.elapsed !== undefined && result.elapsed !== null) {
      parts.push(`<div class="meta">耗时 ${result.elapsed}s</div>`);
    }
    this.showOutput(index, parts.join('\n'), result.ok ? 'ok' : 'error');
  },

  /** 任何一块代码里出现 input( 就露出测试输入框 ——
   *  只按题库 needs_input 标记显示的话，学生自己写了 input() 仍然会撞 EOFError。 */
  syncStdin() {
    const wrap = document.getElementById('stdin-wrap');
    if (!wrap) return;
    const cells = (this.cells || []).join('\n');
    const needs = /(?<![\w.])input\s*\(/.test(cells);
    if (needs) wrap.hidden = false;
  },

  async runCell(index) {
    if (this.busy) return;
    this.syncStdin();
    const cells = this.syncCells();
    if (!(cells[index] || '').trim()) { this.showOutput(index, '<span class="meta">这一块还是空的</span>', ''); return; }
    this.showOutput(index, '<span class="meta">运行中…</span>', '');
    const stdin = document.getElementById('stdin-box');
    const data = await this.api('/api/training/run-cell', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cells, active: index, stdin: stdin ? stdin.value : '',
        question_id: this.current ? this.current.id : '',
        used_ai: !!(this.current && this.usedAi[this.current.id]),
      }),
    });
    this.renderRunResult(index, data);
    // 跑的是最后一块、且满足题目断言时，后端会把成绩结算掉（游客则只提示不记分）
    if (data.settle) await this.celebrate(data.settle, { fromRun: true });
    else if (data.checks_passed) await this.celebrate(null, { fromRun: true, guest: !!data.guest });
  },

  async runAll() {
    if (this.busy) return;
    const cells = this.syncCells();
    const stdin = document.getElementById('stdin-box');
    for (let index = 0; index < cells.length; index += 1) {
      if (!(cells[index] || '').trim()) continue;
      this.showOutput(index, '<span class="meta">运行中…</span>', '');
      // eslint-disable-next-line no-await-in-loop
      const data = await this.api('/api/training/run-cell', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cells, active: index, stdin: stdin ? stdin.value : '',
          question_id: this.current ? this.current.id : '',
          used_ai: !!(this.current && this.usedAi[this.current.id]),
        }),
      });
      this.renderRunResult(index, data);
      if (data.settle) await this.celebrate(data.settle, { fromRun: true });
      else if (data.checks_passed) await this.celebrate(null, { fromRun: true, guest: !!data.guest });
      if (!data.ok) break;      // 前面出错就没必要往后跑（和 Jupyter 一致）
    }
  },

  async submit() {
    if (this.busy || !this.current) return;
    this.setBusy(true, '判题中…');
    const stdin = document.getElementById('stdin-box');
    const data = await this.api('/api/training/judge', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_id: this.current.id,
        cells: this.syncCells(),
        stdin: stdin ? stdin.value : '',
        exam_id: this.examId || '',
        used_ai: !!this.usedAi[this.current.id],
      }),
    });
    this.setBusy(false);
    if (!data.success) { this.toast(data.error || data.message || '判题失败'); return; }

    const last = this.cells.length - 1;
    this.renderRunResult(last, { ok: data.passed, stdout: data.stdout, error: data.error, figures: data.figures });
    if (data.passed) {
      await this.celebrate(data.settle, { guest: !!data.guest });
    } else {
      this.panel('settle', '还差一点', `
        <div class="settle-pop fail">
          <span class="big">🔍</span>
          <div class="txt">${data.check_failed
            ? '代码能跑通，但结果没满足题目要求。看看下面的断言提示——它告诉你哪一项对不上。'
            : '代码还没跑通，先按下面的报错改一改。'}</div>
        </div>`);
      this.markExamDot('failed');
    }
  },

  /** 通关结算面板。「运行就跑通了」与「提交判题通过」共用这一段，
      分两处写迟早会长歪，所以统一在这里渲染。 */
  async celebrate(settle, { fromRun = false, guest = false } = {}) {
    settle = settle || {};
    if (guest) {
      // 游客判题本身是准的，只是没有账本可写。这里必须把话说白，
      // 否则学生看到的是一句「0 星 +0」，只会以为平台坏了。
      this.panel('settle', '✅ 做对了！', `
        <div class="settle-pop">
          <span class="big">🫥</span>
          <div class="txt">代码满足题目要求，但<b>当前是游客模式，这次成绩不会保存</b>
            ——不计积分、不涨修为、进度也不累计。<br>
            <a href="/login">登录 / 注册</a> 之后再把这题做一遍，就能正常记分了。</div>
        </div>`);
      this.markExamDot('done');
      if (this.current) this.current.solved = true;
      return;
    }
    const stars = settle.stars || 0;
    const starText = '★'.repeat(stars) + '☆'.repeat(3 - stars);
    let tip = '';
    if (settle.clears > 1) {
      tip = `这是第 ${settle.clears} 次通关，重复练习的分数会递减——想拿高分就一次做对。`;
    } else if (fromRun) {
      tip = '这次运行同时满足了题目要求，成绩已经记上，不用再点「提交判题」。';
    }
    this.panel('settle', '🎉 通过！', `
      <div class="settle-pop">
        <span class="big">${starText}</span>
        <div class="txt">本次掌握度 <b>${stars} 星</b>。
          ${settle.note ? this.esc(settle.note) : ''}
          ${tip ? this.esc(tip) : ''}
        </div>
        <span class="plus">+${settle.points || 0}</span>
      </div>`);
    if (window.Cultivation && settle.profile) Cultivation.applySettlement(settle);
    this.markExamDot('done');
    if (this.current) this.current.solved = true;
    await this.loadCatalog();
    this.renderSide();
    if (this.examId) this.advanceExam();
  },

  markExamDot(status) {
    if (!this.exam || !this.current) return;
    const item = (this.exam.items || []).find((i) => i.id === this.current.id);
    if (item) item.status = status;
    this.renderExamStrip();
  },

  panel(key, title, html, { closable = true } = {}) {
    let box = document.getElementById('panel-' + key);
    if (!box) {
      box = document.createElement('div');
      box.className = 'panel';
      box.id = 'panel-' + key;
      document.getElementById('panels').appendChild(box);
    }
    box.innerHTML = `<div class="panel-head">${title}${closable ? '<span class="close" data-close>✕</span>' : ''}</div>
      <div class="panel-body">${html}</div>`;
    if (closable) {
      box.querySelector('[data-close]').addEventListener('click', () => box.remove());
    }
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  },

  showHints() {
    const hints = this.current.hints || [];
    if (!hints.length) { this.panel('hint', '💡 提示', '<p>这道题没有额外提示，试着把题干里的要求一条条对着代码检查。</p>'); return; }
    this.panel('hint', '💡 提示（先自己想一想再看）', '<ol class="hint-list">'
      + hints.map((h) => `<li>${this.md(h)}</li>`).join('') + '</ol>');
    this.usedAi[this.current.id] = true;   // 看过提示就别想拿 3 星了
  },

  async showSolution() {
    if (this.current.solution === undefined) {
      const data = await this.api('/api/training/question/' + encodeURIComponent(this.current.id));
      if (data.success) this.current = data.question;
    }
    if (this.current.blocked_reason) { this.toast(this.current.blocked_reason); return; }
    this.panel('solution', '📖 参考答案与解析', `
      <p style="color:var(--text-secondary);font-size:12.5px">
        ⚠️ 看答案会失去本题的满星机会——建议先自己想 10 分钟，或者点「问 JJ老师」要个思路。
      </p>
      <h4>参考代码</h4>
      <pre><code>${this.esc(this.current.solution || '')}</code></pre>
      <h4>解析</h4>
      ${this.md(this.current.explanation || '')}`);
    this.usedAi[this.current.id] = true;
  },

  async askAI() {
    if (this.busy) return;
    this.setBusy(true, '判题中…');
    const lastOut = document.querySelector('.cell-out.show');
    this.usedAi[this.current.id] = true;
    const box = this.panel('ai', '🤖 JJ老师正在看你的代码…', '<span class="meta">正在连接…</span>', { closable: true });
    const body = document.querySelector('#panel-ai .panel-body');
    let answer = '';
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 90000);
    try {
      const response = await fetch('/api/training/ai-help', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_id: this.current.id,
          statement: this.current.statement,
          code: this.syncCells().join('\n\n# ── 下一个代码块 ──\n\n'),
          error: lastOut ? lastOut.textContent.slice(0, 800) : '',
          ask: '这道题我卡住了，帮我理一下思路，别直接给答案。',
        }),
      });
      if (!response.ok) throw new Error('请求失败（HTTP ' + response.status + '）');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const chunk = await reader.read();
        buffer += decoder.decode(chunk.value || new Uint8Array(), { stream: !chunk.done });
        const frames = buffer.split('\n\n');
        buffer = frames.pop();
        for (const frame of frames) {
          if (!frame.startsWith('data: ')) continue;
          let event;
          try { event = JSON.parse(frame.slice(6)); } catch (e) { continue; }
          if (event.type === 'delta') {
            answer += event.text;
            body.innerHTML = this.md(answer);
          } else if (event.type === 'status' && !answer) {
            body.innerHTML = '<span class="meta">' + this.esc(event.message) + '</span>';
          } else if (event.type === 'error') {
            throw new Error(event.message);
          }
        }
        if (chunk.done) break;
      }
      if (!answer) body.innerHTML = '<span class="meta">模型没有返回内容，稍后再试。</span>';
    } catch (error) {
      body.innerHTML = '<span style="color:var(--red)">'
        + this.esc(error.name === 'AbortError' ? '响应超时，请重试。' : error.message) + '</span>';
    } finally {
      clearTimeout(timer);
      this.setBusy(false);
      const head = document.querySelector('#panel-ai .panel-head');
      if (head) head.childNodes[0].textContent = '🤖 JJ老师';
    }
  },

  // ── 实战模式 ────────────────────────────────────
  renderExamSetup() {
    const detail = this.el.detail;
    if (!detail) return;
    this.exam = null;
    const trackChapters = this.currentTrackChapters();
    const solvedCount = trackChapters.reduce((sum, c) => sum + c.solved, 0);
    detail.innerHTML = `
      <div class="exam-setup">
        <h2>⚔️ 实战模式：自由组卷</h2>
        <p class="sub">
          选定章节与题量，系统会优先抽你没做过的题。<br>
          实战中<b>看不到解析</b>，一直报错的题可以跳过；<b>交卷之后</b>才解锁解析、AI 批卷与针对性建议。
        </p>
        <div class="exam-field">
          <label>赛道</label>
          <div class="wb-seg" style="max-width:320px">
            <button data-exam-track="course" class="${this.track === 'course' ? 'active' : ''}">课程配套</button>
            <button data-exam-track="algorithm" class="${this.track === 'algorithm' ? 'active' : ''}">算法与数据结构</button>
          </div>
        </div>
        <div class="exam-field">
          <label>章节 / 专题（不选则整个赛道随机抽题；已通关 ${solvedCount}）</label>
          <div class="chapter-grid" id="exam-chapters">
            ${trackChapters.map((c) => `
              <div class="pick-row ${this.chapters.has(String(c.id)) ? 'on' : ''}" data-id="${c.id}">
                <span class="t">${this.esc(c.title)}</span>
                <span class="n">${c.count}</span>
              </div>`).join('')}
          </div>
        </div>
        <div class="exam-field">
          <label>题量</label>
          <div class="exam-counts" id="exam-counts">
            ${[3, 5, 8, 10].map((n) => `<button data-count="${n}" class="${n === 5 ? 'active' : ''}">${n} 题</button>`).join('')}
          </div>
        </div>
        <div class="exam-field">
          <label>难度</label>
          <div class="wb-seg" style="max-width:380px" id="exam-diff">
            <button data-diff="" class="active">混合</button>
            <button data-diff="1">只抽简单</button>
            <button data-diff="2">只抽中等</button>
            <button data-diff="3">只抽较难</button>
          </div>
        </div>
        <div class="wb-actions" style="flex-direction:row;gap:10px">
          <button class="wb-btn primary" id="exam-start">开始实战</button>
          <button class="wb-btn" id="exam-last" style="display:none">继续上一次未完成的卷子</button>
        </div>
      </div>`;

    this.examCount = 5;
    this.examDifficulty = '';
    detail.querySelectorAll('[data-exam-track]').forEach((button) => {
      button.addEventListener('click', () => {
        this.track = button.dataset.examTrack;
        try { localStorage.setItem('pymaster_training_track', this.track); } catch (e) {}
        this.chapters.clear();
        this.renderSide();
        this.renderExamSetup();
      });
    });
    detail.querySelectorAll('#exam-chapters .pick-row').forEach((row) => {
      row.addEventListener('click', () => {
        const id = String(row.dataset.id);
        if (this.chapters.has(id)) this.chapters.delete(id);
        else this.chapters.add(id);
        row.classList.toggle('on');
      });
    });
    detail.querySelectorAll('#exam-counts button').forEach((button) => {
      button.addEventListener('click', () => {
        this.examCount = Number(button.dataset.count);
        detail.querySelectorAll('#exam-counts button').forEach((b) => b.classList.toggle('active', b === button));
      });
    });
    detail.querySelectorAll('#exam-diff button').forEach((button) => {
      button.addEventListener('click', () => {
        this.examDifficulty = button.dataset.diff;
        detail.querySelectorAll('#exam-diff button').forEach((b) => b.classList.toggle('active', b === button));
      });
    });
    document.getElementById('exam-start').addEventListener('click', () => this.createExam());
    this.loadLastExam();
  },

  async loadLastExam() {
    const data = await this.api('/api/progress/overview');
    if (!data.success) return;
    const active = (data.exams || []).find((e) => e.status === 'active');
    const button = document.getElementById('exam-last');
    if (!active || !button) return;
    button.style.display = 'inline-block';
    button.textContent = `继续未完成的卷子（${active.done}/${active.count}）`;
    button.addEventListener('click', () => this.openExam(active.id));
  },

  async createExam() {
    const data = await this.api('/api/training/exam', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chapters: [...this.chapters],
        count: this.examCount,
        difficulty: this.examDifficulty || null,
        track: this.track,
      }),
    });
    if (!data.success) { this.toast(data.message || '组卷失败'); return; }
    this.exam = data.exam;
    this.openExamQuestion(0);
  },

  async openExam(examId) {
    const data = await this.api('/api/training/exam/' + encodeURIComponent(examId));
    if (!data.success) { this.toast(data.message || '打不开卷子'); return; }
    this.exam = data.exam;
    if (this.exam.status === 'finished') this.renderExamResult();
    else this.openExamQuestion(0);
  },

  async openExamQuestion(index) {
    if (!this.exam) return;
    const items = this.exam.items || [];
    if (index < 0) index = 0;
    if (index >= items.length) index = items.length - 1;
    this.examIndex = index;
    await this.openQuestion(items[index].id, { examId: this.exam.id, cursor: index });
    this.renderExamStrip();
  },

  renderExamStrip() {
    if (!this.exam) return;
    const detail = this.el.detail;
    const strip = document.createElement('div');
    strip.className = 'exam-strip';
    strip.id = 'exam-strip';
    strip.innerHTML = (this.exam.items || []).map((item, index) => {
      const cls = item.status === 'done' ? 'done'
        : item.status === 'failed' ? 'failed'
        : item.status === 'skipped' ? 'skipped'
        : (index === this.examIndex ? 'current' : '');
      const current = index === this.examIndex ? ' current' : '';
      return `<button class="exam-dot ${cls}${current}" data-go="${index}" title="${this.esc(item.title)}">${index + 1}</button>`;
    }).join('') + `<span style="margin-left:auto;display:flex;gap:8px;align-items:center">
        <span class="q-pill">已完成 ${(this.exam.items || []).filter((i) => ['done', 'skipped'].includes(i.status)).length}/${(this.exam.items || []).length}</span>
        <button class="wb-btn tiny primary" id="exam-finish">交卷并看解析</button>
      </span>`;
    const existing = document.getElementById('exam-strip');
    if (existing) existing.remove();
    detail.insertBefore(strip, detail.firstChild);

    strip.querySelectorAll('[data-go]').forEach((button) => {
      button.addEventListener('click', () => this.openExamQuestion(Number(button.dataset.go)));
    });
    const finish = document.getElementById('exam-finish');
    if (finish) finish.addEventListener('click', () => this.finishExam());
  },

  advanceExam() {
    if (!this.exam) return;
    const items = this.exam.items || [];
    const next = items.findIndex((item, index) => index > this.examIndex && !['done', 'skipped'].includes(item.status));
    if (next >= 0) this.openExamQuestion(next);
  },

  nextExamQuestion() {
    if (!this.exam) return;
    const items = this.exam.items || [];
    if (this.examIndex + 1 < items.length) this.openExamQuestion(this.examIndex + 1);
    else this.toast('已经是最后一题了，可以交卷了。');
  },

  async skipQuestion() {
    if (!this.exam || this.busy) return;
    if (!await this.confirm('跳过这题？跳过的题不算通关，但会计入这次实战记录。')) return;
    await this.api('/api/training/attempt', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: this.current.id, exam_id: this.exam.id }),
    });
    this.markExamDot('skipped');
    this.nextExamQuestion();
  },

  async finishExam() {
    if (!this.exam) return;
    const undone = (this.exam.items || []).filter((i) => !['done', 'skipped', 'failed'].includes(i.status)).length;
    if (undone && !await this.confirm(`还有 ${undone} 题没做，交卷后这些题会按跳过处理。`, { title: '确定交卷？', okText: '交卷' })) return;
    const data = await this.api('/api/training/exam/' + encodeURIComponent(this.exam.id) + '/finish', { method: 'POST' });
    if (!data.success) { this.toast(data.message || '交卷失败'); return; }
    this.exam = data.exam;
    this.renderExamResult();
  },

  renderExamResult() {
    const exam = this.exam;
    const detail = this.el.detail;
    const items = exam.items || [];
    const done = items.filter((i) => i.status === 'done').length;
    const skipped = items.filter((i) => i.status === 'skipped').length;
    const failed = items.filter((i) => i.status === 'failed').length;
    const stars = items.reduce((sum, i) => sum + (i.stars || 0), 0);
    detail.innerHTML = `
      <div class="exam-setup">
        <h2>📊 本次实战结果</h2>
        <div class="score-card">
          <div class="score-cell"><div class="v" style="color:var(--cyan)">${exam.score === null ? '-' : exam.score}</div><div class="k">综合得分</div></div>
          <div class="score-cell"><div class="v" style="color:var(--green)">${done}</div><div class="k">通关题数</div></div>
          <div class="score-cell"><div class="v" style="color:var(--orange)">${skipped}</div><div class="k">跳过</div></div>
          <div class="score-cell"><div class="v" style="color:var(--red)">${failed}</div><div class="k">未通过</div></div>
          <div class="score-cell"><div class="v" style="color:#ffd980">${stars}/${items.length * 3}</div><div class="k">星级合计</div></div>
        </div>
        <div class="q-toolbar" style="border-radius:10px;position:static">
          <button class="wb-btn tiny primary" id="exam-review">🤖 让 JJ老师批卷并给建议</button>
          <span class="grow"></span>
          <button class="wb-btn tiny" id="exam-retry">再组一份</button>
        </div>
        <div id="panels"></div>
        <h2 style="font-size:15px;margin-top:20px">逐题复盘（解析已解锁）</h2>
        <div id="exam-review-list" class="qlist" style="margin-top:10px"></div>
      </div>`;
    const list = document.getElementById('exam-review-list');
    list.innerHTML = items.map((item, index) => {
      const cls = item.status === 'done' ? 'solved' : (item.status === 'failed' ? 'wrong' : '');
      const stars = [1, 2, 3].map((n) => (n <= (item.stars || 0) ? '★' : '<span class="off">★</span>')).join('');
      return `<div class="qcard ${cls}" data-id="${item.id}">
        <div class="q-num">${index + 1}</div>
        <div class="q-body">
          <div class="q-title">${this.esc(item.title)}</div>
          <div class="q-tags">
            <span class="diff d${item.difficulty}">${item.difficulty === 1 ? '简单' : item.difficulty === 2 ? '中等' : '较难'}</span>
            <span>${this.esc(item.chapter_title || '')}</span>
            <span>${{ done: '已通关', skipped: '已跳过', failed: '未通过', todo: '未作答' }[item.status] || item.status}</span>
          </div>
        </div>
        <div class="q-right"><span class="stars">${stars}</span></div>
      </div>`;
    }).join('');
    list.querySelectorAll('.qcard').forEach((card) => {
      card.addEventListener('click', async () => {
        this.examId = '';
        await this.openQuestion(card.dataset.id);
      });
    });
    document.getElementById('exam-retry').addEventListener('click', () => this.renderExamSetup());
    document.getElementById('exam-review').addEventListener('click', () => this.reviewExam());
    if (exam.review) {
      this.panel('review', '🤖 JJ老师的批卷意见', this.md(exam.review), { closable: false });
    }
  },

  async reviewExam() {
    if (!this.exam) return;
    if (this.exam.review) { this.panel('review', '🤖 JJ老师的批卷意见', this.md(this.exam.review)); return; }
    this.panel('review', '🤖 JJ老师正在批卷…', '<span class="meta">正在逐题分析你的代码…</span>', { closable: false });
    const body = document.querySelector('#panel-review .panel-body');
    let text = '';
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 120000);
    try {
      const response = await fetch('/api/training/exam/' + encodeURIComponent(this.exam.id) + '/review', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, signal: controller.signal,
      });
      if (!response.ok) throw new Error('请求失败（HTTP ' + response.status + '）');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (true) {
        const chunk = await reader.read();
        buffer += decoder.decode(chunk.value || new Uint8Array(), { stream: !chunk.done });
        const frames = buffer.split('\n\n');
        buffer = frames.pop();
        for (const frame of frames) {
          if (!frame.startsWith('data: ')) continue;
          let event;
          try { event = JSON.parse(frame.slice(6)); } catch (e) { continue; }
          if (event.type === 'delta') { text += event.text; body.innerHTML = this.md(text); }
          else if (event.type === 'status' && !text) body.innerHTML = '<span class="meta">' + this.esc(event.message) + '</span>';
          else if (event.type === 'error') throw new Error(event.message);
        }
        if (chunk.done) break;
      }
      if (!text) body.innerHTML = '<span class="meta">模型没有返回内容，稍后再试。</span>';
      else { this.exam.review = text; const head = document.querySelector('#panel-review .panel-head'); if (head) head.childNodes[0].textContent = '🤖 JJ老师的批卷意见'; }
    } catch (error) {
      body.innerHTML = '<span style="color:var(--red)">'
        + this.esc(error.name === 'AbortError' ? '批卷超时，请重试。' : error.message) + '</span>';
    } finally {
      clearTimeout(timer);
    }
  },
};

window.Training = Training;
