/**
 * starfield.js — 星辰教练身后那片「星河」（canvas 2D）
 *
 * 目标：一眼看上去是一片**有纵深、有结构、在呼吸**的深空，
 * 而不是「黑底上撒了几个点」。同时它必须是一块背景：
 * 正文永远比它清楚，集显也不能被它拖垮。
 *
 * ── 这片星河是怎么搭起来的（由远及近）─────────────────────
 *
 *   ①  底色        深空渐变。刻意不是纯黑——纯黑看起来像「没画完」。
 *   ②  星云气团    域扭曲 fBm 烘出来的低分辨率贴图。
 *                   「深邃」不是靠更黑，是靠**层次**：气团要有内部结构，
 *                   并且被自己内部的恒星群照亮——这一条是从
 *                   wwwtyro/space-scene-2d 的做法里偷的（它把星云当体积，
 *                   用点光源照亮密度场，所以云是「浮」在星海里的，
 *                   而不是贴了一张渐变）。烘一次用一辈子，主循环一次 drawImage。
 *   ③  银河带      一道斜贯画面的密度脊 + **暗尘带**。尘带是「这是银河」
 *                   最强的线索——没有它，那条带子只是雾。
 *   ④  微星场      几千颗 1px 以下的暗星，整层烘成一张贴图。它负责「星海」的
 *                   量感：真实的夜空是"数不清"，不是"几百颗"。
 *   ⑤  分层星野    四层视差活星。尺寸与亮度走**幂律分布**
 *                   （90% 又小又暗、1% 又大又亮），眼睛才读得出星等；
 *                   颜色走**黑体色温**（Tanner Helland 近似），
 *                   整片天空才不会是同一个白。
 *   ⑥  锚点星      少数几颗带衍射星芒的亮星，作为「远近」的参照物。
 *   ⑦  浮尘/散景   几团很大的虚焦光斑，负责近景那一侧的景深。
 *   ⑧  云海        底部几条横向漂移的雾带。它同时干三件事：
 *                   托住法相（人不再浮在半空）、给画面一个出路、
 *                   以及把「星海」接到「仙家」那一口气上。
 *   ⑨  颗粒/暗角   抖动噪点消掉深色渐变必有的色带；暗角把视线收回中间。
 *
 * ── 四条不能破的约定 ──────────────────────────────────────
 *
 *   1. **噪声只烘一次。** 逐像素 fBm 放进主循环是这台机器上踩过的坑
 *      （开场 CG 最初就是这么把显卡跑满的）。这里全部烘到离屏贴图，
 *      主循环只做 drawImage。
 *   2. **发光一律走预渲染精灵。** 每颗星设一次 shadowBlur 会让帧时间翻几倍。
 *   3. **一定要能停。** 纯色档、页面不可见、系统开了「减少动态效果」，
 *      这三种情况必须真的停掉 rAF，而不是把 canvas 透明了继续空转。
 *   4. **低端机降档后不回头。** 连续掉帧就砍星数与散景，砍过的档位不升回去，
 *      免得在阈值附近来回抖。
 *   5. 整段 create() 不许往外抛。它跑在页面的 DOMContentLoaded 里，
 *      抛出去会把后面「画法相、画等级条」一起带崩（真实踩过）。
 *
 * 对外：create(canvas, options) → { setMode, setPalette, destroy }。
 */
(function () {
  'use strict';

  const DPR_CAP = 1.5;          // 超过这个比例肉眼已看不出差别，纯粹在烧显卡
  const SLOW_FRAME = 42;        // 连续 70 帧平均超过这个毫秒数就降档
  const GAS_LONG = 420;         // 星云贴图长边（它是雾，不是线稿，低分辨率完全够）
  const MIST_W = 1024;          // 云海贴图（x 方向可无缝平铺）
  const MIST_H = 200;
  const GRAIN = 96;             // 抖动噪点贴图尺寸
  const NOISE_N = 256;          // 噪声查找表边长（也是可平铺的周期）

  function reduceMotion() {
    try {
      return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) {
      return false;
    }
  }

  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }

  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }
  function clamp255(v) { return v < 0 ? 0 : (v > 255 ? 255 : v); }

  /** '#rrggbb' → [r,g,b]。绝不返回颜色字面量：上一版这里返回 'rgb(...)'，
   *  调用方再拼 'cc' 当 alpha，拼出 'rgb(1,2,3)cc' 这种非法颜色，
   *  addColorStop 直接抛异常——而它在 create() 里、create 又在 DOMContentLoaded
   *  里，一抛就把后面画法相、画等级条全带崩了。 */
  function toRgb(hex, fallback) {
    const value = String(hex || '').replace('#', '').trim();
    const full = value.length === 3 ? value.split('').map((c) => c + c).join('') : value;
    if (!/^[0-9a-fA-F]{6}$/.test(full)) return fallback;
    return [
      parseInt(full.slice(0, 2), 16),
      parseInt(full.slice(2, 4), 16),
      parseInt(full.slice(4, 6), 16),
    ];
  }

  function rgbStr(c) { return `${Math.round(c[0])},${Math.round(c[1])},${Math.round(c[2])}`; }

  /** 黑体色温 → RGB（Tanner Helland 的经典近似）。
   *  星星的颜色不是随便挑的：3000K 是橙红、5800K 是白、12000K 是蓝白。
   *  「一片有真实色温的天空」和「一片随机白点」，差别就在这。 */
  function kelvin(k) {
    const t = Math.max(1000, Math.min(40000, k)) / 100;
    let r;
    let g;
    let b;
    if (t <= 66) {
      r = 255;
      g = 99.4708025861 * Math.log(t) - 161.1195681661;
    } else {
      r = 329.698727446 * Math.pow(t - 60, -0.1332047592);
      g = 288.1221695283 * Math.pow(t - 60, -0.0755148492);
    }
    if (t >= 66) b = 255;
    else if (t <= 19) b = 0;
    else b = 138.5177312231 * Math.log(t - 10) - 305.0447927307;
    return [clamp255(r), clamp255(g), clamp255(b)];
  }

  /** 色相环上挪一点。整片星云需要两三个不同色相的气团才不单调，
   *  但每个境界只给了一个主色，所以这里自己推。 */
  function shiftHue(rgb, deg, satMul, lightMul) {
    const r = rgb[0] / 255;
    const g = rgb[1] / 255;
    const b = rgb[2] / 255;
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const l = (max + min) / 2;
    const d = max - min;
    let h = 0;
    let s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
    if (d !== 0) {
      if (max === r) h = ((g - b) / d) % 6;
      else if (max === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    h = (h + deg + 360) % 360;
    s = clamp01(s * (satMul == null ? 1 : satMul));
    const L = Math.max(0.03, Math.min(0.97, l * (lightMul == null ? 1 : lightMul)));
    const c = (1 - Math.abs(2 * L - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = L - c / 2;
    let rr = 0;
    let gg = 0;
    let bb = 0;
    if (h < 60) { rr = c; gg = x; } else if (h < 120) { rr = x; gg = c; }
    else if (h < 180) { gg = c; bb = x; } else if (h < 240) { gg = x; bb = c; }
    else if (h < 300) { rr = x; bb = c; } else { rr = c; bb = x; }
    return [Math.round((rr + m) * 255), Math.round((gg + m) * 255), Math.round((bb + m) * 255)];
  }

  // ── 噪声 ─────────────────────────────────────────────────
  // 全部走一张 256×256 的随机表做查表，而不是每次采样现算哈希：
  // 星云贴图要算十万级像素 × 十几次噪声，现算哈希的话单这一块就要一秒多，
  // 页面会明显卡一下。查表版本快三倍以上，而且 256 的周期天然可平铺。
  const NOISE_TAB = new Float32Array(NOISE_N * NOISE_N);
  for (let i = 0; i < NOISE_TAB.length; i += 1) NOISE_TAB[i] = Math.random() * 2 - 1;

  function vn(x, y) {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    const fx = x - ix;
    const fy = y - iy;
    const ux = fx * fx * (3 - 2 * fx);
    const uy = fy * fy * (3 - 2 * fy);
    const x0 = ix & (NOISE_N - 1);
    const y0 = (iy & (NOISE_N - 1)) * NOISE_N;
    const x1 = (ix + 1) & (NOISE_N - 1);
    const y1 = ((iy + 1) & (NOISE_N - 1)) * NOISE_N;
    const a = NOISE_TAB[y0 + x0];
    const b = NOISE_TAB[y0 + x1];
    const c = NOISE_TAB[y1 + x0];
    const d = NOISE_TAB[y1 + x1];
    const top = a + (b - a) * ux;
    const bot = c + (d - c) * ux;
    return top + (bot - top) * uy;
  }

  /** fBm。oct 一般 2-4；每层加一个大位移避免各层在格点上同相。 */
  function fbm(x, y, oct) {
    let sum = 0;
    let amp = 0.5;
    let freq = 1;
    let norm = 0;
    let ox = 0.37;
    let oy = 0.71;
    for (let i = 0; i < oct; i += 1) {
      sum += amp * vn(x * freq + ox, y * freq + oy);
      norm += amp;
      amp *= 0.5;
      freq *= 2;
      ox += 13.1;
      oy += 7.7;
    }
    return sum / (norm || 1);
  }

  /** 域扭曲：fbm(p + 4·fbm(p + 4·fbm(p)))，iquilezles.org/articles/warp。
   *  没有它，星云就是一坨一坨的圆斑；有了它才是被拉扯、卷曲过的气。
   *  这里收成两轮（q 一轮、r 一轮）——第三轮在几百像素的贴图上肉眼分辨不出，
   *  但要多付一倍的噪声成本。 */
  function warped(x, y) {
    const qx = fbm(x, y, 2);
    const qy = fbm(x + 5.2, y + 1.3, 2);
    const rx = fbm(x + 4 * qx + 1.7, y + 4 * qy + 9.2, 2);
    const ry = fbm(x + 4 * qx + 8.3, y + 4 * qy + 2.8, 2);
    return fbm(x + 4 * rx, y + 4 * ry, 3);
  }

  // ── 预渲染精灵 ───────────────────────────────────────────
  /** 一枚发光点。**收紧**的衰减（0.14 → 0.42 就掉到很低）是关键：
   *  上一版衰减太软，每颗星都成了一团虚焦大光斑，整片天空像失焦的照片。 */
  function makeGlow(size, rgb, tight) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const g = c.getContext('2d');
    const r = size / 2;
    const grad = g.createRadialGradient(r, r, 0, r, r, r);
    if (tight) {
      grad.addColorStop(0, 'rgba(255,255,255,1)');
      grad.addColorStop(0.14, 'rgba(255,255,255,0.92)');
      grad.addColorStop(0.3, `rgba(${rgb},0.36)`);
      grad.addColorStop(0.62, `rgba(${rgb},0.07)`);
      grad.addColorStop(1, `rgba(${rgb},0)`);
    } else {
      grad.addColorStop(0, 'rgba(255,255,255,0.9)');
      grad.addColorStop(0.2, `rgba(${rgb},0.55)`);
      grad.addColorStop(0.5, `rgba(${rgb},0.16)`);
      grad.addColorStop(1, `rgba(${rgb},0)`);
    }
    g.fillStyle = grad;
    g.beginPath();
    g.arc(r, r, r, 0, Math.PI * 2);
    g.fill();
    return c;
  }

  /** 四芒衍射星芒。真实望远镜的十字星芒来自副镜支架，形状是
   *  spike = exp(-k·|dx|) + exp(-k·|dy|)（wwwtyro/space-scene-2d 的 star.fs 就这写法）。
   *  canvas 里等价的廉价做法是两条正交接锥形渐变，比逐像素算指数便宜得多。 */
  function makeSpike(size, rgb, thin) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const g = c.getContext('2d');
    const mid = size / 2;
    const arm = size / 2;
    const w = thin || 1.3;
    const arm2 = (rot) => {
      g.save();
      if (rot) { g.translate(mid, mid); g.rotate(Math.PI / 2); g.translate(-mid, -mid); }
      const grad = g.createLinearGradient(mid - arm, mid, mid + arm, mid);
      grad.addColorStop(0, `rgba(${rgb},0)`);
      grad.addColorStop(0.5, `rgba(${rgb},0.9)`);
      grad.addColorStop(1, `rgba(${rgb},0)`);
      g.fillStyle = grad;
      g.beginPath();
      g.moveTo(mid - arm, mid);
      g.lineTo(mid, mid - w);
      g.lineTo(mid + arm, mid);
      g.lineTo(mid, mid + w);
      g.closePath();
      g.fill();
      g.restore();
    };
    arm2(false);
    arm2(true);
    return c;
  }

  /** 虚焦光斑。真实镜头的散景边（球差过校正）会给盘面一圈略亮的边。
   *  这一圈**必须很淡**：一浓就成了画面上一串圆圈。 */
  function makeBokeh(size, rgb) {
    const c = document.createElement('canvas');
    c.width = c.height = size;
    const g = c.getContext('2d');
    const r = size / 2;
    const grad = g.createRadialGradient(r, r, 0, r, r, r);
    grad.addColorStop(0, `rgba(${rgb},0.05)`);
    grad.addColorStop(0.72, `rgba(${rgb},0.05)`);
    grad.addColorStop(0.93, `rgba(${rgb},0.038)`);
    grad.addColorStop(1, `rgba(${rgb},0)`);
    g.fillStyle = grad;
    g.beginPath();
    g.arc(r, r, r, 0, Math.PI * 2);
    g.fill();
    return c;
  }

  let lastStats = null;

  function create(canvas, options) {
    const opts = options || {};
    const dead = { setMode() {}, setPalette() {}, destroy() {} };
    if (!canvas || !canvas.getContext) return dead;

    let ctx;
    try {
      ctx = canvas.getContext('2d', { alpha: false });
    } catch (error) {
      return dead;
    }
    if (!ctx) return dead;

    // ── 调色板 ───────────────────────────────────────────
    // 一片星云只有一种颜色会很"平"；这里从境界主色推出三个色相，
    // 分别给冷气团、主气团、暖核。所以金丹期是金+靛，元婴期是紫+青，
    // 同一个页面在不同境界看是**不一样的天**。
    // 星云的底色**不跟着境界转色相**，只把境界色掺进高密度的核心。
    // 理由：把主色整体做色相旋转，出来的常常是一块说不清颜色的脏雾
    // （金丹期那一版就旋出了一个油污绿）。深空本身就是靛蓝，
    // 境界色出现在"最亮的地方"才既好看又有辨识度。
    const DEEP_INDIGO = [12, 18, 58];
    const MID_INDIGO = [26, 42, 108];
    const VIOLET = [64, 38, 118];
    let gasA = DEEP_INDIGO;
    let gasB = MID_INDIGO;
    let gasC = [255, 206, 130];
    let gasHot = [255, 236, 190];
    let starWarm = [255, 233, 196];
    let starCool = [207, 227, 255];
    let mistRgb = [140, 168, 210];
    let accentRgb = [126, 225, 255];
    let primaryRgb = [143, 163, 184];

    function mix(a, b, t) {
      return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
    }

    function usePalette(next) {
      const p = Object.assign({
        primary: opts.primary || '#8fa3b8',
        deep: opts.deep || '#26313d',
        accent: opts.accent || opts.primary || '#7ee1ff',
        aura: opts.aura || opts.accent || '#dce8f4',
      }, next || {});
      primaryRgb = toRgb(p.primary, [143, 163, 184]);
      accentRgb = toRgb(p.accent, primaryRgb);
      gasA = DEEP_INDIGO;
      // 主气团掺三成境界主色：整片天空会隐隐偏到那个色系，但不会变成脏雾
      // 饱和度乘数是**抬下限**用的：像"凡人"那样本来就是灰蓝的境界，
      // 乘 1 只会得到一片灰雾，星空的"神秘"就没了；
      // 而金丹/元婴本来就是高饱和，乘再大也会被 clamp，不受影响。
      gasB = mix(MID_INDIGO, shiftHue(primaryRgb, 0, 1.5, 0.78), 0.42);
      gasC = shiftHue(primaryRgb, 0, 1.6, 0.98);           // 中亮区：境界主色
      gasHot = shiftHue(accentRgb, -8, 1.15, 1.3);         // 最亮的核：境界点缀色
      starCool = shiftHue(accentRgb, -10, 0.42, 1.4);
      starWarm = shiftHue(primaryRgb, 24, 0.6, 1.4);
      // 云海压成很淡的冷灰蓝：它要的是"气"，不是"一块有颜色的布"
      mistRgb = shiftHue(primaryRgb, -35, 0.3, 1.35);
    }

    usePalette(null);

    // ── 状态 ─────────────────────────────────────────────
    let width = 0;
    let height = 0;
    let dpr = 1;
    let raf = 0;
    let running = false;
    let mode = opts.mode || 'soft';
    let last = 0;
    let elapsed = 0;
    let slowFrames = 0;
    let quality = 1;              // 1 → 0.62 → 0.34，降了不回头
    let stars = [];
    let anchors = [];
    let motes = [];
    let bokehs = [];
    let meteors = [];
    let nextMeteorAt = 4;
    let sprites = {};
    let grainTile = null;
    let grainPattern = null;
    let gas = null;
    let gasReady = false;
    let gasJob = 0;
    let gasMs = 0;
    let gasChunks = 0;
    let mist = null;
    let field = null;
    let baseGrad = null;
    let vignette = null;
    let calmGrad = null;
    let horizonGrad = null;
    // 指针视差：目标值来自鼠标，当前值每帧向它靠一点。
    // 直接用鼠标位置会"跟手"，跟太紧就变成拖拽；缓动一点才像水。
    let ptrX = 0;
    let ptrY = 0;
    let parX = 0;
    let parY = 0;

    // ── 贴图构建 ─────────────────────────────────────────

    /** 微星场：几千颗亚像素暗星，整层烘一次。
     *  它负责"量感"——真实夜空是数不清的，不是几百颗。
     *  烘成贴图之后，这几千颗星的每帧成本是 0。 */
    function buildField() {
      const w = Math.max(64, Math.round(width));
      const h = Math.max(64, Math.round(height));
      field = document.createElement('canvas');
      field.width = w;
      field.height = h;
      const g = field.getContext('2d');
      const area = (w * h) / (1920 * 1080);
      const dense = mode === 'full' ? 1 : 0.7;
      const count = Math.round(Math.min(11000, 4200 * Math.max(0.32, area) * dense * quality));
      const bandTilt = -0.36;
      for (let i = 0; i < count; i += 1) {
        const x = Math.random() * w;
        let y = Math.random() * h;
        // 五分之一的星铺在银河带附近：那条带子必须"由星构成"，
        // 而不是靠一层雾假装
        if (i % 5 === 0) {
          const spread = (Math.random() + Math.random() + Math.random() - 1.5) * h * 0.2;
          const along = (x - w * 0.5) * Math.tan(bandTilt);
          y = Math.min(h + 8, Math.max(-8, h * 0.54 + along + spread));
        }
        const p = Math.random();
        const bright = 0.3 + Math.pow(p, 2.6) * 0.7;
        const tint = p > 0.955 ? starWarm : starCool;
        g.fillStyle = `rgba(${tint[0]},${tint[1]},${tint[2]},${(bright * 0.78).toFixed(3)})`;
        g.fillRect(x, y, Math.random() < 0.012 ? 1.5 : 0.85, Math.random() < 0.012 ? 1.5 : 0.85);
      }
    }

    /** 云海：横向的雾带。
     *
     *  两个容易做错的点：
     *
     *  1. **频率方向**。云海要的是"横着拉长的云丝"，
     *     所以 x 方向的格距必须远大于 y 方向（x 稀疏、y 密）。
     *     反过来做出来是一排竖条纹，看起来像窗帘。
     *  2. **接缝**。噪声表的周期是 256，想让贴图首尾接上就得让
     *     x 方向正好跨整数倍周期——那会把格距锁死在 4px 以下，做不出长云丝。
     *     所以这里不靠噪声本身可平铺，改为**相邻两片镜像拼接**：
     *     镜像在边界处天然连续，横滚时看不出接缝。
     */
    function buildMist() {
      mist = document.createElement('canvas');
      mist.width = MIST_W;
      mist.height = MIST_H;
      const g = mist.getContext('2d');
      const img = g.createImageData(MIST_W, MIST_H);
      const data = img.data;
      const sx = 3.2 / MIST_W;      // 一屏横向只铺 3.2 个格 → 云丝又长又缓
      const sy = 7.5 / MIST_H;      // 纵向 7.5 个格 → 有明显的横向分层
      for (let y = 0; y < MIST_H; y += 1) {
        const vy = y / MIST_H;
        // 上下两端羽化，贴图才不会有两条硬边
        const edge = Math.min(1, Math.sin(Math.PI * clamp01(vy)) * 2.4);
        // 越靠下越浓：云海是"堆在脚下"的，不是一块均匀的板
        const slope = 0.35 + 1.0 * Math.pow(vy, 1.4);
        for (let x = 0; x < MIST_W; x += 1) {
          const n = fbm(x * sx, y * sy, 4);
          const d = Math.max(0, (n + 0.3) * 1.05) * slope * edge;
          const a = Math.pow(d, 2.4);
          const i = (y * MIST_W + x) * 4;
          data[i] = mistRgb[0];
          data[i + 1] = mistRgb[1];
          data[i + 2] = mistRgb[2];
          data[i + 3] = Math.round(clamp01(a) * 255);
        }
      }
      g.putImageData(img, 0, 0);
    }

    /** 把贴图缩小再放大回来，等价于一次廉价的可分离模糊。
     *  星云是"气"：任何硬边都会立刻显出数字感，而逐像素跑高斯在这台机器上
     *  是明确踩过的坑。缩-放走的是 canvas 自己的采样器，一次几毫秒。 */
    function soften(source, times) {
      let src = source;
      for (let i = 0; i < times; i += 1) {
        const small = document.createElement('canvas');
        small.width = Math.max(3, Math.round(src.width / 3));
        small.height = Math.max(3, Math.round(src.height / 3));
        const sg = small.getContext('2d');
        sg.imageSmoothingEnabled = true;
        sg.drawImage(src, 0, 0, small.width, small.height);
        const back = document.createElement('canvas');
        back.width = src.width;
        back.height = src.height;
        const bg = back.getContext('2d');
        bg.imageSmoothingEnabled = true;
        bg.drawImage(small, 0, 0, back.width, back.height);
        src = back;
      }
      return src;
    }

    /** 星云气团：域扭曲 fBm 的密度场 + 被内部恒星群照亮。
     *
     *  分片烘（每片约三分之一的行，用 setTimeout 让出主线程）：
     *  整块烘下来要一两百毫秒，一次做完会让首屏明显顿一下；
     *  分片之后页面全程可响应，星云自己还有一个淡入，看起来是"浮出来"的。
     */
    function buildGas() {
      const job = ++gasJob;
      const gw = GAS_LONG;
      const gh = Math.max(48, Math.round(GAS_LONG * (height / Math.max(1, width))));
      const c = document.createElement('canvas');
      c.width = gw;
      c.height = gh;
      const g = c.getContext('2d');
      const img = g.createImageData(gw, gh);
      const data = img.data;
      const seedOff = Math.random() * 100;

      // 光团：星云被这几个"恒星形成区"照亮，视线才有落点。
      // 刻意偏右、偏下——左上是正文区，那里必须是安静的暗部。
      const lights = [
        [0.76, 0.34, 0.44, 0.95],
        [0.52, 0.70, 0.52, 0.6],
        [0.92, 0.78, 0.38, 0.46],
        [0.30, 0.34, 0.44, 0.34],
        [0.64, 0.12, 0.34, 0.3],
        [0.14, 0.88, 0.4, 0.26],
      ];

      const scale = 1.55;
      const rowsPerChunk = Math.max(6, Math.round(gh / 3));
      let y = 0;
      const t0 = now();

      function chunk() {
        if (job !== gasJob) return;      // 期间换了配色 / 改了尺寸，这次作废
        const until = Math.min(gh, y + rowsPerChunk);
        for (; y < until; y += 1) {
          const vy = y / gh;
          for (let x = 0; x < gw; x += 1) {
            const vx = x / gw;
            const nx = vx * scale + seedOff;
            const ny = vy * scale * 0.72 + seedOff * 0.5;

            // 大尺度遮罩：星云是"天上的几团云"，不是"糊满全屏的壁纸"。
            // 留出大片干净的黑暗，深空才有纵深——这一项让画面从
            // "油污"变回"星云"的贡献最大。
            const mask = clamp01((fbm(vx * 1.05 + 3.3, vy * 1.05 + 8.1, 2) + 0.42) * 1.5);

            // 主密度：域扭曲噪声的低频部分给大团块，
            // 高频取高次幂给被拉扯出来的细丝（幂次必须高，
            // 低了就变成等高线图——那是上一版最难看的地方）。
            const n = warped(nx, ny);
            const bulk = clamp01((fbm(nx * 1.5 + 40, ny * 1.5 + 7, 3) + 0.3) * 1.25);
            // 细丝的幂次要高：低了就变成等高线，是这一版之前最难看的地方
            const fil = Math.pow(clamp01(1 - Math.abs(n) * 1.9), 9);
            let density = (bulk * 0.8 + fil * 0.3) * mask;

            // 银河带：斜贯画面的密度脊，用一层低频噪声把它弯一下，
            // 免得看出来是一条直线
            const off = vy - (0.54 + fbm(vx * 1.4 + 21, vy * 1.4 + 5, 2) * 0.12)
              - (vx - 0.5) * Math.tan(-0.36);
            density += Math.exp(-(off * off) / (2 * 0.055 * 0.055)) * 0.5 * (0.45 + 0.55 * mask);

            // 尘带：沿带子中心的一条暗吸收带。没有它，那条带子只是雾；
            // 有了它，眼睛会读出"前面有东西挡住了后面的星光"。
            const dustMask = Math.exp(-(off * off) / (2 * 0.019 * 0.019));
            const dust = clamp01((fbm(vx * 4.4 + 61, vy * 4.4 + 17, 3) * 0.5 + 0.5) * 1.3 - 0.34);
            density *= 1 - dust * dustMask * 0.8;

            // 被内部光源照亮
            let light = 0;
            for (let i = 0; i < lights.length; i += 1) {
              const dx = (vx - lights[i][0]) * 1.25;
              const dy = vy - lights[i][1];
              light += lights[i][3] / (1 + (dx * dx + dy * dy) / (lights[i][2] * lights[i][2]) * 8);
            }
            light = Math.min(1.5, light * 0.55);

            const glow = Math.pow(Math.max(0, density), 1.05) * light;

            // 上色：深靛 → 主气团 → 境界色 → 最亮的核心。
            // 四段混色而不是"单色 + 调亮"，云才有内部结构。
            const t1 = clamp01(glow * 3.6);
            const t2 = clamp01(glow * 7.5 - 2.2);
            const t3 = clamp01(glow * 16 - 7.4);
            let col = mix(gasA, gasB, t1);
            col = mix(col, gasC, t2);
            col = mix(col, gasHot, t3);
            // 一点紫：两三色相的气团互相错开，眼睛才读得出"体积"
            const violetAmt = clamp01(fbm(vx * 2.2 + 77, vy * 2.2 + 31, 2) * 0.9 + 0.45) * 0.22 * t1;
            col = mix(col, VIOLET, violetAmt);

            // 整体提亮：这张贴图是以 'lighter' 叠上去的，
            // 光靠 alpha 拉不高亮度——加色合成里，颜色本身暗就永远亮不起来。
            // 提亮与 alpha 要一起给，只给一边不是"灰"就是"糊"。
            const gain = 1.75;
            const i = (y * gw + x) * 4;
            data[i] = Math.min(255, col[0] * gain);
            data[i + 1] = Math.min(255, col[1] * gain);
            data[i + 2] = Math.min(255, col[2] * gain);
            // 四周羽化：贴图要整体摆动，边缘不能有硬边
            const feather = Math.min(1, Math.min(vx, 1 - vx, vy, 1 - vy) * 9);
            data[i + 3] = Math.round(clamp01(glow * 2.75) * feather * 255);
          }
        }
        if (y < gh) {
          // 用 setTimeout 而不是 requestIdleCallback：空闲回调在"页面一直很忙"
          // 的时候可能永远排不上，星云就永远不出来。
          window.setTimeout(chunk, 0);
          return;
        }
        g.putImageData(img, 0, 0);
        if (job !== gasJob) return;
        gas = soften(c, 3);
        gasReady = true;
        gasMs = Math.round(now() - t0);
        gasChunks = Math.ceil(gh / rowsPerChunk);
        refreshStats();
        if (!running && mode !== 'off') renderOnce();
      }

      chunk();
    }

    /** 抖动噪点：深色渐变在 8bit 下必然出现色带，这是"平"和"高级"之间
     *  性价比最高的一步。用一张小噪点贴图平铺，每帧随机偏移，代价一次 fillRect。 */
    function buildGrain() {
      grainTile = document.createElement('canvas');
      grainTile.width = grainTile.height = GRAIN;
      const g = grainTile.getContext('2d');
      const img = g.createImageData(GRAIN, GRAIN);
      const data = img.data;
      for (let i = 0; i < data.length; i += 4) {
        const v = 118 + Math.round(Math.random() * 46);
        data[i] = v;
        data[i + 1] = v;
        data[i + 2] = v;
        data[i + 3] = 255;
      }
      g.putImageData(img, 0, 0);
      try { grainPattern = ctx.createPattern(grainTile, 'repeat'); } catch (error) { grainPattern = null; }
    }

    function buildSprites() {
      const accent = rgbStr(accentRgb);
      const warm = rgbStr(starWarm);
      const cool = rgbStr(starCool);
      sprites = {
        // tight 的几枚是"星星"，不 tight 的只给浮尘与散景用
        star: makeGlow(18, cool, true),
        starWarm: makeGlow(18, warm, true),
        starBig: makeGlow(32, warm, true),
        spike: makeSpike(72, '255,255,255', 1.15),
        spikeWarm: makeSpike(72, warm, 1.7),
        mote: makeGlow(34, accent, false),
        bokeh: makeBokeh(128, accent),
      };
    }

    /** 星色：按黑体色温抽。冷蓝白为主、掺一点暖金，
     *  同一片天空里色温不齐，才像真的。 */
    const TEMPS = [3200, 3900, 4600, 5400, 6000, 6000, 6800, 7600, 8600, 10000, 12500, 17000];
    const TINTS = TEMPS.map((k) => kelvin(k));

    /** 活星：四层视差。尺寸与亮度都走幂律——90% 又小又暗、1% 又大又亮，
     *  眼睛才读得出"星等"和"远近"。均匀分布看起来只是一层噪点。 */
    function buildStars() {
      const area = (width * height) / (1920 * 1080);
      const scale = Math.max(0.42, Math.min(2.0, area));
      const dense = mode === 'full' ? 1 : 0.62;
      const count = Math.max(120, Math.round(520 * Math.max(0.55, scale) * dense * quality));
      const bandTilt = -0.36;
      stars = [];
      for (let i = 0; i < count; i += 1) {
        const layer = i % 4;                              // 0 最远 → 3 最近
        const x = Math.random() * width;
        let y = Math.random() * height;
        if (i % 3 === 0) {
          const spread = (Math.random() + Math.random() + Math.random() - 1.5) * height * 0.18;
          const along = (x - width * 0.5) * Math.tan(bandTilt);
          y = Math.min(height + 10, Math.max(-10, height * 0.54 + along + spread));
        }
        const p = Math.random();
        // 幂律尺寸：p 的四次方让绝大多数星贴在最小档
        const size = (layer === 3 ? 0.75 : 0.3) + Math.pow(p, 4.2) * (layer === 3 ? 2.6 : 1.15);
        const alpha = (layer === 0 ? 0.3 : layer === 1 ? 0.46 : layer === 2 ? 0.6 : 0.76)
          + Math.pow(Math.random(), 2.4) * 0.34;
        stars.push({
          x,
          y,
          layer,
          r: size,
          alpha: Math.min(1, alpha),
          tint: TINTS[Math.floor(Math.random() * TINTS.length)],
          // 每颗星自己的闪烁周期，**刻意错开**：整片一起闪是廉价感的元凶
          speed: 0.7 + Math.random() * 3.6,
          phase: Math.random() * Math.PI * 2,
          drift: (layer === 0 ? 1.1 : layer === 1 ? 2.1 : layer === 2 ? 3.6 : 6.2),
          dir: Math.random() < 0.5 ? -1 : 1,
          spike: layer >= 3 && Math.random() < 0.12,
        });
      }
      // 锚点星：极少数又大又亮的，给"远"提供参照物
      const anchorCount = Math.max(4, Math.round((mode === 'full' ? 9 : 6) * Math.min(1, scale + 0.3)));
      anchors = [];
      for (let i = 0; i < anchorCount; i += 1) {
        anchors.push({
          x: Math.random() * width,
          y: height * (0.06 + Math.random() * 0.6),
          r: 1.9 + Math.random() * 1.5,
          speed: 0.5 + Math.random() * 1.1,
          phase: Math.random() * Math.PI * 2,
          spikeLen: 0.8 + Math.random() * 0.7,
        });
      }
    }

    function buildMotes() {
      const count = Math.round(30 * (mode === 'full' ? 1 : 0.62) * Math.min(1.6, quality + 0.4));
      motes = [];
      for (let i = 0; i < count; i += 1) {
        motes.push({
          x: Math.random() * width,
          y: Math.random() * height,
          r: 3 + Math.random() * 9,
          alpha: 0.07 + Math.random() * 0.2,
          rise: 5 + Math.random() * 15,
          wobble: 8 + Math.random() * 22,
          phase: Math.random() * Math.PI * 2,
          speed: 0.12 + Math.random() * 0.3,
        });
      }
    }

    /** 散景：近景的虚焦光斑。它不负责"亮"，负责把画面推得有距离。 */
    function buildBokeh() {
      const count = mode === 'full' && quality > 0.9 ? 8 : 0;
      bokehs = [];
      for (let i = 0; i < count; i += 1) {
        bokehs.push({
          x: Math.random() * width,
          y: Math.random() * height,
          r: 40 + Math.random() * 78,
          alpha: 0.1 + Math.random() * 0.16,
          drift: 3 + Math.random() * 9,
          phase: Math.random() * Math.PI * 2,
        });
      }
    }

    function buildGradients() {
      baseGrad = ctx.createLinearGradient(0, 0, 0, height);
      baseGrad.addColorStop(0, '#03050c');
      baseGrad.addColorStop(0.34, '#050912');
      baseGrad.addColorStop(0.68, '#04070f');
      baseGrad.addColorStop(1, '#010206');

      // 正文区（左上到中部）压一层很淡的安静层：星云最亮的地方必须落在
      // 右侧那块（法相的位置），否则正文会被背景吃掉
      calmGrad = ctx.createLinearGradient(0, 0, width, height * 0.9);
      calmGrad.addColorStop(0, 'rgba(2,4,10,0.34)');
      calmGrad.addColorStop(0.44, 'rgba(2,4,10,0.13)');
      calmGrad.addColorStop(1, 'rgba(2,4,10,0)');

      // 地平线：底部一点极淡的冷光，让"天空"有个下缘，
      // 而不是一路黑到屏幕外面去
      horizonGrad = ctx.createLinearGradient(0, height * 0.62, 0, height);
      horizonGrad.addColorStop(0, 'rgba(0,0,0,0)');
      horizonGrad.addColorStop(0.62, `rgba(${rgbStr(mistRgb)},0.05)`);
      horizonGrad.addColorStop(1, `rgba(${rgbStr(mistRgb)},0.12)`);

      vignette = ctx.createRadialGradient(
        width * 0.52, height * 0.44, Math.min(width, height) * 0.22,
        width * 0.52, height * 0.44, Math.max(width, height) * 0.76,
      );
      vignette.addColorStop(0, 'rgba(0,0,0,0)');
      vignette.addColorStop(0.6, 'rgba(0,0,0,0.16)');
      vignette.addColorStop(1, 'rgba(0,0,0,0.62)');
    }

    /** 尺寸没变就不要重烘贴图：切档（微光↔星海）也会走这里，
     *  而星云是分片烘焙的，不做这个判断的话每次切档都要重算几十万像素。 */
    function resize(force) {
      const rect = canvas.getBoundingClientRect();
      const w = Math.max(1, Math.round(rect.width || window.innerWidth));
      const h = Math.max(1, Math.round(rect.height || window.innerHeight));
      const sameSize = w === width && h === height;
      width = w;
      height = h;
      dpr = Math.min(DPR_CAP, window.devicePixelRatio || 1);
      if (quality < 1) dpr = Math.min(dpr, 1);
      const wantW = Math.round(width * dpr);
      const wantH = Math.round(height * dpr);
      if (canvas.width !== wantW || canvas.height !== wantH) {
        canvas.width = wantW;
        canvas.height = wantH;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }
      buildGradients();
      buildStars();
      buildMotes();
      buildBokeh();
      buildField();
      if (sameSize && !force) return;
      if (quality > 0.5) buildMist();
      buildGas();
      refreshStats();
    }

    function refreshStats() {
      lastStats = {
        w: width, h: height, dpr: Math.round(dpr * 100) / 100, mode, quality,
        liveStars: stars.length, anchors: anchors.length, motes: motes.length,
        bokeh: bokehs.length,
        gas: `${gas ? gas.width + 'x' + gas.height : '-'} ${gasMs}ms/${gasChunks}chunk`,
        // 视差是"看得见但摸不着"的效果，把指针值与当前值放进诊断，
        // 验收脚本才有可能确认它真的接上了（而不是挂了个空监听）
        pointer: [Math.round(ptrX * 100) / 100, Math.round(ptrY * 100) / 100],
        parallax: [Math.round(parX * 1000) / 1000, Math.round(parY * 1000) / 1000],
      };
    }

    /** 只为排查用：同步画 n 帧，返回每帧平均毫秒数。
     *  主循环走的是 frame()，正常运行时永远不会走到这里。
     *  之所以需要它：无头浏览器里 rAF 被虚拟时钟节流，量不到真实帧间隔。 */
    function bench(frames) {
      const n = Math.max(1, frames || 30);
      const t0 = now();
      for (let i = 0; i < n; i += 1) {
        elapsed += 1 / 60;
        easePointer();
        drawSky();
        drawStars(elapsed);
        drawBokeh(elapsed);
        drawMotes(elapsed);
        drawMist(elapsed);
        drawMeteors();
        drawVignette();
        drawGrain();
      }
      refreshStats();
      return Math.round(((now() - t0) / n) * 100) / 100;
    }

    // ── 绘制 ─────────────────────────────────────────────
    function drawSky() {
      ctx.fillStyle = baseGrad;
      ctx.fillRect(0, 0, width, height);

      if (gas && gasReady) {
        // 整片星云以极慢的速度来回摆（±5.5°，一个来回约五分钟），
        // 同时缓慢明灭。贴图四周羽化过，摆动不会露边；
        // 明灭让它看起来是"气"，而不是"一张贴上去的图"。
        const sway = Math.sin(elapsed * 0.021) * 0.096;
        const breath = 0.5 + 0.5 * Math.sin(elapsed * 0.17);
        const base = mode === 'soft' ? 0.78 : 1;
        const over = 1.2 + breath * 0.04;
        ctx.save();
        ctx.globalCompositeOperation = 'lighter';
        ctx.globalAlpha = base * (0.8 + 0.2 * breath);
        ctx.translate(width * 0.58 + parX * 30, height * 0.52 + parY * 22);
        ctx.rotate(sway);
        ctx.drawImage(gas, -width * 0.58 * over, -height * 0.52 * over, width * over, height * over);
        ctx.restore();
        ctx.globalAlpha = 1;
      }
      if (field) {
        ctx.globalAlpha = mode === 'soft' ? 0.76 : 1;
        ctx.drawImage(field, -parX * 12, -parY * 9, width, height);
        ctx.globalAlpha = 1;
      }
      // 左上安静层 + 地平线：一个压住星云保正文，一个给天空一个下缘
      ctx.fillStyle = calmGrad;
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = horizonGrad;
      ctx.fillRect(0, 0, width, height);
    }

    /** 星野分两趟画：先所有方点小星，再所有发光星。
     *  切换 globalCompositeOperation 有代价，逐颗切会把几百颗星的成本翻倍；
     *  分趟之后整段只有两次状态切换。 */
    function drawStars(t) {
      // 指针视差按"层"给：远处的星几乎不动，近处的星跟着走得多。
      // 这一条比任何亮度渐变都更能让人感到「深」。
      const OX = [-3, -7, -13, -22];
      const OY = [-2, -5, -9, -15];
      for (let i = 0; i < stars.length; i += 1) {
        const s = stars[i];
        // 缓慢横漂，越近的层越快 → 视差
        s.x += s.drift * s.dir * 0.016 * (quality < 1 ? 1.8 : 1);
        if (s.x > width + 6) s.x = -6;
        else if (s.x < -6) s.x = width + 6;
      }

      // ① 亚像素小星：直接画方点。**不要**给它们套发光精灵——
      //    那正是上一版看起来"像虚焦光斑、不像星星"的原因。
      for (let i = 0; i < stars.length; i += 1) {
        const s = stars[i];
        if (s.r >= 0.9) continue;
        const tw = 0.68 + 0.32 * Math.sin(t * s.speed + s.phase);
        const alpha = s.alpha * tw;
        if (alpha < 0.03) continue;
        ctx.globalAlpha = alpha;
        ctx.fillStyle = `rgb(${s.tint[0]},${s.tint[1]},${s.tint[2]})`;
        const sz = s.r < 0.55 ? 1 : 1.35;
        const li = s.layer | 0;
        ctx.fillRect(s.x + (parX + 1) * OX[li], s.y + (parY + 1) * OY[li], sz, sz);
      }

      // ② 亮一点的星：预渲染发光精灵（收紧的），少数带星芒
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < stars.length; i += 1) {
        const s = stars[i];
        if (s.r < 0.9) continue;
        const tw = 0.68 + 0.32 * Math.sin(t * s.speed + s.phase);
        const alpha = s.alpha * tw;
        if (alpha < 0.03) continue;
        const size = 5 + s.r * 7;
        const li2 = s.layer | 0;
        const sx = s.x + (parX + 1) * OX[li2];
        const sy = s.y + (parY + 1) * OY[li2];
        ctx.globalAlpha = alpha;
        ctx.drawImage(s.r > 2 ? sprites.starBig : sprites.star, sx - size / 2, sy - size / 2, size, size);
        if (s.spike) {
          ctx.globalAlpha = alpha * 0.5;
          const len = 22 + s.r * 15;
          ctx.drawImage(sprites.spike, sx - len / 2, sy - len / 2, len, len);
        }
      }

      // ③ 锚点星：更大、更亮、带十字星芒
      for (let i = 0; i < anchors.length; i += 1) {
        const a = anchors[i];
        const tw = 0.6 + 0.4 * Math.sin(t * a.speed + a.phase);
        const size = 14 + a.r * 12;
        ctx.globalAlpha = 0.72 * tw;
        ctx.drawImage(sprites.starBig, a.x - size / 2, a.y - size / 2, size, size);
        ctx.globalAlpha = 0.55 * tw;
        const len = size * (1.7 + a.spikeLen);
        ctx.drawImage(sprites.spike, a.x - len / 2, a.y - len / 2, len, len);
        const size2 = size * 0.7;
        ctx.globalAlpha = 0.4 * tw;
        ctx.drawImage(sprites.spikeWarm, a.x - size2 / 2, a.y - size2 / 2, size2, size2);
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    function drawBokeh(t) {
      if (!bokehs.length) return;
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < bokehs.length; i += 1) {
        const b = bokehs[i];
        const y = b.y + Math.sin(t * 0.06 + b.phase) * b.drift + (parY + 1) * 26;
        const bx = b.x + (parX + 1) * 30;
        ctx.globalAlpha = b.alpha;
        ctx.drawImage(sprites.bokeh, bx - b.r, y - b.r, b.r * 2, b.r * 2);
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    function drawMotes(t) {
      if (!motes.length) return;
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < motes.length; i += 1) {
        const m = motes[i];
        const y = m.y - ((t * m.rise) % (height + 60));
        const wrapY = y < -30 ? y + height + 60 : y;
        const x = m.x + Math.sin(t * m.speed + m.phase) * m.wobble;
        const alpha = m.alpha * (0.55 + 0.45 * Math.sin(t * m.speed * 1.7 + m.phase));
        const size = m.r * 3.2;
        ctx.globalAlpha = Math.max(0, alpha);
        ctx.drawImage(sprites.mote, x - size / 2, wrapY - size / 2, size, size);
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    /** 云海：底部三条不同速度的雾带。它同时干三件事——
     *  托住法相、给画面一个出路、把"星海"接到"仙家"那一口气上。
     *  横滚靠 drawImage 的偏移，偏移量对贴图宽度取模，所以永远接得上。 */
    function drawMist(t) {
      if (!mist) return;
      const bands = [
        { y: 0.74, h: 0.34, speed: 2.6, alpha: 0.09 },
        { y: 0.83, h: 0.30, speed: -4.4, alpha: 0.12 },
        { y: 0.90, h: 0.24, speed: 7.4, alpha: 0.15 },
      ];
      const dens = mode === 'full' ? 1 : 0.55;
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < bands.length; i += 1) {
        const b = bands[i];
        const bh = height * b.h;
        const bw = bh * (MIST_W / MIST_H);
        const span = bw * 2;                 // 一正一反两片才算一个完整循环
        let ox = (t * b.speed) % span - parX * 34;
        if (ox < 0) ox += span;
        ctx.globalAlpha = b.alpha * dens;
        for (let k = -2; k * bw < width + bw; k += 1) {
          const x = k * bw - ox;
          // 奇偶片镜像：边界处两侧的值天然相等，所以横滚无接缝
          const flip = (((k % 2) + 2) % 2) === 1;
          ctx.save();
          ctx.translate(x + (flip ? bw : 0), height * b.y);
          if (flip) ctx.scale(-1, 1);
          ctx.drawImage(mist, 0, 0, bw, bh);
          ctx.restore();
        }
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    /** 流星：拖尾要长、要带弧度。它是"这片天在动"的证据。 */
    function drawMeteors() {
      if (elapsed >= nextMeteorAt && meteors.length < (mode === 'full' ? 2 : 1)) {
        const fromLeft = Math.random() < 0.62;
        meteors.push({
          x: fromLeft ? -80 : width * (0.3 + Math.random() * 0.6),
          y: height * (0.03 + Math.random() * 0.38),
          vx: (fromLeft ? 1 : 0.5) * (330 + Math.random() * 260),
          vy: (fromLeft ? 0.62 : 0.38) * (150 + Math.random() * 140),
          curve: (Math.random() - 0.5) * 110,
          wide: 1.3 + Math.random() * 1.2,
          born: elapsed,
          life: 0.95 + Math.random() * 0.65,
        });
        nextMeteorAt = elapsed + (mode === 'full' ? 5 : 7) + Math.random() * (mode === 'full' ? 10 : 14);
      }
      if (!meteors.length) return;
      const accent = rgbStr(accentRgb);
      meteors = meteors.filter((m) => elapsed - m.born <= m.life);
      ctx.globalCompositeOperation = 'lighter';
      for (let i = 0; i < meteors.length; i += 1) {
        const m = meteors[i];
        const age = elapsed - m.born;
        const p = age / m.life;
        const x = m.x + m.vx * age;
        const y = m.y + m.vy * age + m.curve * p * p;
        const mag = Math.hypot(m.vx, m.vy);
        const nx = m.vx / mag;
        const ny = m.vy / mag;
        const fade = Math.sin(Math.PI * Math.min(1, p * 1.12));
        const tail = 130 + 190 * (1 - p);
        const grad = ctx.createLinearGradient(x, y, x - nx * tail, y - ny * tail);
        grad.addColorStop(0, `rgba(255,255,255,${0.95 * fade})`);
        grad.addColorStop(0.24, `rgba(${accent},${0.44 * fade})`);
        grad.addColorStop(1, 'rgba(140,205,255,0)');
        ctx.strokeStyle = grad;
        ctx.lineWidth = m.wide;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.lineTo(x - nx * tail, y - ny * tail);
        ctx.stroke();
        // 头部光点 + 一圈小光晕：没有它，流星看起来像一根飘过去的线头
        ctx.globalAlpha = fade;
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, m.wide * 1.1, 0, Math.PI * 2);
        ctx.fill();
        const hs = 24;
        ctx.globalAlpha = fade * 0.6;
        ctx.drawImage(sprites.star, x - hs / 2, y - hs / 2, hs, hs);
      }
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    function drawGrain() {
      if (!grainPattern || quality < 0.9) return;
      const ox = Math.round(Math.random() * GRAIN);
      const oy = Math.round(Math.random() * GRAIN);
      ctx.save();
      // 'overlay' 在深色上同时提亮暗部与压暗亮部，比直接叠灰自然；
      // 但它对纯黑几乎不起作用，所以再补一层极淡的 'lighter'。
      ctx.globalAlpha = 0.05;
      ctx.globalCompositeOperation = 'overlay';
      ctx.translate(-ox, -oy);
      ctx.fillStyle = grainPattern;
      ctx.fillRect(0, 0, width + GRAIN, height + GRAIN);
      ctx.globalAlpha = 0.02;
      ctx.globalCompositeOperation = 'lighter';
      ctx.fillRect(0, 0, width + GRAIN, height + GRAIN);
      ctx.restore();
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = 1;
    }

    function drawVignette() {
      ctx.fillStyle = vignette;
      ctx.fillRect(0, 0, width, height);
    }

    function frame(nowMs) {
      if (!running) return;
      raf = window.requestAnimationFrame(frame);
      const dt = last ? Math.min(120, nowMs - last) : 16;
      last = nowMs;
      elapsed += dt / 1000;
      easePointer();

      // 连续掉帧 → 降档，降了不回头（免得在阈值附近来回抖）
      if (dt > SLOW_FRAME) {
        slowFrames += 1;
        if (slowFrames > 70 && quality > 0.5) {
          quality = quality > 0.9 ? 0.62 : 0.34;
          resize(true);
          slowFrames = 0;
        }
      } else if (slowFrames > 0) {
        slowFrames -= 1;
      }

      drawSky();
      drawStars(elapsed);
      drawBokeh(elapsed);
      drawMotes(elapsed);
      drawMist(elapsed);
      drawMeteors();
      drawVignette();
      drawGrain();
    }

    function renderOnce() {
      // 减少动态效果：只画一帧静态星河，不启动 rAF
      elapsed = 12;
      drawSky();
      drawStars(0);
      drawMist(0);
      drawVignette();
    }

    // ── 生命周期 ─────────────────────────────────────────
    function start() {
      if (running || mode === 'off') return;
      if (reduceMotion()) { renderOnce(); return; }
      running = true;
      last = 0;
      raf = window.requestAnimationFrame(frame);
    }

    function stop() {
      running = false;
      if (raf) window.cancelAnimationFrame(raf);
      raf = 0;
    }

    function onVisibility() {
      if (document.hidden) stop();
      else if (mode !== 'off') start();
    }

    /** 指针位置 → [-1,1]。各层按不同系数平移，眼睛立刻读出"这些星在不同的深度"。
     *  这是整块背景里唯一一处"能上手玩"的东西，所以缓动要给够（约 0.3 秒跟上）。 */
    function onPointer(event) {
      if (reduceMotion()) return;
      const e = event.touches ? event.touches[0] : event;
      if (!e) return;
      ptrX = (e.clientX / Math.max(1, window.innerWidth) - 0.5) * 2;
      ptrY = (e.clientY / Math.max(1, window.innerHeight) - 0.5) * 2;
    }

    function easePointer() {
      parX += (ptrX - parX) * 0.06;
      parY += (ptrY - parY) * 0.06;
    }

    let resizeTimer = 0;
    function onResize() {
      // 拖窗口会连续触发。星云一烘就是几十万像素，不防抖拖一次要重算十几遍。
      if (resizeTimer) window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        resizeTimer = 0;
        resize(true);
        if (!running && mode !== 'off') renderOnce();
      }, 240);
      if (!running && mode !== 'off') {
        resize();
        renderOnce();
      }
    }

    // 任何一步都不许抛出去：create() 跑在页面的 DOMContentLoaded 里，
    // 抛出去会把后面画法相、画等级条全带崩（真实踩过）。
    try {
      if (mode === 'off') {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width || 1, canvas.height || 1);
      } else {
        resize(true);
        buildSprites();
        buildGrain();
        start();
      }
      document.addEventListener('visibilitychange', onVisibility);
      window.addEventListener('resize', onResize);
      window.addEventListener('pointermove', onPointer, { passive: true });
    } catch (error) {
      return dead;
    }

    return {
      /** off 纯净 / soft 微光 / full 星海 */
      setMode(next) {
        if (next === mode) return;
        mode = next;
        if (mode === 'off') {
          stop();
          gasReady = false;
          gasJob += 1;
          ctx.setTransform(1, 0, 0, 1, 0, 0);
          ctx.fillStyle = '#000';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
          return;
        }
        resize();
        if (!running) start();
      },
      /** 星云跟着境界换色（元婴是紫的、金丹是金的……） */
      setPalette(next) {
        usePalette(next);
        buildSprites();
        buildField();
        buildMist();
        buildGas();
        if (!running && mode !== 'off') renderOnce();
      },
      /** 诊断用，见上面 bench() 的说明 */
      bench,
      destroy() {
        stop();
        gasJob += 1;
        if (resizeTimer) window.clearTimeout(resizeTimer);
        document.removeEventListener('visibilitychange', onVisibility);
        window.removeEventListener('resize', onResize);
        window.removeEventListener('pointermove', onPointer);
      },
    };
  }

  // diag 只给排查用：验收脚本靠它读烘焙耗时与星数，不是一个公开 API。
  window.StarField = {
    create,
    kelvin,
    rgbOf: (hex, fallback) => rgbStr(toRgb(hex, fallback || [143, 163, 184])),
    shiftHue,
    diag() { return lastStats || '(none)'; },
  };
})();
