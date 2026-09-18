/* ============================================================
   auth.js — 登录页的背景、之禅轮播与表单细节
   ------------------------------------------------------------
   登录页与开场 CG 是同一套视觉语言，所以这块背景也照 CG 的做法来：
   深海底色 + 有机孢子 + 星野视差，外加"点一下就有水波"的触感。
   表单本身仍由 main.js 驱动（登录 / 注册 / 本机账号），这里只做增强。
   ============================================================ */
(function () {
  'use strict';

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const rand = (a, b) => a + Math.random() * (b - a);
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ══════════ 1. 背景画布：星野 + 孢子 + 水波 ══════════ */
  const canvas = document.getElementById('auth-bg');
  const ctx = canvas ? canvas.getContext('2d') : null;

  if (ctx) {
    let W = 0, H = 0, dpr = 1;
    let stars = [], spores = [], ripples = [];
    let ptr = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5 };
    let t = 0;

    function resize() {
      dpr = Math.min(devicePixelRatio || 1, 2);
      W = innerWidth; H = innerHeight;
      canvas.width = Math.floor(W * dpr);
      canvas.height = Math.floor(H * dpr);
      canvas.style.width = W + 'px';
      canvas.style.height = H + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const area = W * H;
      stars = Array.from({ length: Math.min(260, Math.round(area / 8200)) }, () => ({
        x: Math.random() * W, y: Math.random() * H,
        z: rand(0.25, 1), ph: Math.random() * Math.PI * 2,
        hue: Math.random() < 0.6 ? '175,240,255' : (Math.random() < 0.7 ? '175,255,150' : '190,170,255'),
      }));
      // 孢子：大而柔的绿色光斑，是这张背景的"有机感"来源
      spores = Array.from({ length: Math.min(46, Math.round(area / 42000)) }, () => ({
        x: Math.random() * W, y: Math.random() * H,
        r: rand(24, 92), a: rand(0.03, 0.10),
        vy: rand(-0.10, -0.03), vx: rand(-0.05, 0.05),
        hue: Math.random() < 0.68 ? '140,240,120' : '110,235,215',
      }));
    }

    function draw() {
      t += 0.016;
      ptr.x = lerp(ptr.x, ptr.tx, 0.05);
      ptr.y = lerp(ptr.y, ptr.ty, 0.05);

      ctx.clearRect(0, 0, W, H);
      // 底色：两团大范围辉光，随指针轻微位移
      const ox = (ptr.x - 0.5) * 40, oy = (ptr.y - 0.5) * 26;
      const g1 = ctx.createRadialGradient(W * 0.22 + ox, H * 0.26 + oy, 0, W * 0.22 + ox, H * 0.26 + oy, Math.max(W, H) * 0.55);
      g1.addColorStop(0, 'rgba(60,140,80,0.16)');
      g1.addColorStop(1, 'rgba(60,140,80,0)');
      ctx.fillStyle = g1;
      ctx.fillRect(0, 0, W, H);
      const g2 = ctx.createRadialGradient(W * 0.82 - ox, H * 0.72 - oy, 0, W * 0.82 - ox, H * 0.72 - oy, Math.max(W, H) * 0.5);
      g2.addColorStop(0, 'rgba(40,120,140,0.16)');
      g2.addColorStop(1, 'rgba(40,120,140,0)');
      ctx.fillStyle = g2;
      ctx.fillRect(0, 0, W, H);

      ctx.globalCompositeOperation = 'lighter';

      // 孢子缓慢上浮
      spores.forEach((s) => {
        s.x += s.vx; s.y += s.vy;
        if (s.y < -s.r) { s.y = H + s.r; s.x = Math.random() * W; }
        if (s.x < -s.r) s.x = W + s.r;
        if (s.x > W + s.r) s.x = -s.r;
        const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.r);
        g.addColorStop(0, 'rgba(' + s.hue + ',' + s.a + ')');
        g.addColorStop(1, 'rgba(' + s.hue + ',0)');
        ctx.fillStyle = g;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fill();
      });

      // 星野视差
      const sx = (ptr.x - 0.5) * 26, sy = (ptr.y - 0.5) * 18;
      stars.forEach((st) => {
        const a = (0.16 + st.z * 0.5 + Math.sin(t * 1.1 + st.ph) * 0.12);
        ctx.beginPath();
        ctx.arc(st.x + sx * st.z, st.y + sy * st.z, Math.max(0.4, st.z * 1.3), 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + st.hue + ',' + a.toFixed(3) + ')';
        ctx.fill();
      });

      // 水波（点击 / 聚焦时溅出来的）
      for (let i = ripples.length - 1; i >= 0; i--) {
        const r = ripples[i];
        r.r += 2.6;
        r.life -= 0.017;
        if (r.life <= 0) { ripples.splice(i, 1); continue; }
        const a = r.life * r.life * 0.6;
        ctx.beginPath();
        ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(150,240,255,' + a.toFixed(3) + ')';
        ctx.lineWidth = 1.1;
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(r.x, r.y, r.r * 1.14, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(157,255,87,' + (a * 0.32).toFixed(3) + ')';
        ctx.stroke();
      }

      ctx.globalCompositeOperation = 'source-over';
      requestAnimationFrame(draw);
    }

    addEventListener('resize', resize, { passive: true });
    addEventListener('pointermove', (e) => {
      ptr.tx = e.clientX / innerWidth;
      ptr.ty = e.clientY / innerHeight;
    }, { passive: true });

    resize();
    if (REDUCED) {
      // 少动效：只画一帧静态星野
      t = 10;
      ctx.globalCompositeOperation = 'lighter';
      stars.forEach((st) => {
        ctx.beginPath();
        ctx.arc(st.x, st.y, Math.max(0.4, st.z * 1.3), 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + st.hue + ',0.5)';
        ctx.fill();
      });
      ctx.globalCompositeOperation = 'source-over';
    } else {
      requestAnimationFrame(draw);
    }

    // 点哪儿哪儿起涟漪 —— 和开场 CG 的"水流触感"是同一个手感
    addEventListener('pointerdown', (e) => {
      if (REDUCED) return;
      for (let i = 0; i < 3; i++) {
        setTimeout(() => {
          ripples.push({ x: e.clientX, y: e.clientY, r: 6 + i * 8, life: 1 - i * 0.18 });
        }, i * 80);
      }
    }, { passive: true });
  }

  /* ══════════ 2. Python 之禅轮播 ══════════ */
  const zenBox = document.getElementById('auth-zen');
  const ZEN = [
    ['简洁胜于复杂', 'Simple is better than complex.'],
    ['可读性很重要', 'Readability counts.'],
    ['优美胜于丑陋', 'Beautiful is better than ugly.'],
    ['现在胜于从不', 'Now is better than never.'],
    ['面对歧义，拒绝猜测的诱惑', 'Refuse the temptation to guess.'],
  ];
  if (zenBox && !REDUCED) {
    let i = 0;
    setInterval(() => {
      i = (i + 1) % ZEN.length;
      zenBox.classList.remove('swap');
      void zenBox.offsetWidth;
      zenBox.innerHTML = ZEN[i][0] + '<em>' + ZEN[i][1] + '</em>';
      zenBox.classList.add('swap');
    }, 5200);
  }

  /* ══════════ 3. 密码明文开关 ══════════ */
  document.querySelectorAll('input[type="password"]').forEach((input) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'pw-toggle';
    btn.textContent = '👁';
    btn.title = '显示 / 隐藏密码';
    btn.tabIndex = -1;
    btn.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.textContent = show ? '🙈' : '👁';
      btn.style.color = show ? 'var(--a-cyan)' : '';
      input.focus();
    });
    input.parentElement.appendChild(btn);
  });

  /* ══════════ 4. 选项卡联动（文案 + 滑块） ══════════ */
  const tabsBox = document.getElementById('auth-tabs');
  const titleEl = document.getElementById('auth-title');
  const subEl = document.getElementById('auth-sub');
  const COPY = {
    login: ['欢迎回来', '登录后学习记录、错题与修为都会保存在这台电脑上。'],
    register: ['创建你的账号', '信息只写进本机的 data/ 目录，不联网、不上传。'],
  };
  document.querySelectorAll('.auth-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      const key = tab.dataset.tab === 'register' ? 'register' : 'login';
      if (tabsBox) tabsBox.classList.toggle('reg', key === 'register');
      if (titleEl && COPY[key]) {
        titleEl.textContent = COPY[key][0];
        subEl.textContent = COPY[key][1];
      }
      // 切换表单时顺便把第一个输入框对好，省一次点击
      setTimeout(() => {
        const form = document.getElementById(key === 'register' ? 'register-form' : 'login-form');
        const first = form && form.querySelector('input');
        if (first && !first.value) first.focus();
      }, 60);
    });
  });

  /* ══════════ 5. 背景音乐（沿用平台那套） ══════════ */
  function tryPlayMusic() {
    try {
      if (window.AmbientMusic && typeof window.AmbientMusic.play === 'function') {
        window.AmbientMusic.play();
      }
    } catch (e) { /* 没配音乐资源就安静地算了 */ }
  }
  const once = () => {
    tryPlayMusic();
    removeEventListener('click', once);
    removeEventListener('touchstart', once);
    removeEventListener('keydown', once);
  };
  addEventListener('click', once);
  addEventListener('touchstart', once);
  addEventListener('keydown', once);
})();
