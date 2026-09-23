/* 模型未配置提示条
 * ----------------
 * 学生在首次向导里选了「暂时不配置」之后，必须在某个地方能再找到配置入口，
 * 否则就再也回不去了。这里在右下角挂一个不挡内容的小胶囊：
 *   · 未配置 → 提示「AI 功能未开启」，点一下回到 /setup
 *   · 已配置 → 完全不出现（不做任何提示，避免打扰）
 * 关闭按钮记在 sessionStorage 里，只在本标签页有效，刷新页面还会回来 ——
 * 因为「AI 用不了」这件事不该被永久隐藏。
 */
(function () {
  'use strict';
  if (window.__aiNoticeLoaded) return;
  window.__aiNoticeLoaded = true;

  // 配置页自己不需要这条提示
  if (location.pathname.indexOf('/setup') === 0) return;
  // 开场 CG 是全屏短片，盖上去会破坏观感
  if (location.pathname.indexOf('/intro') === 0) return;

  var KEY = 'pymaster-ai-notice-hidden';
  try { if (sessionStorage.getItem(KEY) === '1') return; } catch (e) { /* 隐私模式 */ }

  function render() {
    var box = document.createElement('div');
    box.id = 'ai-notice-chip';
    box.innerHTML =
      '<span class="ain-dot"></span>' +
      '<span class="ain-text">AI 功能未开启（点此配置大模型）</span>' +
      '<button class="ain-close" title="本次关闭" aria-label="关闭">×</button>';
    document.body.appendChild(box);

    box.querySelector('.ain-text').addEventListener('click', function () {
      location.href = '/setup';
    });
    box.querySelector('.ain-dot').addEventListener('click', function () {
      location.href = '/setup';
    });
    box.querySelector('.ain-close').addEventListener('click', function (e) {
      e.stopPropagation();
      try { sessionStorage.setItem(KEY, '1'); } catch (err) { /* 忽略 */ }
      box.remove();
    });
  }

  var css = document.createElement('style');
  css.textContent = [
    '#ai-notice-chip{position:fixed;right:18px;bottom:18px;z-index:900;display:flex;',
    'align-items:center;gap:9px;padding:9px 12px;border-radius:999px;',
    'background:rgba(13,18,25,.94);border:1px solid rgba(255,176,66,.42);',
    'box-shadow:0 6px 22px rgba(0,0,0,.42);font-size:12.5px;color:#f0c07a;',
    'cursor:pointer;backdrop-filter:blur(8px);animation:ain-in .45s ease both}',
    '@keyframes ain-in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}',
    '#ai-notice-chip:hover{border-color:rgba(255,176,66,.8);color:#ffd79a}',
    '#ai-notice-chip .ain-dot{width:7px;height:7px;border-radius:50%;background:#ffb042;',
    'box-shadow:0 0 8px rgba(255,176,66,.85);flex:0 0 auto}',
    '#ai-notice-chip .ain-text{cursor:pointer;text-decoration:underline;',
    'text-underline-offset:3px;text-decoration-thickness:1px}',
    '#ai-notice-chip .ain-close{background:none;border:none;color:inherit;',
    'font-size:15px;line-height:1;cursor:pointer;opacity:.6;padding:0 2px;font-family:inherit}',
    '#ai-notice-chip .ain-close:hover{opacity:1}',
    '@media (max-width:760px){#ai-notice-chip{right:10px;bottom:10px;font-size:11.5px;',
    'padding:8px 10px}}'
  ].join('');
  document.head.appendChild(css);

  fetch('/api/setup/status', { headers: { 'Accept': 'application/json' } })
    .then(function (r) { return r.json(); })
    .then(function (res) { if (res && res.success && !res.configured) render(); })
    .catch(function () { /* 拿不到状态就什么都不显示，不打扰用户 */ });
})();
