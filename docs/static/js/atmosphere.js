/* ============================================================
   atmosphere.js — PyMaster 全站氛围层
   ------------------------------------------------------------
   把开场 CG 那套"六层叠加"的观感搬成全站通用的一层，但用 2D 画布实现：
   不是每一页都需要真正的 3D，而全站每页都挂 three.js 是浪费。

   每帧只做这几件事（都在预算内）：
     ① 贴两次预渲染的星云（反向缓慢漂移）
     ② 画三层视差星野（预渲染星点贴图，不是逐个 arc()）
     ③ 画漂浮孢子
     ④ 画指针水波（环带高光 + 局部折射重绘）
     ⑤ 画跟随指针的一汪光
   星云是开机用 2D 画布画一次的贴图，不是逐像素噪声函数 ——
   这条是拿集成显卡换来的教训（见 SKILL 里的性能红线）。

   主题按 body 类名自动判定，也可以用 <body data-atm="silk"> 显式指定。
   ============================================================ */
(function () {
  'use strict';

  if (window.__pmAtmosphereLoaded) return;
  window.__pmAtmosphereLoaded = true;

  const TAU = Math.PI * 2;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const rand = (a, b) => a + Math.random() * (b - a);
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const COARSE = matchMedia('(pointer: coarse)').matches;
  const DPR_CAP = COARSE ? 1.15 : 1.35;

  /* ══════════ 主题表 ══════════
     每个主题就是一组画星云/星野/孢子用的参数。改风格只改这里。 */
  const THEMES = {
    // 深海 + 生物荧光绿：主页与章节页，和开场 CG 同一套色
    abyss: {
      base: '#02060b',
      clouds: [
        [0.16, 0.24, 0.54, '120,225,140', 0.44],
        [0.82, 0.30, 0.50, '80,205,215', 0.38],
        [0.54, 0.90, 0.56, '60,115,195', 0.42],
        [0.05, 0.78, 0.46, '125,95,215', 0.32],
        [0.44, 0.18, 0.36, '160,255,120', 0.24],
      ],
      clumps: 40,
      snow: 520,
      starHues: ['175,240,255', '175,255,150', '190,170,255'],
      starCount: 300,
      spores: 26,
      sporeHues: ['150,245,120', '110,240,215', '150,140,255'],
      glow: '150,240,230',
      glowAlpha: 0.22,
      rippleHue: '150,240,255',
      rippleAlt: '157,255,87',
      drift: 1.0,
      intensity: 1,
      nebA: 0.95, nebB: 0.58,
    },
    // 深空：知识星海，星更密更亮，偏紫
    nebula: {
      base: '#02040e',
      clouds: [
        [0.20, 0.28, 0.58, '90,120,220', 0.50],
        [0.78, 0.34, 0.52, '150,110,230', 0.44],
        [0.50, 0.86, 0.60, '60,140,220', 0.38],
        [0.08, 0.72, 0.44, '190,120,235', 0.30],
        [0.62, 0.14, 0.34, '110,200,255', 0.26],
      ],
      clumps: 30,
      snow: 640,
      starHues: ['210,225,255', '170,190,255', '190,160,255', '150,240,255'],
      starCount: 420,
      spores: 30,
      sporeHues: ['140,170,255', '190,150,255', '120,230,250'],
      glow: '160,180,255',
      glowAlpha: 0.20,
      rippleHue: '180,200,255',
      rippleAlt: '190,160,255',
      drift: 0.75,
      intensity: 1,
      nebA: 0.60, nebB: 0.30,
    },
    // 绢本：修行阁。暖墨底 + 淡墨云气 + 微尘，一个霓虹色都不要
    silk: {
      base: '#0b0906',
      clouds: [
        [0.22, 0.26, 0.62, '196,176,140', 0.22],
        [0.80, 0.40, 0.56, '150,140,124', 0.18],
        [0.52, 0.88, 0.60, '120,104,84', 0.20],
        [0.10, 0.74, 0.50, '176,150,112', 0.14],
      ],
      clumps: 26,
      snow: 240,
      starHues: ['255,240,214', '236,220,190', '214,200,178'],
      starCount: 90,
      spores: 34,
      sporeHues: ['232,214,180', '214,196,160', '246,236,214'],
      glow: '236,216,176',
      glowAlpha: 0.10,
      rippleHue: '240,226,196',
      rippleAlt: '206,186,150',
      drift: 0.5,
      intensity: 0.8,
      nebA: 0.85, nebB: 0.45,
    },
    // 纸面：浅色主题专用。深色星云压在浅色页面上只会变成一层灰绿的泥，
    // 所以浅色模式换一套底 —— 米白宣纸 + 极淡的暖灰晕 + 少量浮尘，
    // 和深色模式是"两种材质"，不是同一张图调亮度。
    paper: {
      base: '#eef2f7',
      clouds: [
        [0.18, 0.22, 0.62, '198,214,232', 0.55],
        [0.84, 0.34, 0.58, '214,206,232', 0.42],
        [0.52, 0.90, 0.64, '186,206,226', 0.46],
        [0.08, 0.76, 0.52, '224,214,198', 0.34],
      ],
      clumps: 22,
      snow: 380,
      starHues: ['150,172,200', '168,158,198', '140,180,176'],
      starCount: 120,
      spores: 30,
      sporeHues: ['188,204,224', '206,196,222', '196,212,206'],
      glow: '178,200,224',
      glowAlpha: 0.16,
      rippleHue: '112,148,186',
      rippleAlt: '150,132,186',
      drift: 0.6,
      intensity: 0.9,
      nebA: 0.9, nebB: 0.5,
    },
    // 工作台：刷题 / 教练 / 仪表盘。只留极暗的底和稀疏星点，别抢注意力
    workbench: {
      base: '#05070c',
      clouds: [
        [0.18, 0.22, 0.56, '80,150,190', 0.22],
        [0.84, 0.36, 0.52, '110,100,200', 0.18],
        [0.50, 0.92, 0.58, '60,130,170', 0.18],
      ],
      clumps: 22,
      snow: 0,
      starHues: ['190,225,255', '180,255,210', '200,190,255'],
      starCount: 150,
      spores: 14,
      sporeHues: ['120,220,235', '150,240,160', '160,150,240'],
      glow: '140,200,220',
      glowAlpha: 0.12,
      rippleHue: '150,230,245',
      rippleAlt: '150,200,255',
      drift: 0.7,
      intensity: 0.85,
      nebA: 0.72, nebB: 0.40,
    },
  };

  function isLightTheme() {
    if (document.documentElement.getAttribute('data-theme') !== 'light') return false;
    // 再确认一次页面本身支持浅色：深色设计的页面（刷题、练习场…）
    // 一旦被套上纸面材质，就会出现"浅底 + 深面板"的割裂感。
    const cls = document.body ? document.body.classList : null;
    if (!cls) return false;
    return cls.contains('chapter-page') || cls.contains('dashboard-page');
  }

  function pickTheme() {
    // 浅色主题优先：这一套材质和深色的不是一回事，不能靠调透明度凑
    if (isLightTheme()) return 'paper';
    const explicit = (document.body.dataset.atm || '').trim();
    if (THEMES[explicit]) return explicit;
    const cls = document.body.className || '';
    if (/cultivation-page/.test(cls)) return 'silk';
    if (/workbench-page/.test(cls)) return 'workbench';
    return 'abyss';
  }

  let THEME_KEY = pickTheme();
  let T = THEMES[THEME_KEY];
  const BASE_THEME = THEME_KEY;   // 深色下的本页主题，切回深色时用它
  document.body.dataset.atm = THEME_KEY;

  /* ══════════ 画布与图层 ══════════ */
  const canvas = document.createElement('canvas');
  canvas.className = 'atm-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  document.body.insertBefore(canvas, document.body.firstChild);
  const ctx = canvas.getContext('2d', { alpha: false });

  // 暗角与噪点跟在 canvas 后面：都在内容之下，只压背景不压正文
  ['atm-vignette', 'atm-grain'].forEach((cls) => {
    const el = document.createElement('div');
    el.className = cls;
    el.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(el, canvas.nextSibling);
  });

  let W = 0, H = 0, dpr = 1;

  /* ══════════ 预渲染贴图 ══════════ */

  /** 星云底图：一次性画好，之后只是缩放贴图。 */
  function buildNebula(w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const x = c.getContext('2d');
    x.fillStyle = T.base;
    x.fillRect(0, 0, w, h);
    x.globalCompositeOperation = 'lighter';

    T.clouds.forEach(([cx, cy, r, rgb, a]) => {
      const g = x.createRadialGradient(cx * w, cy * h, 0, cx * w, cy * h, r * Math.max(w, h));
      g.addColorStop(0, 'rgba(' + rgb + ',' + a + ')');
      g.addColorStop(0.45, 'rgba(' + rgb + ',' + (a * 0.34) + ')');
      g.addColorStop(1, 'rgba(' + rgb + ',0)');
      x.fillStyle = g;
      x.fillRect(0, 0, w, h);
    });

    // 孢子绒面：上半部更密
    for (let i = 0; i < T.snow; i++) {
      const cx = Math.random() * w;
      const cy = Math.pow(Math.random(), 1.5) * h * 0.9;
      const r = rand(0.8, 6) * (1 + (1 - cy / h));
      const rgb = T.sporeHues[(Math.random() * T.sporeHues.length) | 0];
      const a = rand(0.04, 0.26) * (1 - (cy / h) * 0.5);
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, r * 3.2);
      g.addColorStop(0, 'rgba(' + rgb + ',' + a + ')');
      g.addColorStop(0.4, 'rgba(' + rgb + ',' + (a * 0.36) + ')');
      g.addColorStop(1, 'rgba(' + rgb + ',0)');
      x.fillStyle = g;
      x.beginPath();
      x.arc(cx, cy, r * 3.2, 0, TAU);
      x.fill();
    }

    // 暗色团块：把平铺的辉光咬出层次，像水底的岩与苔
    x.globalCompositeOperation = 'source-over';
    for (let i = 0; i < T.clumps; i++) {
      const cx = Math.random() * w;
      const cy = Math.random() * h;
      const r = rand(0.05, 0.22) * w;
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, r);
      const dark = THEME_KEY === 'silk' ? '6,5,3' : '2,5,9';
      g.addColorStop(0, 'rgba(' + dark + ',0.66)');
      g.addColorStop(0.6, 'rgba(' + dark + ',0.24)');
      g.addColorStop(1, 'rgba(' + dark + ',0)');
      x.fillStyle = g;
      x.fillRect(0, 0, w, h);
    }
    return c;
  }

  /** 星点/孢子的软光斑贴图，避免每帧几十次 createRadialGradient。 */
  function buildGlowSprite(rgb, size) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const x = c.getContext('2d');
    const g = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.25, 'rgba(' + rgb + ',0.72)');
    g.addColorStop(0.55, 'rgba(' + rgb + ',0.16)');
    g.addColorStop(1, 'rgba(' + rgb + ',0)');
    x.fillStyle = g;
    x.fillRect(0, 0, size, size);
    return c;
  }

  let nebulaA = null, nebulaB = null;
  let starSprites = T.starHues.map((h) => buildGlowSprite(h, 32));
  let sporeSprites = T.sporeHues.map((h) => buildGlowSprite(h, 96));
  let pointerGlow = buildGlowSprite(T.glow, 256);

  /* ══════════ 元素 ══════════ */
  let stars = [], spores = [], ripples = [];
  const ptr = { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, px: 0.5, py: 0.5, vx: 0, vy: 0, active: false };
  let intro = 0;          // 入场：0 → 1
  let arrived = false;
  let t = 0;

  function buildStars() {
    const n = Math.round(T.starCount * (W < 700 ? 0.55 : 1));
    stars = Array.from({ length: n }, () => {
      const depth = rand(0.25, 1);
      return {
        x: Math.random() * W, y: Math.random() * H, z: depth,
        s: rand(0.7, 2.6) * (0.5 + depth),
        ph: Math.random() * TAU,
        tw: rand(0.6, 2.1),
        sp: starSprites[(Math.random() * starSprites.length) | 0],
      };
    });
  }

  function buildSpores() {
    const n = Math.round(T.spores * (W < 700 ? 0.5 : 1));
    spores = Array.from({ length: n }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      r: rand(26, 110), a: rand(0.05, 0.16),
      vy: rand(-0.16, -0.05), vx: rand(-0.07, 0.07),
      sp: sporeSprites[(Math.random() * sporeSprites.length) | 0],
      ph: Math.random() * TAU,
    }));
  }

  function resize() {
    dpr = Math.min(devicePixelRatio || 1, DPR_CAP);
    W = innerWidth; H = innerHeight;
    canvas.width = Math.max(1, Math.floor(W * dpr));
    canvas.height = Math.max(1, Math.floor(H * dpr));
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    rebuildArt();
  }

  /** 按当前主题重建配色相关的素材与元素（切主题 / 首次初始化都走它） */
  function rebuildArt() {
    starSprites = T.starHues.map((h) => buildGlowSprite(h, 32));
    sporeSprites = T.sporeHues.map((h) => buildGlowSprite(h, 96));
    pointerGlow = buildGlowSprite(T.glow, 256);
    nebulaA = buildNebula(640, 400);
    nebulaB = buildNebula(360, 240);
    buildStars();
    buildSpores();
  }

  /** 深浅主题切换时换材质；这是"两种材质"，不是同一张图调亮度 */
  function applyTheme() {
    const next = pickTheme();
    if (next === THEME_KEY) return;
    THEME_KEY = next;
    T = THEMES[next];
    document.body.dataset.atm = next;
    // 重新开始时不要从"深色慢慢淡入"，直接给成片
    intro = 1;
    rebuildArt();
    draw();
  }

  /* ══════════ 水波 ══════════ */
  function addRipple(x, y, strength, growth) {
    ripples.push({
      x, y, r: 3,
      sr: strength === undefined ? 0.42 : strength,
      gr: growth === undefined ? 1.5 : growth,
      life: 1,
    });
    if (ripples.length > 26) ripples.shift();
  }

  function shockwave(x, y, big) {
    const n = big ? 4 : 2;
    for (let i = 0; i < n; i++) {
      setTimeout(() => addRipple(x, y, (big ? 0.8 : 0.45) - i * 0.14, (big ? 2.6 : 1.8) - i * 0.35), i * 80);
    }
  }

  /* ══════════ 指针交互 ══════════ */
  if (!COARSE) {
    addEventListener('pointermove', (e) => {
      ptr.tx = e.clientX / W;
      ptr.ty = e.clientY / H;
      ptr.vx = e.clientX - (ptr.lx === undefined ? e.clientX : ptr.lx);
      ptr.vy = e.clientY - (ptr.ly === undefined ? e.clientY : ptr.ly);
      ptr.lx = e.clientX; ptr.ly = e.clientY;
      ptr.active = true;
      // 走得越快，水面搅动越明显
      const speed = Math.hypot(ptr.vx, ptr.vy);
      if (speed > 2 && Math.random() < clamp(speed / 130, 0.01, 0.14)) {
        addRipple(e.clientX, e.clientY, clamp(speed / 340, 0.05, 0.22), 0.42);
      }
    }, { passive: true });

    addEventListener('pointerdown', (e) => {
      // 只对背景起反应：点在按钮/输入框上就别炸水花了
      if (e.target && e.target.closest && e.target.closest('a,button,input,textarea,select,label,[contenteditable],.wb-top,.topbar')) return;
      shockwave(e.clientX, e.clientY, false);
    }, { passive: true });
    addEventListener('pointerleave', () => { ptr.active = false; }, { passive: true });
  }

  /* ══════════ 绘制 ══════════ */
  function drawNebulaLayer(tile, ax, ay, aw, ah, alpha) {
    ctx.globalAlpha = alpha;
    ctx.drawImage(tile, ax, ay, aw, ah);
  }

  function draw() {
    const drift = t * 0.006 * T.drift;
    const ox = (ptr.x - 0.5) * 34;
    const oy = (ptr.y - 0.5) * 22;

    ctx.globalAlpha = 1;
    ctx.fillStyle = T.base;
    ctx.fillRect(0, 0, W, H);
    ctx.globalCompositeOperation = 'lighter';

    /* ① 星云：两层反向漂移，比单层更有"活着"的感觉，却只花两次贴图 */
    // 入场淡入只占一部分（0.6 → 1）：首帧就得是成片的亮度，
    // 否则截图、低帧率设备、或标签页没被激活时，看到的会是一块纯黑底。
    const k = 0.6 + 0.4 * intro;
    const s1 = 1.22;
    drawNebulaLayer(nebulaA,
      -W * (s1 - 1) / 2 + ox + Math.sin(drift) * 26,
      -H * (s1 - 1) / 2 + oy + Math.cos(drift * 0.8) * 18,
      W * s1, H * s1, T.nebA * k);
    ctx.globalAlpha = T.nebB * k * T.intensity;
    const s2 = 1.6;
    ctx.drawImage(nebulaB,
      -W * (s2 - 1) / 2 - ox * 1.6 - Math.sin(drift * 1.3) * 40,
      -H * (s2 - 1) / 2 - oy * 1.6 + Math.cos(drift * 1.1) * 30,
      W * s2, H * s2);

    /* ② 星野：三层视差 + 呼吸闪烁 + 快速移动时拉出短拖尾 */
    const streak = clamp(Math.hypot(ptr.vx, ptr.vy) / 26, 0, 1);
    const starK = 0.45 + 0.55 * intro;
    for (let i = 0; i < stars.length; i++) {
      const st = stars[i];
      const a = (0.18 + st.z * 0.55 + Math.sin(t * st.tw + st.ph) * 0.14) * starK;
      if (a <= 0.01) continue;
      const x = st.x + ox * st.z * 2.2;
      const y = st.y + oy * st.z * 2.2;
      const size = st.s * 4.4;
      ctx.globalAlpha = Math.min(1, a);
      if (streak > 0.25 && st.z > 0.6) {
        // 拖尾：把星点沿运动方向拉长，画面立刻"快"起来
        ctx.drawImage(st.sp, x - size / 2, y - size / 2, size + streak * 14, size);
      } else {
        ctx.drawImage(st.sp, x - size / 2, y - size / 2, size, size);
      }
    }

    /* ③ 孢子：大而柔的光斑缓慢上浮 */
    for (let i = 0; i < spores.length; i++) {
      const sp = spores[i];
      sp.x += sp.vx; sp.y += sp.vy;
      if (sp.y < -sp.r) { sp.y = H + sp.r; sp.x = Math.random() * W; }
      if (sp.x < -sp.r) sp.x = W + sp.r;
      if (sp.x > W + sp.r) sp.x = -sp.r;
      const pulse = 0.75 + Math.sin(t * 0.5 + sp.ph) * 0.25;
      ctx.globalAlpha = sp.a * pulse * k * T.intensity;
      const d = sp.r * 2;
      ctx.drawImage(sp.sp, sp.x - sp.r + ox * 0.5, sp.y - sp.r + oy * 0.5, d, d);
    }

    /* ④ 指针水波：环带高光 + 小半径处的局部折射重绘 */
    let refractions = 0;
    for (let i = ripples.length - 1; i >= 0; i--) {
      const rp = ripples[i];
      rp.r += rp.gr;
      rp.life -= 0.013;
      if (rp.life <= 0) { ripples.splice(i, 1); continue; }
      const a = rp.life * rp.life * rp.sr;

      // 局部折射：只在小半径时做，且每帧最多两次，避免全屏重绘
      if (refractions < 2 && rp.r < Math.min(W, H) * 0.22) {
        refractions++;
        const box = rp.r + 14;
        ctx.save();
        ctx.beginPath();
        ctx.arc(rp.x, rp.y, box, 0, TAU);
        ctx.arc(rp.x, rp.y, Math.max(0, rp.r - 12), 0, TAU, true);
        ctx.clip();
        ctx.globalAlpha = a * 0.5;
        // 把星云按"越靠外越偏移"重画一条环带，看起来就是水面把背景顶开了
        const s = 1.08;
        ctx.drawImage(nebulaA, rp.x - box, rp.y - box, box * 2, box * 2,
          rp.x - box * s + (rp.x - W / 2) * 0.006, rp.y - box * s + (rp.y - H / 2) * 0.006, box * 2 * s, box * 2 * s);
        ctx.restore();
      }

      ctx.globalAlpha = a * 0.55;
      ctx.strokeStyle = 'rgba(' + T.rippleHue + ',1)';
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.arc(rp.x, rp.y, rp.r, 0, TAU);
      ctx.stroke();
      ctx.globalAlpha = a * 0.22;
      ctx.strokeStyle = 'rgba(' + T.rippleAlt + ',1)';
      ctx.beginPath();
      ctx.arc(rp.x, rp.y, rp.r * 0.87, 0, TAU);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(rp.x, rp.y, rp.r * 1.12, 0, TAU);
      ctx.stroke();
    }

    /* ⑤ 跟随指针的一汪光：让"水"有存在感 */
    if (ptr.active && !COARSE) {
      const gx = ptr.x * W, gy = (1 - ptr.y) * H;
      const gs = Math.max(W, H) * 0.55;
      ctx.globalAlpha = T.glowAlpha * intro;
      ctx.drawImage(pointerGlow, gx - gs / 2, gy - gs / 2, gs, gs);
    }

    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ══════════ 主循环（约 40fps，背景不需要 60） ══════════ */
  let last = 0, acc = 0, paused = false;
  let frameCost = 0, frames = 0, degraded = 0;

  function loop(now) {
    requestAnimationFrame(loop);
    if (paused) return;
    const dt = Math.min(now - last, 100);
    last = now;
    acc += dt;
    if (acc < 25) return;
    acc = 0;

    if (REDUCED) { if (intro < 1) { intro = 1; draw(); } return; }

    t += 0.025;
    ptr.x = lerp(ptr.x, ptr.tx, 0.055);
    ptr.y = lerp(ptr.y, ptr.ty, 0.055);
    ptr.vx *= 0.9; ptr.vy *= 0.9;

    if (intro < 1) {
      intro = Math.min(1, intro + 0.022);
      if (!arrived && intro > 0.25) {
        arrived = true;
        // 入场：从画面中心推一圈水波出来，像镜头落定
        addRipple(W / 2, H * 0.45, 0.85, 3.4);
      }
    }

    const t0 = performance.now();
    draw();
    frameCost += performance.now() - t0;
    if (++frames >= 60) {
      // 自适应降档：背景是配角，拖慢主机就是本末倒置
      if (frameCost / frames > 14 && degraded < 2) {
        degraded++;
        T.spores = Math.max(6, Math.round(T.spores * 0.5));
        T.starCount = Math.max(60, Math.round(T.starCount * 0.55));
        buildStars(); buildSpores();
      }
      frameCost = 0; frames = 0;
    }
  }

  /* ══════════ 启动 ══════════ */
  let rt = 0;
  addEventListener('resize', () => {
    clearTimeout(rt);
    rt = setTimeout(() => { resize(); if (REDUCED) draw(); }, 180);
  }, { passive: true });

  document.addEventListener('visibilitychange', () => { paused = document.hidden; });

  // 主题开关在 main.js 里，它只改 html[data-theme]；这里跟着换材质。
  // 轮询而不是 MutationObserver：属性变化极低频，轮询更省心也更便宜。
  setInterval(applyTheme, 400);

  resize();
  // 先在低亮度下画一帧，避免刚打开时闪一下纯黑
  draw();
  requestAnimationFrame((n) => { last = n; requestAnimationFrame(loop); });

  // 给外部留的口子：切主题、手动炸水波
  window.PyMasterAtmosphere = {
    get theme() { return THEME_KEY; },
    ripple: addRipple,
    shock: shockwave,
    redraw: draw,
    applyTheme: applyTheme,
  };
})();
