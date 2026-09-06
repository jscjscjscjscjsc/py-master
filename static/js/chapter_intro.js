const ChapterIntro = {
  open(id, title, description, points) {
    if (Number(id) === 8) return;
    const key = `pymaster.chapter-intro.${id}`;
    if (sessionStorage.getItem(key)) return;
    const first = (points && points[0]) || '基础语法';
    const route = (points || []).slice(0, 4).join(' · ');
    const overlay = document.createElement('div');
    overlay.className = 'chapter-intro-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-label', `第${id}章序章`);
    overlay.innerHTML = `
      <div class="chapter-intro-card">
        <div class="chapter-intro-seal">第${id}章</div>
        <div class="chapter-intro-kicker">PYMASTER · 入卷引</div>
        <h1 class="chapter-intro-title">${this._escape(title)}</h1>
        <p class="chapter-intro-desc">${this._escape(description)}</p>
        <div class="chapter-intro-rule"></div>
        <div class="chapter-intro-quote">从「${this._escape(first)}」落笔，<br>让每一次运行都成为可验证的思想。</div>
        <div class="chapter-intro-route">本章脉络：${this._escape(route)}</div>
        <div class="chapter-intro-actions">
          <button class="chapter-intro-skip" type="button">稍后再读</button>
          <button class="chapter-intro-start" type="button">展开本章 · 开始研习</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    requestAnimationFrame(() => overlay.classList.add('is-visible'));
    const close = () => { sessionStorage.setItem(key, '1'); overlay.classList.remove('is-visible'); setTimeout(() => overlay.remove(), 350); };
    overlay.querySelector('.chapter-intro-skip').addEventListener('click', close);
    overlay.querySelector('.chapter-intro-start').addEventListener('click', close);
    overlay.addEventListener('click', (event) => { if (event.target === overlay) close(); });
  },
  _escape(value) { return String(value || '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char])); }
};
