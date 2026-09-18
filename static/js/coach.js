/**
 * coach.js — 星辰教练：多会话聊天（对齐主流对话产品的操作习惯）
 *
 * 三件事必须做对，否则用户会立刻不信任这个页面：
 * 1. 流式过程中不能丢字、不能卡死（SSE 分帧要处理跨 chunk 的半截 JSON）；
 * 2. 切会话时不能把上一个会话的内容渲染到新会话里（用请求序号丢弃过期响应）；
 * 3. 回答里的代码块要能读、能复制（先转义再渲染，绝不直接塞 HTML）。
 */
const Coach = {
  sessions: [],
  currentId: '',
  limit: 10,
  isGuest: false,
  sending: false,
  requestSeq: 0,
  quota: null,

  el: {},

  init(options) {
    this.isGuest = !!(options && options.isGuest);
    this.limit = (options && options.limit) || 10;
    this.el = {
      sessions: document.getElementById('coach-sessions'),
      thread: document.getElementById('coach-thread'),
      inner: document.getElementById('thread-inner'),
      input: document.getElementById('coach-input'),
      send: document.getElementById('coach-send'),
      newBtn: document.getElementById('coach-new'),
      title: document.getElementById('coach-title'),
      copy: document.getElementById('coach-copy'),
      rename: document.getElementById('coach-rename'),
      deleteBtn: document.getElementById('coach-delete'),
      clear: document.getElementById('coach-clear'),
      limit: document.getElementById('coach-limit'),
      quota: document.getElementById('coach-quota'),
      toast: document.getElementById('coach-toast'),
      side: document.getElementById('coach-side'),
      menu: document.getElementById('coach-menu'),
    };
    this.bind();
    this.renderEmpty();
    this.renderSessions();      // 游客也能看到「能聊但不保存」的说明
    if (!this.isGuest) {
      this.loadSessions();
      this.loadQuota();
    }
  },

  bind() {
    const { input, send, newBtn, copy, rename, deleteBtn, clear, menu } = this.el;
    if (input) {
      input.addEventListener('input', () => this.autoGrow());
      input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
          event.preventDefault();
          this.send();
        }
      });
    }
    if (send) send.addEventListener('click', () => this.send());
    if (newBtn) newBtn.addEventListener('click', () => this.newSession());
    if (copy) copy.addEventListener('click', () => this.copyCurrent());
    if (rename) rename.addEventListener('click', () => this.renameCurrent());
    if (deleteBtn) deleteBtn.addEventListener('click', () => this.deleteCurrent());
    if (clear) clear.addEventListener('click', () => this.clearCurrent());
    if (menu) menu.addEventListener('click', () => this.el.side.classList.toggle('open'));
    document.querySelectorAll('.prompt-card').forEach((card) => {
      card.addEventListener('click', () => {
        if (!this.el.input) return;
        this.el.input.value = card.dataset.q || card.textContent.trim();
        this.autoGrow();
        this.el.input.focus();
      });
    });
  },

  autoGrow() {
    const input = this.el.input;
    if (!input) return;
    input.style.height = 'auto';
    input.style.height = Math.min(190, input.scrollHeight) + 'px';
  },

  toast(message, ms = 2200) {
    if (window.UI && UI.toast) { UI.toast(message, ms); return; }
    const box = this.el.toast;
    if (!box) return;
    box.textContent = message;
    box.classList.add('show');
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(() => box.classList.remove('show'), ms);
  },

  async api(url, options) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({ success: false, message: '服务返回了非 JSON 内容' }));
    return data;
  },

  async loadSessions() {
    const data = await this.api('/api/coach/sessions');
    if (!data.success) return;
    this.sessions = data.sessions || [];
    this.renderSessions();
    if (!this.currentId && this.sessions.length) {
      this.open(this.sessions[0].id);
    }
  },

  renderSessions() {
    const box = this.el.sessions;
    if (!box) return;
    if (this.isGuest) {
      box.innerHTML = '<div class="coach-limit">游客模式下可以随便聊，但不会保存。注册后最多保存 '
        + this.limit + ' 个对话。</div>';
      return;
    }
    if (!this.sessions.length) {
      box.innerHTML = '<div class="coach-limit">还没有对话。点上面的「新对话」或直接在右边提问。</div>';
    } else {
      box.innerHTML = this.sessions.map((s) => {
        const badge = s.source && s.source !== 'manual'
          ? `<span class="session-source ${this.esc(s.source)}">${
              { exercise: '练习', training: '刷题', exam: '实战' }[s.source] || '答疑'}</span>` : '';
        return `<div class="session-item${s.id === this.currentId ? ' active' : ''}" data-id="${this.esc(s.id)}">
          <div class="s-title">${badge}${this.esc(s.title || '新的对话')}</div>
          <div class="s-meta">${s.message_count} 条 · ${this.esc((s.updated_at || '').slice(5, 16))}</div>
          <div class="session-actions">
            <button title="一键复制这段对话" data-act="copy">⧉</button>
            <button title="重命名" data-act="rename">✎</button>
            <button title="删除" data-act="delete" class="danger">✕</button>
          </div>
        </div>`;
      }).join('');
      box.querySelectorAll('.session-item').forEach((node) => {
        node.addEventListener('click', (event) => {
          const button = event.target.closest('button[data-act]');
          const id = node.dataset.id;
          if (button) {
            event.stopPropagation();
            const act = button.dataset.act;
            if (act === 'copy') this.copySession(id);
            if (act === 'rename') this.renameSession(id);
            if (act === 'delete') this.deleteSession(id);
            return;
          }
          this.open(id);
        });
      });
    }
    if (this.el.limit) {
      this.el.limit.innerHTML = `已保存 <b>${this.sessions.length}</b> / ${this.limit} 个对话。` +
        (this.sessions.length >= this.limit ? ' 到上限了，删一个再新建。' : '');
    }
    if (this.el.newBtn) this.el.newBtn.disabled = this.sessions.length >= this.limit;
  },

  renderEmpty() {
    if (!this.el.inner) return;
    // 有法相数据时，空态就是「教练站在你面前自我介绍」：
    // 左边是它这一境的样子，右边是它想跟你说的话。
    const hero = window.CoachScene && CoachScene.heroHtml ? CoachScene.heroHtml() : '';
    this.el.inner.innerHTML = `
      <div class="coach-empty">
        ${hero || `<div class="avatar-lg" style="font-size:38px">🌟</div>
        <h2>我是 JJ老师，你的星辰教练</h2>
        <p>问我 Python 与 AI 的任何问题。我讲完一定会反问你一个问题——
           因为真正的理解，发生在你开口回答的那一刻。</p>`}
        <div class="prompt-cards">
          <div class="prompt-card" data-q="列表和元组到底该用哪个？有什么区别？"><b>列表 vs 元组</b>什么时候该用哪个？</div>
          <div class="prompt-card" data-q="什么是装饰器？能不能用生活里的例子解释一下"><b>装饰器是什么</b>用生活例子讲一遍</div>
          <div class="prompt-card" data-q="大模型是怎么知道你下一个字该说什么的？"><b>大模型原理</b>它怎么预测下一个字</div>
          <div class="prompt-card" data-q="我写的代码总是报 IndexError，我该怎么排查这类错误？"><b>报错排查</b>IndexError 怎么定位</div>
        </div>
      </div>`;
    document.querySelectorAll('.prompt-card').forEach((card) => {
      card.addEventListener('click', () => {
        if (!this.el.input) return;
        this.el.input.value = card.dataset.q || '';
        this.autoGrow();
        this.el.input.focus();
      });
    });
    if (window.CoachScene && CoachScene.bindHero) CoachScene.bindHero(this.el.inner);
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  },

  confirm(message, options) {
    if (window.UI && UI.confirm) return UI.confirm(message, options);
    return Promise.resolve(window.confirm(message));
  },

  prompt(title, defaultValue) {
    if (window.UI && UI.prompt) return UI.prompt(title, defaultValue);
    return Promise.resolve(window.prompt(title, defaultValue));
  },

  /** Markdown 渲染统一交给 md_lite.js（教练页与刷题页共用同一套规则） */
  md(text) {
    if (window.MdLite) return window.MdLite.toHtml(text);
    return this.esc(text || '').replace(/\n/g, '<br>');
  },

  async open(sessionId) {
    if (!sessionId) return;
    this.currentId = sessionId;
    this.requestSeq += 1;
    this.renderSessions();
    const data = await this.api('/api/coach/sessions/' + encodeURIComponent(sessionId));
    if (!data.success) { this.toast(data.message || '打不开这个对话'); return; }
    if (data.session.id !== this.currentId) return;  // 用户已经切到别的会话了
    if (this.el.title) this.el.title.textContent = data.session.title || '新的对话';
    this.renderMessages(data.session.messages || []);
    this.el.side.classList.remove('open');
  },

  renderMessages(messages) {
    if (!messages.length) { this.renderEmpty(); return; }
    this.el.inner.innerHTML = messages.map((m) => this.messageHtml(m)).join('');
    this.bindMessageTools();
    this.scrollToEnd();
  },

  messageHtml(message) {
    const isUser = message.role === 'user';
    const meta = message.meta || {};
    const badge = meta.source && meta.source !== 'coach' && meta.source !== 'manual'
      ? `<span class="session-source ${this.esc(meta.source)}">${
          { exercise: '练习答疑', training: '刷题答疑', exam: '实战答疑' }[meta.source] || '答疑'}</span> ` : '';
    return `<div class="msg-row ${isUser ? 'me' : 'jj'}">
      <div class="msg-avatar">${isUser ? '我' : 'JJ'}</div>
      <div>
        <div class="bubble">${badge}${isUser ? this.esc(message.content).replace(/\n/g, '<br>') : this.md(message.content)}</div>
        <div class="msg-tools">
          <button data-copy="${this.esc(encodeURIComponent(message.content || ''))}">复制</button>
          <span style="font-size:11px;color:var(--text-muted)">${this.esc(message.ts || '')}</span>
        </div>
      </div>
    </div>`;
  },

  bindMessageTools() {
    this.el.inner.querySelectorAll('button[data-copy]').forEach((button) => {
      button.addEventListener('click', async () => {
        const text = decodeURIComponent(button.dataset.copy);
        await this.copyText(text);
        this.toast('已复制这一条');
      });
    });
  },

  scrollToEnd() {
    const thread = this.el.thread;
    if (thread) thread.scrollTop = thread.scrollHeight;
  },

  async copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      // 非 https / 老浏览器下 clipboard API 不可用，退回到隐藏 textarea
      const area = document.createElement('textarea');
      area.value = text;
      area.style.position = 'fixed';
      area.style.opacity = '0';
      document.body.appendChild(area);
      area.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      document.body.removeChild(area);
      return ok;
    }
  },

  async copySession(sessionId) {
    const data = await this.api('/api/coach/sessions/' + encodeURIComponent(sessionId) + '/transcript');
    if (!data.success) { this.toast(data.message || '复制失败'); return; }
    const ok = await this.copyText(data.text);
    this.toast(ok ? '整段对话已复制（Markdown 格式）' : '复制失败，请手动选中复制');
  },

  copyCurrent() {
    if (!this.currentId) { this.toast('还没有可以复制的对话'); return; }
    this.copySession(this.currentId);
  },

  async newSession() {
    if (this.isGuest) { this.toast('游客模式不保存对话，直接提问就好'); this.el.input.focus(); return; }
    const data = await this.api('/api/coach/sessions', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!data.success) { this.toast(data.message || '新建失败'); return; }
    this.sessions = data.sessions || [];
    this.currentId = data.session.id;
    this.renderSessions();
    if (this.el.title) this.el.title.textContent = '新的对话';
    this.renderEmpty();
    this.el.input.focus();
  },

  async renameSession(sessionId) {
    const current = this.sessions.find((s) => s.id === sessionId);
    const name = await this.prompt('给这段对话起个名字', current ? current.title : '');
    if (name === null) return;
    await this.api('/api/coach/sessions/' + encodeURIComponent(sessionId) + '/rename', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: name }),
    });
    await this.loadSessions();
    if (sessionId === this.currentId && this.el.title) this.el.title.textContent = name || '新的对话';
    this.toast('已重命名');
  },

  renameCurrent() {
    if (!this.currentId) { this.toast('先选中一个对话'); return; }
    this.renameSession(this.currentId);
  },

  async deleteSession(sessionId) {
    const current = this.sessions.find((s) => s.id === sessionId);
    if (!await this.confirm(`删除对话「${current ? current.title : ''}」？删了就找不回来了。`,
        { title: '删除对话', okText: '删除', danger: true })) return;
    const data = await this.api('/api/coach/sessions/' + encodeURIComponent(sessionId), { method: 'DELETE' });
    if (!data.success) { this.toast(data.message || '删除失败'); return; }
    this.sessions = data.sessions || [];
    if (sessionId === this.currentId) {
      this.currentId = '';
      if (this.sessions.length) await this.open(this.sessions[0].id);
      else { this.renderEmpty(); if (this.el.title) this.el.title.textContent = '新的对话'; }
    }
    this.renderSessions();
    this.toast('已删除');
  },

  deleteCurrent() {
    if (!this.currentId) { this.toast('先选中一个对话'); return; }
    this.deleteSession(this.currentId);
  },

  async clearCurrent() {
    if (!this.currentId) { this.toast('先选中一个对话'); return; }
    if (!await this.confirm('清空这段对话的所有消息？（对话标题保留）', { title: '清空消息', okText: '清空' })) return;
    const data = await this.api('/api/coach/sessions/' + encodeURIComponent(this.currentId) + '/clear',
      { method: 'POST' });
    if (!data.success) { this.toast(data.message || '清空失败'); return; }
    this.renderEmpty();
    await this.loadSessions();
    this.toast('已清空消息');
  },

  async loadQuota() {
    const quota = await this.api('/api/ai-quota');
    if (!quota.success || !this.el.quota) return;
    this.quota = quota;
    this.el.quota.textContent = quota.is_unlimited
      ? '今日 AI 次数：不限'
      : `今日 AI 次数：${quota.remaining}/${quota.limit}`;
  },

  appendRow(role, content) {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = this.messageHtml({ role, content, ts: '', meta: {} });
    const node = wrapper.firstElementChild;
    this.el.inner.appendChild(node);
    this.scrollToEnd();
    const bubble = node.querySelector('.bubble');
    const tools = node.querySelector('.msg-tools');
    if (tools) {
      tools.innerHTML = '<span style="font-size:11px;color:var(--text-muted)">刚刚</span>';
    }
    return bubble;
  },

  async send() {
    const input = this.el.input;
    const question = (input.value || '').trim();
    if (!question || this.sending) return;
    if (this.el.inner.querySelector('.coach-empty')) this.el.inner.innerHTML = '';

    this.sending = true;
    this.el.send.disabled = true;
    const bubble = this.appendRow('user', question);
    input.value = '';
    this.autoGrow();

    const replyNode = this.appendRow('jj', '');
    replyNode.innerHTML = '<span class="typing-dots"><span>●</span><span>●</span><span>●</span></span> '
      + '<span style="color:var(--text-muted);font-size:12.5px">JJ老师正在想…</span>';

    const seq = ++this.requestSeq;
    let answer = '';
    let done = false;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 90000);
    try {
      const response = await fetch('/api/coach/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, session_id: this.currentId }),
        signal: controller.signal,
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.message || data.error || `请求失败（HTTP ${response.status}）`);
      }
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
          if (event.type === 'session' && event.session_id) {
            this.currentId = this.currentId || event.session_id;
            this._pendingTitle = question;
          }
          if (event.type === 'delta') {
            answer += event.text;
            if (seq === this.requestSeq) { replyNode.innerHTML = this.md(answer); this.scrollToEnd(); }
          }
          if (event.type === 'status' && !answer && seq === this.requestSeq) {
            replyNode.textContent = event.message;
          }
          if (event.type === 'error') throw new Error(event.message);
          if (event.type === 'done') done = true;
        }
        if (chunk.done) break;
      }
      if (!done) throw new Error('连接提前结束，请重试。');
      if (seq === this.requestSeq) {
        const wrapper = replyNode.closest('.msg-row');
        const tools = wrapper && wrapper.querySelector('.msg-tools');
        if (tools) {
          tools.innerHTML = `<button data-copy="${this.esc(encodeURIComponent(answer))}">复制</button>
            <span style="font-size:11px;color:var(--text-muted)">刚刚</span>`;
          this.bindMessageTools();
        }
      }
      if (!this.isGuest) {
        // 新会话的第一句话会决定标题：回来之后把标题同步到顶栏，
        // 否则顶栏一直显示「新的对话」，看起来像没保存成功。
        if (this._pendingTitle && this.el.title) this.el.title.textContent = this._pendingTitle;
        await this.loadSessions();
        this.loadQuota();
      }
    } catch (error) {
      const message = error.name === 'AbortError' ? '响应超时，请重试。' : error.message;
      replyNode.innerHTML = '<span style="color:var(--red)">'
        + this.esc(answer ? answer + '\n\n' + message : message) + '</span>';
      if (!answer) this.el.input.value = question;
    } finally {
      clearTimeout(timer);
      this.sending = false;
      this.el.send.disabled = false;
      this.el.input.focus();
      if (!this.isGuest) this.loadSessions();
    }
  },
};

window.Coach = Coach;
