/**
 * PyMaster 讲解配图 · 程序化作图引擎
 *
 * 用代码而不是第三方生图模型出图。核心收益不只是省钱：
 * 技术课件里大量出现中文关键词、代码、对照表，
 * 生成式模型画不出正确文字（常见乱码伪文字），而程序化作图可以精确排版。
 *
 * 每个镜头由分镜脚本给出一个 visual 规格，这里按 layout 渲染成 1080×1080 的课件图。
 */

// ── 设计规范 ────────────────────────────────────────────────
export const PALETTE = {
  paper: '#F7F1E4',
  paperDeep: '#EFE5D2',
  ink: '#2A2622',
  inkSoft: '#6B6154',
  inkFaint: '#9C9286',
  jade: '#2E6F68',
  jadeSoft: '#DCEBE7',
  orange: '#D9773F',
  orangeSoft: '#FAE6D6',
  gold: '#C0913C',
  goldSoft: '#F7EBD2',
  red: '#B94A38',
  redSoft: '#F6DEDA',
  cyan: '#2E8B9E',
  cyanSoft: '#DBEDF1',
  green: '#3E8E5A',
  greenSoft: '#DDEEDF',
  white: '#FFFFFF',
};

const ACCENT_BY_LAYOUT = {
  hook: { main: PALETTE.orange, soft: PALETTE.orangeSoft, label: '场景引入' },
  concept: { main: PALETTE.jade, soft: PALETTE.jadeSoft, label: '概念拆解' },
  code: { main: PALETTE.green, soft: PALETTE.greenSoft, label: '代码演示' },
  compare: { main: PALETTE.cyan, soft: PALETTE.cyanSoft, label: '对比辨析' },
  pitfall: { main: PALETTE.red, soft: PALETTE.redSoft, label: '常见坑' },
  summary: { main: PALETTE.gold, soft: PALETTE.goldSoft, label: '本节小结' },
  flow: { main: PALETTE.jade, soft: PALETTE.jadeSoft, label: '执行流程' },
};

// ── 吉祥物（纯 SVG，保证每张图形象完全一致）────────────────
// 蛇蛇老师：盘坐着的小绿蛇 + 圆框眼镜。用几何形体拼，避免手写复杂路径导致形变。
function mascotSnake(size = 220, mood = 'happy') {
  const pupil = mood === 'alert' ? 5.0 : 6.8;
  return `
<svg class="mascot mascot-snake" viewBox="0 0 240 220" width="${size}" height="${size * 220 / 240}" aria-hidden="true">
  <!-- 盘坐的底座 -->
  <ellipse cx="118" cy="184" rx="78" ry="25" fill="#48A468"/>
  <ellipse cx="118" cy="166" rx="66" ry="21" fill="#5CBB7C"/>
  <ellipse cx="118" cy="170" rx="46" ry="13" fill="none" stroke="#3B8B57" stroke-width="3" opacity=".45"/>
  <!-- 尾尖 -->
  <path d="M42 182 q-18 2 -22 14" fill="none" stroke="#48A468" stroke-width="15" stroke-linecap="round"/>
  <!-- 脖子 -->
  <path d="M150 168 C152 138 156 116 152 96" fill="none" stroke="#48A468" stroke-width="40" stroke-linecap="round"/>
  <path d="M150 168 C152 138 156 116 152 96" fill="none" stroke="#8FD9A4" stroke-width="13" stroke-linecap="round" opacity=".55"/>
  <!-- 头 -->
  <ellipse cx="150" cy="62" rx="50" ry="43" fill="#48A468"/>
  <ellipse cx="150" cy="76" rx="33" ry="25" fill="#8FD9A4" opacity=".45"/>
  <!-- 腮红 -->
  <ellipse cx="112" cy="80" rx="10" ry="6.6" fill="#F0A48F" opacity=".8"/>
  <ellipse cx="188" cy="80" rx="10" ry="6.6" fill="#F0A48F" opacity=".8"/>
  <!-- 圆框眼镜 -->
  <circle cx="133" cy="60" r="19.5" fill="#FFFFFF" stroke="#2A2622" stroke-width="3.8"/>
  <circle cx="167" cy="60" r="19.5" fill="#FFFFFF" stroke="#2A2622" stroke-width="3.8"/>
  <line x1="146" y1="58" x2="154" y2="58" stroke="#2A2622" stroke-width="3.8" stroke-linecap="round"/>
  <!-- 眼睛 -->
  <circle cx="133" cy="61" r="${pupil}" fill="#2A2622"/>
  <circle cx="167" cy="61" r="${pupil}" fill="#2A2622"/>
  <circle cx="135.4" cy="58" r="2.2" fill="#FFFFFF"/>
  <circle cx="169.4" cy="58" r="2.2" fill="#FFFFFF"/>
  <!-- 嘴 -->
  ${mood === 'alert'
      ? '<ellipse cx="150" cy="92" rx="7.5" ry="8.5" fill="#B94A38"/>'
      : '<path d="M139 88 Q150 99 161 88" fill="none" stroke="#2A2622" stroke-width="3.4" stroke-linecap="round"/>'}
</svg>`;
}

function mascotChick(size = 140) {
  return `
<svg class="mascot mascot-chick" viewBox="0 0 150 160" width="${size}" height="${size * 160 / 150}" aria-hidden="true">
  <ellipse cx="75" cy="98" rx="50" ry="46" fill="#F5CE45"/>
  <circle cx="75" cy="54" r="35" fill="#F5CE45"/>
  <path d="M66 22 q5 -17 15 -15 q-8 6 -6 15" fill="#F0A93B"/>
  <path d="M80 20 q8 -15 17 -12 q-9 6 -9 14" fill="#F0A93B"/>
  <ellipse cx="49" cy="64" rx="7.5" ry="5" fill="#F0A48F" opacity=".8"/>
  <ellipse cx="101" cy="64" rx="7.5" ry="5" fill="#F0A48F" opacity=".8"/>
  <circle cx="62" cy="52" r="5.4" fill="#2A2622"/>
  <circle cx="88" cy="52" r="5.4" fill="#2A2622"/>
  <circle cx="63.8" cy="50" r="1.9" fill="#FFFFFF"/>
  <circle cx="89.8" cy="50" r="1.9" fill="#FFFFFF"/>
  <path d="M66 66 q9 9 18 0 q-9 5 -18 0" fill="#E8862F"/>
  <ellipse cx="26" cy="100" rx="12" ry="21" fill="#EFC13C" transform="rotate(-14 26 100)"/>
  <ellipse cx="124" cy="100" rx="12" ry="21" fill="#EFC13C" transform="rotate(14 124 100)"/>
  <path d="M60 142 v10 M60 152 h-9 M60 152 h9" stroke="#E8862F" stroke-width="4.6" stroke-linecap="round" fill="none"/>
  <path d="M92 142 v10 M92 152 h-9 M92 152 h9" stroke="#E8862F" stroke-width="4.6" stroke-linecap="round" fill="none"/>
</svg>`;
}

// ── 基础样式 ────────────────────────────────────────────────
export function baseCss() {
  return `
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1080px; overflow: hidden; }
body {
  font-family: "Microsoft YaHei", "微软雅黑", "SimHei", "Noto Sans SC", sans-serif;
  background: ${PALETTE.paper};
  color: ${PALETTE.ink};
  -webkit-font-smoothing: antialiased;
}
.stage { position: relative; width: 1080px; height: 1080px; padding: 56px 60px 76px; display: flex; flex-direction: column; }
.grain {
  position: absolute; inset: 0; pointer-events: none; opacity: .5;
  background-image: radial-gradient(${PALETTE.paperDeep} 1.1px, transparent 1.1px);
  background-size: 26px 26px;
}
.halo {
  position: absolute; width: 620px; height: 620px; border-radius: 50%;
  right: -180px; top: -200px; filter: blur(6px); opacity: .5;
}

/* 顶部：类别胶囊 + 标题 */
.head { position: relative; z-index: 2; margin-bottom: 30px; }
.chip {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 9px 20px; border-radius: 999px;
  font-size: 25px; font-weight: 700; letter-spacing: .06em;
}
.chip-dot { width: 13px; height: 13px; border-radius: 50%; }
.title {
  margin-top: 22px; font-size: 62px; font-weight: 800; line-height: 1.16;
  letter-spacing: -.01em; max-width: 940px;
}
.subtitle { margin-top: 14px; font-size: 30px; color: ${PALETTE.inkSoft}; line-height: 1.4; font-weight: 500; }

/* 内容区 */
.body { position: relative; z-index: 2; flex: 1; min-height: 0; display: flex; flex-direction: column; justify-content: center; gap: 22px; }

/* 底部：课程条 */
.foot {
  position: absolute; left: 60px; right: 60px; bottom: 30px; z-index: 2;
  display: flex; align-items: center; justify-content: space-between;
  font-size: 22px; color: ${PALETTE.inkFaint}; border-top: 2px solid ${PALETTE.paperDeep}; padding-top: 16px;
}
.foot strong { color: ${PALETTE.inkSoft}; font-weight: 700; }
.foot .no { font-variant-numeric: tabular-nums; letter-spacing: .06em; }
`;
}

// ── 通用零件 ────────────────────────────────────────────────
function bulletRow(item, index, accent) {
  const text = typeof item === 'string' ? item : (item.text || '');
  const icon = typeof item === 'string' ? '' : (item.icon || '');
  return `
  <div class="bl">
    <span class="bl-idx" style="background:${accent.soft};color:${accent.main}">
      ${icon || index + 1}
    </span>
    <span class="bl-tx">${text}</span>
  </div>`;
}

/** 按最长行自动缩放字号：宁可字小一点，也不能把代码截断成错的 */
function fitFont(code, base = 28, areaWidth = 900, min = 17) {
  const longest = String(code || '').split('\n').reduce((max, line) => Math.max(max, line.length), 1);
  return Math.max(min, Math.min(base, Math.floor(areaWidth / (longest * 0.58))));
}

function codeBlock(code, accent, output) {
  const lines = highlightPython(code || '');
  const size = fitFont(code);
  const outHtml = (output || '').trim()
    ? `<div class="run">
         <div class="run-bar"><span class="run-dot"></span>运行结果</div>
         <pre class="run-out">${escapeHtml(output.trim())}</pre>
       </div>`
    : '';
  return `
  <div class="codecard">
    <div class="codecard-bar">
      <span class="tl" style="background:#E8867C"></span>
      <span class="tl" style="background:#E9C25E"></span>
      <span class="tl" style="background:#8CC48A"></span>
      <span class="codecard-name">example.py</span>
    </div>
    <pre class="code" style="font-size:${size}px">${lines}</pre>
  </div>${outHtml}`;
}

function escapeHtml(text) {
  return String(text == null ? '' : text)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

const PY_KEYWORDS = new Set(['def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while', 'in',
  'not', 'and', 'or', 'import', 'from', 'as', 'with', 'try', 'except', 'finally', 'raise',
  'lambda', 'yield', 'global', 'nonlocal', 'pass', 'break', 'continue', 'assert', 'del',
  'is', 'None', 'True', 'False', 'async', 'await']);
const PY_BUILTINS = new Set(['print', 'len', 'range', 'type', 'int', 'str', 'float', 'bool',
  'list', 'dict', 'set', 'tuple', 'sum', 'max', 'min', 'sorted', 'enumerate', 'zip',
  'input', 'isinstance', 'abs', 'round', 'open', 'id', 'repr', 'format', 'map', 'filter']);

/** 极简 Python 词法着色：关键字/字符串/注释/数字/内置函数 */
export function highlightPython(code) {
  const out = [];
  const lines = String(code || '').split('\n');
  for (const line of lines) {
    let html = '';
    let i = 0;
    while (i < line.length) {
      const ch = line[i];
      if (ch === '#') {
        html += `<span class="c-cm">${escapeHtml(line.slice(i))}</span>`;
        break;
      }
      if (ch === '"' || ch === "'") {
        const quote = ch;
        let j = i + 1;
        while (j < line.length && line[j] !== quote) {
          if (line[j] === '\\') j++;
          j++;
        }
        const raw = line.slice(i, Math.min(j + 1, line.length));
        html += `<span class="c-st">${escapeHtml(raw)}</span>`;
        i = j + 1;
        continue;
      }
      if (/[0-9]/.test(ch) && !/[A-Za-z_]/.test(line[i - 1] || '')) {
        let j = i;
        while (j < line.length && /[0-9._]/.test(line[j])) j++;
        html += `<span class="c-nu">${escapeHtml(line.slice(i, j))}</span>`;
        i = j;
        continue;
      }
      if (/[A-Za-z_]/.test(ch)) {
        let j = i;
        while (j < line.length && /[A-Za-z0-9_]/.test(line[j])) j++;
        const word = line.slice(i, j);
        const next = line[j];
        let cls = '';
        if (PY_KEYWORDS.has(word)) cls = 'c-kw';
        else if (PY_BUILTINS.has(word)) cls = 'c-bi';
        else if (next === '(') cls = 'c-fn';
        else if (/^[A-Z]/.test(word)) cls = 'c-cl';
        html += cls ? `<span class="${cls}">${word}</span>` : escapeHtml(word);
        i = j;
        continue;
      }
      html += escapeHtml(ch);
      i++;
    }
    out.push(html);
  }
  return out.join('\n');
}

// ── 各 layout ───────────────────────────────────────────────

function layoutHook(spec, accent) {
  const q = spec.question || spec.subtitle || '';
  return `
  <div class="body hook-body">
    <div class="bubble-wrap">
      <div class="bubble" style="border-color:${accent.main}">
        <div class="bubble-tip" style="background:${accent.main}"></div>
        <p class="bubble-tx">${escapeHtml(q)}</p>
      </div>
      <div class="hero">
        ${mascotSnake(330, spec.mood === 'alert' ? 'alert' : 'happy')}
        ${mascotChick(150)}
      </div>
    </div>
    ${(spec.bullets || []).length ? `<div class="bullets">${spec.bullets.map((b, i) => bulletRow(b, i, accent)).join('')}</div>` : ''}
  </div>`;
}

function layoutConcept(spec, accent) {
  const bullets = spec.bullets || [];
  // 4 条要点时右栏会被吉祥物挤到只剩七八个字宽，改成要点占满整幅、吉祥物退到角落
  const wide = bullets.length >= 4;
  return `
  <div class="body">
    <div class="concept-wrap ${wide ? 'is-wide' : ''}">
      <div class="concept-main">
        <div class="bullets">${bullets.map((b, i) => bulletRow(b, i, accent)).join('')}</div>
      </div>
      <div class="concept-side ${wide ? 'is-corner' : ''}">${mascotSnake(wide ? 250 : 335)}</div>
    </div>
    ${spec.highlight ? `<div class="ribbon" style="background:${accent.soft};border-color:${accent.main}">
        <span class="ribbon-k" style="color:${accent.main}">要点</span>
        <span class="ribbon-v">${escapeHtml(spec.highlight)}</span></div>` : ''}
  </div>`;
}

function layoutCode(spec, accent) {
  return `
  <div class="body">
    ${codeBlock(spec.code, accent, spec.output)}
    ${(spec.bullets || []).length ? `<div class="bullets tight">${spec.bullets.map((b, i) => bulletRow(b, i, accent)).join('')}</div>` : ''}
  </div>`;
}

function layoutCompare(spec, accent) {
  const side = (data, tone) => {
    const lines = data && data.lines ? data.lines : [];
    return `
    <div class="cmp-col" style="border-color:${tone.main};background:${tone.soft}">
      <div class="cmp-label" style="background:${tone.main}">${escapeHtml((data && data.label) || '')}</div>
      <ul class="cmp-list">
        ${lines.map((l) => `<li>${escapeHtml(l)}</li>`).join('')}
      </ul>
    </div>`;
  };
  return `
  <div class="body">
    <div class="cmp">
      ${side(spec.left, { main: accent.main, soft: accent.soft })}
      <div class="cmp-vs">VS</div>
      ${side(spec.right, { main: PALETTE.orange, soft: PALETTE.orangeSoft })}
    </div>
    ${spec.highlight ? `<div class="ribbon" style="background:${accent.soft};border-color:${accent.main}">
        <span class="ribbon-k" style="color:${accent.main}">结论</span>
        <span class="ribbon-v">${escapeHtml(spec.highlight)}</span></div>` : ''}
  </div>`;
}

function layoutPitfall(spec, accent) {
  const badSize = fitFont(spec.wrong_code, 26, 880);
  const goodSize = fitFont(spec.right_code, 26, 880);
  return `
  <div class="body">
    <div class="pit">
      <div class="pit-row bad">
        <div class="pit-tag" style="background:${PALETTE.red}">✕ 容易踩的坑</div>
        <div class="pit-tx">${escapeHtml(spec.wrong || '')}</div>
      </div>
      ${spec.wrong_code ? `<pre class="pit-code bad-code" style="font-size:${badSize}px">${highlightPython(spec.wrong_code)}</pre>` : ''}
      <div class="pit-row good">
        <div class="pit-tag" style="background:${PALETTE.green}">✓ 正确做法</div>
        <div class="pit-tx">${escapeHtml(spec.right_answer || '')}</div>
      </div>
      ${spec.right_code ? `<pre class="pit-code good-code" style="font-size:${goodSize}px">${highlightPython(spec.right_code)}</pre>` : ''}
    </div>
    ${spec.highlight ? `<div class="ribbon" style="background:${accent.soft};border-color:${accent.main}">
        <span class="ribbon-k" style="color:${accent.main}">记住</span>
        <span class="ribbon-v">${escapeHtml(spec.highlight)}</span></div>` : ''}
  </div>`;
}

function layoutSummary(spec, accent) {
  const items = spec.bullets || [];
  return `
  <div class="body">
    <div class="sum-wrap">
      <div class="sum-list">
        ${items.map((b, i) => {
          const text = typeof b === 'string' ? b : (b.text || '');
          return `<div class="sum-item" style="border-color:${accent.main}">
            <span class="sum-no" style="background:${accent.main}">${i + 1}</span>
            <span class="sum-tx">${escapeHtml(text)}</span>
          </div>`;
        }).join('')}
      </div>
      <div class="sum-side">${mascotSnake(220)}${mascotChick(120)}</div>
    </div>
  </div>`;
}

function layoutFlow(spec, accent) {
  const steps = spec.steps || (spec.bullets || []).map((b) => (typeof b === 'string' ? b : b.text));
  return `
  <div class="body">
    <div class="flow">
      ${steps.map((s, i) => `
        <div class="flow-node" style="border-color:${accent.main};background:${accent.soft}">
          <span class="flow-no" style="color:${accent.main}">${String(i + 1).padStart(2, '0')}</span>
          <span class="flow-tx">${escapeHtml(s)}</span>
        </div>
        ${i < steps.length - 1 ? `<div class="flow-arrow" style="color:${accent.main}">↓</div>` : ''}
      `).join('')}
    </div>
    ${spec.highlight ? `<div class="ribbon" style="background:${accent.soft};border-color:${accent.main}">
        <span class="ribbon-k" style="color:${accent.main}">关键</span>
        <span class="ribbon-v">${escapeHtml(spec.highlight)}</span></div>` : ''}
  </div>`;
}

const LAYOUTS = {
  hook: layoutHook,
  concept: layoutConcept,
  code: layoutCode,
  compare: layoutCompare,
  pitfall: layoutPitfall,
  summary: layoutSummary,
  flow: layoutFlow,
};

// ── 组装一张图 ──────────────────────────────────────────────
export function renderScene(visual, meta = {}) {
  const layoutKey = LAYOUTS[visual && visual.layout] ? visual.layout : 'concept';
  const accent = ACCENT_BY_LAYOUT[layoutKey] || ACCENT_BY_LAYOUT.concept;
  const body = LAYOUTS[layoutKey](visual || {}, accent);
  const title = escapeHtml(visual && visual.title ? visual.title : '');
  const subtitle = visual && visual.subtitle ? escapeHtml(visual.subtitle) : '';
  const chapter = escapeHtml(meta.chapterTitle || '');
  const no = meta.sceneNo ? `${String(meta.sceneNo).padStart(2, '0')} / ${String(meta.sceneTotal || 0).padStart(2, '0')}` : '';

  return `<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>${baseCss()}${sceneCss()}</style></head>
<body>
<div class="stage">
  <div class="grain"></div>
  <div class="halo" style="background:${accent.soft}"></div>
  <div class="head">
    <div class="chip" style="background:${accent.soft};color:${accent.main}">
      <span class="chip-dot" style="background:${accent.main}"></span>${accent.label}
    </div>
    ${title ? `<div class="title">${title}</div>` : ''}
    ${subtitle ? `<div class="subtitle">${subtitle}</div>` : ''}
  </div>
  ${body}
  <div class="foot">
    <span>🐍 <strong>PyMaster</strong> · ${chapter}</span>
    <span class="no">${no}</span>
  </div>
</div>
</body></html>`;
}

function sceneCss() {
  return `
/* 吉祥物 */
.mascot { display: block; }
.mascot-chick { margin-left: -26px; }

/* hook */
.hook-body { justify-content: center; gap: 34px; }
.bubble-wrap { position: relative; }
.bubble {
  position: relative; background: ${PALETTE.white}; border: 4px solid;
  border-radius: 30px; padding: 30px 38px; box-shadow: 0 12px 0 rgba(42,38,34,.06);
}
.bubble-tx { font-size: 40px; font-weight: 700; line-height: 1.45; }
.bubble-tip {
  position: absolute; left: 74px; bottom: -19px; width: 34px; height: 34px;
  transform: rotate(45deg); border-radius: 6px;
}
.hero { display: flex; align-items: flex-end; justify-content: center; margin-top: 44px; }

/* bullets */
.bullets { display: flex; flex-direction: column; gap: 26px; }
.bullets.cols-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 22px 26px; }
.bullets.tight { gap: 16px; margin-top: 6px; }
.bl { display: flex; align-items: center; gap: 18px; }
.bl-idx {
  flex: 0 0 auto; width: 60px; height: 60px; border-radius: 17px;
  display: flex; align-items: center; justify-content: center;
  font-size: 27px; font-weight: 800;
}
.bl-tx { font-size: 35px; font-weight: 650; line-height: 1.34; }

/* concept */
.concept-wrap { display: flex; align-items: center; gap: 30px; }
.concept-main { flex: 1; min-width: 0; }
.concept-side { flex: 0 0 auto; }
.concept-side.is-corner {
  position: absolute; right: 8px; bottom: -12px; opacity: .92; pointer-events: none;
}
.concept-wrap.is-wide .bl-tx { font-size: 34px; }

/* ribbon */
.ribbon {
  margin-top: 30px; display: flex; align-items: center; gap: 20px;
  border-left: 9px solid; border-radius: 16px; padding: 24px 28px;
}
.ribbon-k { font-size: 28px; font-weight: 800; letter-spacing: .08em; white-space: nowrap; }
.ribbon-v { font-size: 35px; font-weight: 700; line-height: 1.4; }

/* code */
.codecard { border-radius: 20px; overflow: hidden; background: #1B2130; box-shadow: 0 14px 34px rgba(27,33,48,.28); }
.codecard-bar { display: flex; align-items: center; gap: 10px; padding: 14px 20px; background: #232B3D; }
.tl { width: 15px; height: 15px; border-radius: 50%; }
.codecard-name { margin-left: 10px; font-size: 21px; color: #8895AE; font-family: Consolas, monospace; }
.code {
  padding: 26px 30px; font-family: Consolas, "Cascadia Code", monospace;
  font-size: 28px; line-height: 1.62; color: #D8E3F5; white-space: pre; overflow: hidden;
}
.c-kw { color: #FF9EC4; } .c-st { color: #A8E6A1; } .c-cm { color: #6E7C93; font-style: italic; }
.c-nu { color: #FFCB7A; } .c-bi { color: #7FD3FF; } .c-fn { color: #C9B6FF; } .c-cl { color: #FFD479; }

.run { margin-top: 22px; border-radius: 18px; overflow: hidden; border: 3px solid ${PALETTE.greenSoft}; }
.run-bar {
  display: flex; align-items: center; gap: 10px; padding: 12px 20px;
  background: ${PALETTE.greenSoft}; color: ${PALETTE.green}; font-size: 22px; font-weight: 800;
}
.run-dot { width: 12px; height: 12px; border-radius: 50%; background: ${PALETTE.green}; }
.run-out {
  padding: 20px 26px; background: ${PALETTE.white}; font-family: Consolas, monospace;
  font-size: 28px; line-height: 1.55; color: ${PALETTE.ink}; white-space: pre-wrap;
}

/* compare */
.cmp { display: grid; grid-template-columns: 1fr 96px 1fr; align-items: stretch; gap: 0; }
.cmp-col { border: 4px solid; border-radius: 22px; padding: 24px 24px 26px; }
.cmp-label {
  display: inline-block; color: #fff; font-size: 27px; font-weight: 800;
  padding: 8px 20px; border-radius: 999px; margin-bottom: 18px;
}
.cmp-list { list-style: none; display: flex; flex-direction: column; gap: 14px; }
.cmp-list li {
  font-size: 29px; font-weight: 600; line-height: 1.4; padding-left: 26px; position: relative;
}
.cmp-list li::before {
  content: ''; position: absolute; left: 0; top: 14px;
  width: 12px; height: 12px; border-radius: 3px; background: currentColor; opacity: .45;
}
.cmp-vs {
  display: flex; align-items: center; justify-content: center;
  font-size: 34px; font-weight: 900; color: ${PALETTE.inkFaint}; letter-spacing: .04em;
}

/* pitfall */
.pit { display: flex; flex-direction: column; gap: 16px; }
.pit-row { display: flex; align-items: flex-start; gap: 16px; }
.pit-tag {
  flex: 0 0 auto; color: #fff; font-size: 24px; font-weight: 800;
  padding: 9px 18px; border-radius: 12px; white-space: nowrap;
}
.pit-tx { font-size: 31px; font-weight: 600; line-height: 1.45; padding-top: 4px; }
.pit-code {
  margin: 0 0 6px 0; border-radius: 16px; padding: 20px 24px;
  font-family: Consolas, monospace; font-size: 26px; line-height: 1.55; white-space: pre;
  overflow: hidden;
}
.bad-code { background: #2A1D1D; color: #FFD9D2; border-left: 8px solid ${PALETTE.red}; }
.good-code { background: #1C2620; color: #D6F5DC; border-left: 8px solid ${PALETTE.green}; }

/* summary */
.sum-wrap { display: flex; align-items: center; gap: 30px; }
.sum-list { flex: 1; display: flex; flex-direction: column; gap: 22px; min-width: 0; }
.sum-item {
  display: flex; align-items: center; gap: 20px; background: ${PALETTE.white};
  border-left: 9px solid; border-radius: 16px; padding: 22px 24px;
  box-shadow: 0 8px 0 rgba(42,38,34,.05);
}
.sum-no {
  flex: 0 0 auto; width: 52px; height: 52px; border-radius: 50%; color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 27px; font-weight: 800;
}
.sum-tx { font-size: 31px; font-weight: 700; line-height: 1.4; }
.sum-side { flex: 0 0 auto; display: flex; align-items: flex-end; }

/* flow */
.flow { display: flex; flex-direction: column; align-items: stretch; gap: 6px; }
.flow-node {
  display: flex; align-items: center; gap: 20px; border: 4px solid;
  border-radius: 18px; padding: 22px 26px;
}
.flow-no { font-size: 30px; font-weight: 900; font-variant-numeric: tabular-nums; }
.flow-tx { font-size: 31px; font-weight: 650; line-height: 1.35; }
.flow-arrow { text-align: center; font-size: 30px; font-weight: 900; line-height: 1; }
`;
}
