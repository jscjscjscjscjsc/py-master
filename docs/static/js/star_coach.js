/**
 * star_coach.js — 星辰教练的法相（11 境，程序化生成，零图片素材）
 *
 * 设计上刻意与 portrait.js（你的神识画像）分开：
 *
 *   portrait.js 画的是「你」——无脸、披甲、正面而立，是一枚拓印；
 *   star_coach.js 画的是「教练」——有脸、有冠、手上有引路星，
 *   是一尊会随你升境而换了法身的**活物**。
 *
 * 三个必须守住的约定：
 *
 * 1. **凡尘要萌，金仙要盛。** 同一个骨架函数吃 COACH_FORMS 的参数：
 *    tier 0 是抱星星的大头娃娃（三头身），tier 10 是一个悬于星海之上、
 *    掌托星系、周天法阵环绕的法相（七头身）。中间九境连续过渡，不是特例。
 * 2. **身形比例必须像「人」。** 第一版画成了上窄下宽的一口钟，看起来像
 *    国际象棋的兵。所以骨架里必须有肩线、腰身、袍摆三段，头身比按境界走：
 *    三头身（童）→ 五头半（少年）→ 六头半（修士）→ 七头（仙身）。
 * 3. **任何字段缺失都要能画。** 缺 art 就退回凡尘形态，绝不抛异常：
 *    这个组件挂在聊天页上，它挂掉就等于整个页面白屏。
 *
 * 动效全部交给 CSS（见 coach_scene.css），这里只生成静态几何 +
 * 写进行内变量（--sc-*），和 portrait.js 是同一套做法。
 */
(function () {
  'use strict';

  const CX = 160;              // 中轴
  const HALO_CY = 200;         // 背光/法阵的中心（比头低一点，重心才稳）
  const FLOOR = 440;           // 取景框底边

  // ── 随机源：同一个人 + 同一境，永远得到同一尊法相 ────────
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

  function r1(v) { return Math.round(v * 10) / 10; }
  function pick(rand, min, max) { return min + rand() * (max - min); }

  function polar(cx, cy, radius, deg) {
    const a = (deg * Math.PI) / 180;
    return [r1(cx + Math.cos(a) * radius), r1(cy + Math.sin(a) * radius)];
  }

  // ── 基础图形 ────────────────────────────────────────────
  /** n 角星：引路星、法印、冠饰都用它，尖角数与半径比决定「灵物」还是「利器」 */
  function starPath(cx, cy, outer, points, innerRatio, rot) {
    const pts = [];
    const steps = points * 2;
    for (let i = 0; i < steps; i += 1) {
      const radius = i % 2 ? outer * innerRatio : outer;
      const a = ((i / steps) * 360 + (rot || 0) - 90) * Math.PI / 180;
      pts.push(`${r1(cx + Math.cos(a) * radius)} ${r1(cy + Math.sin(a) * radius)}`);
    }
    return `M${pts.join(' L')} Z`;
  }

  /** 缺口圆环：缺口角度由种子决定，所以同一个境界不同人纹路不同 */
  function gapRing(radius, gapDeg, offsetDeg) {
    return `stroke-dasharray="${r1(360 - gapDeg)} ${r1(gapDeg)}" stroke-dashoffset="${r1(offsetDeg || 0)}"`;
  }

  /** 环上的刻度：像罗盘，也像 HUD 的准星——神仙感与科技感的公共部分 */
  function ticks(cx, cy, radius, count, len, cls) {
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const a = (i / count) * 360;
      const [x1, y1] = polar(cx, cy, radius - len / 2, a);
      const [x2, y2] = polar(cx, cy, radius + len / 2, a);
      out.push(`<path class="${cls || 'sc-tick'}" d="M${x1} ${y1} L${x2} ${y2}"/>`);
    }
    return out.join('');
  }

  // ── 骨架：四族身形 ──────────────────────────────────────
  // 每一族给出一组人体测量值，后面所有部件（甲、袖、冠、星）都挂在这些
  // 锚点上，所以调比例只改这里，不用碰画法。
  const SHAPES = {
    // 三头身：头占身高三分之一，这是「萌」的硬指标，别按真人比例修
    child: {
      headR: 44, headY: 116, neckW: 17,
      shoulderY: 176, shoulderW: 40, waistY: 238, waistW: 34,
      hemY: 302, hemW: 50, armW: 12, star: [160, 236], sleeve: 0,
    },
    // 五头半：少年的肩膀开始出现，但还没长开
    youth: {
      headR: 34, headY: 108, neckW: 14,
      shoulderY: 156, shoulderW: 48, waistY: 236, waistW: 35,
      hemY: 372, hemW: 76, armW: 13, star: [252, 232], sleeve: 1,
    },
    // 六头半：修士。肩宽腰窄，袍摆明显外扩
    adept: {
      headR: 32, headY: 104, neckW: 13,
      shoulderY: 150, shoulderW: 54, waistY: 244, waistW: 36,
      hemY: 392, hemW: 84, armW: 14, star: [264, 228], sleeve: 2,
    },
    // 七头身：仙身。肩最宽、身最长、袍摆散成光
    immortal: {
      headR: 31, headY: 100, neckW: 12,
      shoulderY: 144, shoulderW: 60, waistY: 248, waistW: 38,
      hemY: 414, hemW: 94, armW: 15, star: [272, 224], sleeve: 3,
    },
  };

  function measure(form) {
    return Object.assign({}, SHAPES[form] || SHAPES.child);
  }

  /** 躯干 + 袍摆：肩线 → 腰身 → 外扩的裙摆。这条路径是本文件的骨。 */
  function torsoPath(m) {
    return `M${CX - m.neckW} ${m.shoulderY - 12}
      C${r1(CX - m.shoulderW * 0.72)} ${m.shoulderY - 14} ${CX - m.shoulderW} ${m.shoulderY - 4} ${CX - m.shoulderW} ${m.shoulderY + 10}
      C${CX - m.shoulderW - 2} ${m.shoulderY + 40} ${CX - m.waistW} ${m.waistY - 44} ${CX - m.waistW} ${m.waistY}
      C${CX - m.waistW - 5} ${m.waistY + 52} ${r1(CX - m.hemW * 0.84)} ${m.hemY - 72} ${CX - m.hemW} ${m.hemY}
      L${CX + m.hemW} ${m.hemY}
      C${r1(CX + m.hemW * 0.84)} ${m.hemY - 72} ${CX + m.waistW + 5} ${m.waistY + 52} ${CX + m.waistW} ${m.waistY}
      C${CX + m.waistW} ${m.waistY - 44} ${CX + m.shoulderW + 2} ${m.shoulderY + 40} ${CX + m.shoulderW} ${m.shoulderY + 10}
      C${CX + m.shoulderW} ${m.shoulderY - 4} ${r1(CX + m.shoulderW * 0.72)} ${m.shoulderY - 14} ${CX + m.neckW} ${m.shoulderY - 12} Z`;
  }

  /** 双臂：左臂垂下，右臂向外摊开（托着引路星）。两条弧度都从肩点起。 */
  function arms(m) {
    const sy = m.shoulderY + 16;
    const drop = (m.hemY - m.shoulderY) * 0.52;
    return {
      left: `M${CX - m.shoulderW + 6} ${sy} C${CX - m.shoulderW - 22} ${sy + drop * 0.5}
        ${CX - m.shoulderW - 30} ${sy + drop * 0.8} ${CX - m.shoulderW - 20} ${sy + drop}`,
      right: `M${CX + m.shoulderW - 6} ${sy} C${CX + m.shoulderW + 26} ${sy + drop * 0.34}
        ${CX + m.shoulderW + 48} ${sy + drop * 0.54} ${CX + m.shoulderW + 56} ${sy + drop * 0.66}`,
      handL: [CX - m.shoulderW - 20, sy + drop],
      handR: [CX + m.shoulderW + 56, sy + drop * 0.66],
    };
  }

  /**
   * 袖与手。这是第一版最难看的部件，教训是：**不要把赤裸的手臂整条画出来**。
   * 修仙的身形该是「宽袖垂下来，手从袖口露一截」——
   * 所以袖是一个钟形，手是袖口下方的一枚小圆掌，中间只留一段极短的前臂。
   */
  function sleevesAndHands(art, m) {
    const level = m.sleeve || 0;
    const spanY = m.hemY - m.shoulderY;
    const sleeves = [];
    const arms = [];
    const hands = [];

    if (!level) {
      // 童形：两只短手从肩侧弯到胸前，正好托住那颗引路星
      const sy = m.shoulderY + 10;
      const hy = m.star[1] + 24;
      [-1, 1].forEach((side) => {
        const hx = CX + side * 26;
        const d = `M${CX + side * (m.shoulderW + 4)} ${sy} Q${CX + side * (m.shoulderW + 22)} ${hy - 20} ${hx} ${hy}`;
        arms.push(`<path class="sc-arm-base" stroke-width="${m.armW + 4}" d="${d}"/>`);
        arms.push(`<path class="sc-arm-line" stroke-width="${m.armW}" d="${d}"/>`);
        hands.push([hx, hy, m.armW * 0.6]);
      });
      return { sleeves, arms, hands };
    }

    // [左右, 袖长比, 袖宽比]：右袖短一些，因为它那条手臂是抬起来托星的
    const specs = [[-1, 0.46, 0.5], [1, 0.3, 0.56]];
    specs.forEach(([side, lenRatio, wideRatio]) => {
      const len = spanY * lenRatio * (0.86 + level * 0.06);
      const wide = m.shoulderW * wideRatio * (0.9 + level * 0.1);
      const x0 = CX + side * (m.shoulderW - 6);
      const x1 = CX + side * (m.shoulderW + wide);
      const yb = m.shoulderY + len;
      sleeves.push(`<path class="sc-sleeve" d="M${r1(x0)} ${m.shoulderY + 6}
        C${r1(x0 + side * wide * 0.34)} ${r1(m.shoulderY + len * 0.5)} ${r1(x1)} ${r1(m.shoulderY + len * 0.64)} ${r1(x1)} ${r1(yb)}
        C${r1(x1 - side * wide * 0.38)} ${r1(yb + len * 0.16)} ${r1(x0 - side * 8)} ${r1(yb + len * 0.12)} ${r1(x0 - side * 2)} ${r1(m.shoulderY + len * 0.78)} Z"/>`);
      sleeves.push(`<path class="sc-sleeve-hem" d="M${r1(x1)} ${r1(yb)}
        C${r1(x1 - side * wide * 0.38)} ${r1(yb + len * 0.16)} ${r1(x0 - side * 8)} ${r1(yb + len * 0.12)} ${r1(x0 - side * 2)} ${r1(m.shoulderY + len * 0.78)}"/>`);
      const hx = r1(x1 - side * wide * 0.18);
      const hy = r1(yb + m.armW * 0.55);
      const fx = r1(x0 + side * wide * 0.68);
      const fy = r1(yb - len * 0.12);
      arms.push(`<path class="sc-arm-base" stroke-width="${m.armW + 3}" d="M${fx} ${fy} L${hx} ${hy}"/>`);
      arms.push(`<path class="sc-arm-line" stroke-width="${Math.max(6, m.armW - 1)}" d="M${fx} ${fy} L${hx} ${hy}"/>`);
      hands.push([hx, hy, r1(m.armW * 0.66)]);
    });
    return { sleeves, arms, hands };
  }

  // ── 脸 ──────────────────────────────────────────────────
  // 教练唯一「像活的」的地方。境界越高，眼睛越不像人的眼睛——
  // 到金仙只剩面甲里的两枚光瞳，这是有意为之：它已经不需要像人了。
  function face(art, m, uid) {
    const y = m.headY;
    const r = m.headR;
    const eye = art.eye || 'dot';
    const eyeY = y + r * 0.12;
    const out = [];

    if (eye === 'dot') {
      // 豆豆眼 + 高光 + 腮红：凡尘与炼气期的「萌」全靠这三样
      const dx = r * 0.36;
      [-1, 1].forEach((side) => {
        out.push(`<circle class="sc-eye" cx="${r1(CX + side * dx)}" cy="${r1(eyeY)}" r="${r1(r * 0.19)}"/>`);
        out.push(`<circle class="sc-eye-hi" cx="${r1(CX + side * dx + r * 0.07)}" cy="${r1(eyeY - r * 0.07)}" r="${r1(r * 0.07)}"/>`);
        out.push(`<ellipse class="sc-blush" cx="${r1(CX + side * dx * 1.9)}" cy="${r1(eyeY + r * 0.36)}"
          rx="${r1(r * 0.21)}" ry="${r1(r * 0.115)}"/>`);
      });
      out.push(`<path class="sc-mouth" d="M${r1(CX - r * 0.1)} ${r1(eyeY + r * 0.42)}
        Q${r1(CX)} ${r1(eyeY + r * 0.62)} ${r1(CX + r * 0.1)} ${r1(eyeY + r * 0.42)}"/>`);
      return out.join('');
    }

    if (eye === 'ring' || eye === 'star') {
      const dx = r * 0.4;
      [-1, 1].forEach((side) => {
        const ex = CX + side * dx;
        if (eye === 'ring') {
          out.push(`<circle class="sc-eye-ring" cx="${r1(ex)}" cy="${r1(eyeY)}" r="${r1(r * 0.2)}"/>`);
          out.push(`<circle class="sc-eye" cx="${r1(ex)}" cy="${r1(eyeY)}" r="${r1(r * 0.08)}"/>`);
        } else {
          out.push(`<path class="sc-eye-star" d="${starPath(ex, eyeY, r * 0.27, 4, 0.34, 0)}"/>`);
        }
      });
      out.push(`<path class="sc-mouth" d="M${r1(CX - r * 0.08)} ${r1(eyeY + r * 0.44)}
        L${r1(CX + r * 0.08)} ${r1(eyeY + r * 0.44)}"/>`);
      return out.join('');
    }

    // ── 高境：面甲化的眼 ─────────────────────────────────
    // 关键教训：**一条横贯整张脸的光带会被读成一张嘴**——第一版就是这样，
    // 所有高境法相都像在抿嘴笑。所以必须画成左右两只分开的眼睛。
    const dx = r * 0.42;
    const w = r * 0.34;
    const h = r * (eye === 'third' ? 0.2 : 0.16);
    const tilt = eye === 'third' ? 7 : 3;
    const lens = (cx) => `M${r1(cx - w)} ${r1(eyeY)} Q${r1(cx)} ${r1(eyeY - h)} ${r1(cx + w)} ${r1(eyeY)}
      Q${r1(cx)} ${r1(eyeY + h)} ${r1(cx - w)} ${r1(eyeY)} Z`;
    const eyes = [-1, 1].map((side) =>
      `<g transform="rotate(${r1(-side * tilt)} ${CX} ${r1(eyeY)})">
        <path class="sc-visor-band" d="${lens(CX + side * dx)}" fill="url(#${uid}-visor)"/>
      </g>`).join('');

    if (eye === 'third') {
      return eyes
        + `<path class="sc-third-eye" d="${starPath(CX, y - r * 0.5, r * 0.17, 4, 0.3, 0)}"/>`
        + `<circle class="sc-third-eye-core" cx="${CX}" cy="${r1(y - r * 0.5)}" r="${r1(r * 0.055)}"/>`;
    }
    if (eye === 'void') {
      // 金仙：面甲里只留两枚带环的光瞳——它已经不靠五官表达情绪了
      return eyes + [-1, 1].map((side) =>
        `<circle class="sc-void-ring" cx="${r1(CX + side * dx)}" cy="${r1(eyeY)}" r="${r1(r * 0.21)}"/>`
        + `<circle class="sc-void-core" cx="${r1(CX + side * dx)}" cy="${r1(eyeY)}" r="${r1(r * 0.075)}"/>`).join('');
    }
    // 合体 / 大乘 / 渡劫：面甲里两点稳定的眼芒
    return eyes + [-1, 1].map((side) =>
      `<circle class="sc-visor-pupil" cx="${r1(CX + side * dx)}" cy="${r1(eyeY)}" r="${r1(r * 0.07)}"/>`).join('');
  }

  /** 面甲/头冠：高境的头是一顶盔，不是一颗光脑袋 */
  function helm(art, m) {
    if (art.tier < 5) return '';
    const r = m.headR;
    const y = m.headY;
    // 渡劫与仙人境这一档的盔是**发光**的：黑盔配金冠在深色底上会糊成一团
    const radiant = art.tier >= 9 ? ' is-radiant' : '';
    const out = [
      `<path class="sc-helm" d="M${r1(CX - r)} ${r1(y + r * 0.06)}
        A${r1(r)} ${r1(r * 1.06)} 0 0 1 ${r1(CX + r)} ${r1(y + r * 0.06)}
        C${r1(CX + r * 0.9)} ${r1(y - r * 0.22)} ${r1(CX - r * 0.9)} ${r1(y - r * 0.22)} ${r1(CX - r)} ${r1(y + r * 0.06)} Z"/>`,
    ];
    if (art.tier >= 7) {
      out.push(`<path class="sc-helm-nasal" d="M${CX} ${r1(y - r * 0.72)} L${CX} ${r1(y + r * 1.02)}"/>`);
    }
    return `<g class="sc-helm-group${radiant}">${out.join('')}</g>`;
  }

  // ── 星冕（冠）────────────────────────────────────────────
  // crest 0..5：从「一撮呆毛」一路长到「大星冠 + 悬空光冠」。
  function crown(art, m) {
    const top = m.headY - m.headR;
    const level = art.crest || 0;
    const r = m.headR;
    const out = [];

    if (level === 0) {
      // 呆毛：两根，长短不一。这是「萌」最省笔墨的一招。
      out.push(`<path class="sc-ahoge" d="M${r1(CX - r * 0.16)} ${r1(top + 6)}
        C${r1(CX - r * 0.4)} ${r1(top - r * 0.46)} ${r1(CX + r * 0.14)} ${r1(top - r * 0.6)} ${r1(CX + r * 0.2)} ${r1(top - r * 0.12)}"/>`);
      out.push(`<path class="sc-ahoge" d="M${r1(CX + r * 0.34)} ${r1(top + 8)}
        C${r1(CX + r * 0.62)} ${r1(top - r * 0.2)} ${r1(CX + r * 0.8)} ${r1(top - r * 0.34)} ${r1(CX + r * 0.68)} ${r1(top + 0.02)}"/>`);
      return `<g class="sc-crown">${out.join('')}</g>`;
    }

    // 束发环：贴着头顶的一道弧 + 正中一颗宝石。位置在头顶**之上**，
    // 不能压到脸——第一版把它画进了额头，看起来像一根天线。
    const bandY = m.headY - r * 0.62;
    out.push(`<path class="sc-circlet" d="M${r1(CX - r * 0.96)} ${r1(bandY + r * 0.14)}
      Q${CX} ${r1(bandY - r * 0.46)} ${r1(CX + r * 0.96)} ${r1(bandY + r * 0.14)}"/>`);
    out.push(`<path class="sc-circlet-gem" d="${starPath(CX, bandY - r * 0.3, r * 0.14, 4, 0.3, 0)}"/>`);

    // 侧翼：crest 2 起。做成向斜后上方扫出去的薄鳍，而不是兔耳朵
    if (level >= 2) {
      [-1, 1].forEach((side) => {
        const h = r * (0.8 + level * 0.12);
        out.push(`<path class="sc-crown-wing" d="M${r1(CX + side * r * 0.82)} ${r1(bandY - r * 0.28)}
          C${r1(CX + side * r * 1.36)} ${r1(bandY - r * 0.72)} ${r1(CX + side * r * 1.52)} ${r1(bandY - r * 0.62 - h * 0.6)}
          ${r1(CX + side * r * 1.06)} ${r1(bandY - h * 0.72)}
          C${r1(CX + side * r * 1.02)} ${r1(bandY - h * 0.4)} ${r1(CX + side * r * 0.9)} ${r1(bandY - r * 0.2)} ${r1(CX + side * r * 0.82)} ${r1(bandY - r * 0.28)} Z"/>`);
      });
    }
    // 冠面：crest 3 起，立起一顶真正的三尖冠（不是一根螺丝钉）
    if (level >= 3) {
      const h = r * (0.7 + level * 0.16);
      out.push(`<path class="sc-crown-face" d="M${r1(CX - r * 0.86)} ${r1(bandY - r * 0.34)}
        L${r1(CX - r * 0.46)} ${r1(bandY - r * 0.34 - h * 0.3)}
        L${r1(CX - r * 0.16)} ${r1(bandY - r * 0.4)}
        L${CX} ${r1(bandY - r * 0.42 - h)}
        L${r1(CX + r * 0.16)} ${r1(bandY - r * 0.4)}
        L${r1(CX + r * 0.46)} ${r1(bandY - r * 0.34 - h * 0.3)}
        L${r1(CX + r * 0.86)} ${r1(bandY - r * 0.34)} Z"/>`);
    }
    // 悬空光冠：crest 4 起，冠上再浮一圈小环 —— 神仙感的标志
    if (level >= 4) {
      const cy = bandY - r * (1.5 + level * 0.14);
      const rr = r * (0.7 + level * 0.06);
      out.push(`<g class="sc-float-crown" style="--sc-spin-dur:${26 - level * 2}s">
        <ellipse cx="${CX}" cy="${r1(cy)}" rx="${r1(rr)}" ry="${r1(rr * 0.22)}" fill="none" class="sc-float-crown-ring"/>
        ${ticks(CX, cy, rr * 0.74, 8 + level * 2, r * 0.15, 'sc-float-crown-tick')}
      </g>`);
    }
    return `<g class="sc-crown">${out.join('')}</g>`;
  }

  // ── 甲片 / 法袍细节 ─────────────────────────────────────
  // 甲片是**贴着胸口**的横带，不是悬空的四边形——第一版画成了后者。
  function plates(art, m, rand) {
    const count = art.plates || 0;
    if (!count) return '';
    const out = [];
    // 胸甲：一整片，从锁骨盖到胸口
    const chestY = m.shoulderY + 16;
    const half = m.waistW + (m.shoulderW - m.waistW) * 0.72 - 4;
    out.push(`<path class="sc-plate" d="M${r1(CX - half)} ${r1(chestY)}
      Q${CX} ${r1(chestY + 16)} ${r1(CX + half)} ${r1(chestY)}
      Q${CX} ${r1(chestY + 30)} ${r1(CX - half)} ${r1(chestY)} Z"/>`);
    // 肩甲：左右各几片，短的，只压住肩头
    for (let i = 1; i < count; i += 1) {
      [-1, 1].forEach((side) => {
        const y = m.shoulderY + 4 + (i - 1) * 24;
        const inner = CX + side * (m.shoulderW * 0.44);
        const outer = CX + side * (m.shoulderW + 2 - (i - 1) * 4);
        out.push(`<path class="sc-plate" d="M${r1(inner)} ${r1(y)}
          Q${r1((inner + outer) / 2)} ${r1(y + 12)} ${r1(outer)} ${r1(y + 2)}
          Q${r1((inner + outer) / 2)} ${r1(y + 20)} ${r1(inner)} ${r1(y)} Z"/>`);
      });
    }
    // 腰封：把上下两截断开，身形才有腰
    const by = m.waistY;
    out.push(`<path class="sc-belt" d="M${r1(CX - m.waistW - 1)} ${r1(by - 5)} Q${CX} ${r1(by + 5)} ${r1(CX + m.waistW + 1)} ${r1(by - 5)}"/>`);
    out.push(`<path class="sc-belt-gem" d="${starPath(CX, by + 2, 4.2, 4, 0.34, 0)}"/>`);
    // 胸口中缝 + 一条纵向灵脉（高境才有，且带电路折角）
    out.push(`<path class="sc-spine" d="M${CX} ${r1(m.shoulderY + 24)} L${CX} ${r1(m.hemY - 40)}"/>`);
    if (art.tier >= 5) {
      let d = `M${CX} ${r1(m.shoulderY + 34)}`;
      let x = CX;
      const step = (m.hemY - m.shoulderY) / 6;
      for (let i = 0; i < 5; i += 1) {
        x += (i % 2 ? -1 : 1) * pick(rand, 14, 30);
        x = Math.max(CX - m.waistW + 4, Math.min(CX + m.waistW - 4, x));
        d += ` L${r1(x)} ${r1(m.shoulderY + 34 + (i + 1) * step)}`;
      }
      out.push(`<path class="sc-circuit" d="${d}"/>`);
    }
    return `<g class="sc-plates">${out.join('')}</g>`;
  }

  // ── 披风 / 飘带 ─────────────────────────────────────────
  function cape(art, m, rand) {
    const level = art.cape || 0;
    if (!level) return '';
    const spread = m.shoulderW * (1.32 + level * 0.2);
    const bottom = m.hemY - 4;
    const wob = pick(rand, 12, 26);
    const out = [];
    [-1, 1].forEach((side) => {
      out.push(`<path class="sc-cape" d="M${r1(CX + side * (m.shoulderW * 0.8))} ${r1(m.shoulderY + 8)}
        C${r1(CX + side * spread * 0.9)} ${r1(m.shoulderY + 34)} ${r1(CX + side * spread)} ${r1(bottom - 110)}
        ${r1(CX + side * (spread - wob))} ${r1(bottom)}
        L${r1(CX + side * (m.shoulderW + 2))} ${r1(bottom - 40)} Z"/>`);
    });
    if (level >= 2) {
      const dots = [];
      for (let i = 0; i < level * 8; i += 1) {
        const side = i % 2 ? 1 : -1;
        const x = CX + side * pick(rand, m.shoulderW * 1.05, spread * 0.92);
        const y = pick(rand, m.shoulderY + 30, bottom - 30);
        dots.push(`<circle cx="${r1(x)}" cy="${r1(y)}" r="${r1(pick(rand, 0.8, 1.8))}"/>`);
      }
      out.push(`<g class="sc-cape-stars">${dots.join('')}</g>`);
    }
    return `<g class="sc-capes">${out.join('')}</g>`;
  }

  function ribbons(art, m) {
    const pairs = art.ribbon || 0;
    if (!pairs) return '';
    const out = [];
    const y0 = m.waistY - 6;
    for (let i = 0; i < pairs; i += 1) {
      const spread = m.shoulderW * (0.9 + i * 0.4);
      const drop = m.hemY - y0 - i * 12;
      const dur = 7 + i * 1.6;
      [-1, 1].forEach((side) => {
        out.push(`<path class="sc-ribbon" style="--sc-sway:${r1(dur)}s;--sc-sway-delay:${r1(i * 0.6)}s"
          d="M${r1(CX + side * (m.waistW - 4))} ${r1(y0)}
          C${r1(CX + side * spread)} ${r1(y0 + drop * 0.32)}
          ${r1(CX + side * (spread + 24))} ${r1(y0 + drop * 0.64)}
          ${r1(CX + side * (spread + 4))} ${r1(y0 + drop)}"/>`);
      });
    }
    return `<g class="sc-ribbons">${out.join('')}</g>`;
  }

  // ── 引路星：教练手上/身边那颗东西 ───────────────────────
  // orb 星丸（低境，圆润可爱）/ shard 星棱（中境，锐利）/ galaxy 掌心星系（高境）
  function guideStar(art, m, uid, rand) {
    const [sx, sy] = m.star;
    const kind = art.star || 'orb';
    const out = [];

    if (kind === 'orb' || kind === 'shard') {
      const isOrb = kind === 'orb';
      const r = isOrb ? (art.tier >= 2 ? 15 : 13) : 17;
      // 辉光要足够亮、足够大：太淡的话在高境的深色背景上会读成一块空洞
      out.push(`<circle class="sc-star-glow" cx="${sx}" cy="${sy}" r="${r * (isOrb ? 3 : 3.4)}" fill="url(#${uid}-star-glow)"/>`);
      if (!isOrb) {
        out.push(`<g class="sc-star-orbit" style="--sc-spin-dur:${r1(9 + rand() * 5)}s">
          <ellipse cx="${sx}" cy="${sy}" rx="${r * 1.9}" ry="${r * 0.72}" fill="none" class="sc-orbit-line"/>
        </g>`);
      }
      out.push(`<path class="sc-star-body" d="${starPath(sx, sy, r, isOrb ? 4 : 6, isOrb ? 0.42 : 0.36, isOrb ? 0 : 12)}"/>`);
      out.push(`<path class="sc-star-inner" d="${starPath(sx, sy, r * (isOrb ? 0.4 : 0.5), isOrb ? 4 : 6, 0.38, isOrb ? 0 : 12)}"/>`);
      return `<g class="sc-guide-star">${out.join('')}</g>`;
    }

    // galaxy：三条倾斜轨道 + 沿轨道的星点 + 亮核，像一只手托着的星系
    out.push(`<circle class="sc-star-glow" cx="${sx}" cy="${sy}" r="58" fill="url(#${uid}-star-glow)"/>`);
    // 星系的盘面：一团扁椭圆，让「这是一个有形状的星系」立得住
    out.push(`<ellipse class="sc-galaxy-disc" cx="${sx}" cy="${sy}" rx="30" ry="11"
      transform="rotate(-16 ${sx} ${sy})" fill="url(#${uid}-galaxy)"/>`);
    const orbits = [[24, 8.6, -16], [31, 11, 22], [18, 6.4, 62]];
    orbits.forEach(([rx, ry, rot], i) => {
      out.push(`<g class="sc-star-orbit" style="--sc-spin-dur:${r1(16 + i * 6)}s;--sc-spin-from:${rot}deg;--sc-spin-to:${rot + 360}deg">
        <ellipse cx="${sx}" cy="${sy}" rx="${rx}" ry="${ry}" fill="none" class="sc-orbit-line"/>
        <circle class="sc-orbit-body" cx="${r1(sx + rx)}" cy="${sy}" r="${r1(1.7 + i * 0.4)}"/>
      </g>`);
    });
    out.push(`<circle class="sc-galaxy-core" cx="${sx}" cy="${sy}" r="4.6"/>`);
    out.push(`<circle class="sc-galaxy-ring" cx="${sx}" cy="${sy}" r="12"/>`);
    return `<g class="sc-guide-star">${out.join('')}</g>`;
  }

  // ── 周天星斗：环绕整尊法相的轨道星体 ─────────────────────
  function orbiters(art, rand) {
    const count = art.orbit || 0;
    if (!count) return '';
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const rx = 128 + i * 26;
      const ry = rx * pick(rand, 0.2, 0.34);
      const tilt = pick(rand, -34, 34);
      const dur = 26 + i * 12 + rand() * 8;
      const phase = pick(rand, 0, 360);
      out.push(`<g class="sc-orbiter" style="--sc-spin-dur:${r1(dur)}s;--sc-spin-from:${Math.round(tilt + phase)}deg;--sc-spin-to:${Math.round(tilt + phase + 360)}deg">
        <ellipse cx="${CX}" cy="${HALO_CY}" rx="${r1(rx)}" ry="${r1(ry)}" fill="none" class="sc-orbiter-path"/>
        <circle class="sc-orbiter-body" cx="${r1(CX + rx)}" cy="${HALO_CY}" r="${r1(2 + i * 0.7)}"/>
      </g>`);
    }
    return `<g class="sc-orbiters">${out.join('')}</g>`;
  }

  // ── 悬浮碎片：高境才有，画成棱形而不是圆点，才有「科技」味 ──
  function shards(art, rand) {
    const count = art.shards || 0;
    if (!count) return '';
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const a = rand() * 360;
      const radius = pick(rand, 108, 182) * (art.tier >= 9 ? 1.18 : 1);
      const [x, y] = polar(CX, HALO_CY, radius, a);
      const size = pick(rand, 3.2, 7.4);
      out.push(`<path class="sc-shard" style="--sc-dur:${r1(pick(rand, 6, 13))}s;--sc-delay:${r1(rand() * 9)}s"
        d="M${x} ${r1(y - size)} L${r1(x + size * 0.5)} ${y} L${x} ${r1(y + size)} L${r1(x - size * 0.5)} ${y} Z"/>`);
    }
    return `<g class="sc-shards">${out.join('')}</g>`;
  }

  // ── 地轮：脚下的法阵投影 ────────────────────────────────
  // 有它，法相才是「站在自己的法阵上」；没有它，人像浮在半空的贴纸。
  // 层数跟着法阵环数走，所以低境脚下是干净的一圈，高境是一叠转盘。
  function groundDisc(art, m, uid, rand) {
    const count = Math.min(4, art.rings || 0);
    if (!count) return '';
    const cy = r1(m.hemY + 16);
    const rx = r1(m.hemW * (1.46 + count * 0.13));
    const ry = r1(rx * 0.25);
    const out = [`<ellipse class="sc-ground-glow" cx="${CX}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#${uid}-ground)"/>`];
    for (let i = 0; i < count; i += 1) {
      const k = 1 - i * 0.17;
      const gap = Math.round(pick(rand, 30, 90));
      out.push(`<ellipse class="sc-ground-ring" style="--sc-delay:${r1(i * 0.6)}s"
        cx="${CX}" cy="${cy}" rx="${r1(rx * k)}" ry="${r1(ry * k)}"
        stroke-dasharray="${r1(180 - gap)} ${gap}" stroke-dashoffset="${Math.round(pick(rand, 0, 60))}"/>`);
    }
    // 轮上的刻度：只画左右两侧各几根，中间留白（人站的地方不该有刻度）
    const ticks = [];
    for (let i = 0; i < 14; i += 1) {
      const a = (i / 14) * Math.PI * 2;
      const [x1, y1] = [CX + Math.cos(a) * rx * 0.94, cy + Math.sin(a) * ry * 0.94];
      const [x2, y2] = [CX + Math.cos(a) * rx * 1.04, cy + Math.sin(a) * ry * 1.04];
      if (Math.abs(y1 - cy) < ry * 0.42) continue;
      ticks.push(`<path class="sc-ground-tick" d="M${r1(x1)} ${r1(y1)} L${r1(x2)} ${r1(y2)}"/>`);
    }
    out.push(`<g class="sc-ground-ticks">${ticks.join('')}</g>`);
    return `<g class="sc-ground">${out.join('')}</g>`;
  }

  // ── 法纹：袍面上的纹路，境界越高越密 ────────────────────
  // 中间境界最缺的就是这个：只有一件素袍加一条腰带，看起来就是「简陋」。
  // 纹路不追求复杂，只要求**对称且有节奏**——对称的纹样才像法袍。
  function robeMarks(art, m, rand) {
    const count = art.plates || 0;
    if (!count) return '';
    const out = [];
    const rows = Math.min(5, count + 1);
    const span = Math.max(1, m.hemY - m.waistY - 30);
    for (let i = 0; i < rows; i += 1) {
      const y = r1(m.waistY + 22 + (i / rows) * span);
      const half = m.waistW + (m.hemW - m.waistW) * ((y - m.waistY) / Math.max(1, m.hemY - m.waistY));
      [-1, 1].forEach((side) => {
        const x1 = CX + side * half * 0.16;
        const x2 = CX + side * half * 0.62;
        const x3 = CX + side * half * 0.86;
        out.push(`<path class="sc-robe-mark" d="M${r1(x1)} ${y} Q${r1(x2)} ${r1(y + 7)} ${r1(x3)} ${r1(y - 5)}"/>`);
      });
      if (i % 2 === 0) {
        out.push(`<circle class="sc-robe-dot" cx="${CX}" cy="${y}" r="1.5"/>`);
      }
    }
    // 袍角的一圈光点：把下摆「收边」，不然袍摆会显得像一块布
    for (let i = 0; i < 7; i += 1) {
      const t = i / 6;
      const x = r1(CX - m.hemW + t * m.hemW * 2);
      out.push(`<circle class="sc-robe-dot" style="--sc-delay:${r1(i * 0.4)}s" cx="${x}" cy="${r1(m.hemY - 6 - Math.sin(t * Math.PI) * 6)}" r="1.7"/>`);
    }
    return `<g class="sc-robe">${out.join('')}</g>`;
  }

  // ── 丹田星核（金丹）──────────────────────────────────────
  // 「结丹」是这条修行线上辨识度最高的一步，所以这一颗东西必须**立得住**：
  // 上一版是两个圆（一个底色圆 + 一个白点），放大一看就是个灯泡。
  //
  // 现在按一颗真正的发光球体来搭，由外到内七层：
  //
  //   ① 外层辉光   光要"溢出"躯干——所以这一层不被身体裁切，
  //                否则看起来只是胸口贴了个亮片，而不是体内在烧
  //   ② 日冕       更暖更亮的一圈，与①错开呼吸
  //   ③ 吸积盘     倾斜的椭圆环，**前后两半分开画**：后半压在球后、
  //                前半压在球前。这是"立体"最省事也最有效的一招
  //   ④ 能量丝     几条绕核旋进的弧线，转速与方向各不相同——
  //                同一个速度转所有东西，会立刻显出"这是个贴图"
  //   ⑤ 球体       菲涅尔：中心最亮、边缘转深、最外一圈又亮回来（临边增亮），
  //                有这三段，平面圆才会被读成球
  //   ⑥ 丹纹       球面上两道缓慢自转的弧，金丹的"丹"字就落在这里
  //   ⑦ 脉冲/伴星  向外扩散的脉冲环 + 带拖尾的绕行小星
  //
  // 参数不够的境界直接不画——低境该朴素，特效堆早了就没有「长大」的感觉。
  function arcPath(cx, cy, r0, r1v, a0, a1, squash, steps) {
    const n = steps || 18;
    let d = '';
    for (let i = 0; i <= n; i += 1) {
      const t = i / n;
      const a = ((a0 + (a1 - a0) * t) * Math.PI) / 180;
      const rr = r0 + (r1v - r0) * t;
      d += `${i ? ' L' : 'M'}${r1(cx + Math.cos(a) * rr)} ${r1(cy + Math.sin(a) * rr * squash)}`;
    }
    return d;
  }

  function coreStar(art, m, uid, rand, body, rich) {
    const has = (art.orbit || 0) >= 1 || (art.rings || 0) >= 2;
    if (!has) return '';
    const cy = r1((m.shoulderY + m.waistY) / 2 + 4);
    const r = (art.form === 'child' ? 9.5 : 11.5) + Math.min(7, (art.halo || 0) * 1.7);
    const tier = art.tier || 0;

    // ① + ② 辉光与日冕（不裁切）
    const bloom = `
      <circle class="sc-core-bloom" cx="${CX}" cy="${cy}" r="${r1(r * 6.2)}" fill="url(#${uid}-bloom)"/>
      <circle class="sc-core-corona" cx="${CX}" cy="${cy}" r="${r1(r * 3.3)}" fill="url(#${uid}-corona)"/>`;

    // ③ 吸积盘：前后两半分开画
    const rx = r1(r * 2.5);
    const ry = r1(r * 0.66);
    const tilt = Math.round(pick(rand, -26, -12));
    const disc = rich ? `
      <g class="sc-core-disc" transform="rotate(${tilt} ${CX} ${cy})">
        <path class="sc-core-disc-back" d="M${r1(CX - rx)} ${cy} A${rx} ${ry} 0 0 1 ${r1(CX + rx)} ${cy}"/>
        <path class="sc-core-disc-front" d="M${r1(CX - rx)} ${cy} A${rx} ${ry} 0 0 0 ${r1(CX + rx)} ${cy}"/>
      </g>` : '';

    // ④ 能量丝：绕核旋进的弧线，转速/方向/相位都错开
    const filCount = rich ? Math.min(6, 3 + Math.round(tier / 2)) : 0;
    const filaments = Array.from({ length: filCount }, (_, i) => {
      const a0 = pick(rand, 0, 360);
      const span = pick(rand, 110, 240);
      const rr = r * pick(rand, 1.35, 2.5);
      const squash = pick(rand, 0.34, 0.82);
      const dur = r1(pick(rand, 5, 13));
      const back = i % 2 === 1;
      return `<path class="sc-core-fil${back ? ' is-back' : ''}"
        style="--sc-spin-dur:${dur}s;--sc-spin-from:${a0}deg;--sc-spin-to:${a0 + 360}deg"
        d="${arcPath(CX, cy, rr * 0.72, rr, 0, span, squash)}"/>`;
    }).join('');

    // ⑤⑥ 球体：菲涅尔三段 + 丹纹 + 高光（被躯干裁切 → 看起来在体内）
    const orb = `
      <circle class="sc-core-orb" cx="${CX}" cy="${cy}" r="${r1(r)}" fill="url(#${uid}-orb)"/>
      <circle class="sc-core-limb" cx="${CX}" cy="${cy}" r="${r1(r * 0.965)}" fill="none"/>
      ${rich ? `<g class="sc-core-swirl" style="--sc-spin-dur:${r1(pick(rand, 14, 26))}s">
        <path d="${arcPath(CX, cy, r * 0.12, r * 0.86, -150, 60, 0.78)}"/>
        <path d="${arcPath(CX, cy, r * 0.2, r * 0.8, 40, 220, 0.62)}"/>
      </g>` : ''}
      <circle class="sc-core-hot" cx="${r1(CX - r * 0.1)}" cy="${r1(cy - r * 0.12)}" r="${r1(r * 0.42)}" fill="url(#${uid}-hot)"/>`;

    // 星芒：只在够高的境界出现，是"它比别的核更盛"的直接信号
    const flare = rich && tier >= 4 ? [0, 45, 90, 135].map((a, i) => {
      const len = r * (i % 2 === 0 ? 4.4 : 2.9);
      const [x1, y1] = [CX + Math.cos((a * Math.PI) / 180) * len, cy + Math.sin((a * Math.PI) / 180) * len];
      const [x2, y2] = [CX - Math.cos((a * Math.PI) / 180) * len, cy - Math.sin((a * Math.PI) / 180) * len];
      return `<path class="sc-core-ray" style="--sc-delay:${r1(i * 0.7)}s" d="M${r1(x1)} ${r1(y1)} L${r1(x2)} ${r1(y2)}"/>`;
    }).join('') : '';

    // ⑦ 脉冲环：向外扩散。"它在跳"的证据，缺了它这颗核就只是块石头
    const pulses = [0, 1.1, 2.2].map((delay) =>
      `<circle class="sc-core-pulse" style="--sc-delay:${r1(delay)}s" cx="${CX}" cy="${cy}" r="${r1(r)}"/>`).join('');

    // 绕行小星：数量跟着 orbit 走（金丹 2 颗 → 仙人 4 颗），
    // 一近一远、转速不同，并且带一小段拖尾
    const satCount = 1 + Math.min(3, art.orbit || 1);
    const satellites = Array.from({ length: satCount }, (_, i) => {
      const srx = r1(r * (2.0 + i * 1.35));
      const dur = r1(9 + i * 7 + rand() * 4);
      const t0 = Math.round(pick(rand, -28, 28) + i * 60);
      const sr = r1(1.5 + i * 0.7);
      return `<g class="sc-core-sat" style="--sc-spin-dur:${dur}s;--sc-spin-from:${t0}deg;--sc-spin-to:${t0 + 360}deg">
        ${rich ? `<path class="sc-core-sat-tail" d="M${r1(CX + srx - sr * 7)} ${cy} A${r1(srx)} ${r1(srx * 0.42)} 0 0 1 ${r1(CX + srx)} ${cy}"/>` : ''}
        <circle class="sc-core-sat-body" cx="${r1(CX + srx)}" cy="${cy}" r="${sr}"/>
      </g>`;
    }).join('');

    // 旋转类元素统一以"核心"为轴：--sc-core-cy 交给 CSS 的 transform-origin 用。
    // （不能用 transform-box:fill-box + origin:center —— 一段弧、一颗小星的
    //   包围盒中心就是它自己，绕着它转等于原地打转，看起来像动画没生效。）
    return `<g class="sc-core" style="--sc-core-cy:${cy}px">
      ${bloom}
      ${pulses}
      ${disc}
      ${filaments}
      <g clip-path="url(#${uid}-coreclip)">${orb}</g>
      ${flare}
      ${satellites}
    </g>`;
  }

  // ── 灵气上升：贴身的一小簇火星，缓慢上浮 ──────────────────
  // 和 motes 分开画：motes 是「浮在身边的星尘」，这一簇是「从身上升起来的气」，
  // 方向单一（向上）、速度更慢，眼睛才会读出「在烧」的感觉。
  function risingSparks(art, m, rand) {
    const count = Math.min(12, Math.round((art.particles || 0) / 4));
    if (!count) return '';
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const x = r1(CX + pick(rand, -m.shoulderW * 1.5, m.shoulderW * 1.5));
      const y = r1(m.waistY + pick(rand, 0, 120));
      out.push(`<circle class="sc-spark" cx="${x}" cy="${y}" r="${r1(pick(rand, 1, 2.2))}"
        style="--sc-dur:${r1(pick(rand, 6, 12))}s;--sc-delay:${r1(rand() * 8)}s;--sc-rise:${r1(pick(rand, 60, 130))}px"/>`);
    }
    return `<g class="sc-sparks">${out.join('')}</g>`;
  }

  // ── 灵光粒子：绕体漂浮，数量与境界挂钩 ──────────────────
  function motes(art, rand) {
    // 上限 44：再多就该交给背景星海去画了，SVG 里每个粒子都是一个要合成动画的元素
    const count = Math.min(44, art.particles || 0);
    const inner = Math.round(count * 0.34);   // 贴着身子的近粒子
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const a = rand() * 360;
      // 分近/远两簇而不是均匀铺在一个圆环上：均匀铺出来是一圈规整的甜甜圈，
      // 看起来像装饰模板，不像「浮在身边的星尘」。
      const radius = i < inner ? pick(rand, 46, 92) : pick(rand, 104, 218);
      const [x, y] = polar(CX, HALO_CY, radius, a);
      out.push(`<circle class="sc-mote" cx="${x}" cy="${r1(y + pick(rand, -12, 12))}" r="${r1(pick(rand, 1, 2.7))}"
        style="--sc-dur:${r1(pick(rand, 5, 12))}s;--sc-delay:${r1(rand() * 8)}s"/>`);
    }
    return `<g class="sc-motes">${out.join('')}</g>`;
  }

  // ── 法阵 ────────────────────────────────────────────────
  // 一层法阵 = 一圈缺口环 + 刻度；奇数层反向旋转（偶数层顺时针）。
  // 这一叠是「修仙」最容易被认出来的符号，所以放在最底层、半径最大。
  function rings(art, uid, rand) {
    const count = art.rings || 0;
    if (!count) return '';
    const out = [];
    for (let i = 0; i < count; i += 1) {
      const radius = 118 + i * 20;
      const gap = pick(rand, 26, 74);
      const off = pick(rand, 0, 360);
      const tilt = pick(rand, -20, 20);
      const dur = r1(30 + i * 8 + rand() * 12);
      const reverse = i % 2 === 1;
      out.push(`<g class="sc-ring" style="--sc-spin-dur:${dur}s;--sc-spin-from:${Math.round(tilt)}deg;--sc-spin-to:${Math.round(reverse ? tilt - 360 : tilt + 360)}deg">
        <circle cx="${CX}" cy="${HALO_CY}" r="${r1(radius)}" fill="none"
          stroke="url(#${uid}-ring)" stroke-width="${i === 0 ? 1.5 : 1}" opacity="${r1(0.6 - i * 0.05)}" ${gapRing(radius, gap, off)}/>
        ${i < 3 ? ticks(CX, HALO_CY, radius, 12 + i * 6, 5 + i, 'sc-tick') : ''}
      </g>`);
    }
    return `<g class="sc-rings">${out.join('')}</g>`;
  }

  // ── 背光 ────────────────────────────────────────────────
  function halo(art, uid) {
    const layers = art.halo || 0;
    const out = [`<ellipse class="sc-glow" cx="${CX}" cy="${HALO_CY}" rx="186" ry="220" fill="url(#${uid}-halo)"/>`];
    for (let i = 0; i < Math.min(layers, 4); i += 1) {
      const radius = 100 + i * 21;
      out.push(`<circle class="sc-halo-ring" cx="${CX}" cy="${HALO_CY}" r="${radius}" fill="none"
        stroke="url(#${uid}-ring)" stroke-width="0.9" opacity="${r1(0.36 - i * 0.06)}"
        ${gapRing(radius, 60 + i * 30, i * 40)}/>`);
    }
    if (art.sun) {
      // 日轮：只有仙人境·金仙这一尊有。一圈亮盘 + 32 道光芒，
      // 让「满级」和「差一级」在缩略图尺寸下也能一眼分辨。
      out.push(`<circle class="sc-sun-disc" cx="${CX}" cy="${HALO_CY}" r="118" fill="url(#${uid}-sun)"/>`);
      const rays = [];
      for (let i = 0; i < 32; i += 1) {
        const a = (i / 32) * 360;
        const len = i % 2 === 0 ? 74 : 40;
        const [x1, y1] = polar(CX, HALO_CY, 122, a);
        const [x2, y2] = polar(CX, HALO_CY, 122 + len, a);
        rays.push(`<path d="M${x1} ${y1} L${x2} ${y2}"/>`);
      }
      out.push(`<g class="sc-sun-rays">${rays.join('')}</g>`);
    }
    if (layers >= 3) {
      // 光芒：24 道长短交替的放射线。神仙感最直接的一招，也是最便宜的一招。
      const rays = [];
      for (let i = 0; i < 24; i += 1) {
        const a = (i / 24) * 360;
        const long = i % 2 === 0;
        const [x1, y1] = polar(CX, HALO_CY, 148, a);
        const [x2, y2] = polar(CX, HALO_CY, 148 + (long ? 48 : 25), a);
        rays.push(`<path d="M${x1} ${y1} L${x2} ${y2}"/>`);
      }
      out.push(`<g class="sc-rays">${rays.join('')}</g>`);
    }
    return `<g class="sc-halo">${out.join('')}</g>`;
  }

  // ── 科技元素：金仙那一档才出现的「非修仙」语汇 ───────────
  // 一块悬浮的全息拓片：网格 + 三条数据线 + 几个光点。
  // 放在左手边，和右手的星系形成左右平衡——一个给「科技」，一个给「仙」。
  function holoPanel(art, m) {
    if (art.tier < 8) return '';
    const w = art.tier >= 10 ? 76 : 64;
    const h = art.tier >= 10 ? 96 : 78;
    const x = CX - m.shoulderW - w - 6;
    const y = m.shoulderY + 18;
    const lines = [];
    for (let i = 1; i < 4; i += 1) {
      lines.push(`<path d="M${r1(x + 6)} ${r1(y + (h / 4) * i)} L${r1(x + w - 6)} ${r1(y + (h / 4) * i)}"/>`);
    }
    const bars = [0.42, 0.68, 0.9, 0.55].map((ratio, i) =>
      `<path class="sc-holo-bar" style="--sc-bar-delay:${r1(i * 0.7)}s"
        d="M${r1(x + 13 + i * 14)} ${r1(y + h - 12)} L${r1(x + 13 + i * 14)} ${r1(y + h - 12 - (h - 32) * ratio)}"/>`).join('');
    return `<g class="sc-holo">
      <rect x="${r1(x)}" y="${r1(y)}" width="${r1(w)}" height="${r1(h)}" rx="5" class="sc-holo-frame"/>
      <g class="sc-holo-grid">${lines.join('')}</g>
      <g class="sc-holo-bars">${bars}</g>
      ${[[0.2, 0.2], [0.8, 0.3], [0.35, 0.75]].map(([px, py]) =>
        `<circle class="sc-holo-dot" cx="${r1(x + w * px)}" cy="${r1(y + h * py)}" r="1.7"/>`).join('')}
    </g>`;
  }

  // ── 主体 ────────────────────────────────────────────────
  function render(options) {
    const opts = options || {};
    const art = Object.assign({
      form: 'child', tier: 0, primary: '#8fa3b8', deep: '#26313d', aura: '#dce8f4', accent: '#7ee1ff',
      eye: 'dot', halo: 0, rings: 0, crest: 0, cape: 0, ribbon: 0,
      plates: 0, orbit: 0, shards: 0, particles: 8, star: 'orb',
      name: '星尘童儿', title: '', whisper: '', realm: '凡尘', level: 0,
    }, opts.art || {});

    const seed = `${opts.seed || 'guest'}|${art.realm}|${art.level}`;
    const rand = rngFrom(seed);
    const uid = `sc${(hashSeed(seed) % 100000).toString(36)}`;
    const m = measure(art.form);
    // 图鉴一次要画十一尊，缩略图尺寸下那些能量丝/吸积盘根本看不出，
    // 却会各带一份 CSS 动画。所以缩略图走简版，大图才上全套。
    const rich = opts.rich !== false;
    const limb = sleevesAndHands(art, m);
    const body = torsoPath(m);
    const parts = [];

    // ① 背光 + 法阵（最底层，一切都被它托着）
    parts.push(halo(art, uid));
    parts.push(rings(art, uid, rand));
    parts.push(groundDisc(art, m, uid, rand));
    parts.push(orbiters(art, rand));

    // ② 后面的东西：碎星、披风、飘带、大袖
    parts.push(shards(art, rand));
    parts.push(cape(art, m, rand));
    parts.push(ribbons(art, m));
    parts.push(`<g class="sc-sleeves">${limb.sleeves.join('')}</g>`);

    // ③ 身体：暗底 + 上缘的灵光 + 一条边缘轮廓光
    parts.push(`<path class="sc-body" d="${body}" fill="url(#${uid}-body)"/>`);
    parts.push(`<path class="sc-body-top" d="${body}" fill="url(#${uid}-body-top)"/>`);
    parts.push(`<path class="sc-body-rim" d="${body}" fill="none" stroke="url(#${uid}-rim)" stroke-width="2"/>`);

    // ④ 前臂与手：只露袖口下面那一点点，裸臂整条画出来会很难看
    parts.push(`<g class="sc-arms">
      ${limb.arms.join('')}
      ${limb.hands.map(([x, y, r]) => `<circle class="sc-hand" cx="${x}" cy="${y}" r="${r}"/>`).join('')}
    </g>`);

    // ⑤ 胸甲与灵脉（裁进身体里）
    parts.push(`<g class="sc-inner" clip-path="url(#${uid}-clip)">${plates(art, m, rand)}</g>`);
    parts.push(`<g class="sc-inner" clip-path="url(#${uid}-clip)">${robeMarks(art, m, rand)}</g>`);
    if (art.tier >= 5) {
      parts.push(`<path class="sc-dissolve" d="${body}" fill="url(#${uid}-dissolve)"/>`);
    }

    // ⑤b 丹田星核：金丹期起才有。核心那几层压在胸甲之上、身体之内，
    //     所以它看起来是「身体里在发光」；但外层辉光故意**不裁切**，
    //     光要能溢出躯干，否则胸口那个亮斑会像贴上去的。
    parts.push(coreStar(art, m, uid, rand, body, rich));

    // ⑥ 头、面甲、脸、冠
    parts.push(`<circle class="sc-head-shape" cx="${CX}" cy="${m.headY}" r="${m.headR}" fill="url(#${uid}-head)"/>`);
    parts.push(helm(art, m));
    parts.push(`<circle class="sc-head-rim" cx="${CX}" cy="${m.headY}" r="${m.headR}" fill="none"
      stroke="url(#${uid}-rim)" stroke-width="1.5"/>`);
    parts.push(face(art, m, uid));
    parts.push(crown(art, m));

    // ⑦ 引路星 + 全息拓片（最前面，焦距最近）
    parts.push(guideStar(art, m, uid, rand));
    parts.push(holoPanel(art, m));

    // ⑧ 灵光粒子 + 上升的灵气
    parts.push(risingSparks(art, m, rand));
    parts.push(motes(art, rand));

    // ⑨ 取景角标：让这张图看起来像一枚「法相拓印」，而不是随便一张插画
    const corners = [[30, 44, 1, 1], [290, 44, -1, 1], [30, FLOOR - 34, 1, -1], [290, FLOOR - 34, -1, -1]]
      .map(([x, y, sx, sy]) => `<path d="M${x} ${y + sy * 20} L${x} ${y} L${x + sx * 20} ${y}"/>`).join('');
    parts.push(`<g class="sc-frame">${corners}</g>`);

    const cls = ['sc-figure', opts.className || ''].filter(Boolean).join(' ');
    return `<svg class="${cls}" viewBox="0 0 320 ${FLOOR}" width="${opts.width || '100%'}"
      ${opts.height ? `height="${opts.height}"` : ''} role="img"
      aria-label="${esc(opts.label || art.name || '星辰教练法相')}" style="--sc-primary:${esc(art.primary)};--sc-aura:${esc(art.aura)};--sc-accent:${esc(art.accent || art.primary)};--sc-deep:${esc(art.deep)}">
      <defs>
        <radialGradient id="${uid}-halo" cx="50%" cy="44%" r="62%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.4"/>
          <stop offset="38%" stop-color="${esc(art.primary)}" stop-opacity="0.2"/>
          <stop offset="72%" stop-color="${esc(art.primary)}" stop-opacity="0.06"/>
          <stop offset="100%" stop-color="${esc(art.deep)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-star-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.95"/>
          <stop offset="26%" stop-color="${esc(art.aura)}" stop-opacity="0.5"/>
          <stop offset="62%" stop-color="${esc(art.primary)}" stop-opacity="0.2"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-sun" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.2"/>
          <stop offset="60%" stop-color="${esc(art.primary)}" stop-opacity="0.12"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-galaxy" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="${uid}-body" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${esc(art.deep)}" stop-opacity="0.62"/>
          <stop offset="30%" stop-color="#0a1119" stop-opacity="0.92"/>
          <stop offset="62%" stop-color="#060a13" stop-opacity="0.98"/>
          <stop offset="100%" stop-color="#04070d" stop-opacity="1"/>
        </linearGradient>
        <linearGradient id="${uid}-body-top" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.16"/>
          <stop offset="26%" stop-color="${esc(art.primary)}" stop-opacity="0.04"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </linearGradient>
        <linearGradient id="${uid}-head" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${esc(art.deep)}" stop-opacity="0.72"/>
          <stop offset="72%" stop-color="#0a1119" stop-opacity="0.96"/>
        </linearGradient>
        <linearGradient id="${uid}-rim" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="1"/>
          <stop offset="52%" stop-color="${esc(art.primary)}" stop-opacity="0.78"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0.12"/>
        </linearGradient>
        <linearGradient id="${uid}-ring" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.9"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0.3"/>
        </linearGradient>
        <linearGradient id="${uid}-visor" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.35"/>
          <stop offset="50%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="1"/>
          <stop offset="100%" stop-color="${esc(art.aura)}" stop-opacity="0.35"/>
        </linearGradient>
        <linearGradient id="${uid}-dissolve" x1="0" y1="0.5" x2="0" y2="1">
          <stop offset="0%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
          <stop offset="70%" stop-color="${esc(art.primary)}" stop-opacity="0.12"/>
          <stop offset="100%" stop-color="${esc(art.aura)}" stop-opacity="0.55"/>
        </linearGradient>
        <radialGradient id="${uid}-ground" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.primary)}" stop-opacity="0.3"/>
          <stop offset="60%" stop-color="${esc(art.primary)}" stop-opacity="0.1"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-core" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.85"/>
          <stop offset="34%" stop-color="${esc(art.primary)}" stop-opacity="0.4"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <!-- 丹田星核的七层用到的渐变。层次全靠它们分开：
             辉光/日冕给"存在感的范围"，orb 三段给"球"，hot 给"温度"。 -->
        <radialGradient id="${uid}-bloom" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.aura)}" stop-opacity="0.3"/>
          <stop offset="26%" stop-color="${esc(art.primary)}" stop-opacity="0.16"/>
          <stop offset="62%" stop-color="${esc(art.primary)}" stop-opacity="0.05"/>
          <stop offset="100%" stop-color="${esc(art.deep)}" stop-opacity="0"/>
        </radialGradient>
        <radialGradient id="${uid}-corona" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="0.6"/>
          <stop offset="22%" stop-color="${esc(art.aura)}" stop-opacity="0.34"/>
          <stop offset="58%" stop-color="${esc(art.primary)}" stop-opacity="0.14"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </radialGradient>
        <!-- 球体三段：高温心 → 主色 → 冷下来的边缘。中间那一段是"体积"的来源。 -->
        <radialGradient id="${uid}-orb" cx="46%" cy="44%" r="58%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
          <stop offset="26%" stop-color="${esc(art.aura)}" stop-opacity="1"/>
          <stop offset="56%" stop-color="${esc(art.primary)}" stop-opacity="0.96"/>
          <stop offset="84%" stop-color="${esc(art.deep)}" stop-opacity="0.92"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0.85"/>
        </radialGradient>
        <radialGradient id="${uid}-hot" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
          <stop offset="40%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="0.7"/>
          <stop offset="100%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="${uid}-disc" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
          <stop offset="50%" stop-color="${esc(art.accent || art.aura)}" stop-opacity="0.85"/>
          <stop offset="100%" stop-color="${esc(art.primary)}" stop-opacity="0"/>
        </linearGradient>
        <clipPath id="${uid}-clip"><path d="${body}"/></clipPath>
        <!-- 只裁球体那几层，不含辉光：光必须能溢出躯干 -->
        <clipPath id="${uid}-coreclip"><path d="${body}"/></clipPath>
      </defs>
      ${parts.join('')}
      <g class="sc-seed" data-seed="${esc(seed)}"></g>
    </svg>`;
  }

  // ── 对外 ────────────────────────────────────────────────
  window.StarCoach = {
    render,
    hashSeed,
    rngFrom,
    esc,
    starPath,
    SHAPES,
  };
})();
