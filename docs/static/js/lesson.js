/* ============================================================
   lesson.js — 教案正文的代码复制
   ------------------------------------------------------------
   教材 HTML 里每个代码块本来就有顶栏（.md-codebar）和复制按钮，
   但按钮写的是 onclick="copyBlock(this)"，而 copyBlock 这个函数
   在整库里从来没有被定义过 —— 所以它一直是坏的（点了没反应）。

   这里只补上这个函数，不再往 DOM 里注入第二层顶栏。
   ============================================================ */
(function () {
  'use strict';

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText && isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    // 非安全上下文（http 的局域网地址、file://）下 clipboard API 不可用，
    // 而线上部署初期很可能就是 http，所以必须留这条退路。
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
        document.body.appendChild(ta);
        ta.select();
        ta.setSelectionRange(0, text.length);
        var ok = document.execCommand('copy');
        ta.remove();
        ok ? resolve() : reject(new Error('execCommand 复制失败'));
      } catch (err) { reject(err); }
    });
  }

  /** 教材里的复制按钮：onclick="copyBlock(this)" */
  window.copyBlock = function (btn) {
    var block = btn.closest ? btn.closest('.md-codeblock') : null;
    var code = block ? block.querySelector('code') : null;
    var text = code ? code.textContent : '';
    if (!text) return;

    var label = btn.dataset.label || btn.textContent;
    btn.dataset.label = label;

    var done = function (msg, cls) {
      btn.textContent = msg;
      if (cls) btn.classList.add(cls);
      setTimeout(function () {
        btn.textContent = label;
        btn.classList.remove('done', 'fail');
      }, 1600);
    };

    copyText(text).then(function () {
      done('已复制', 'done');
    }).catch(function () {
      done('复制失败', 'fail');
    });
  };
})();
