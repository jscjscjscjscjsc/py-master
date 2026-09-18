/* ============================================================
   intro_cg.js — PyMaster 引导 CG（开场动画）
   ------------------------------------------------------------
   一部可交互的 5 幕短片：溯源 → 禅 → 龟叔 → 大竞赛 → 启程

   三件"高级感"是刻意做进去的：
     1. 竖直章节导航栏：滚动跟随高亮，鼠标压上去有水波纹扩散 + 水滴声
     2. 水流触感：指针走过之处，WebGL 背景被涟漪扭曲，2D 画布叠一圈水面波
     3. 横向可延伸的 3D 卡片：hover 沿 Z 轴伸出，点击有冲击波并被推得更近

   无外部依赖（three.js 走本地 static/vendor），WebGL 不可用时自动降级为
   纯 CSS 星云 + 全部文字交互，短片照样能看完。
   ============================================================ */
(function () {
  'use strict';

  /* ═══════════════ 0. 小工具 ═══════════════ */
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => Array.from(document.querySelectorAll(s));
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = (t) => t * t * (3 - 2 * t);
  const smoother = (t) => t * t * t * (t * (t * 6 - 15) + 10);
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = (arr) => arr[(Math.random() * arr.length) | 0];

  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const COARSE = matchMedia('(pointer: coarse)').matches;
  const MOBILE = innerWidth < 820 || COARSE;

  const BODY = document.body;
  const NEXT = BODY.dataset.next || '/intro/done';
  const IS_STATIC = BODY.dataset.static === '1';
  const SECS = $$('.cg-sec');
  const HOLO_EL = document.querySelector('.cg-holo');

  const CH = [
    { cn: '溯源', en: 'Origin' },
    { cn: '禅', en: 'The Zen' },
    { cn: '龟叔', en: 'The Creator' },
    { cn: '大竞赛', en: 'The Race' },
    { cn: '启程', en: 'The Call' },
  ];
  const LAST = CH.length - 1;

  // 允许直接落到某一幕：/intro?ch=3。既能给外部链接用，
  // 也让"重看某一幕"不必从头等一遍。
  const CH_PARAM = new URLSearchParams(location.search).get('ch');
  const START_CH = CH_PARAM === null ? null : clamp(parseInt(CH_PARAM, 10) || 0, 0, LAST);

  /* ═══════════════ 1. 全局状态 ═══════════════ */
  const S = {
    target: 0,          // 目标位置（浮点章节）
    pos: 0,             // 平滑后的实际位置
    vel: 0,
    dragging: false,
    dragStart: 0,
    dragPos: 0,
    autoPlay: !REDUCED, // 未交互时像电影一样自己走
    autoTimer: null,
    finished: false,
    ready: false,
    startedAt: performance.now(),
    pointer: { x: 0.5, y: 0.5, tx: 0.5, ty: 0.5, vx: 0, vy: 0, lastX: 0, lastY: 0, moved: false },
    ripples: [],
    weight: new Array(CH.length).fill(0),
    chapLit: -1,
  };

  /* ═══════════════ 2. 自定义指针 ═══════════════ */
  const cursorEl = $('#cg-cursor');
  const cursorDot = $('#cg-cursor-dot');
  let curX = innerWidth / 2, curY = innerHeight / 2;
  let curTX = curX, curTY = curY;

  if (COARSE) BODY.classList.add('cg-touch');

  function onPointerMove(e) {
    const x = e.clientX, y = e.clientY;
    S.pointer.lastX = S.pointer.x;
    S.pointer.lastY = S.pointer.y;
    S.pointer.tx = x / innerWidth;
    S.pointer.ty = 1 - y / innerHeight;
    curTX = x; curTY = y;

    const dx = x - (S.pointer._px || x);
    const dy = y - (S.pointer._py || y);
    S.pointer._px = x; S.pointer._py = y;
    S.pointer.vx = dx; S.pointer.vy = dy;

    // 指针走得越快，水面搅动越明显
    const speed = Math.hypot(dx, dy);
    if (!COARSE && speed > 1.5 && Math.random() < clamp(speed / 90, 0.02, 0.22)) {
      addRipple(x, y, clamp(speed / 260, 0.06, 0.28), 0.32);
    }
  }
  addEventListener('pointermove', onPointerMove, { passive: true });

  const HOT_SEL = '[data-hot],a,button,.cg-card,.cg-node,.cg-pill,.cg-btn';
  addEventListener('pointerover', (e) => {
    const t = e.target && e.target.closest ? e.target.closest(HOT_SEL) : null;
    if (cursorEl) cursorEl.classList.toggle('cg-hover', !!t);
  });

  /* ═══════════════ 3. 水面涟漪（2D 画布层） ═══════════════ */
  const water = $('#cg-water');
  const wctx = water ? water.getContext('2d') : null;

  function addRipple(x, y, strength, growth) {
    if (!wctx) return;
    S.ripples.push({
      x, y,
      r: 4,
      sr: strength === undefined ? 0.5 : strength,
      gr: growth === undefined ? 1.6 : growth,
      life: 1,
    });
    if (S.ripples.length > 42) S.ripples.shift();
    if (gl) pushGLRipple(x / innerWidth, 1 - y / innerHeight, strength);
  }

  function addShock(x, y) {
    for (let i = 0; i < 4; i++) {
      setTimeout(() => addRipple(x, y, 0.85 - i * 0.16, 2.6 - i * 0.4), i * 90);
    }
  }

  function sizeWater() {
    if (!water) return;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    water.width = Math.floor(innerWidth * dpr);
    water.height = Math.floor(innerHeight * dpr);
    water.style.width = innerWidth + 'px';
    water.style.height = innerHeight + 'px';
    wctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function drawWater() {
    if (!wctx) return;
    wctx.clearRect(0, 0, innerWidth, innerHeight);
    wctx.globalCompositeOperation = 'screen';
    for (let i = S.ripples.length - 1; i >= 0; i--) {
      const rp = S.ripples[i];
      rp.r += rp.gr;
      rp.life -= 0.0125;
      if (rp.life <= 0) { S.ripples.splice(i, 1); continue; }
      const a = rp.life * rp.life * rp.sr;
      // 主环
      wctx.beginPath();
      wctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
      wctx.strokeStyle = 'rgba(150,240,255,' + (a * 0.55).toFixed(3) + ')';
      wctx.lineWidth = 1.2;
      wctx.stroke();
      // 色散：内外各错开一点，形成"水"的厚度
      wctx.beginPath();
      wctx.arc(rp.x, rp.y, rp.r * 0.86, 0, Math.PI * 2);
      wctx.strokeStyle = 'rgba(157,255,87,' + (a * 0.2).toFixed(3) + ')';
      wctx.stroke();
      wctx.beginPath();
      wctx.arc(rp.x, rp.y, rp.r * 1.1, 0, Math.PI * 2);
      wctx.strokeStyle = 'rgba(167,146,255,' + (a * 0.16).toFixed(3) + ')';
      wctx.stroke();
      // 中心的水光
      if (rp.r < 40) {
        const g = wctx.createRadialGradient(rp.x, rp.y, 0, rp.x, rp.y, 40 - rp.r);
        g.addColorStop(0, 'rgba(200,255,255,' + (a * 0.16).toFixed(3) + ')');
        g.addColorStop(1, 'rgba(200,255,255,0)');
        wctx.fillStyle = g;
        wctx.fillRect(rp.x - 40, rp.y - 40, 80, 80);
      }
    }
    wctx.globalCompositeOperation = 'source-over';
  }

  /* ═══════════════ 4. 环境音（纯 WebAudio，零素材） ═══════════════ */
  const Snd = {
    ctx: null, master: null, wet: null, padGain: null, on: true, started: false, nodes: [],

    boot() {
      if (this.ctx) return true;
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      try { this.ctx = new AC(); } catch (e) { return false; }

      this.master = this.ctx.createGain();
      this.master.gain.value = 0;
      this.master.connect(this.ctx.destination);

      // 生成一段噪声脉冲响应当混响，营造"深海空间"
      const len = Math.floor(this.ctx.sampleRate * 3.2);
      const ir = this.ctx.createBuffer(2, len, this.ctx.sampleRate);
      for (let c = 0; c < 2; c++) {
        const d = ir.getChannelData(c);
        for (let i = 0; i < len; i++) {
          d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 2.6);
        }
      }
      const conv = this.ctx.createConvolver();
      conv.buffer = ir;
      const wet = this.ctx.createGain();
      wet.gain.value = 0.62;
      this.wet = this.ctx.createGain();
      this.wet.connect(conv);
      conv.connect(wet);
      wet.connect(this.master);

      // 低通，把所有声音压成"水下"的听感
      const lp = this.ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.value = 1500;
      lp.Q.value = 0.6;
      lp.connect(this.master);
      lp.connect(this.wet);

      this.bus = lp;
      return true;
    },

    pad() {
      if (!this.ctx || this.padGain) return;
      const now = this.ctx.currentTime;
      const g = this.ctx.createGain();
      g.gain.value = 0;
      g.connect(this.bus);
      this.padGain = g;

      // D 小调的氛围和弦，缓慢呼吸
      const freqs = [73.42, 110.0, 146.83, 174.61, 220.0, 293.66];
      freqs.forEach((f, i) => {
        const o = this.ctx.createOscillator();
        o.type = i % 2 ? 'triangle' : 'sine';
        o.frequency.value = f * (1 + (Math.random() - 0.5) * 0.006);
        const og = this.ctx.createGain();
        og.gain.value = 0.16 / (1 + i * 0.5);
        const lfo = this.ctx.createOscillator();
        lfo.frequency.value = 0.035 + Math.random() * 0.05;
        const lg = this.ctx.createGain();
        lg.gain.value = og.gain.value * 0.75;
        lfo.connect(lg); lg.connect(og.gain);
        o.connect(og); og.connect(g);
        o.start(); lfo.start();
        this.nodes.push(o, lfo);
      });
      g.gain.linearRampToValueAtTime(0.9, now + 6);
    },

    setOn(on) {
      this.on = on;
      if (!this.master) return;
      const t = this.ctx.currentTime;
      this.master.gain.cancelScheduledValues(t);
      this.master.gain.linearRampToValueAtTime(on ? 0.5 : 0, t + (on ? 1.6 : 0.7));
    },

    start() {
      if (this.started || !this.on) return;
      if (!this.boot()) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();
      this.started = true;
      this.pad();
      this.setOn(true);
    },

    /** 水滴：指针压到导航节点 / 文字上时 */
    drop(pitch) {
      if (!this.started || !this.on) return;
      const c = this.ctx, t = c.currentTime;
      const o = c.createOscillator();
      o.type = 'sine';
      const f = pitch || rand(760, 1500);
      o.frequency.setValueAtTime(f, t);
      o.frequency.exponentialRampToValueAtTime(f * 0.55, t + 0.16);
      const g = c.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.16, t + 0.008);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.34);
      o.connect(g); g.connect(this.bus);
      o.start(t); o.stop(t + 0.4);
    },

    /** 换幕：一段低频掠过 */
    whoosh() {
      if (!this.started || !this.on) return;
      const c = this.ctx, t = c.currentTime;
      const n = c.createBufferSource();
      const len = Math.floor(c.sampleRate * 1.1);
      const buf = c.createBuffer(1, len, c.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 1.6);
      n.buffer = buf;
      const f = c.createBiquadFilter();
      f.type = 'bandpass';
      f.Q.value = 1.1;
      f.frequency.setValueAtTime(260, t);
      f.frequency.exponentialRampToValueAtTime(1500, t + 0.55);
      const g = c.createGain();
      g.gain.value = 0.14;
      n.connect(f); f.connect(g); g.connect(this.bus);
      n.start(t);
    },
  };

  const soundBtn = $('#cg-sound');
  function armSound() {
    Snd.start();
    if (soundBtn && Snd.started) soundBtn.textContent = 'SOUND ON';
    addEventListener('pointerdown', armSound, { once: true });
    addEventListener('keydown', armSound, { once: true });
  }
  armSound();

  if (soundBtn) {
    soundBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!Snd.started) { Snd.on = true; Snd.start(); Snd.drop(900); }
      else Snd.setOn(!Snd.on);
      soundBtn.textContent = Snd.on ? 'SOUND ON' : 'SOUND OFF';
      soundBtn.style.opacity = Snd.on ? '1' : '0.55';
    });
  }

  /* ═══════════════ 5. 渲染层：three.js 场景 ═══════════════ */
  let gl = null;             // { renderer, scene, camera, ... }
  let glRipples = [];        // 传给背景着色器的涟漪
  let glRippleSeeds = new Array(6).fill(0).map(() => [0, 0, 0, 0]);
  let glRippleCursor = 0;
  let _v3 = null;            // 复用的三维向量（THREE 就绪后再建）

  function pushGLRipple(x, y, strength) {
    glRippleSeeds[glRippleCursor] = [x, y - 0.06, 0.0, clamp(strength || 0.4, 0.05, 1)];
    glRippleCursor = (glRippleCursor + 1) % glRippleSeeds.length;
  }

  /* ── 5.1 程序化贴图 ─────────────────────────────── */
  function glowSprite(size, tint) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const x = c.getContext('2d');
    const g = x.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.28, 'rgba(' + tint + ',0.72)');
    g.addColorStop(0.62, 'rgba(' + tint + ',0.14)');
    g.addColorStop(1, 'rgba(' + tint + ',0)');
    x.fillStyle = g;
    x.fillRect(0, 0, size, size);
    const t = new THREE.CanvasTexture(c);
    if (THREE.sRGBEncoding !== undefined) t.encoding = THREE.sRGBEncoding;
    return t;
  }

  /** 把一段画在离屏 canvas 上的图形采样成点云 */
  function samplePoints(drawFn, w, h, step, scaleX, scaleY, depthJitter) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const x = c.getContext('2d');
    drawFn(x, w, h);
    const data = x.getImageData(0, 0, w, h).data;
    const pts = [];
    for (let py = 0; py < h; py += step) {
      for (let px = 0; px < w; px += step) {
        const i = (py * w + px) * 4;
        if (data[i + 3] < 90) continue;
        pts.push({
          x: (px / w - 0.5) * scaleX,
          y: -(py / h - 0.5) * scaleY,
          z: (Math.random() - 0.5) * (depthJitter || 0.4),
          r: data[i] / 255, g: data[i + 1] / 255, b: data[i + 2] / 255,
        });
      }
    }
    return pts;
  }

  function pointsFrom(pts, size, map, opacity, useColor) {
    const n = pts.length;
    const pos = new Float32Array(n * 3);
    const col = new Float32Array(n * 3);
    const rnd = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const p = pts[i];
      pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
      col[i * 3] = useColor ? p.r : 1;
      col[i * 3 + 1] = useColor ? p.g : 1;
      col[i * 3 + 2] = useColor ? p.b : 1;
      // 起手位置：随机球壳，用于"聚合"动画
      const th = Math.random() * Math.PI * 2;
      const ph = Math.acos(rand(-1, 1));
      const rr = rand(20, 46);
      rnd[i * 3] = Math.sin(ph) * Math.cos(th) * rr;
      rnd[i * 3 + 1] = Math.sin(ph) * Math.sin(th) * rr * 0.7;
      rnd[i * 3 + 2] = Math.cos(ph) * rr * 0.6;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    geo.setAttribute('aRandom', new THREE.BufferAttribute(rnd, 3));
    const mat = new THREE.PointsMaterial({
      size: size, map: map, transparent: true, opacity: opacity,
      depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: !!useColor,
      sizeAttenuation: true,
    });
    const points = new THREE.Points(geo, mat);
    points.userData.pos = pos;
    points.userData.rnd = rnd;
    points.userData.n = n;
    return points;
  }

  /** 每帧把点云在"散开"和"成形"之间插值（聚合动画） */
  function assemble(points, k) {
    const geo = points.geometry;
    const attr = geo.getAttribute('position');
    const tgt = points.userData.pos;
    const rnd = points.userData.rnd;
    const arr = attr.array;
    const n = points.userData.n;
    const e = smoother(clamp(k, 0, 1));
    if (points.userData.k === undefined) points.userData.k = -1;
    if (Math.abs(points.userData.k - e) < 0.002) return;
    points.userData.k = e;
    for (let i = 0; i < n; i++) {
      const i3 = i * 3;
      arr[i3] = lerp(rnd[i3], tgt[i3], e);
      arr[i3 + 1] = lerp(rnd[i3 + 1], tgt[i3 + 1], e);
      arr[i3 + 2] = lerp(rnd[i3 + 2], tgt[i3 + 2], e);
    }
    attr.needsUpdate = true;
  }

  /** 有机星云底图：一次性用 2D 画布画好，之后只用它贴图。
   *  不用逐帧噪声函数，是因为全屏 5 阶 fbm 会把集成显卡拖到个位数帧率。 */
  function nebulaTexture(w, h) {
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const x = c.getContext('2d');
    x.fillStyle = '#03060b';
    x.fillRect(0, 0, w, h);
    x.globalCompositeOperation = 'lighter';

    // 大团星云
    const clouds = [
      [0.16, 0.24, 0.52, '120,225,140', 0.30],
      [0.82, 0.30, 0.48, '80,205,215', 0.26],
      [0.54, 0.88, 0.55, '60,115,195', 0.30],
      [0.05, 0.78, 0.44, '125,95,215', 0.22],
      [0.44, 0.20, 0.34, '160,255,120', 0.16],
      [0.68, 0.66, 0.30, '90,230,200', 0.12],
    ];
    clouds.forEach(([cx, cy, r, rgb, a]) => {
      const g = x.createRadialGradient(cx * w, cy * h, 0, cx * w, cy * h, r * Math.max(w, h));
      g.addColorStop(0, 'rgba(' + rgb + ',' + a + ')');
      g.addColorStop(0.45, 'rgba(' + rgb + ',' + (a * 0.35) + ')');
      g.addColorStop(1, 'rgba(' + rgb + ',0)');
      x.fillStyle = g;
      x.fillRect(0, 0, w, h);
    });

    // 孢子/绒面：上半部更密，呼应参考图里那层深绿有机质感
    for (let i = 0; i < 620; i++) {
      const cx = Math.random() * w;
      const cy = Math.pow(Math.random(), 1.5) * h * 0.86;
      const r = rand(1.5, 11) * (1 + (1 - cy / h));
      const warm = Math.random();
      const rgb = warm < 0.62 ? '150,245,120' : (warm < 0.86 ? '110,240,215' : '150,140,255');
      const a = rand(0.05, 0.30) * (1 - cy / h * 0.5);
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, r * 3.4);
      g.addColorStop(0, 'rgba(' + rgb + ',' + a + ')');
      g.addColorStop(0.4, 'rgba(' + rgb + ',' + (a * 0.4) + ')');
      g.addColorStop(1, 'rgba(' + rgb + ',0)');
      x.fillStyle = g;
      x.beginPath();
      x.arc(cx, cy, r * 3.4, 0, Math.PI * 2);
      x.fill();
    }

    // 暗色团块：把平铺的辉光"咬"出层次，像水底的岩与苔
    x.globalCompositeOperation = 'source-over';
    for (let i = 0; i < 46; i++) {
      const cx = Math.random() * w;
      const cy = Math.random() * h;
      const r = rand(0.05, 0.2) * w;
      const g = x.createRadialGradient(cx, cy, 0, cx, cy, r);
      g.addColorStop(0, 'rgba(2,5,9,0.72)');
      g.addColorStop(0.6, 'rgba(2,5,9,0.28)');
      g.addColorStop(1, 'rgba(2,5,9,0)');
      x.fillStyle = g;
      x.fillRect(0, 0, w, h);
    }

    const tex = new THREE.CanvasTexture(c);
    if (THREE.sRGBEncoding !== undefined) tex.encoding = THREE.sRGBEncoding;
    tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
    tex.minFilter = THREE.LinearFilter;
    tex.generateMipmaps = false;
    return tex;
  }

  /* ── 5.2 场景搭建 ───────────────────────────────── */
  function initGL() {
    const canvas = $('#cg-webgl');
    if (!canvas || typeof THREE === 'undefined') return null;

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({
        canvas: canvas, antialias: !MOBILE, alpha: false, powerPreference: 'high-performance',
      });
    } catch (e) { return null; }
    if (!renderer || !renderer.getContext) return null;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x03060b, 0.016);
    const camera = new THREE.PerspectiveCamera(52, innerWidth / innerHeight, 0.1, 400);
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, MOBILE ? 1.25 : 1.5));
    renderer.setSize(innerWidth, innerHeight, false);
    renderer.setClearColor(0x03060b, 1);
    if (THREE.sRGBEncoding !== undefined) renderer.outputEncoding = THREE.sRGBEncoding;

    const G = {
      renderer: renderer, scene: scene, camera: camera,
      glow: glowSprite(64, '180,255,240'),
      glowBlue: glowSprite(64, '120,190,255'),
      glowGreen: glowSprite(64, '190,255,140'),
      groups: [], t: 0,
    };
    G.glowWhite = glowSprite(48, '255,255,255');
    _v3 = new THREE.Vector3();

    /* —— A. 背景：有机星云（预渲染贴图 + 涟漪扭曲） —— */
    const nebTex = nebulaTexture(1024, 640);
    const nebTexB = nebTex.clone();
    nebTexB.needsUpdate = true;
    const bgMat = new THREE.ShaderMaterial({
      uniforms: {
        uTime: { value: 0 },
        uAspect: { value: innerWidth / innerHeight },
        uTexAspect: { value: 1024 / 640 },
        uPointer: { value: new THREE.Vector2(0.5, 0.5) },
        uScroll: { value: 0 },
        uTex: { value: nebTex },
        uTexB: { value: nebTexB },
        uRipples: { value: glRippleSeeds.map((r) => new THREE.Vector4(r[0], r[1], r[2], r[3])) },
      },
      vertexShader: [
        'varying vec2 vUv;',
        'void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
      ].join('\n'),
      fragmentShader: [
        'precision highp float;',
        'uniform float uTime, uAspect, uTexAspect, uScroll;',
        'uniform vec2 uPointer;',
        'uniform vec4 uRipples[6];',
        'uniform sampler2D uTex, uTexB;',
        'varying vec2 vUv;',
        // 把平面 UV 换算成"按贴图比例取样"，避免星云被拉伸
        'vec2 fitUv(vec2 uv){',
        '  float pa = uAspect, ta = uTexAspect;',
        '  if (pa > ta) { float s = ta/pa; return vec2(uv.x, 0.5 + (uv.y-0.5)*s); }',
        '  float s = pa/ta; return vec2(0.5 + (uv.x-0.5)*s, uv.y);',
        '}',
        'void main(){',
        '  vec2 uv = vUv;',
        '  vec2 p = uv; p.x *= uAspect;',
        // 涟漪：指针划过的地方，水面把背景顶开
        '  vec2 disp = vec2(0.0);',
        '  for(int i=0;i<6;i++){',
        '    vec4 r = uRipples[i];',
        '    if(r.w < 0.002) continue;',
        '    vec2 rp = vec2(r.x*uAspect, r.y);',
        '    float d = distance(p, rp);',
        '    float ring = exp(-pow((d - r.z)*7.0, 2.0)) * r.w;',
        '    disp += normalize(p - rp + 1e-5) * ring * 0.05;',
        '  }',
        // 两层星云反向缓慢漂移，比单层更有"活着"的感觉，但只花两次采样
        '  float t = uTime * 0.008;',
        '  vec2 off = disp + (uPointer - 0.5) * 0.02;',
        '  vec2 uvA = fitUv(uv + off + vec2(t, -t * 0.7));',
        '  vec2 uvB = fitUv(uv * 0.82 + 0.09 + off * 1.6 - vec2(t * 1.3, t * 0.5));',
        '  vec3 col = texture2D(uTex, uvA).rgb;',
        '  col = max(col, texture2D(uTexB, uvB).rgb * 0.62);',
        // 跟随指针的一汪水光
        '  float pd = distance(p, vec2(uPointer.x*uAspect, uPointer.y));',
        '  col += vec3(0.14,0.38,0.42) * exp(-pd*3.6) * 0.26;',
        // 章节推进时整体略微提亮，配合镜头
        '  col *= 1.0 + uScroll*0.14;',
        // 暗角
        '  float v = smoothstep(1.22, 0.26, distance(uv, vec2(0.5)));',
        '  col *= 0.34 + 0.66*v;',
        '  gl_FragColor = vec4(col, 1.0);',
        '}',
      ].join('\n'),
      depthTest: false, depthWrite: false,
    });
    const bgDist = 70;
    const bgH = 2 * Math.tan((52 * Math.PI / 180) / 2) * bgDist;
    const bgMesh = new THREE.Mesh(new THREE.PlaneGeometry(bgH * 1.9, bgH * 1.25), bgMat);
    bgMesh.position.z = -bgDist;
    bgMesh.renderOrder = -1000;
    bgMesh.frustumCulled = false;
    camera.add(bgMesh);
    scene.add(camera);
    G.bg = bgMesh;
    G.bgMat = bgMat;

    /* —— B. 星野 —— */
    (function stars() {
      const n = MOBILE ? 700 : 1500;
      const pos = new Float32Array(n * 3);
      const col = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) {
        const r = rand(28, 120);
        const th = Math.random() * Math.PI * 2;
        const ph = Math.acos(rand(-1, 1));
        pos[i * 3] = Math.sin(ph) * Math.cos(th) * r;
        pos[i * 3 + 1] = Math.sin(ph) * Math.sin(th) * r * 0.72;
        pos[i * 3 + 2] = Math.cos(ph) * r * 0.8 - 18;
        const c = Math.random();
        if (c < 0.62) { col[i * 3] = 0.78; col[i * 3 + 1] = 0.94; col[i * 3 + 2] = 1.0; }
        else if (c < 0.86) { col[i * 3] = 0.72; col[i * 3 + 1] = 1.0; col[i * 3 + 2] = 0.62; }
        else { col[i * 3] = 0.82; col[i * 3 + 1] = 0.74; col[i * 3 + 2] = 1.0; }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      const mat = new THREE.PointsMaterial({
        size: 0.62, map: G.glowWhite, transparent: true, opacity: 0.9,
        depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true, sizeAttenuation: true,
      });
      G.starField = new THREE.Points(geo, mat);
      scene.add(G.starField);
    })();

    /* —— C. 第 0 幕：双蛇（Python 标志点云） —— */
    const ch0 = new THREE.Group();
    ch0.position.set(4.0, 0, 0);
    (function serpent() {
      const blue = 'M50 4 C28 4 26 13 26 24 L26 38 L52 38 L52 43 L16 43 C5 43 1 52 1 64 C1 76 6 84 18 84 L30 84 L30 66 C30 55 38 49 48 49 L70 49 C79 49 85 44 85 35 L85 23 C85 12 76 4 50 4 Z';
      // 只取轮廓：填色画得很淡（低于采样透明度阈值，不会被取到），
      // 描边画得实。结果是线框式的点云，比实心点阵干净得多。
      const pts = samplePoints(function (x, w, h) {
        x.clearRect(0, 0, w, h);
        x.save();
        x.scale(w / 100, h / 100);
        x.lineJoin = 'round';
        const draw = function (fill, stroke) {
          const p = new Path2D(blue);
          x.fillStyle = fill;
          x.fill(p);
          x.strokeStyle = stroke;
          x.lineWidth = 2.4;
          x.stroke(p);
        };
        draw('rgba(95,168,224,0.22)', 'rgba(150,215,255,1)');
        x.save();
        x.translate(50, 44); x.rotate(Math.PI); x.translate(-50, -44);
        draw('rgba(255,212,59,0.22)', 'rgba(255,225,120,1)');
        x.restore();
        x.restore();
      }, 260, 260, 2, 15, 15, 0.22);

      const p = pointsFrom(pts, 0.17, G.glow, 0.95, true);
      p.scale.set(0.9, 0.9, 0.9);
      ch0.add(p);
      ch0.userData.cloud = p;

      // 两条蛇的眼睛：标志形状里那两颗白点（位置按上一步的取形量出来的）
      [[2.05, 3.15], [-1.55, -2.35]].forEach((v, i) => {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({
          map: i ? G.glowGreen : G.glowWhite, transparent: true, opacity: 0.95,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }));
        s.position.set(v[0], v[1], 0.2);
        s.scale.set(0.9, 0.9, 0.9);
        ch0.add(s);
        ch0.userData['eye' + i] = s;
      });

      // 外圈光环
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(7.5, 7.62, 128),
        new THREE.MeshBasicMaterial({ color: 0x72f6e4, transparent: true, opacity: 0.24, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false })
      );
      ch0.add(ring);
      ch0.userData.ring = ring;
    })();
    scene.add(ch0);
    G.ch0 = ch0;
    G.groups.push(ch0);

    /* —— D. 第 1 幕：禅 · 碑林长廊 —— */
    const ZEN = [
      'Beautiful is better than ugly.',
      'Explicit is better than implicit.',
      'Simple is better than complex.',
      'Complex is better than complicated.',
      'Flat is better than nested.',
      'Sparse is better than dense.',
      'Readability counts.',
      "Special cases aren't special enough to break the rules.",
      'Although practicality beats purity.',
      'Errors should never pass silently.',
      'Unless explicitly silenced.',
      'In the face of ambiguity, refuse the temptation to guess.',
      'There should be one-- and preferably only one --obvious way to do it.',
      "Although that way may not be obvious at first unless you're Dutch.",
      'Now is better than never.',
      'Although never is often better than *right* now.',
      "If the implementation is hard to explain, it's a bad idea.",
      'If the implementation is easy to explain, it may be a good idea.',
      "Namespaces are one honking great idea -- let's do more of those!",
    ];
    const ch1 = new THREE.Group();
    (function steles() {
      const slabs = [];
      ZEN.forEach((line, i) => {
        const fs = 46;
        const c = document.createElement('canvas');
        const m = c.getContext('2d');
        m.font = '400 ' + fs + 'px "Cascadia Code","Consolas",monospace';
        const tw = Math.ceil(m.measureText(line).width) + 60;
        c.width = tw; c.height = fs + 46;
        const x = c.getContext('2d');
        x.font = '400 ' + fs + 'px "Cascadia Code","Consolas",monospace';
        x.fillStyle = i < 8 ? '#d8fbff' : 'rgba(190,235,255,0.72)';
        x.textBaseline = 'middle';
        x.fillText(line, 30, c.height / 2);
        const tex = new THREE.CanvasTexture(c);
        if (THREE.sRGBEncoding !== undefined) tex.encoding = THREE.sRGBEncoding;
        tex.minFilter = THREE.LinearFilter;

        const hgt = 1.3;
        const wid = hgt * (c.width / c.height);
        const mesh = new THREE.Mesh(
          new THREE.PlaneGeometry(wid, hgt),
          new THREE.MeshBasicMaterial({
            map: tex, transparent: true, opacity: 0, blending: THREE.AdditiveBlending,
            depthWrite: false, side: THREE.DoubleSide,
          })
        );
        const z = -12 - i * 3.4;
        // 整条长廊压在右半边、沿 -Z 远去：近处大而低，远处小而高，
        // 视觉上是从右下往画面中央收的一条碑道，左半边留给正文。
        mesh.position.set(7.4 + rand(-0.4, 0.4), -1.6 + Math.sin(i * 0.7) * 1.2, z);
        mesh.rotation.y = -0.12;
        mesh.userData.delay = i / ZEN.length;
        ch1.add(mesh);
        slabs.push(mesh);
      });
      ch1.userData.slabs = slabs;
    })();
    scene.add(ch1);
    G.ch1 = ch1;
    G.groups.push(ch1);

    /* —— E. 第 2 幕：龟叔 · 全息点云 —— */
    const ch2 = new THREE.Group();
    ch2.position.set(5.2, 0.2, 0);
    (function holo() {
      const pts = samplePoints(function (x, w, h) {
        x.clearRect(0, 0, w, h);
        x.strokeStyle = '#eaf4ff';
        x.lineWidth = 2.0;
        x.lineCap = 'round';
        const cx = w / 2, cy = h * 0.52, s = Math.min(w, h) / 240;
        x.save();
        x.translate(cx, cy);
        x.scale(s, s);
        // 头
        x.beginPath(); x.ellipse(0, -14, 44, 52, 0, 0, Math.PI * 2); x.stroke();
        // 肩与领
        x.beginPath(); x.moveTo(-64, 44); x.quadraticCurveTo(-58, 88, -22, 96); x.lineTo(22, 96);
        x.quadraticCurveTo(58, 88, 64, 44); x.stroke();
        x.beginPath(); x.moveTo(-18, 44); x.lineTo(0, 60); x.lineTo(18, 44); x.stroke();
        // 侧发
        x.beginPath(); x.ellipse(-37, -14, 9, 30, -0.18, 0, Math.PI * 2); x.stroke();
        x.beginPath(); x.ellipse(37, -14, 9, 30, 0.18, 0, Math.PI * 2); x.stroke();
        // 眉
        x.beginPath(); x.moveTo(-23, -31); x.quadraticCurveTo(-15, -36, -6, -31); x.stroke();
        x.beginPath(); x.moveTo(23, -31); x.quadraticCurveTo(15, -36, 6, -31); x.stroke();
        // 眼镜（标志性的圆框）
        x.beginPath(); x.ellipse(-14, -20, 15, 13.5, 0, 0, Math.PI * 2); x.stroke();
        x.beginPath(); x.ellipse(14, -20, 15, 13.5, 0, 0, Math.PI * 2); x.stroke();
        x.beginPath(); x.moveTo(1, -20); x.lineTo(-1, -20); x.stroke();
        x.beginPath(); x.moveTo(-29, -22); x.lineTo(-36, -24); x.stroke();
        x.beginPath(); x.moveTo(29, -22); x.lineTo(36, -24); x.stroke();
        // 瞳孔
        x.beginPath(); x.arc(-14, -20, 2.6, 0, Math.PI * 2); x.fillStyle = '#eaf4ff'; x.fill();
        x.beginPath(); x.arc(14, -20, 2.6, 0, Math.PI * 2); x.fill();
        // 鼻 / 嘴
        x.beginPath(); x.moveTo(0, -10); x.quadraticCurveTo(5, -2, 1, 5); x.stroke();
        x.beginPath(); x.arc(0, 12, 15, 0.24, Math.PI - 0.24); x.stroke();
        // 山羊胡
        x.beginPath(); x.moveTo(-17, 24); x.quadraticCurveTo(-16, 36, -5, 41);
        x.quadraticCurveTo(0, 43, 5, 41); x.quadraticCurveTo(16, 36, 17, 24); x.stroke();
        // 头顶微光轮廓
        x.beginPath(); x.ellipse(0, -52, 34, 16, 0, Math.PI, 0); x.stroke();
        x.restore();
      }, 260, 340, 2, 9.6, 12.6, 0.5);

      // 三层 RGB 色散：全息投影的色差
      const layers = [
        { c: [1.0, 0.18, 0.35], dx: -0.07, op: 0.46 },
        { c: [0.34, 1.0, 0.42], dx: 0.07, op: 0.46 },
        { c: [0.6, 0.85, 1.0], dx: 0, op: 0.95 },
      ];
      const clouds = layers.map((L) => {
        const geo = new THREE.BufferGeometry();
        const n = pts.length;
        const pos = new Float32Array(n * 3);
        const col = new Float32Array(n * 3);
        const rnd = new Float32Array(n * 3);
        for (let i = 0; i < n; i++) {
          const p = pts[i];
          pos[i * 3] = p.x + L.dx; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
          col[i * 3] = L.c[0]; col[i * 3 + 1] = L.c[1]; col[i * 3 + 2] = L.c[2];
          // 同样从球壳里"粒子化重组"
          const th = Math.random() * Math.PI * 2;
          const ph = Math.acos(rand(-1, 1));
          const rr = rand(16, 36);
          rnd[i * 3] = Math.sin(ph) * Math.cos(th) * rr + L.dx;
          rnd[i * 3 + 1] = Math.sin(ph) * Math.sin(th) * rr * 0.8;
          rnd[i * 3 + 2] = Math.cos(ph) * rr * 0.5;
        }
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
        geo.setAttribute('aRandom', new THREE.BufferAttribute(rnd, 3));
        const mat = new THREE.PointsMaterial({
          size: 0.19, map: G.glowWhite, transparent: true, opacity: L.op,
          depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true, sizeAttenuation: true,
        });
        const pt = new THREE.Points(geo, mat);
        pt.userData.pos = pos; pt.userData.rnd = rnd; pt.userData.n = n;
        ch2.add(pt);
        return pt;
      });
      ch2.userData.clouds = clouds;

      // 扫描环
      const rings = [];
      for (let i = 0; i < 3; i++) {
        const r = new THREE.Mesh(
          new THREE.RingGeometry(3.6, 3.68, 72),
          new THREE.MeshBasicMaterial({ color: 0x72f6e4, transparent: true, opacity: 0.4, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false })
        );
        r.rotation.x = Math.PI / 2;
        r.userData.off = i / 3;
        ch2.add(r);
        rings.push(r);
      }
      ch2.userData.rings = rings;

      // 底座光晕
      const halo = new THREE.Sprite(new THREE.SpriteMaterial({
        map: G.glow, transparent: true, opacity: 0.4, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      halo.scale.set(14, 14, 1);
      halo.position.y = -6.6;
      ch2.add(halo);
    })();
    scene.add(ch2);
    G.ch2 = ch2;
    G.groups.push(ch2);

    /* —— F. 第 3 幕：大竞赛 · 语言天际线 —— */
    const ch3 = new THREE.Group();
    (function skyline() {
      const langs = ['Python', 'C++', 'Java', 'JavaScript', 'C', 'Rust', 'Go', 'R'];
      const cols = [0x9dff57, 0x4b8bbe, 0xa792ff, 0xffd43b, 0x72f6e4, 0xff8a5c, 0x6ee7ff, 0xff6b9d];
      const pillars = [];
      langs.forEach((name, i) => {
        const hero = i === 0;
        const hgt = hero ? 9.2 : rand(2.6, 6.4) - i * 0.15;
        const g = new THREE.Group();
        const col = new THREE.Color(cols[i]);

        const core = new THREE.Mesh(
          new THREE.BoxGeometry(1.5, hgt, 1.5),
          new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: hero ? 0.22 : 0.1, blending: THREE.AdditiveBlending, depthWrite: false })
        );
        core.position.y = hgt / 2;
        g.add(core);

        const edges = new THREE.LineSegments(
          new THREE.EdgesGeometry(new THREE.BoxGeometry(1.5, hgt, 1.5)),
          new THREE.LineBasicMaterial({ color: col, transparent: true, opacity: hero ? 0.85 : 0.42, blending: THREE.AdditiveBlending, depthWrite: false })
        );
        edges.position.y = hgt / 2;
        g.add(edges);

        // 柱顶亮环
        const cap = new THREE.Mesh(
          new THREE.RingGeometry(0.85, 1.05, 32),
          new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: hero ? 0.95 : 0.5, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false })
        );
        cap.rotation.x = -Math.PI / 2;
        cap.position.y = hgt;
        g.add(cap);

        // 上升的数据粒子
        const pn = hero ? 240 : 70;
        const pp = new Float32Array(pn * 3);
        for (let k = 0; k < pn; k++) {
          pp[k * 3] = rand(-0.6, 0.6);
          pp[k * 3 + 1] = rand(0, hgt * 1.15);
          pp[k * 3 + 2] = rand(-0.6, 0.6);
        }
        const pgeo = new THREE.BufferGeometry();
        pgeo.setAttribute('position', new THREE.BufferAttribute(pp, 3));
        const pdust = new THREE.Points(pgeo, new THREE.PointsMaterial({
          size: 0.15, map: G.glowWhite, color: col, transparent: true, opacity: hero ? 0.9 : 0.4,
          depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
        }));
        pdust.userData.h = hgt;
        g.add(pdust);

        // 语言名
        const c = document.createElement('canvas');
        c.width = 512; c.height = 128;
        const x = c.getContext('2d');
        x.font = (hero ? '600 ' : '400 ') + (hero ? 74 : 56) + 'px "Segoe UI",system-ui,sans-serif';
        x.textAlign = 'center'; x.textBaseline = 'middle';
        x.fillStyle = '#' + col.getHexString();
        x.shadowColor = '#' + col.getHexString();
        x.shadowBlur = 26;
        x.fillText(name, 256, 66);
        const tex = new THREE.CanvasTexture(c);
        if (THREE.sRGBEncoding !== undefined) tex.encoding = THREE.sRGBEncoding;
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({
          map: tex, transparent: true, opacity: 0.95, depthWrite: false, blending: THREE.AdditiveBlending,
        }));
        sp.scale.set(hero ? 5.6 : 4.2, hero ? 1.4 : 1.05, 1);
        sp.position.y = hgt + (hero ? 1.5 : 1.1);
        g.add(sp);

        const x0 = -langs.length * 0.95;
        g.position.set(x0 + i * 1.9, 0, rand(-1.2, 1.2));
        g.userData = { hgt: hgt, hero: hero, cap: cap, core: core, edges: edges, dust: pdust, label: sp };
        ch3.add(g);
        pillars.push(g);
      });

      // 地面网格
      const grid = new THREE.GridHelper(46, 34, 0x1c4a52, 0x0d2630);
      grid.material.transparent = true;
      grid.material.opacity = 0.34;
      grid.position.y = -0.02;
      ch3.add(grid);

      ch3.position.set(2.8, -6.6, -5);
      ch3.scale.setScalar(0.86);
      ch3.userData.pillars = pillars;
    })();
    scene.add(ch3);
    G.ch3 = ch3;
    G.groups.push(ch3);

    /* —— G. 第 4 幕：启程 · 汇聚光环 —— */
    const ch4 = new THREE.Group();
    (function call() {
      const rings = [];
      for (let i = 0; i < 4; i++) {
        const r = new THREE.Mesh(
          new THREE.RingGeometry(6 + i * 2.4, 6.06 + i * 2.4, 128),
          new THREE.MeshBasicMaterial({
            color: i % 2 ? 0xa792ff : 0x72f6e4, transparent: true, opacity: 0.3,
            side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false,
          })
        );
        r.rotation.x = rand(-0.5, 0.5);
        r.rotation.y = rand(-0.4, 0.4);
        ch4.add(r);
        rings.push(r);
      }
      ch4.userData.rings = rings;

      // 向心粒子：像星流被吸进中心
      const n = MOBILE ? 500 : 1100;
      const pos = new Float32Array(n * 3);
      const col = new Float32Array(n * 3);
      const seed = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        const r = rand(16, 60);
        const th = Math.random() * Math.PI * 2;
        pos[i * 3] = Math.cos(th) * r;
        pos[i * 3 + 1] = rand(-16, 16) * (r / 45);
        pos[i * 3 + 2] = Math.sin(th) * r * 0.5;
        seed[i] = Math.random();
        const c = new THREE.Color(i % 3 === 0 ? 0x9dff57 : (i % 3 === 1 ? 0x72f6e4 : 0xa792ff));
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
      geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
      const pts = new THREE.Points(geo, new THREE.PointsMaterial({
        size: 0.34, map: G.glowWhite, transparent: true, opacity: 0.8,
        depthWrite: false, blending: THREE.AdditiveBlending, vertexColors: true, sizeAttenuation: true,
      }));
      pts.userData.base = pos.slice(0);
      pts.userData.seed = seed;
      ch4.add(pts);
      ch4.userData.flow = pts;
    })();
    scene.add(ch4);
    G.ch4 = ch4;
    G.groups.push(ch4);

    return G;
  }

  /* ── 5.3 相机关键帧 ─────────────────────────────── */
  const CAM = [
    { p: [0.0, 0.0, 26.0], l: [0.0, 0.0, 0.0], fov: 52 },     // 双蛇
    { p: [-1.5, 1.2, 6.0], l: [0.0, 1.0, -40.0], fov: 46 },   // 碑林长廊
    { p: [-3.4, 0.4, 14.0], l: [1.4, 0.1, 0.0], fov: 42 },    // 全息人像
    { p: [0.0, 4.6, 26.0], l: [0.0, -2.6, 0.0], fov: 52 },    // 语言天际线
    { p: [0.0, 0.0, 30.0], l: [0.0, 0.0, -4.0], fov: 44 },    // 启程
  ];

  function camAt(f) {
    const a = clamp(Math.floor(f), 0, LAST);
    const b = clamp(a + 1, 0, LAST);
    const t = smoother(clamp(f - a, 0, 1));
    const A = CAM[a], B = CAM[b];
    return {
      p: [lerp(A.p[0], B.p[0], t), lerp(A.p[1], B.p[1], t), lerp(A.p[2], B.p[2], t)],
      l: [lerp(A.l[0], B.l[0], t), lerp(A.l[1], B.l[1], t), lerp(A.l[2], B.l[2], t)],
      fov: lerp(A.fov, B.fov, t),
    };
  }

  /* ═══════════════ 6. 章节导航栏 ═══════════════ */
  const rail = $('#cg-rail');
  const railFill = $('#cg-rail-fill');
  const nodes = [];

  if (rail) {
    CH.forEach((c, i) => {
      const btn = document.createElement('button');
      btn.className = 'cg-node';
      btn.type = 'button';
      btn.dataset.hot = '1';
      btn.setAttribute('aria-label', c.cn + ' ' + c.en);
      btn.innerHTML =
        '<span class="cg-node-label"><b>' + c.cn + '</b><em>' + c.en + '</em></span>' +
        '<span class="cg-node-dot"></span>';
      btn.addEventListener('pointerenter', () => {
        const r = btn.getBoundingClientRect();
        addRipple(r.left + r.width / 2, r.top + r.height / 2, 0.5, 1.5);
        Snd.drop(820 + i * 130);
      });
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        takeControl();
        flyTo(i);
        const r = btn.getBoundingClientRect();
        addShock(r.left + r.width / 2, r.top + r.height / 2);
      });
      rail.appendChild(btn);
      nodes.push(btn);
    });
  }

  function flyTo(i, instant) {
    S.target = clamp(i, 0, LAST);
    if (instant) { S.pos = S.target; }
    if (S.target !== S.chapLit) Snd.whoosh();
  }

  /* ═══════════════ 7. 滚动 / 拖动 / 键盘 ═══════════════ */
  const WHEEL_UNIT = 620;

  function takeControl() {
    if (S.autoPlay) {
      S.autoPlay = false;
      clearTimeout(S.autoTimer);
      const cue = $('#cg-cue');
      if (cue) cue.classList.add('hide');
    }
  }

  function scrollBy(delta) {
    S.target = clamp(S.target + delta, 0, LAST);
  }

  addEventListener('wheel', (e) => {
    takeControl();
    // 触控板的自然滚动在这里同样成立：往下滚就是把叙事往前推
    scrollBy(clamp(e.deltaY / WHEEL_UNIT, -1.1, 1.1));
    if (Math.abs(e.deltaY) > 24) {
      addRipple(e.clientX, e.clientY, 0.22, 1.0);
    }
  }, { passive: true });

  addEventListener('keydown', (e) => {
    const k = e.key;
    if (k === 'Escape') { finish(true); return; }
    if (k === 'Enter') { finish(false); return; }
    if (k === 'ArrowDown' || k === 'ArrowRight' || k === 'PageDown' || k === ' ') {
      e.preventDefault(); takeControl(); flyTo(Math.round(S.target) + 1);
    } else if (k === 'ArrowUp' || k === 'ArrowLeft' || k === 'PageUp') {
      e.preventDefault(); takeControl(); flyTo(Math.round(S.target) - 1);
    } else if (k === 'Home') { takeControl(); flyTo(0); }
    else if (k === 'End') { takeControl(); flyTo(LAST); }
  });

  // 拖拽：鼠标按住上下拖 = 拉片
  let dragY = 0, dragT = 0, dragV = 0;
  addEventListener('pointerdown', (e) => {
    if (e.target.closest('a,button,.cg-card')) return;
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    S.dragging = true;
    dragY = e.clientY; dragT = S.target; dragV = 0;
    takeControl();
    addRipple(e.clientX, e.clientY, 0.55, 1.9);
    Snd.drop(640);
  });
  addEventListener('pointermove', (e) => {
    if (!S.dragging) return;
    const dy = e.clientY - dragY;
    dragV = dy;
    S.target = clamp(dragT - dy / (innerHeight * 0.52), 0, LAST);
  }, { passive: true });
  function endDrag() {
    if (!S.dragging) return;
    S.dragging = false;
    // 甩一下的惯性
    if (Math.abs(dragV) > 40) {
      S.target = clamp(S.target - (dragV / innerHeight) * 0.9, 0, LAST);
    }
  }
  addEventListener('pointerup', endDrag);
  addEventListener('pointercancel', endDrag);

  // 触摸
  let touchY = 0, touchT = 0;
  addEventListener('touchstart', (e) => {
    if (e.target.closest('a,button,.cg-card,.cg-deck')) return;
    touchY = e.touches[0].clientY; touchT = S.target;
    takeControl();
  }, { passive: true });
  addEventListener('touchmove', (e) => {
    if (!touchY) return;
    const dy = e.touches[0].clientY - touchY;
    S.target = clamp(touchT - dy / (innerHeight * 0.6), 0, LAST);
  }, { passive: true });
  addEventListener('touchend', () => { touchY = 0; }, { passive: true });

  /* ═══════════════ 8. 横向 3D 卡片 ═══════════════ */
  const deck = $('#cg-deck');
  if (deck) {
    const cards = Array.from(deck.children);
    cards.forEach((card, i) => {
      const rectOf = () => card.getBoundingClientRect();

      card.addEventListener('pointerenter', () => {
        const r = rectOf();
        addRipple(r.left + r.width / 2, r.top + r.height / 2, 0.42, 1.4);
        Snd.drop(680 + i * 90);
      });

      // 卡片本身跟随指针倾斜，做出"伸手可及"的立体触感
      card.addEventListener('pointermove', (e) => {
        const r = rectOf();
        const nx = (e.clientX - r.left) / r.width - 0.5;
        const ny = (e.clientY - r.top) / r.height - 0.5;
        card.style.setProperty('--mx', ((nx + 0.5) * 100).toFixed(1) + '%');
        card.style.setProperty('--my', ((ny + 0.5) * 100).toFixed(1) + '%');
        if (card.classList.contains('cg-open')) return;
        card.style.transform = 'translateZ(72px) translateX(-6px) rotateY(' + (5 + nx * 7).toFixed(2) +
          'deg) rotateX(' + (-ny * 6).toFixed(2) + 'deg) scale(1.035)';
      });
      card.addEventListener('pointerleave', () => { card.style.transform = ''; });

      const toggle = (e) => {
        const open = card.classList.toggle('cg-open');
        card.style.transform = '';
        const r = rectOf();
        addShock(r.left + r.width / 2, r.top + r.height / 2);
        // 推开同排的其他卡片，做出"横向上被延伸出去"的位移感
        cards.forEach((o, j) => {
          if (o === card) return;
          const d = j - i;
          o.style.transform = 'translateX(' + (open ? Math.sign(d) * 26 : 0) + 'px) translateZ(' +
            (open ? -40 : 0) + 'px) scale(' + (open ? 0.96 : 1) + ')';
          if (!open) setTimeout(() => { o.style.transform = ''; }, 20);
        });
        Snd.drop(open ? 1180 : 560);
        takeControl();
        if (e) e.stopPropagation();
      };
      card.addEventListener('click', toggle);
      card.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(e); }
      });
    });
  }

  /* ═══════════════ 9. 禅：文字上的水流 ═══════════════ */
  $$('.cg-zen-row').forEach((row, i) => {
    row.addEventListener('pointerenter', () => {
      const r = row.getBoundingClientRect();
      addRipple(r.left + 30, r.top + r.height / 2, 0.5, 1.7);
      Snd.drop(900 + i * 60);
    });
    row.addEventListener('pointermove', (e) => {
      if (Math.random() < 0.14) addRipple(e.clientX, e.clientY, 0.2, 0.9);
    });
  });

  /* ═══════════════ 10. 出口 ═══════════════ */
  const enterBtn = $('#cg-enter');
  const skipBtn = $('#cg-skip');
  const replayBtn = $('#cg-replay');

  function finish(skipped) {
    if (S.finished) return;
    S.finished = true;
    if (Snd.master && Snd.ctx) {
      try { Snd.master.gain.linearRampToValueAtTime(0, Snd.ctx.currentTime + 0.6); } catch (e) {}
    }
    const url = IS_STATIC ? 'index.html' : (NEXT + (skipped ? '?skip=1' : ''));
    const wipe = document.createElement('div');
    wipe.style.cssText = 'position:fixed;inset:0;z-index:60;background:radial-gradient(circle at 50% 50%,#0a1a22,#03060b 70%);' +
      'opacity:0;transition:opacity .7s cubic-bezier(.22,.61,.36,1);pointer-events:none;';
    document.body.appendChild(wipe);
    requestAnimationFrame(() => { wipe.style.opacity = '1'; });
    setTimeout(() => { location.href = url; }, 620);
  }

  if (enterBtn) {
    enterBtn.addEventListener('mouseenter', (e) => {
      const r = enterBtn.getBoundingClientRect();
      addRipple(r.left + r.width / 2, r.top + r.height / 2, 0.6, 1.8);
    });
    enterBtn.addEventListener('click', (e) => { e.preventDefault(); finish(false); });
  }
  if (skipBtn) {
    skipBtn.addEventListener('click', (e) => { e.stopPropagation(); finish(true); });
  }
  if (replayBtn) {
    replayBtn.addEventListener('click', () => {
      takeControl();
      S.finished = false;
      S.target = 0;
      Snd.drop(760);
      const r = replayBtn.getBoundingClientRect();
      addShock(r.left + r.width / 2, r.top + r.height / 2);
    });
  }

  /* ═══════════════ 11. 自动播放（电影感） ═══════════════ */
  const DWELL = [7600, 9200, 9200, 10400, 0];

  function scheduleAuto() {
    clearTimeout(S.autoTimer);
    if (!S.autoPlay) return;
    const i = Math.round(S.target);
    if (i >= LAST) return;
    S.autoTimer = setTimeout(() => {
      if (!S.autoPlay || document.hidden) { scheduleAuto(); return; }
      flyTo(Math.round(S.target) + 1);
      scheduleAuto();
    }, DWELL[i] || 9000);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) clearTimeout(S.autoTimer);
    else scheduleAuto();
  });

  /* ═══════════════ 12. 主循环 ═══════════════ */
  let waterT = 0, lastT = performance.now();
  // 自适应画质：教室里的老机器跑不动全分辨率时自动降档，宁可糊一点也别卡
  let fpsAcc = 0, fpsN = 0, quality = MOBILE ? 1.25 : 1.5, degradeStage = 0;

  function checkPerf(dt) {
    if (!gl || degradeStage >= 2) return;
    fpsAcc += dt; fpsN++;
    if (fpsN < 70) return;
    const avg = fpsAcc / fpsN;
    fpsAcc = 0; fpsN = 0;
    if (avg > 0.042) {
      degradeStage++;
      quality = degradeStage >= 2 ? 0.75 : 1.0;
      gl.renderer.setPixelRatio(Math.min(devicePixelRatio || 1, quality));
      gl.renderer.setSize(innerWidth, innerHeight, false);
    }
  }

  function frame(now) {
    requestAnimationFrame(frame);
    const dt = Math.min(now - lastT, 60) / 1000;
    lastT = now;
    if (!S.ready) return;
    checkPerf(dt);

    /* — 位置平滑：阻尼插值，产生"惯性镜头" — */
    const k = REDUCED ? 1 : 0.082;
    const prev = S.pos;
    S.pos = lerp(S.pos, S.target, k);
    S.vel = S.pos - prev;
    if (Math.abs(S.pos - S.target) < 0.0006) S.pos = S.target;

    /* — 指针平滑 — */
    S.pointer.x = lerp(S.pointer.x, S.pointer.tx, 0.06);
    S.pointer.y = lerp(S.pointer.y, S.pointer.ty, 0.06);

    /* — 自定义指针 — */
    if (cursorDot) {
      curX = lerp(curX, curTX, 0.42); curY = lerp(curY, curTY, 0.42);
      cursorDot.style.transform = 'translate(' + curTX.toFixed(1) + 'px,' + curTY.toFixed(1) + 'px)';
      if (cursorEl) cursorEl.style.transform = 'translate(' + curX.toFixed(1) + 'px,' + curY.toFixed(1) + 'px)';
    }

    /* — 章节权重 — */
    let active = -1, best = -1;
    for (let i = 0; i < CH.length; i++) {
      const d = Math.abs(S.pos - i);
      const w = smooth(clamp(1 - d * 1.55, 0, 1));
      S.weight[i] = w;
      if (w > best) { best = w; active = i; }
      const sec = SECS[i];
      if (sec) {
        const on = w > 0.42;
        if (on !== sec.classList.contains('cg-on')) {
          sec.classList.toggle('cg-on', on);
          if (on) zenLit(i);
        }
        if (w > 0.02) {
          sec.style.opacity = w.toFixed(3);
          sec.style.transform = 'translateY(' + ((S.pos - i) * -34).toFixed(1) + 'px)';
          sec.style.visibility = 'visible';
        } else {
          sec.style.visibility = 'hidden';
        }
      }
    }

    const finalEl = $('#cg-final');
    if (finalEl) finalEl.classList.toggle('cg-on', S.weight[LAST] > 0.5);

    // 导航 / HUD 状态
    if (active !== S.chapLit) {
      S.chapLit = active;
      nodes.forEach((n, i) => n.classList.toggle('cg-active', i === active));
      const cn = $('#cg-chap'), nm = $('#cg-chap-name');
      if (cn) cn.textContent = String(active).padStart(2, '0');
      if (nm) nm.textContent = CH[active].cn;
      if (active === 3) lightDeck();
    }
    const prog = S.pos / LAST;
    if (railFill) railFill.style.transform = 'scaleY(' + prog.toFixed(4) + ')';
    const footFill = $('#cg-foot-fill');
    if (footFill) footFill.style.width = (prog * 100).toFixed(2) + '%';

    /* — 水波层 — */
    waterT += dt;
    if (waterT > 0.033) { waterT = 0; drawWater(); }

    /* — 环境音：随镜头位置给一点起伏 — */
    if (Snd.padGain && Snd.started) {
      Snd.padGain.gain.value = 0.9 + Math.sin(now * 0.00018) * 0.18 + S.pos * 0.05;
    }

    if (gl) renderGL(dt, now);
  }

  function zenLit(chapter) {
    if (chapter !== 1) return;
    $$('.cg-zen-row').forEach((row, i) => {
      setTimeout(() => {
        row.classList.add('cg-lit');
        if (i === 0) Snd.drop(1040);
      }, 220 + i * 190);
    });
  }

  function lightDeck() {
    if (!deck) return;
    Array.from(deck.children).forEach((c, i) => {
      setTimeout(() => {
        c.classList.add('cg-hot');
        setTimeout(() => c.classList.remove('cg-hot'), 620);
      }, 260 + i * 130);
    });
  }

  /* ── 12.1 WebGL 每帧更新 ───────────────────────── */
  function renderGL(dt, now) {
    const G = gl, t = now * 0.001;
    G.t = t;
    const c = G.camera;
    const cam = camAt(S.pos);

    // 指针视差 + 冲击惯性
    const px = (S.pointer.x - 0.5), py = (S.pointer.y - 0.5);
    c.position.set(
      cam.p[0] + px * 1.9 + S.vel * 90,
      cam.p[1] + py * 1.2 + Math.sin(t * 0.11) * 0.14,
      cam.p[2]
    );
    const lx = cam.l[0] + px * 0.9, ly = cam.l[1] + py * 0.5, lz = cam.l[2];
    c.lookAt(lx, ly, lz);
    if (Math.abs(c.fov - cam.fov) > 0.01) { c.fov = cam.fov; c.updateProjectionMatrix(); }

    // 背景着色器
    G.bgMat.uniforms.uTime.value = t;
    G.bgMat.uniforms.uAspect.value = innerWidth / innerHeight;
    G.bgMat.uniforms.uScroll.value = S.pos / LAST;
    G.bgMat.uniforms.uPointer.value.set(S.pointer.x, S.pointer.y);
    // 涟漪场：半径随时间长大，强度衰减
    for (let i = 0; i < glRippleSeeds.length; i++) {
      const r = glRippleSeeds[i];
      if (r[3] > 0.001) {
        r[2] += dt * 0.55;
        r[3] *= Math.pow(0.36, dt);
        if (r[3] < 0.002) r[3] = 0;
      }
      G.bgMat.uniforms.uRipples.value[i].set(r[0], r[1], r[2], r[3]);
    }

    // 星野：跟随指针轻微视差
    if (G.starField) {
      G.starField.rotation.y = px * 0.16 + t * 0.005;
      G.starField.rotation.x = -py * 0.12;
      G.starField.position.z = S.pos * 1.6;
    }

    /* — 第 0 幕：双蛇聚合 — */
    const w0 = S.weight[0];
    if (w0 > 0.01) {
      G.ch0.visible = true;
      const cl = G.ch0.userData.cloud;
      assemble(cl, clamp(w0 * 1.5, 0, 1));
      cl.rotation.y = Math.sin(t * 0.22) * 0.34 + (1 - clamp(w0 * 1.4, 0, 1)) * 1.2;
      cl.rotation.x = Math.sin(t * 0.17) * 0.07;
      cl.material.opacity = 0.95 * clamp(w0 * 1.6, 0, 1);
      const pulse = 1 + Math.sin(t * 1.6) * 0.06;
      if (G.ch0.userData.eye0) {
        G.ch0.userData.eye0.scale.setScalar(0.9 * pulse * clamp(w0 * 1.6, 0, 1));
        G.ch0.userData.eye1.scale.setScalar(0.9 * pulse * clamp(w0 * 1.6, 0, 1));
        G.ch0.userData.eye0.material.opacity = 0.95 * clamp(w0, 0, 1);
        G.ch0.userData.eye1.material.opacity = 0.95 * clamp(w0, 0, 1);
      }
      if (G.ch0.userData.ring) {
        G.ch0.userData.ring.rotation.z = t * 0.12;
        G.ch0.userData.ring.material.opacity = 0.24 * clamp(w0 * 1.4, 0, 1);
        G.ch0.userData.ring.scale.setScalar(1 + Math.sin(t * 0.8) * 0.02);
      }
      G.ch0.position.z = (1 - clamp(w0 * 1.5, 0, 1)) * 6;
    } else G.ch0.visible = false;

    /* — 第 1 幕：碑林逐条点亮 — */
    const w1 = S.weight[1];
    if (w1 > 0.01) {
      G.ch1.visible = true;
      const local = clamp(S.pos - 0.55, 0, 1);
      G.ch1.userData.slabs.forEach((m, i) => {
        const d = Math.abs(local - m.userData.delay);
        const a = clamp(1 - d * 3.4, 0, 1);
        // 压到 0.5 以下：它是背景里的长廊，不能盖住左边的正文
        m.material.opacity = a * 0.42 * w1;
        m.position.x += Math.sin(t * 0.4 + i) * 0.0012;
      });
      G.ch1.position.z = (S.pos - 1) * -4;
    } else G.ch1.visible = false;

    /* — 第 2 幕：全息人像 — */
    const w2 = S.weight[2];
    if (w2 > 0.01) {
      G.ch2.visible = true;
      const k2 = clamp((w2 - 0.25) * 1.7, 0, 1);
      G.ch2.userData.clouds.forEach((cl, i) => {
        assemble(cl, k2);
        cl.material.opacity = (i === 2 ? 0.95 : 0.46) * clamp(w2 * 1.4, 0, 1);
      });

      // 把点云钉在右侧那个扫描取景框里：从取景框的屏幕坐标反推世界坐标，
      // 这样不管窗口多大、镜头怎么飞，人像都稳稳落在框中央。
      const fr = HOLO_EL ? HOLO_EL.getBoundingClientRect() : null;
      const useFrame = fr && fr.width > 10 && fr.height > 10;
      const ndcX = useFrame ? ((fr.left + fr.width / 2) / innerWidth) * 2 - 1 : 0.34;
      const ndcY = useFrame ? -(((fr.top + fr.height / 2) / innerHeight) * 2 - 1) : 0.02;
      const dist = 15;
      _v3.set(ndcX, ndcY, 0.5).unproject(c);
      _v3.sub(c.position).normalize().multiplyScalar(dist);
      _v3.add(c.position);
      G.ch2.position.lerp(_v3, 0.18);

      const hWorld = 2 * Math.tan((c.fov / 2) * Math.PI / 180) * dist;
      const want = useFrame
        ? (fr.height / innerHeight) * hWorld / 12.6 * 1.32
        : 0.9;
      _v3.set(want, want, want);
      G.ch2.scale.lerp(_v3, 0.18);

      G.ch2.rotation.y = Math.sin(t * 0.24) * 0.2 + px * 0.22;
      G.ch2.userData.rings.forEach((r, i) => {
        const ph = ((t * 0.34 + r.userData.off) % 1);
        r.position.y = lerp(6.4, -6.4, ph);
        r.scale.setScalar(1 - ph * 0.22);
        r.material.opacity = (0.42 * Math.sin(ph * Math.PI)) * clamp(w2 * 1.3, 0, 1);
      });
    } else G.ch2.visible = false;

    /* — 第 3 幕：语言天际线 — */
    const w3 = S.weight[3];
    if (w3 > 0.01) {
      G.ch3.visible = true;
      const rise = clamp((w3 - 0.2) * 1.5, 0, 1);
      // 天际线是背景层：压低亮度，别跟前面的卡片抢注意力
      const dim = 0.42 * clamp(w3 * 1.4, 0, 1);
      G.ch3.userData.pillars.forEach((g, i) => {
        const u = g.userData;
        const s = smoother(clamp(rise * 1.4 - i * 0.045, 0, 1));
        g.scale.y = Math.max(0.001, s);
        g.position.y = 0;
        u.cap.material.opacity = (u.hero ? 0.95 : 0.5) * s * (0.7 + Math.sin(t * 1.6 + i) * 0.3) * dim;
        u.label.material.opacity = clamp((s - 0.5) * 2, 0, 1) * (u.hero ? 1 : 0.62) * dim;
        u.edges.material.opacity = (u.hero ? 0.85 : 0.42) * s * dim;
        u.core.material.opacity = (u.hero ? 0.22 : 0.1) * s * dim;
        // 数据粒子持续上升
        const arr = u.dust.geometry.getAttribute('position').array;
        const hh = u.hgt * s;
        for (let k = 0; k < arr.length; k += 3) {
          arr[k + 1] += dt * (u.hero ? 1.7 : 0.9);
          if (arr[k + 1] > hh * 1.16) arr[k + 1] = 0;
        }
        u.dust.geometry.getAttribute('position').needsUpdate = true;
        u.dust.material.opacity = (u.hero ? 0.9 : 0.4) * s * dim;
      });
      G.ch3.rotation.y = Math.sin(t * 0.1) * 0.06 + px * 0.16;
      G.ch3.position.z = -5 + (1 - clamp(w3 * 1.5, 0, 1)) * -8;
    } else G.ch3.visible = false;

    /* — 第 4 幕：向心星流 — */
    const w4 = S.weight[4];
    if (w4 > 0.01) {
      G.ch4.visible = true;
      G.ch4.userData.rings.forEach((r, i) => {
        r.rotation.z += dt * (0.06 + i * 0.03) * (i % 2 ? -1 : 1);
        r.material.opacity = 0.3 * clamp(w4 * 1.3, 0, 1);
        r.scale.setScalar(1 + Math.sin(t * 0.5 + i) * 0.03);
      });
      const flow = G.ch4.userData.flow;
      const arr = flow.geometry.getAttribute('position').array;
      const base = flow.userData.base;
      const n = arr.length / 3;
      for (let i = 0; i < n; i++) {
        const i3 = i * 3;
        const s = (t * 0.14 + flow.userData.seed[i]) % 1;
        const shrink = 1 - s * 0.82;
        arr[i3] = base[i3] * (shrink * 0.22 + 0.78) * (1 - s * 0.6);
        arr[i3 + 1] = base[i3 + 1] * (shrink * 0.2 + 0.8) * (1 - s * 0.5);
        arr[i3 + 2] = base[i3 + 2] * (shrink * 0.22 + 0.78) * (1 - s * 0.6) + s * 6;
      }
      flow.geometry.getAttribute('position').needsUpdate = true;
      flow.material.opacity = 0.8 * clamp(w4 * 1.2, 0, 1);
      G.ch4.rotation.y = px * 0.6;
      G.ch4.rotation.x = -py * 0.3;
    } else G.ch4.visible = false;

    G.renderer.render(G.scene, G.camera);
  }

  /* ═══════════════ 13. 尺寸 / 启动 ═══════════════ */
  function resize() {
    sizeWater();
    if (!gl) return;
    gl.camera.aspect = innerWidth / innerHeight;
    gl.camera.updateProjectionMatrix();
    gl.renderer.setSize(innerWidth, innerHeight, false);
    gl.renderer.setPixelRatio(Math.min(devicePixelRatio || 1, quality));
  }
  addEventListener('resize', resize, { passive: true });

  const TIPS = [
    '正在生成星云…',
    '正在唤醒两条蛇…',
    '正在抄写 Python 之禅…',
    '正在构建全息档案…',
    '正在统计语言排行…',
    '就绪 —',
  ];

  function boot() {
    sizeWater();
    if (START_CH !== null) {
      S.target = START_CH;
      S.pos = START_CH;
      S.autoPlay = false;
      BODY.classList.add('cg-instant');
    }
    const bar = $('#cg-load-bar');
    const tip = $('#cg-load-tip');
    let step = 0;
    const tick = setInterval(() => {
      step++;
      if (bar) bar.style.width = Math.min(100, step * 22) + '%';
      if (tip && TIPS[step]) tip.textContent = TIPS[step];
      if (step >= 5) clearInterval(tick);
    }, 190);

    // 让加载层先画一帧，避免首帧卡顿看着像死机
    setTimeout(() => {
      gl = initGL();
      if (!gl) {
        // WebGL 不可用：CSS 星云兜底，其余交互照常
        BODY.classList.add('cg-nogl');
        if (tip) tip.textContent = '当前环境不支持 3D，已切换到轻量模式';
      }
      S.ready = true;
      requestAnimationFrame(frame);

      setTimeout(() => {
        const loader = $('#cg-loader');
        if (loader) loader.classList.add('cg-gone');
        scheduleAuto();
      }, 900);
      // 开场先给一圈水波，把"水"这件事交代清楚
      setTimeout(() => {
        addRipple(innerWidth * 0.42, innerHeight * 0.52, 0.7, 2.2);
        Snd.start();
      }, 420);
    }, 60);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // 给外部（登录页"重看开场"等）留的口子
  window.PyMasterIntro = { finish: finish, flyTo: flyTo, addRipple: addRipple };
})();
