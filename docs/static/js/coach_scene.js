/**
 * coach_scene.js — 把「星辰教练的法相」接进聊天页
 *
 * 分工：star_coach.js 只画那尊法相，starfield.js 只管背后那片星海，
 * 这个文件负责把两者接到页面上，以及三件用户能感觉到的事：
 *
 *   1. **能关。** 背景分三档：星海（满）→ 微光（默认）→ 纯净（全关）。
 *      默认取微光而不是星海，是因为这是个聊天页：正文必须始终是主角。
 *      选择记在 localStorage，下次进来还是你选的那档。
 *   2. **看得见解锁。** 每一次升境都会换一尊法相。进页面时如果发现法相变了，
 *      播一条「教练显化新身」的提示——这是升级最直接的反馈。
 *   3. **图鉴能翻。** 十一尊法相列出来，未到达的是灰的，点开能看它长什么样、
 *      第几境解锁、还差多少修为。看得见的目标才叫目标。
 *
 * 拿不到 /api/coach/forms 时整块静默降级（页面照常聊天），绝不弹错误。
 */
const CoachScene = {
  MODES: ['soft', 'full', 'off'],
  MODE_LABEL: {
    soft: { icon: '✦', text: '微光', hint: '背景：微光（点击切到星海）' },
    full: { icon: '✦', text: '星海', hint: '背景：星海（点击切到纯净）' },
    off: { icon: '◌', text: '纯净', hint: '背景：纯净（点击切到微光）' },
  },
  MODE_STORE: 'pymaster_coach_scene',
  SEEN_STORE: 'pymaster_coach_form_seen',

  data: null,
  field: null,
  mode: 'soft',
  figure: null,

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  },

  async mount() {
    this.mode = this.readMode();
    this.applyMode(this.mode, { silent: true });
    this.bindToggle();
    const data = await this.load();
    try {
      this.paint(data);
    } catch (error) {
      // 法相画不出来不影响聊天：静默降级，页面照常
    }
    // ?forms=1 直接摊开形象谱系：分享给别人看「教练会变成什么样」时用的深链
    try {
      if (new URLSearchParams(window.location.search).get('forms')) this.openGallery();
    } catch (e) { /* 老浏览器没有 URLSearchParams，忽略即可 */ }
    return data;
  },

  async load() {
    try {
      const response = await fetch('/api/coach/forms');
      const data = await response.json();
      this.data = data && data.success ? data : null;
    } catch (error) {
      this.data = null;
    }
    return this.data;
  },

  // ── 背景档位 ─────────────────────────────────────────
  /** ?scene=full / soft / off 直接定档，不进 localStorage。
   *  给「把这一屏发给别人看」和逐状态截图验收用：没有它就只能靠手点。 */
  readMode() {
    try {
      const forced = new URLSearchParams(window.location.search).get('scene');
      if (this.MODES.indexOf(forced) >= 0) return forced;
    } catch (e) { /* 老浏览器没有 URLSearchParams，接着读本地存的 */ }
    try {
      const saved = localStorage.getItem(this.MODE_STORE);
      if (this.MODES.indexOf(saved) >= 0) return saved;
    } catch (e) { /* 隐私模式下 localStorage 会抛，忽略 */ }
    // 第一次进来默认给星海档：这一页的卖点就是那片星空，
    // 上来先给最满的那一版，嫌吵的人自己点两下切到微光/纯净（选择会记住）。
    return 'full';
  },

  writeMode(mode) {
    try { localStorage.setItem(this.MODE_STORE, mode); } catch (e) { /* 存不了也无所谓 */ }
  },

  applyMode(mode, options) {
    const opts = options || {};
    this.mode = mode;
    document.body.dataset.scene = mode;
    const label = this.MODE_LABEL[mode] || this.MODE_LABEL.soft;
    const button = document.getElementById('coach-scene-toggle');
    if (button) {
      button.innerHTML = `<span class="scene-icon">${label.icon}</span>${label.text}`;
      button.title = label.hint;
      button.setAttribute('aria-label', label.hint);
    }
    if (this.field) this.field.setMode(mode);
    if (!opts.silent) this.writeMode(mode);
  },

  cycleModes() {
    const next = this.MODES[(this.MODES.indexOf(this.mode) + 1) % this.MODES.length];
    this.applyMode(next);
    this.writeMode(next);
    this.announce(next);
  },

  announce(mode) {
    const text = {
      soft: '背景切到微光版：星海淡入，正文最清楚',
      full: '背景切到星海版：满屏星辰与灵光粒子',
      off: '背景已关闭 · 纯净版，只剩对话本身',
    }[mode];
    if (text && window.Coach && Coach.toast) Coach.toast(text);
  },

  bindToggle() {
    const button = document.getElementById('coach-scene-toggle');
    if (button) button.addEventListener('click', () => this.cycleModes());
    const open = document.getElementById('coach-forms-open');
    if (open) open.addEventListener('click', () => this.openGallery());
    this.bindParallax();
  },

  /** 法相跟着指针轻微位移。
   *
   *  星海画布自己也在做视差，这里是让"人"和"天"用不同的系数动——
   *  两者一旦错开，法相就从"印在背景上的一张图"变成了"站在星海前面"。
   *  平滑交给 CSS 的 transition，不在 JS 里跑补间：少一个 rAF 循环。
   *  系统开了「减少动态效果」就整个不挂。 */
  bindParallax() {
    let reduce = false;
    try {
      reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) { reduce = false; }
    if (reduce) return;
    const figure = document.getElementById('coach-scene-figure');
    if (!figure) return;
    let pending = false;
    let nx = 0;
    let ny = 0;
    const apply = () => {
      pending = false;
      figure.style.transform = `translate3d(${nx.toFixed(1)}px, ${ny.toFixed(1)}px, 0)`;
    };
    window.addEventListener('pointermove', (event) => {
      // 法相在右边，所以它的位移方向与星海相反一点，纵深才立得住
      nx = -(event.clientX / Math.max(1, window.innerWidth) - 0.5) * 26;
      ny = -(event.clientY / Math.max(1, window.innerHeight) - 0.5) * 16;
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(apply);
    }, { passive: true });
  },

  // ── 上色 ─────────────────────────────────────────────
  // 拿不到后端数据时（在线演示站没有 /api/coach/forms）用的兜底：
  // 星海背景是纯前端的，不该跟着一起没了，所以给一份凡尘配色。
  FALLBACK_ART: {
    form: 'child', tier: 0, primary: '#8fa3b8', deep: '#26313d',
    aura: '#dce8f4', accent: '#7ee1ff',
  },

  paint(data) {
    const art = Object.assign({}, this.FALLBACK_ART, (data && data.art) || {});
    const canvas = document.getElementById('coach-scene-canvas');
    if (canvas && window.StarField) {
      // 星海是装饰，画不出来也得让聊天能用：这里一旦抛出去，
      // 会把同一次 DOMContentLoaded 里后面的等级条一起带崩（真实踩过）
      try {
        this.field = window.StarField.create(canvas, {
          mode: this.mode === 'off' ? 'off' : this.mode,
          primary: art.primary,
          deep: art.deep,
          accent: art.accent || art.aura,
        });
      } catch (error) {
        this.field = null;
      }
    }
    if (!data) {
      // 没有谱系数据（在线演示站 / 接口异常）：法相与图鉴的入口直接收起来，
      // 不给用户一个「点了没反应」的按钮
      this.withdrawFormsEntry();
      return;
    }
    this.paintBackgroundFigure(art, data);
    this.paintHeadAvatar(art);
    this.refreshHero();
    this.celebrate(data);
  },

  withdrawFormsEntry() {
    ['coach-forms-open', 'coach-hero-forms'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
  },

  /** 背影：整页背后那一尊。永远 pointer-events:none，绝不和聊天抢点击。 */
  paintBackgroundFigure(art, data) {
    const box = document.getElementById('coach-scene-figure');
    if (!box || !window.StarCoach) return;
    box.innerHTML = window.StarCoach.render({ art, seed: data.user, width: '100%' });
  },

  /** 顶栏那个小圆头像换成当前法相的印记，而不是永远一个「JJ」 */
  paintHeadAvatar(art) {
    const box = document.querySelector('.coach-avatar');
    if (!box || !window.StarCoach) return;
    const size = 30;
    box.classList.add('is-sigil');
    box.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 40 40" aria-hidden="true"
        style="--sc-primary:${this.esc(art.primary)};--sc-aura:${this.esc(art.aura)}">
      <circle cx="20" cy="20" r="18" fill="none" stroke="currentColor" stroke-width="1" opacity="0.35"/>
      <circle cx="20" cy="20" r="13.5" fill="none" stroke="currentColor" stroke-width="0.8" opacity="0.5"
        stroke-dasharray="${art.rings ? '88 12' : '110 0'}"/>
      <path d="${window.StarCoach.starPath(20, 20, 8.4 + Math.min(5, (art.crest || 0)) * 0.6, art.tier >= 4 ? 8 : 5, 0.42, 0)}"
        fill="currentColor" opacity="0.92"/>
      ${art.eye === 'dot' ? '<circle cx="16.4" cy="19.4" r="1.5" fill="#05070f"/><circle cx="23.6" cy="19.4" r="1.5" fill="#05070f"/>' : ''}
    </svg>`;
    box.style.color = art.primary;
  },

  refreshHero() {
    // 空态里那尊大法相由 coach.js 的 renderEmpty 生成，数据到齐后重画一次
    const inner = document.getElementById('thread-inner');
    if (!inner || !inner.querySelector('.coach-empty')) return;
    if (window.Coach && Coach.renderEmpty) Coach.renderEmpty();
  },

  /** 空态大图：交给 Coach.renderEmpty 用（它才知道什么时候该显示空态） */
  heroHtml() {
    const data = this.data;
    if (!data) return '';
    const art = data.art || {};
    const profile = data.profile || {};
    const next = data.next;
    const levelLine = profile.level > 0
      ? `第 ${profile.level} 境 · ${this.esc(profile.name || '')}`
      : '尚未入门 · 凡人';
    const unlockLine = next
      ? `再进 <b>${this.esc(next.realm)}</b>（第 ${next.unlock_level} 境）就换新形象，
         还差 <b>${Math.max(0, next.unlock_need - (profile.points || 0))}</b> 修为`
      : '你已走到最后一境，教练以金仙之身与你相对。';
    return `
      <div class="coach-hero">
        <div class="coach-hero-art">
          ${window.StarCoach ? window.StarCoach.render({
            art, seed: data.user, className: 'is-hero', label: art.name + ' 法相',
          }) : ''}
          <div class="hero-form-name" style="--sc-primary:${this.esc(art.primary)}">${this.esc(art.name || '')}</div>
          <button class="hero-forms-btn" id="coach-hero-forms">形象谱系 · 共 ${(data.forms || []).length} 尊</button>
        </div>
        <div class="coach-hero-txt">
          <div class="kicker">STAR COACH&nbsp;&nbsp;/&nbsp;&nbsp;${levelLine}</div>
          <h2>我是 JJ老师，你的星辰教练</h2>
          <div class="form-title" style="color:${this.esc(art.primary)}">${this.esc(art.title || '')}</div>
          <p class="form-whisper">${this.esc(art.whisper || '')}</p>
          <p>问我 Python 与 AI 的任何问题。我讲完一定会反问你一个问题——
             因为真正的理解，发生在你开口回答的那一刻。</p>
          <div class="unlock-line">${unlockLine}</div>
        </div>
      </div>`;
  },

  bindHero(root) {
    const button = (root || document).querySelector('#coach-hero-forms');
    if (button) button.addEventListener('click', () => this.openGallery());
  },

  // ── 形象谱系（图鉴）────────────────────────────────────
  openGallery(focusRealm) {
    const data = this.data;
    if (!data) {
      if (window.Coach && Coach.toast) Coach.toast('形象谱系还没加载出来，稍等一下');
      return;
    }
    const shell = this.galleryShell();
    this.renderGallery(focusRealm || (data.current && data.current.realm));
    shell.classList.add('show');
  },

  galleryShell() {
    let shell = document.getElementById('coach-gallery-shell');
    if (shell) return shell;
    shell = document.createElement('div');
    shell.id = 'coach-gallery-shell';
    shell.className = 'coach-gallery';
    shell.innerHTML = `
      <div class="gallery-box">
        <header class="gallery-head">
          <div>
            <h2>星辰教练 · 形象谱系</h2>
            <div class="gallery-sub" id="gallery-sub"></div>
          </div>
          <button class="gallery-close" id="gallery-close" title="关闭">×</button>
        </header>
        <div class="gallery-body">
          <div class="gallery-grid" id="gallery-grid"></div>
          <aside class="gallery-detail" id="gallery-detail"></aside>
        </div>
      </div>`;
    document.body.appendChild(shell);
    shell.querySelector('#gallery-close').addEventListener('click', () => shell.classList.remove('show'));
    shell.addEventListener('click', (event) => {
      if (event.target === shell) shell.classList.remove('show');
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') shell.classList.remove('show');
    });
    return shell;
  },

  renderGallery(focusRealm) {
    const data = this.data;
    const grid = document.getElementById('gallery-grid');
    const sub = document.getElementById('gallery-sub');
    if (!grid) return;
    const unlocked = (data.forms || []).filter((f) => f.reached).length;
    if (sub) {
      sub.innerHTML = `已显化 <b>${unlocked}</b> / ${(data.forms || []).length} 尊 ·
        境界每进一步，它就换一副样子`;
    }
    grid.innerHTML = (data.forms || []).map((row) => {
      const art = row.art || {};
      const cls = ['gallery-card'];
      if (row.current) cls.push('is-current');
      if (!row.reached) cls.push('is-locked');
      return `<button class="${cls.join(' ')}" data-realm="${this.esc(row.realm)}"
          style="--sc-primary:${this.esc(art.primary)};--sc-aura:${this.esc(art.aura)}">
        <div class="scg-art">${window.StarCoach ? window.StarCoach.render({
          art, seed: data.user + '|card', width: '100%', label: art.name, rich: false,
        }) : ''}</div>
        <div class="scg-meta">
          <div class="scg-name">${this.esc(art.name || row.realm)}</div>
          <div class="scg-realm">${this.esc(row.realm)} · 第 ${row.unlock_level} 境</div>
          <div class="scg-state">${row.current ? '当前显化'
            : (row.reached ? '已显化' : `${row.unlock_need} 修为解锁`)}</div>
        </div>
        ${row.reached ? '' : '<span class="scg-lock">未显化</span>'}
      </button>`;
    }).join('');
    grid.querySelectorAll('.gallery-card').forEach((card) => {
      card.addEventListener('click', () => this.renderGalleryDetail(card.dataset.realm));
    });
    this.renderGalleryDetail(focusRealm || (data.current && data.current.realm));
    const active = grid.querySelector('.gallery-card.is-current');
    if (active && !focusRealm) active.classList.add('is-focus');
  },

  renderGalleryDetail(realm) {
    const data = this.data;
    const box = document.getElementById('gallery-detail');
    if (!box || !data) return;
    const row = (data.forms || []).find((f) => f.realm === realm) || data.forms[0];
    if (!row) return;
    const art = row.art || {};
    const profile = data.profile || {};
    const gap = Math.max(0, row.unlock_need - (profile.points || 0));
    document.querySelectorAll('.gallery-card').forEach((card) => {
      card.classList.toggle('is-focus', card.dataset.realm === row.realm);
    });
    box.style.setProperty('--sc-primary', art.primary || '#8fa3b8');
    box.style.setProperty('--sc-aura', art.aura || '#dce8f4');
    box.innerHTML = `
      <div class="detail-art ${row.reached ? '' : 'is-locked'}">
        ${window.StarCoach ? window.StarCoach.render({ art, seed: data.user, width: '100%', label: art.name }) : ''}
      </div>
      <div class="detail-body">
        <div class="detail-tag" style="color:${this.esc(art.primary)}">
          ${this.esc(row.realm)} · 第 ${row.unlock_level} 境${row.reached ? '' : ' · 尚未显化'}
        </div>
        <h3>${this.esc(art.name || '')}</h3>
        <div class="detail-title">${this.esc(art.title || '')}</div>
        <blockquote>${this.esc(art.whisper || '')}</blockquote>
        <div class="detail-meta">
          <span>法阵 ${art.rings || 0} 重</span>
          <span>星冕 ${art.crest || 0} 阶</span>
          <span>灵光 ${art.particles || 0} 点</span>
          <span>${this.esc(art.star === 'galaxy' ? '掌中星系' : (art.star === 'shard' ? '星棱' : '星丸'))}</span>
        </div>
        ${row.reached ? `<div class="detail-note ok">${row.current ? '这就是此刻站在你面前的它。' : '这一尊你已经见过。'}</div>`
          : `<div class="detail-note">还差 <b>${gap}</b> 修为到达这一境。满星通关一道较难题约 +189。</div>`}
        ${row.reached ? '' : '<a class="detail-go" href="/training">去刷题 · 涨修为</a>'}
      </div>`;
  },

  // ── 换法相播报 ───────────────────────────────────────
  /** 只在「境界真的变了」时播一次，见过就记下来——否则每次进页面都弹，很快就烦。 */
  celebrate(data) {
    const realm = data.current && data.current.realm;
    if (!realm) return;
    let seen = '';
    try { seen = localStorage.getItem(this.SEEN_STORE) || ''; } catch (e) { seen = ''; }
    try { localStorage.setItem(this.SEEN_STORE, realm); } catch (e) { /* 存不了就每次都当新的，无伤 */ }
    if (!seen || seen === realm) return;
    const art = data.art || {};
    if (window.Coach && Coach.toast) {
      Coach.toast(`教练显化新身 · ${art.name || ''}`, 5200);
    } else if (window.CultivationGame && CultivationGame.toast) {
      CultivationGame.toast(`教练显化新身 · ${art.name || ''}`, art.title || '');
    }
  },
};

window.CoachScene = CoachScene;
