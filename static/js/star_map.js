(function () {
  window.openStarMap = function () { window.location.assign(location.pathname.endsWith('.html') ? 'stars.html' : '/stars'); };
  window.closeStarMap = function () { window.history.back(); };
  return;
  const chapters = [
    ['01', 'Python 起源', '起点'], ['02', '变量与数据', '记忆'], ['03', '条件与循环', '分岔'],
    ['04', '序列与映射', '结构'], ['05', '函数', '引力'], ['06', '模块', '航道'],
    ['07', '异常处理', '信标'], ['08', '函数进阶', '回响'], ['09', '文件与对象', '状态']
  ];
  let raf = 0;
  function openStarMap() {
    let overlay = document.getElementById('star-map-overlay');
    if (!overlay) { overlay = build(); document.body.appendChild(overlay); }
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    draw(overlay.querySelector('canvas'));
  }
  function closeStarMap() {
    const overlay = document.getElementById('star-map-overlay');
    if (overlay) overlay.classList.remove('is-open');
    document.body.style.overflow = '';
    cancelAnimationFrame(raf);
  }
  function build() {
    const overlay = document.createElement('div'); overlay.id = 'star-map-overlay'; overlay.className = 'star-map-overlay';
    overlay.innerHTML = '<canvas class="star-map-canvas"></canvas><div class="star-map-shell"><div class="star-map-head"><div><span class="star-map-kicker">PYMASTER / KNOWLEDGE CONSTELLATION</span><h2>星海知识图谱</h2><p>每颗星是一个可抵达的 Python 章节。沿着概念航线，进入下一段探索。</p></div><button class="star-map-close" aria-label="关闭星海图谱">×</button></div><div class="star-map-stage"><div class="star-map-lines"></div><div class="star-map-nodes"></div></div><div class="star-map-foot"><span>点击节点进入章节</span><span>ESC 关闭</span></div></div>';
    overlay.querySelector('.star-map-close').onclick = closeStarMap;
    overlay.addEventListener('click', e => { if (e.target === overlay) closeStarMap(); });
    const nodes = overlay.querySelector('.star-map-nodes');
    chapters.forEach((ch, i) => {
      const btn = document.createElement('button'); btn.className = 'star-map-node'; btn.dataset.chapter = i + 1;
      const angle = (-Math.PI / 2) + i * (Math.PI * 2 / chapters.length);
      btn.style.left = (50 + Math.cos(angle) * 38) + '%'; btn.style.top = (50 + Math.sin(angle) * 34) + '%';
      btn.innerHTML = '<b>' + ch[0] + '</b><span>' + ch[1] + '</span><small>' + ch[2] + '</small>';
      btn.onclick = () => { window.location.href = '/chapter/' + (i + 1); };
      nodes.appendChild(btn);
    });
    window.addEventListener('keydown', e => { if (e.key === 'Escape') closeStarMap(); }, { once: true });
    return overlay;
  }
  function draw(canvas) {
    const ctx = canvas.getContext('2d'); let t = 0;
    const resize = () => { canvas.width = innerWidth * devicePixelRatio; canvas.height = innerHeight * devicePixelRatio; canvas.style.width = innerWidth + 'px'; canvas.style.height = innerHeight + 'px'; };
    resize(); window.addEventListener('resize', resize, { once: true });
    const stars = Array.from({ length: 180 }, () => ({ x: Math.random(), y: Math.random(), r: Math.random() * 1.8 + .2, a: Math.random() * .7 + .2 }));
    const loop = () => { t += .006; const w = innerWidth, h = innerHeight; ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0); ctx.clearRect(0, 0, w, h); ctx.fillStyle = '#020611'; ctx.fillRect(0, 0, w, h); stars.forEach(s => { ctx.fillStyle = `rgba(148,220,255,${s.a})`; ctx.beginPath(); ctx.arc(s.x * w, (s.y + t * .015) % 1 * h, s.r, 0, Math.PI * 2); ctx.fill(); }); const cx = w * .5, cy = h * .53; for (let i = 0; i < 3; i++) { ctx.strokeStyle = `rgba(103,232,249,${.16 - i * .035})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(cx, cy, 180 + i * 110, 70 + i * 44, -.18, 0, Math.PI * 2); ctx.stroke(); } raf = requestAnimationFrame(loop); };
    loop();
  }
  window.openStarMap = openStarMap; window.closeStarMap = closeStarMap;
})();
