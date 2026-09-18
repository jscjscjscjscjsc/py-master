/**
 * portrait.js — 修行阁的图形引擎：神识画像 / 境界法印 / 装备图
 *
 * ## 这一版为什么整个重画
 *
 * 上一版的画像是一具**无脸的荧光机甲**：方肩、装甲片、面甲光带、霓虹辉光。
 * 它作为「科技风头像」是成立的，但挂在一个叫修行阁的页面上，一眼就被否了：
 * 「一点仙风道骨的感觉都没有」——这个判断是对的，因为它和中国画里
 * 「仙人」的造形语言几乎处处相反。
 *
 * 所以这一版照白描人物的规矩重来，依据是三类公认的原作：
 *
 *   · 梁楷《泼墨仙人图》—— 五官挤在一处、缩颈耸肩、大片墨衣。
 *     启示：仙气不来自精致的脸，而来自**松弛与形骸之外的怪**。
 *   · 《八十七神仙卷》/《朝元仙仗图》—— 白描群仙，「吴带当风」。
 *     启示：**线条才是主角**。七头半到八头身的修长身形、削肩长颈、宽袖长裾，
 *     飘带以长弧线拉出风势；背景留白，不画满。
 *   · 谢赫六法之「骨法用笔」—— 线要有起收顿挫，不是均匀的矢量描边。
 *     启示：主轮廓粗、衣纹细、须发更细，并且**允许一点点手抖**。
 *
 * ## 落到代码上的六条硬规矩（改这张图之前先读一遍）
 *
 * 1. **七头半身**。头半径 29、总高 440。上一版是二头半的方块，比例就先不像人。
 * 2. **削肩、长颈、细腰、宽袖**。肩半宽只有 42（约 1.7 头宽），袖口比肩还宽，
 *    腰半宽 27——这个剪影是「道袍」，「装甲」的剪影正好相反。
 * 3. **不画面甲、五官只几笔**。眉、眼、鼻、嘴各一两笔；眼是细长的一横
 *    （垂目），不是发光的光带。上一版的脸是两条斜切光带，那是最像机甲的部件。
 * 4. **发光改成晕**。背景是淡墨晕染 + 云气 + 远山，不是霓虹径向渐变。
 * 5. **器比光效管用**：葫芦（三境）→ 长剑（五境）→ 丹炉（八境）。
 *    一眼可辨「这是修仙」靠的是葫芦和剑，不是粒子雨。
 * 6. **颜色全部换成传统颜料**（石青/石绿/赭石/朱砂/藤黄/胭脂/月白），
 *    在深色绢本上略提亮。见 game_engine.REALM_ART。
 *
 * 画像随 `用户名 + 境界` 做种子生成：同一境界不同人纹路不同，
 * 同一个人升级后纹路延续、复杂度上升。缺任何字段都退回凡人形态，绝不抛异常。
 */
(function () {
  'use strict';

  const CX = 160;          // 中轴
  const HEAD_Y = 110;      // 头心
  const HEAD_R = 29;       // 头半径（总高 440 / 头高 58 ≈ 七头半）
  const NECK_Y = 142;      // 颈根
  const SHOULDER_Y = 160;  // 肩点
  const WAIST_Y = 246;     // 腰
  const HEM_Y = 436;       // 衣摆
  const GROUND = 456;      // 取景底边

  // ── 随机源：同一个种子永远给出同一张画像 ──────────────
  function hashSeed(text) {
    let h = 2166136261;
    const s = String(text == null ? '' : text);
    for (let i = 0; i < s.length; i += 1) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function rngFrom(text) {
    let a = hashSeed(text) || 1;
    return function next() {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function pick(rand, min, max) { return min + rand() * (max - min); }
  function r1(v) { return Math.round(v * 10) / 10; }

  /**
   * 一条「手绘」的曲线：控制点带一点点确定性抖动。
   * 这是整套画像里最便宜也最要紧的一招——完全笔直的矢量线会立刻显出机器味，
   * ±2 像素的抖动就足够让衣纹读起来像笔画的。
   */
  function inkCurve(rand, pts, wobble) {
    const w = wobble == null ? 2.2 : wobble;
    const j = (v) => r1(v + pick(rand, -w, w));
    const [x0, y0] = pts[0];
    let d = `M${j(x0)} ${j(y0)}`;
    for (let i = 1; i < pts.length; i += 1) {
      const [x, y] = pts[i];
      const [px, py] = pts[i - 1];
      d += ` Q${j(px)} ${j(py)} ${j((px + x) / 2)} ${j((py + y) / 2)}`;
    }
    const last = pts[pts.length - 1];
    return `${d} L${j(last[0])} ${j(last[1])}`;
  }

  // ── 境界法印（符箓感的一枚小印，取代原来的 emoji 圆点）──
  // 全部画在 -12..12 的方寸之内：一两个笔画。像篆刻，不像图标。
  const SIGILS = {
    // 凡尘：一个点加一道底线——尚未起笔
    seed() {
      return '<path d="M-7 4 L7 4" fill="none"/><circle cx="0" cy="-2" r="2.2"/>';
    },
    // 炼气：三缕上升的气
    spiral() {
      return `<path d="M-7 6 C-3 2 -3 -2 0 -6" fill="none"/>
        <path d="M0 7 C4 3 4 -1 1 -5" fill="none"/>
        <path d="M-3 8 C1 5 5 2 7 -2" fill="none" opacity="0.75"/>`;
    },
    // 筑基：井字立基
    frame() {
      return `<path d="M-7 -7 L7 -7 L7 7 L-7 7 Z" fill="none"/>
        <path d="M-7 0 L7 0" fill="none"/>
        <path d="M0 -7 L0 7" fill="none"/>`;
    },
    // 金丹：一颗丹
    core() {
      return `<circle cx="0" cy="0" r="7.5" fill="none"/>
        <circle cx="0" cy="0" r="3"/>
        <path d="M-9 -4 C-6 -9 6 -9 9 -4" fill="none" opacity="0.7"/>`;
    },
    // 元婴：自相似的三重圈
    fractal() {
      return `<circle cx="0" cy="0" r="8" fill="none"/>
        <circle cx="0" cy="0" r="4.4" fill="none" opacity="0.85"/>
        <circle cx="0" cy="0" r="1.6"/>`;
    },
    // 化神：三横一竖，取「神」字的骨架
    twinring() {
      return `<path d="M-7 -5 L7 -5" fill="none"/>
        <path d="M-5 0 L5 0" fill="none"/>
        <path d="M-7 5 L7 5" fill="none"/>
        <path d="M0 -8 L0 8" fill="none" opacity="0.8"/>`;
    },
    // 炼虚：回纹
    grid() {
      return `<path d="M-7 -7 L7 -7 L7 7 L-7 7 Z" fill="none"/>
        <path d="M-3.5 -3.5 L3.5 -3.5 L3.5 3.5 L-1 3.5 L-1 0 L1.5 0" fill="none"/>`;
    },
    // 合体：两个环相扣
    knot() {
      return `<circle cx="-3.2" cy="0" r="5.6" fill="none"/>
        <circle cx="3.2" cy="0" r="5.6" fill="none" opacity="0.85"/>`;
    },
    // 大乘：山字
    poly() {
      return `<path d="M-8 6 L-3.4 -5 L0 1 L3.4 -5 L8 6 Z" fill="none"/>
        <path d="M-6 8 L6 8" fill="none" opacity="0.7"/>`;
    },
    // 渡劫：雷纹折线
    bolt() {
      return `<path d="M-6 -8 L2 -2 L-2 -1 L5 8" fill="none"/>
        <path d="M2 -8 L-4 -1" fill="none" opacity="0.6"/>`;
    },
    // 仙人：云头纹——仙人的坐骑是云
    infinity() {
      return `<path d="M-8 2 C-8 -4 -2 -4 0 1 C2 6 8 6 8 0 C8 -6 2 -6 0 -1 C-2 4 -8 4 -8 2 Z" fill="none"/>`;
    },
  };

  function sigil(glyph, rand) {
    const draw = SIGILS[glyph] || SIGILS.seed;
    return draw(rand || rngFrom(glyph));
  }

  // ── 装备图（18 件，24×24 网格、线稿）────────────────────
  // 保持线稿：和画像的笔意一致，锁着时直接降成灰色轮廓。
  const ICONS = {
    spark: '<path d="M12 2.5 L13.6 9.2 L20.5 12 L13.6 14.8 L12 21.5 L10.4 14.8 L3.5 12 L10.4 9.2 Z"/>',
    chevrons: '<path d="M4 8 L12 4 L20 8"/><path d="M4 13 L12 9 L20 13"/><path d="M4 18 L12 14 L20 18"/>',
    bracer: '<path d="M4 7 H20 V17 H4 Z"/><path d="M9 7 V17"/><path d="M15 7 V17"/><path d="M4 12 H20"/>',
    ring: '<circle cx="12" cy="13" r="6.5"/><path d="M8.5 6.5 L12 2 L15.5 6.5"/>',
    blade: '<path d="M12 2 L14.5 8 L14.5 15 L12 22 L9.5 15 L9.5 8 Z"/><path d="M6.5 11 H17.5"/>',
    lens: '<circle cx="11" cy="11" r="6.5"/><path d="M15.8 15.8 L21 21"/><circle cx="11" cy="11" r="2"/>',
    boots: '<path d="M8 2.5 V12 L4.5 17.5 V21 H17 V18 L14 15.5 V2.5 Z"/><path d="M6 19.5 H16"/>',
    flag: '<path d="M6 21 V3"/><path d="M6 4.5 H18 L15 8.5 L18 12.5 H6 Z"/>',
    compass: '<circle cx="12" cy="12" r="9"/><path d="M8.5 15.5 L11 11 L15.5 8.5 L13 13 Z"/>',
    token: '<path d="M12 3 L20 7.5 V16.5 L12 21 L4 16.5 V7.5 Z"/><path d="M9 12 L11.5 14.5 L15.5 9.5"/>',
    scroll: '<path d="M6 4 H18 V20 H6 Z"/><path d="M9 8.5 H15"/><path d="M9 12 H15"/><path d="M9 15.5 H13"/>',
    chain: '<circle cx="8.5" cy="12" r="5"/><circle cx="15.5" cy="12" r="5"/><path d="M11 12 H13"/>',
    armor: '<path d="M12 2.5 L20 5.5 V12 C20 16.5 16.5 20 12 21.5 C7.5 20 4 16.5 4 12 V5.5 Z"/><path d="M12 6.5 V17"/>',
    lamp: '<path d="M9 3 H15"/><path d="M10 3 V7 L7 11 V18 H17 V11 L14 7 V3"/><path d="M9 21 H15"/><path d="M12 10.5 V15"/>',
    cloak: '<path d="M12 3 L6 6.5 V14 L4 21 H20 L18 14 V6.5 Z"/><path d="M12 3 V21"/><path d="M9 8 L12 11 L15 8"/>',
    crown: '<path d="M3.5 18 L5.5 7 L9.5 11.5 L12 5 L14.5 11.5 L18.5 7 L20.5 18 Z"/><path d="M3.5 20.5 H20.5"/>',
    eye: '<path d="M2.5 12 C6 6.5 9 4.5 12 4.5 C15 4.5 18 6.5 21.5 12 C18 17.5 15 19.5 12 19.5 C9 19.5 6 17.5 2.5 12 Z"/><circle cx="12" cy="12" r="3.2"/>',
    seal: '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 12 L11.5 14.5 L15.5 9.5"/>',
  };

  function icon(name, options) {
    const opts = options || {};
    const path = ICONS[name] || ICONS.spark;
    const size = opts.size || 24;
    const cls = opts.className ? ` class="${esc(opts.className)}"` : '';
    return `<svg${cls} width="${size}" height="${size}" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="${opts.weight || 1.5}" stroke-linecap="round"
      stroke-linejoin="round" aria-hidden="true">${path}</svg>`;
  }

  function sigilSvg(glyph, options) {
    const opts = options || {};
    const size = opts.size || 40;
    const cls = opts.className ? ` class="${esc(opts.className)}"` : '';
    const rand = rngFrom(opts.seed || glyph);
    return `<svg${cls} width="${size}" height="${size}" viewBox="-14 -14 28 28" aria-hidden="true">
      <g fill="currentColor" stroke="currentColor" stroke-width="${opts.weight || 1.3}"
         stroke-linecap="round" stroke-linejoin="round">${sigil(glyph, rand)}</g>
    </svg>`;
  }

  // ── 头：发髻、道冠、眉眼须 ──────────────────────────────
  function head(art, rand) {
    const tier = art.tier || 0;
    const out = [];
    const top = HEAD_Y - HEAD_R;

    // 发髻：头顶一枚圆髻 + 一支簪。这支簪是「道」最省笔墨的一个记号
    // 头：一个蛋形，不是一颗球——球会立刻读成玩偶
    out.push(`<path class="pm-face" d="M${CX} ${r1(HEAD_Y - HEAD_R * 1.06)}
      C${r1(CX + HEAD_R * 0.98)} ${r1(HEAD_Y - HEAD_R * 0.9)} ${r1(CX + HEAD_R * 0.86)} ${r1(HEAD_Y + HEAD_R * 0.66)}
      ${CX} ${r1(HEAD_Y + HEAD_R * 1.06)}
      C${r1(CX - HEAD_R * 0.86)} ${r1(HEAD_Y + HEAD_R * 0.66)} ${r1(CX - HEAD_R * 0.98)} ${r1(HEAD_Y - HEAD_R * 0.9)}
      ${CX} ${r1(HEAD_Y - HEAD_R * 1.06)} Z"/>`);
    out.push(`<path class="pm-hair" d="M${CX} ${r1(top + 6)}
      C${r1(CX - 23)} ${r1(top + 1)} ${r1(CX - 22)} ${r1(top - 22)} ${CX} ${r1(top - 25)}
      C${r1(CX + 22)} ${r1(top - 22)} ${r1(CX + 23)} ${r1(top + 1)} ${CX} ${r1(top + 6)} Z"/>`);
    out.push(`<path class="pm-pin" d="M${r1(CX - 19)} ${r1(top - 14)} L${r1(CX + 18)} ${r1(top - 21)}"/>`);

    // 道冠：三境之后加一顶小冠（方胜形，不是皇冠）
    if (tier >= 3) {
      const h = 12 + Math.min(10, (tier - 2) * 2);
      out.push(`<path class="pm-crown" d="M${r1(CX - 13)} ${r1(top - 23)}
        L${r1(CX - 9)} ${r1(top - 23 - h)} L${r1(CX + 9)} ${r1(top - 23 - h)} L${r1(CX + 13)} ${r1(top - 23)} Z"/>`);
    }
    // 白眉长毫：六境之后，两条垂下来的长眉——「寿者相」最直接的记号
    if (tier >= 6) {
      const l = 10 + (tier - 5) * 3.4;
      [-1, 1].forEach((side) => {
        const x0 = CX + side * (HEAD_R * 0.42);
        out.push(`<path class="pm-brow-long" d="M${r1(x0)} ${r1(HEAD_Y - 12)}
          C${r1(x0 + side * l * 0.7)} ${r1(HEAD_Y - 15)} ${r1(x0 + side * l)} ${r1(HEAD_Y - 8)}
          ${r1(x0 + side * l * 0.86)} ${r1(HEAD_Y + 2)}"/>`);
      });
    } else {
      [-1, 1].forEach((side) => {
        const x0 = CX + side * (HEAD_R * 0.42);
        out.push(`<path class="pm-brow" d="M${r1(x0)} ${r1(HEAD_Y - 8)}
          Q${r1(x0 + side * 6)} ${r1(HEAD_Y - 11)} ${r1(x0 + side * 12)} ${r1(HEAD_Y - 7)}"/>`);
      });
    }

    // 眼：细长的一横，末端略下压（垂目）。仙人不是瞪着眼看人的
    [-1, 1].forEach((side) => {
      const x0 = CX + side * (HEAD_R * 0.18);
      out.push(`<path class="pm-eye" d="M${r1(x0)} ${r1(HEAD_Y - 2)}
        Q${r1(x0 + side * HEAD_R * 0.2)} ${r1(HEAD_Y + 2)} ${r1(x0 + side * HEAD_R * 0.44)} ${r1(HEAD_Y - 1.6)}"/>`);
    });
    // 鼻与嘴：各一笔。多一笔就俗
    out.push(`<path class="pm-nose" d="M${CX} ${r1(HEAD_Y + 1)} L${CX} ${r1(HEAD_Y + 9)}
      M${r1(CX - 3)} ${r1(HEAD_Y + 10)} Q${CX} ${r1(HEAD_Y + 12)} ${r1(CX + 3)} ${r1(HEAD_Y + 10)}"/>`);
    out.push(`<path class="pm-mouth" d="M${r1(CX - 5)} ${r1(HEAD_Y + 17)} Q${CX} ${r1(HEAD_Y + 19)} ${r1(CX + 5)} ${r1(HEAD_Y + 17)}"/>`);
    [-1, 1].forEach((side) => {
      out.push(`<path class="pm-ear" d="M${r1(CX + side * 24)} ${r1(HEAD_Y - 2)}
        Q${r1(CX + side * 28)} ${r1(HEAD_Y + 4)} ${r1(CX + side * 24)} ${r1(HEAD_Y + 10)}"/>`);
    });

    // 须：三缕，随境界变长。炼气期才开始长须，凡尘还没有
    if (tier >= 1) {
      const len = 8 + tier * 4.6;
      const sway = pick(rand, 3, 8);
      [-1, 0, 1].forEach((k) => {
        const x0 = CX + k * 7;
        out.push(`<path class="pm-beard" d="M${r1(x0)} ${r1(HEAD_Y + 19)}
          C${r1(x0 + pick(rand, -2, 2))} ${r1(HEAD_Y + 24 + len * 0.4)}
          ${r1(x0 + k * 3 + sway * 0.4)} ${r1(HEAD_Y + 26 + len * 0.75)}
          ${r1(x0 + k * 4 + (k ? sway * 0.5 : 0))} ${r1(HEAD_Y + 27 + len)}"/>`);
      });
    }
    return out.join('');
  }

  // ── 身：削肩、长颈、交领、宽袖、飘带 ────────────────────
  // 关键：**大袖是道袍剪影的一部分，不是贴在身上的两块布**。
  // 上一版把袖子画成两个独立的钟形，结果成了两只挂在肩上的白耳朵。
  // 正确的剪影是：颈根 → 削肩 → 袖外缘垂下 → 在袖口处收进腰 → 再放出去成裾。
  // 那条「收进来」的折角就是袖口，白描里靠它一眼认出宽袖。
  function body(art, rand) {
    const tier = art.tier || 0;
    const out = [];
    const shoulderHalf = 40;                 // 肩半宽（削肩）
    const sleeveOut = 50 + tier * 1.6;       // 袖外缘：比肩宽，但不夸张
    const cuffY = WAIST_Y + 6;               // 袖口高度：垂到腰
    const waistHalf = 34;                    // 腰半宽（只比袖口窄一点，落差大就成了花瓶）
    const hemHalf = 62 + tier * 1.8;         // 衣摆

    // 颈：两根短线
    out.push(`<path class="pm-neck" d="M${CX - 6} ${NECK_Y - 6} L${CX - 6} ${SHOULDER_Y - 8}
      M${CX + 6} ${NECK_Y - 6} L${CX + 6} ${SHOULDER_Y - 8}"/>`);

    // 道袍剪影：一整条闭合路径（左右对称），袖口那条折角就在 cuffY 上
    out.push(`<path class="pm-garment" d="M${CX - 7} ${SHOULDER_Y - 10}
      C${r1(CX - 20)} ${SHOULDER_Y - 8} ${r1(CX - shoulderHalf)} ${SHOULDER_Y - 2} ${r1(CX - shoulderHalf)} ${SHOULDER_Y + 12}
      C${r1(CX - shoulderHalf - 9)} ${r1(SHOULDER_Y + 54)} ${r1(CX - sleeveOut)} ${r1(cuffY - 46)} ${r1(CX - sleeveOut)} ${cuffY}
      C${r1(CX - sleeveOut + 3)} ${r1(cuffY + 12)} ${r1(CX - waistHalf - 6)} ${r1(cuffY + 10)} ${r1(CX - waistHalf)} ${r1(cuffY + 14)}
      C${r1(CX - waistHalf - 10)} ${r1(HEM_Y - 96)} ${r1(CX - hemHalf)} ${r1(HEM_Y - 62)} ${r1(CX - hemHalf)} ${HEM_Y}
      Q${r1(CX - hemHalf * 0.62)} ${r1(HEM_Y + 9)} ${r1(CX - hemHalf * 0.2)} ${r1(HEM_Y + 1)}
      Q${r1(CX + hemHalf * 0.2)} ${r1(HEM_Y + 9)} ${r1(CX + hemHalf * 0.62)} ${r1(HEM_Y + 1)}
      Q${r1(CX + hemHalf * 0.88)} ${r1(HEM_Y + 7)} ${r1(CX + hemHalf)} ${HEM_Y}
      C${r1(CX + hemHalf)} ${r1(HEM_Y - 62)} ${r1(CX + waistHalf + 10)} ${r1(HEM_Y - 96)} ${r1(CX + waistHalf)} ${r1(cuffY + 14)}
      C${r1(CX + waistHalf + 6)} ${r1(cuffY + 10)} ${r1(CX + sleeveOut - 3)} ${r1(cuffY + 12)} ${r1(CX + sleeveOut)} ${cuffY}
      C${r1(CX + sleeveOut)} ${r1(cuffY - 46)} ${r1(CX + shoulderHalf + 9)} ${r1(SHOULDER_Y + 54)} ${r1(CX + shoulderHalf)} ${SHOULDER_Y + 12}
      C${r1(CX + shoulderHalf)} ${SHOULDER_Y - 2} ${r1(CX + 20)} ${SHOULDER_Y - 8} ${CX + 7} ${SHOULDER_Y - 10} Z"/>`);

    // 袖口内缘：一线弧，交代袖子的口是张开的
    [-1, 1].forEach((side) => {
      out.push(`<path class="pm-cuff" d="M${r1(CX + side * (sleeveOut - 6))} ${r1(cuffY - 30)}
        Q${r1(CX + side * (sleeveOut - 20))} ${r1(cuffY + 4)} ${r1(CX + side * (waistHalf + 8))} ${r1(cuffY + 12)}"/>`);
    });

    // 交领：两笔斜线在胸前交成一个「y」，道袍最认得出的一处
    const collarY = SHOULDER_Y + 44;
    out.push(`<path class="pm-lapel" d="M${CX - 9} ${SHOULDER_Y - 6} L${CX - 13} ${collarY}
      L${CX} ${collarY + 12}
      M${CX + 9} ${SHOULDER_Y - 6} L${CX + 13} ${collarY} L${CX} ${collarY + 12}"/>`);
    // 领缘：贴着颈根的两笔弧，交领的「交」在这里才交代得清
    out.push(`<path class="pm-lapel faint" d="M${CX - 7} ${SHOULDER_Y - 8} Q${CX} ${SHOULDER_Y + 2} ${CX + 7} ${SHOULDER_Y - 8}"/>`);
    // 腰带：拢袖的手就搭在这上面
    out.push(`<path class="pm-belt" d="M${r1(CX - waistHalf + 2)} ${r1(cuffY + 20)}
      Q${CX} ${r1(cuffY + 26)} ${r1(CX + waistHalf - 2)} ${r1(cuffY + 20)}"/>`);
    // 拢袖的手：腹前一段弧加两点指尖，绝不画五指
    out.push(`<path class="pm-hands" d="M${CX - 16} ${r1(cuffY + 18)} Q${CX} ${r1(cuffY + 30)} ${CX + 16} ${r1(cuffY + 18)}"/>`);
    out.push(`<circle class="pm-finger" cx="${CX - 8}" cy="${r1(cuffY + 24)}" r="1.6"/>`);
    out.push(`<circle class="pm-finger" cx="${CX + 8}" cy="${r1(cuffY + 24)}" r="1.6"/>`);

    // 衣纹：从肩与腰向下撇的几条长弧。条数随境界增加，是「笔意」的主要载体
    const folds = 3 + Math.min(4, Math.floor(tier / 3));
    for (let i = 0; i < folds; i += 1) {
      const side = i % 2 ? 1 : -1;
      const x0 = CX + side * pick(rand, 12, 30);
      const y0 = pick(rand, cuffY + 14, WAIST_Y + 40);
      out.push(`<path class="pm-fold" d="${inkCurve(rand, [
        [x0, y0],
        [r1(x0 + side * pick(rand, 8, 22)), y0 + 48],
        [r1(CX + side * pick(rand, 26, hemHalf - 14)), r1(y0 + 112)],
      ], 2.4)}"/>`);
    }
    // 袖上两道褶：让袖子不至于是一块空白的布
    [-1, 1].forEach((side) => {
      const y0 = pick(rand, SHOULDER_Y + 40, SHOULDER_Y + 56);
      out.push(`<path class="pm-fold sleeve" d="${inkCurve(rand, [
        [r1(CX + side * (shoulderHalf + 4)), y0],
        [r1(CX + side * (sleeveOut - 14)), y0 + 56],
        [r1(CX + side * (sleeveOut - 6)), r1(cuffY - 16)],
      ], 2)}"/>`);
    });

    // 飘带（披帛）：从肩后绕到腰侧再甩出去，末端细尖——「吴带当风」靠它
    const pairs = 1 + Math.min(2, Math.floor(tier / 4));
    for (let i = 0; i < pairs; i += 1) {
      const drop = 320 + i * 26;
      [-1, 1].forEach((side) => {
        const x0 = CX + side * (shoulderHalf - 14);
        out.push(`<path class="pm-ribbon" style="--pm-sway:${r1(9 + i * 2.5)}s;--pm-sway-delay:${r1(i * 0.8)}s"
          d="${inkCurve(rand, [
            [x0, SHOULDER_Y + 6],
            [r1(CX + side * (sleeveOut + 12 + i * 12)), WAIST_Y + 10],
            [r1(CX + side * (waistHalf + 52 + i * 16)), drop - 60],
            [r1(CX + side * (waistHalf + 34 + i * 20)), drop],
          ], 2.8)}"/>`);
      });
    }
    return out.join('');
  }

  // ── 器：葫芦 → 长剑 → 丹炉 ──────────────────────────────
  // 修仙的「器」比任何光效都管用：一眼就知道这是修仙，不是科幻。
  function vessels(art) {
    const tier = art.tier || 0;
    const out = [];

    if (tier >= 3) {
      // 葫芦：两段圆，悬在左手边
      const gx = CX - 96;
      const gy = WAIST_Y + 40;
      out.push(`<g class="pm-gourd">
        <path d="M${gx} ${gy - 22} C${gx - 8} ${gy - 21} ${gx - 9} ${gy - 12} ${gx - 4.6} ${gy - 8}
          C${gx - 4.6} ${gy - 5} ${gx - 4.6} ${gy - 4} ${gx - 4.6} ${gy - 3}
          C${gx - 14} ${gy + 1} ${gx - 15} ${gy + 20} ${gx} ${gy + 25}
          C${gx + 15} ${gy + 20} ${gx + 14} ${gy + 1} ${gx + 4.6} ${gy - 3}
          C${gx + 4.6} ${gy - 4} ${gx + 4.6} ${gy - 5} ${gx + 4.6} ${gy - 8}
          C${gx + 9} ${gy - 12} ${gx + 8} ${gy - 21} ${gx} ${gy - 22} Z"/>
        <path d="M${gx - 3} ${gy - 21} L${gx - 3} ${gy - 28} M${gx + 3} ${gy - 21} L${gx + 3} ${gy - 28}"/>
      </g>`);
    }
    if (tier >= 5) {
      // 长剑：竖在右手边。剑身要有收锋、剑格要出头、穗子要甩开，
      // 否则一条直线加一横只会读成一把尺子（上一版就是这样）
      const sx = CX + 106;
      const top = SHOULDER_Y + 6;
      const tip = HEM_Y - 24;
      out.push(`<g class="pm-sword">
        <path d="M${sx - 4} ${top} L${sx + 4} ${top} L${sx + 2.4} ${r1(tip - 16)} L${sx} ${tip} L${sx - 2.4} ${r1(tip - 16)} Z"/>
        <path d="M${sx - 7} ${top + 26} Q${sx} ${top + 30} ${sx + 7} ${top + 26}"/>
        <path d="M${sx - 9} ${top + 8} L${sx + 9} ${top + 8}"/>
        <path d="M${sx} ${top - 4} L${sx} ${top + 8}"/>
        <path d="M${sx - 9} ${top + 8} C${sx - 18} ${top + 20} ${sx - 12} ${top + 34} ${sx - 16} ${top + 48}"/>
      </g>`);
    }
    if (tier >= 8) {
      // 丹炉：三足两耳，底下托一朵云。到这一境，器自己浮在身前
      const fx = CX;
      const fy = HEM_Y + 26;
      out.push(`<g class="pm-cauldron">
        <path d="M${fx - 22} ${fy - 14} L${fx + 22} ${fy - 14} L${fx + 16} ${fy + 10} L${fx - 16} ${fy + 10} Z"/>
        <path d="M${fx - 22} ${fy - 17} L${fx + 22} ${fy - 17}"/>
        <path d="M${fx - 16} ${fy + 10} L${fx - 19} ${fy + 22} M${fx + 16} ${fy + 10} L${fx + 19} ${fy + 22}
          M${fx} ${fy + 10} L${fx} ${fy + 22}"/>
        <path d="M${fx - 22} ${fy - 6} C${fx - 30} ${fy - 10} ${fx - 30} ${fy - 2} ${fx - 24} ${fy - 2}"/>
        <path d="M${fx + 22} ${fy - 6} C${fx + 30} ${fy - 10} ${fx + 30} ${fy - 2} ${fx + 24} ${fy - 2}"/>
      </g>`);
    }
    return out.join('');
  }

  // ── 背景：淡墨晕、云气、远山、云纹法环 ──────────────────
  function backdrop(art, uid, rand) {
    const tier = art.tier || 0;
    const out = [];
    // 晕（不是光）：一圈边界不齐的淡墨，像在绢上洇开
    out.push(`<ellipse class="pm-halo" cx="${CX}" cy="${WAIST_Y + 6}" rx="${r1(148 + tier * 3)}"
      ry="${r1(196 + tier * 4)}" fill="url(#${uid}-halo)"/>`);

    // 云气：横向的 S 形长线，愈高境愈多
    const clouds = 2 + Math.min(3, Math.floor(tier / 3));
    for (let i = 0; i < clouds; i += 1) {
      const y = WAIST_Y - 30 + i * 62 + pick(rand, -12, 12);
      out.push(`<path class="pm-cloud" style="--pm-drift:${r1(16 + i * 5)}s;--pm-drift-delay:${r1(i * 1.4)}s"
        d="${inkCurve(rand, [
          [r1(24 + pick(rand, 0, 30)), r1(y + pick(rand, -8, 8))],
          [96, r1(y - pick(rand, 6, 16))],
          [160, r1(y + pick(rand, -4, 10))],
          [226, r1(y - pick(rand, 4, 14))],
          [r1(296 - pick(rand, 0, 30)), r1(y + pick(rand, -6, 8))],
        ], 3)}"/>`);
    }
    // 远山：四境之后，脚下一线远山淡影
    if (tier >= 4) {
      out.push(`<path class="pm-mountain" d="${inkCurve(rand, [
        [10, GROUND - 34], [70, GROUND - 70], [128, GROUND - 40],
        [190, GROUND - 78], [250, GROUND - 44], [310, GROUND - 62],
      ], 4)}"/>`);
      out.push(`<path class="pm-mountain faint" d="${inkCurve(rand, [
        [10, GROUND - 14], [86, GROUND - 42], [150, GROUND - 16],
        [224, GROUND - 46], [310, GROUND - 22],
      ], 4)}"/>`);
    }
    // 云纹法环：五境之后。环上是「云头」短弧，不是罗盘刻度——刻度是仪器的语言
    if (tier >= 5) {
      const count = Math.min(2, Math.floor((tier - 3) / 3));
      for (let i = 0; i < count; i += 1) {
        const radius = 112 + i * 24;
        const ticks = [];
        for (let k = 0; k < 10; k += 1) {
          const a = (k / 10) * Math.PI * 2 + i;
          const x1 = r1(CX + Math.cos(a) * (radius - 5));
          const y1 = r1(WAIST_Y + 6 + Math.sin(a) * (radius - 5) * 0.94);
          const x2 = r1(CX + Math.cos(a) * (radius + 5));
          const y2 = r1(WAIST_Y + 6 + Math.sin(a) * (radius + 5) * 0.94);
          ticks.push(`<path d="M${x1} ${y1} Q${r1((x1 + x2) / 2 + 3)} ${r1((y1 + y2) / 2 - 3)} ${x2} ${y2}"/>`);
        }
        out.push(`<g class="pm-ring" style="--pm-spin:${r1(86 + i * 38)}s;--pm-from:${i * 9}deg;--pm-to:${i * 9 + 360}deg">
          <circle cx="${CX}" cy="${WAIST_Y + 6}" r="${radius}" fill="none"
            stroke="url(#${uid}-ring)" stroke-width="0.8" opacity="${r1(0.3 - i * 0.09)}"/>
          <g class="pm-cloud-ticks">${ticks.join('')}</g>
        </g>`);
      }
    }
    return out.join('');
  }

  /** 丹田：一颗内丹。修仙的「核心」在这里，不在胸口的光带 */
  function core(art, uid) {
    const tier = art.tier || 0;
    const y = WAIST_Y - 26;
    const out = [`<circle class="pm-dantian" cx="${CX}" cy="${y}" r="${r1(12 + tier * 0.5)}" fill="url(#${uid}-core)" opacity="0.55"/>`];
    if (tier >= 1) {
      out.push(`<circle class="pm-dantian-ring" cx="${CX}" cy="${y}" r="${r1(7 + tier * 0.3)}" fill="none"/>`);
    }
    out.push(`<g class="pm-core" transform="translate(${CX} ${y}) scale(${r1(0.5 + tier * 0.035)})"
      fill="none" stroke="${esc(art.aura)}" stroke-width="1.2" stroke-linecap="round"
      stroke-linejoin="round">${sigil(art.glyph, rngFrom(`core|${art.glyph}`))}</g>`);
    return out.join('');
  }

  /** 灵光：不再是粒子雨，改成几缕浮尘 —— 少而慢 */
  function motes(art, rand) {
    const count = Math.min(18, Math.max(3, Math.round((art.particles || 6) * 0.55)));
    const out = [];
    for (let i = 0; i < count; i += 1) {
      out.push(`<circle class="pm-particle" cx="${r1(pick(rand, 34, 286))}" cy="${r1(pick(rand, 120, GROUND - 30))}"
        r="${r1(pick(rand, 0.9, 2.1))}"
        style="--pm-dur:${r1(pick(rand, 7, 15))}s;--pm-delay:${r1(rand() * 9)}s"/>`);
    }
    return `<g class="pm-particles">${out.join('')}</g>`;
  }

  // ── 主体 ────────────────────────────────────────────────
  function render(options) {
    const opts = options || {};
    const art = Object.assign({
      tier: 0, primary: '#c9a961', deep: '#3a4450', aura: '#e8eef5',
      glyph: 'seed', rings: 0, particles: 6,
    }, opts.art || {});
    const seed = `${opts.seed || 'guest'}|${art.glyph}|${opts.level || 0}`;
    const rand = rngFrom(seed);
    const uid = `pm${(hashSeed(seed) % 100000).toString(36)}`;
    const parts = [];

    // ① 晕、云、山、法环（一切都在淡墨里，不发光）
    parts.push(backdrop(art, uid, rand));
    // ② 器（葫芦 / 剑 / 丹炉）
    parts.push(vessels(art));
    // ③ 身、袖、飘带
    parts.push(body(art, rand));
    // ④ 丹田内丹
    parts.push(core(art, uid));
    // ⑤ 头（发髻、眉眼、须）
    parts.push(head(art, rand));
    // ⑥ 浮尘
    parts.push(motes(art, rand));
    // ⑦ 界栏：两条细竖线，像卷轴的天头地脚，不是取景框
    parts.push(`<g class="pm-frame">
      <path d="M26 40 L26 ${GROUND - 18}"/>
      <path d="M294 40 L294 ${GROUND - 18}"/>
      <path d="M26 40 L294 40" opacity="0.5"/>
      <path d="M26 ${GROUND - 18} L294 ${GROUND - 18}" opacity="0.5"/>
    </g>`);

    const cls = ['pm-portrait', opts.className || ''].filter(Boolean).join(' ');
    return `<svg class="${cls}" viewBox="0 0 320 ${GROUND}" width="${opts.width || '100%'}"
      ${opts.height ? `height="${opts.height}"` : ''} role="img"
      aria-label="${esc(opts.label || '神识画像')}" style="--pm-primary:${esc(art.primary)};--pm-aura:${esc(art.aura)}">
      <defs>
        <radialGradient id="${uid}-halo" cx="50%" cy="46%" r="58%">
          <stop offset="0%" stop-color="${esc(art.primary)}" stop-opacity="0.09"/>
          <stop offset="52%" stop-color="${esc(art.deep)}" stop-opacity="0.3"/>
          <stop offset="100%" stop-color="${esc(art.deep)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-core" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.5"/>
          <stop offset="60%" stop-color="${esc(art.primary)}" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="${uid}-ring" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.7"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0.25"/>
        </linearGradient>
      </defs>
      ${parts.join('')}
      <g class="pm-seed" data-seed="${esc(seed)}"></g>
    </svg>`;
  }

  window.Portrait = { render, icon, sigil: sigilSvg, SIGILS, ICONS, hashSeed, rngFrom, esc };
})();
