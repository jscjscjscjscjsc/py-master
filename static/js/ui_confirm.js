/**
 * ui_confirm.js — 应用内确认框，替代 window.confirm
 *
 * 为什么非换不可：
 * 1. **原生 confirm 会阻塞页面主线程**。它弹出期间页面完全冻结——
 *    在嵌入式浏览器（本平台就支持在 webview 里打开）中，它可能让整页卡死，
 *    连「取消」都点不动。
 * 2. 原生弹窗样式与深色界面完全割裂，还带着「localhost 说：」这种前缀。
 * 3. 原生 confirm 是同步的，无法在等待用户选择时更新界面（比如显示「正在提交」）。
 *
 * 用法（注意要 await）：
 *     if (!await UI.confirm('确定交卷？')) return;
 *     if (!await UI.confirm('删除后不可恢复', { danger: true, okText: '删除' })) return;
 */
const UI = {
  _resolve: null,

  confirm(message, options = {}) {
    const opts = Object.assign(
      { title: '请确认', okText: '确定', cancelText: '取消', danger: false }, options);
    return new Promise((resolve) => {
      this._resolve = resolve;
      let mask = document.getElementById('ui-confirm-mask');
      if (!mask) {
        mask = document.createElement('div');
        mask.id = 'ui-confirm-mask';
        mask.className = 'ui-mask';
        document.body.appendChild(mask);
      }
      mask.innerHTML = `
        <div class="ui-dialog" role="dialog" aria-modal="true">
          <div class="ui-dialog-title">${this.esc(opts.title)}</div>
          <div class="ui-dialog-body">${this.esc(message)}</div>
          <div class="ui-dialog-actions">
            <button class="wb-btn" data-act="cancel">${this.esc(opts.cancelText)}</button>
            <button class="wb-btn ${opts.danger ? 'danger' : 'primary'}" data-act="ok">${this.esc(opts.okText)}</button>
          </div>
        </div>`;
      mask.classList.add('show');
      const finish = (value) => {
        mask.classList.remove('show');
        const resolver = this._resolve;
        this._resolve = null;
        if (resolver) resolver(value);
      };
      mask.querySelector('[data-act="ok"]').addEventListener('click', () => finish(true));
      mask.querySelector('[data-act="cancel"]').addEventListener('click', () => finish(false));
      mask.addEventListener('click', (event) => { if (event.target === mask) finish(false); });
      const onKey = (event) => {
        if (event.key === 'Escape') { document.removeEventListener('keydown', onKey); finish(false); }
        if (event.key === 'Enter') { document.removeEventListener('keydown', onKey); finish(true); }
      };
      document.addEventListener('keydown', onKey);
      const ok = mask.querySelector('[data-act="ok"]');
      if (ok) ok.focus();
    });
  },

  /** 输入框弹窗，替代 window.prompt。返回值：字符串或 null（取消） */
  prompt(title, defaultValue = '', options = {}) {
    const opts = Object.assign({ okText: '确定', cancelText: '取消' }, options);
    return new Promise((resolve) => {
      let mask = document.getElementById('ui-confirm-mask');
      if (!mask) {
        mask = document.createElement('div');
        mask.id = 'ui-confirm-mask';
        mask.className = 'ui-mask';
        document.body.appendChild(mask);
      }
      mask.innerHTML = `
        <div class="ui-dialog" role="dialog" aria-modal="true">
          <div class="ui-dialog-title">${this.esc(title)}</div>
          <input class="ui-dialog-input" id="ui-dialog-input" value="${this.esc(defaultValue)}" maxlength="60">
          <div class="ui-dialog-actions">
            <button class="wb-btn" data-act="cancel">${this.esc(opts.cancelText)}</button>
            <button class="wb-btn primary" data-act="ok">${this.esc(opts.okText)}</button>
          </div>
        </div>`;
      mask.classList.add('show');
      const input = mask.querySelector('#ui-dialog-input');
      const finish = (value) => {
        mask.classList.remove('show');
        resolve(value);
      };
      mask.querySelector('[data-act="ok"]').addEventListener('click', () => finish(input.value));
      mask.querySelector('[data-act="cancel"]').addEventListener('click', () => finish(null));
      mask.addEventListener('click', (event) => { if (event.target === mask) finish(null); });
      input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') finish(input.value);
        if (event.key === 'Escape') finish(null);
      });
      input.focus();
      input.select();
    });
  },

  /** 轻提示（不阻塞、不打断） */
  toast(message, ms = 2200) {
    let box = document.getElementById('ui-toast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'ui-toast';
      box.className = 'ui-toast';
      document.body.appendChild(box);
    }
    box.textContent = message;
    box.classList.add('show');
    clearTimeout(this._timer);
    this._timer = setTimeout(() => box.classList.remove('show'), ms);
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },
};

window.UI = UI;
