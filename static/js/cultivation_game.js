/**
 * cultivation_game.js — 修行阁：用户画像子系统的全部界面
 *
 * 数据全部来自 `/api/game/state`（服务端由 game_engine 推导），
 * 前端不做任何成长计算——它只负责把「你已经走到哪」画出来。
 *
 * 页面结构（从上到下就是一条闭环）：
 *   法相 → 境界试炼 → 神功 → 装备 → 修行地图 → 攻略
 * 即：我是谁 → 现在该练什么 → 练成了什么 → 下一步去哪 → 怎么走最快。
 *
 * 同一个文件也挂在学习仪表盘上，只为了 `openLevel()`：
 * 让「点开等级看这一境的肖像」在仪表盘上也能用，而不必跳页。
 */
const CultivationGame = {
  data: null,
  loading: false,
  seenKey: 'pymaster_game_seen_equip',

  // ── 数据 ──────────────────────────────────────────────
  async load(force) {
    if (this.data && !force) return this.data;
    if (this.loading) return null;
    this.loading = true;
    try {
      const response = await fetch('/api/game/state');
      const data = await response.json();
      this.data = data && data.success ? data : null;
    } catch (error) {
      this.data = null;
    }
    this.loading = false;
    // 每次拿到新数据都过一遍解锁播报：仪表盘上点开等级、试炼刚好达成，
    // 也能收到同一条提示，而不是只有修行阁页面才播报。
    if (this.data) this.celebrate(this.data);
    return this.data;
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  },

  artStyle(art) {
    if (!art) return '';
    return `--pm-primary:${art.primary};--pm-aura:${art.aura};`;
  },

  sigil(glyph, art, options) {
    const opts = options || {};
    return window.Portrait.sigil(glyph, {
      size: opts.size || 40,
      className: opts.className || 'pm-sigil',
      seed: opts.seed || glyph,
    });
  },

  // ── 渲染：整页 ────────────────────────────────────────
  async renderInto(root) {
    const data = await this.load();
    if (!data) {
      root.innerHTML = '<div class="empty-note">修行数据加载失败，刷新页面重试。</div>';
      return;
    }
    this.root = root;
    root.innerHTML = this.heroHtml(data) + this.trialsHtml(data)
      + this.skillsHtml(data) + this.equipHtml(data)
      + this.mapHtml(data) + this.guideHtml(data);
    this.bind(root);
  },

  heroHtml(d) {
    const p = d.profile;
    const art = d.art;
    const power = d.power;
    const stats = d.stats;
    const trial = d.trials.find((t) => t.realm === p.realm) || d.trials[0];
    const nextLine = p.is_max
      ? '已至巅峰 · 无出其右'
      : `距 ${this.esc(p.next_name)} 还差 <b>${p.to_next}</b> 修为`;

    return `
    <div class="cult-hero" style="${this.artStyle(art)}">
      <div class="cult-hero-portrait" id="cult-portrait" title="点击放大法相">
        ${window.Portrait.render({ seed: d.user, art, level: p.level, label: p.name + ' 的神识画像' })}
        <div class="zoom-hint">点击放大法相</div>
      </div>
      <div class="cult-hero-body">
        <div class="cult-kicker">SHENSHI PORTRAIT / ${this.esc(art.realm)}</div>
        <div class="cult-title">
          <span class="name" style="color:${art.primary}">${this.esc(p.name)}</span>
          <span class="realm-tag" style="color:${art.primary}">第 ${p.level} / ${p.max_level} 境</span>
        </div>
        <div class="cult-whisper">${this.esc(art.whisper || '')}</div>

        <div class="cult-power">
          <b>${power.total}</b><span>战力</span>
        </div>
        <span class="cult-power-why" id="power-why">战力怎么算的？</span>
        <div class="cult-power-parts" id="power-parts">
          ${power.parts.map((x) => `<span class="chip">${this.esc(x.label)} <b>+${x.value}</b> <span style="opacity:.6">${this.esc(x.note)}</span></span>`).join('')}
        </div>

        <div class="cult-bar-row">
          <div class="cult-bar-label"><span>${nextLine}</span>
            <span>${p.points} / ${p.is_max ? p.points : p.next_need}</span></div>
          <div class="cult-bar"><i style="width:${Math.round(p.progress)}%"></i></div>
        </div>

        <div class="cult-metrics">
          <div class="cult-metric"><div class="k">通关</div><div class="v">${stats.total_solved}<small> 题</small></div></div>
          <div class="cult-metric"><div class="k">满星</div><div class="v">${stats.stars3}<small> 题</small></div></div>
          <div class="cult-metric"><div class="k">较难题满星</div><div class="v">${stats.stars3_hard}<small> 题</small></div></div>
          <div class="cult-metric"><div class="k">本境试炼</div><div class="v">${trial ? trial.progress : 0}<small>%</small></div></div>
        </div>

        <div class="cult-hero-actions">
          <a class="cult-btn primary" href="/training">去刷题 · 涨修为</a>
          <button class="cult-btn" id="open-level">查看本境详情</button>
          <a class="cult-btn" href="/progress">学习仪表盘</a>
        </div>
      </div>
    </div>`;
  },

  trialsHtml(d) {
    // 取当前境界与前后相邻境界的试炼：升到哪一境就看哪一境的功课，
    // 远处的境界不列出来（那只会变成噪音）
    const currentTier = (d.art || {}).tier || 0;
    const rows = d.trials
      .slice()
      .sort((a, b) => Math.abs(a.tier - currentTier) - Math.abs(b.tier - currentTier))
      .slice(0, 3)
      .sort((a, b) => a.tier - b.tier);
    return `
    <section class="cult-section">
      <div class="cult-section-head"><h2>境界试炼</h2><span class="rule"></span>
        <span class="sub">每个大境界三条目标，全达成给一次突破奖励</span></div>
      <div class="cult-trials">
        ${rows.map((t) => `
          <div class="trial-card ${t.realm === d.profile.realm ? 'is-current' : ''} ${t.done ? 'is-done' : ''}"
               style="${this.artStyle((d.realms.find((r) => r.realm === t.realm) || {}).art)}"> 
            <div class="trial-head">
              ${this.sigil((d.realms.find((r) => r.realm === t.realm) || {}).art?.glyph || 'seed',
                null, { size: 26, className: 'pm-sigil' })}
              <span class="realm">${this.esc(t.realm)}</span>
              <span class="state">${t.claimed ? '已通过' : (t.done ? '已达成' : '进行中')}</span>
              <span class="reward">突破奖励 +${t.reward} 修为</span>
            </div>
            <div class="trial-objectives">
              ${t.objectives.map((o) => `
                <div class="objective ${o.done ? 'done' : ''}">
                  <span class="text">${o.done ? '已达成 · ' : ''}${this.esc(o.text)}</span>
                  <span class="count">${o.have}/${o.target}</span>
                  <div class="bar"><i style="width:${o.ratio}%"></i></div>
                </div>`).join('')}
            </div>
          </div>`).join('')}
      </div>
    </section>`;
  },

  skillsHtml(d) {
    const levels = d.levels;
    return `
    <section class="cult-section">
      <div class="cult-section-head"><h2>神功</h2><span class="rule"></span>
        <span class="sub">每升一级得一式，名字就是这段路要练的计算机功夫</span></div>
      <div class="skill-grid">
        ${levels.filter((lv) => lv.level > 0).map((lv) => `
          <div class="skill-card ${lv.current ? 'is-current' : (lv.reached ? '' : 'is-locked')}"
               data-level="${lv.level}" style="--pm-primary:${lv.primary}">
            <div class="lv">${this.sigil(this.realmGlyph(d, lv.realm), null, { size: 16, className: 'pm-sigil' })}
              第 ${lv.level} 境 · ${this.esc(lv.name)}</div>
            <div class="nm">《${this.esc(lv.skill.name)}》</div>
            <div class="tm">${this.esc(lv.skill.term)}</div>
            ${lv.reached ? `<span class="stamp">${lv.current ? '当前' : '已得'}</span>`
              : `<span class="stamp" style="color:var(--text-muted)">${lv.need} 修为</span>`}
          </div>`).join('')}
      </div>
    </section>`;
  },

  realmGlyph(d, realm) {
    const hit = (d.realms || []).find((r) => r.realm === realm);
    return (hit && hit.art && hit.art.glyph) || 'seed';
  },

  equipHtml(d) {
    const unlocked = d.equipment.filter((e) => e.unlocked).length;
    return `
    <section class="cult-section">
      <div class="cult-section-head"><h2>装备</h2><span class="rule"></span>
        <span class="sub">已解锁 ${unlocked} / ${d.equipment.length} 件 · 多数靠「满星通关较难题」解锁</span></div>
      <div class="equip-grid">
        ${d.equipment.map((e) => `
          <div class="equip-card ${e.unlocked ? 'on' : ''}" style="${this.artStyle(d.art)}">
            ${e.unlocked ? '<span class="badge">已解锁</span>' : ''}
            <div class="glyph">${window.Portrait.icon(e.icon, { size: 26 })}</div>
            <div class="nm">${this.esc(e.name)}<span class="slot">${this.esc(e.slot)}</span></div>
            <div class="hint">解锁方式：${this.esc(e.hint)}</div>
            ${e.unlocked
              ? `<div class="why">${this.esc(e.why || '')}</div>`
              : `<div class="prog"><i style="width:${e.ratio}%"></i></div>
                 <div class="meta"><span>${e.have} / ${e.target}</span><span>${e.ratio}%</span></div>`}
          </div>`).join('')}
      </div>
    </section>`;
  },

  mapHtml(d) {
    return `
    <section class="cult-section">
      <div class="cult-section-head"><h2>修行地图</h2><span class="rule"></span>
        <span class="sub">十境三十级 · 点任意一境可预览那一境的法相与神功</span></div>
      <div class="map-scroll">
        <div class="cult-map">
          ${d.realms.map((r) => {
            const trial = r.trial || {};
            const flag = !r.reached ? `${r.range.need} 修为开启`
              : (trial.done ? `试炼已通 +${trial.reward}` : `试炼 ${trial.progress || 0}%`);
            return `
            <div class="map-node ${r.reached ? 'reached' : ''} ${r.current ? 'current' : ''}"
                 data-level="${r.range.start}" style="${this.artStyle(r.art)}">
              <div class="rail"><i></i></div>
              <div class="disc">${this.sigil(r.art.glyph, null, {
                size: 30, className: 'pm-sigil' + (r.current ? ' is-current' : (r.reached ? '' : ' is-locked')),
              })}</div>
              <div class="label">${this.esc(r.realm)}</div>
              <div class="need">Lv.${r.range.start}–${r.range.end}</div>
              <div class="flag ${trial.done ? 'ok' : ''}">${this.esc(flag)}</div>
            </div>`;
          }).join('')}
        </div>
      </div>
    </section>`;
  },

  guideHtml(d) {
    const g = d.guide;
    return `
    <section class="cult-section">
      <div class="cult-section-head"><h2>攻略</h2><span class="rule"></span>
        <span class="sub">按你现在的进度算出来的，不是写死的教程</span></div>
      <div class="guide-grid">
        <div class="guide-steps">
          ${g.steps.map((s) => `
            <div class="guide-card">
              <h3>${this.esc(s.title)}</h3>
              ${s.text ? `<p>${this.esc(s.text)}</p>` : ''}
              ${s.items ? `<div class="pick-list">${s.items.map((q) => `
                <a class="pick" href="/training?q=${encodeURIComponent(q.id)}">
                  <span class="diff d${q.difficulty}">${this.esc(q.difficulty_label)}</span>
                  <span class="ttl">${this.esc(q.title)}${q.wrong ? ' · 错过一次' : (q.started ? ' · 已开头' : '')}</span>
                  <span class="gain">满星 +${q.estimate}</span>
                </a>`).join('')}</div>` : ''}
            </div>`).join('')}
        </div>
        <div class="guide-card">
          <h3>效率心法</h3>
          <ul class="tips">${g.tips.map((t) => `<li>${this.esc(t)}</li>`).join('')}</ul>
        </div>
      </div>
    </section>`;
  },

  // ── 交互 ──────────────────────────────────────────────
  bind(root) {
    const why = root.querySelector('#power-why');
    const parts = root.querySelector('#power-parts');
    if (why && parts) {
      why.addEventListener('click', () => parts.classList.toggle('show'));
    }
    const openLevel = root.querySelector('#open-level');
    if (openLevel && this.data) {
      openLevel.addEventListener('click', () => this.openLevel(this.data.profile.level));
    }
    const portrait = root.querySelector('#cult-portrait');
    if (portrait && this.data) {
      portrait.addEventListener('click', () => this.zoom(this.data.profile.level));
    }
    root.querySelectorAll('[data-level]').forEach((el) => {
      el.addEventListener('click', () => this.openLevel(parseInt(el.dataset.level, 10)));
    });
  },

  /** 放大法相：一整屏只看画像，像挂了一幅自己的拓印 */
  zoom(level) {
    if (!this.data) return;
    const art = this.artFor(level);
    const box = this.modalShell();
    box.querySelector('.cult-modal-body').innerHTML = `
      ${window.Portrait.render({ seed: this.data.user, art, level, label: '法相' })}
      <div style="text-align:center;margin-top:10px;font-size:12.5px;color:var(--text-muted)">
        ${this.esc(this.data.user)} · ${this.esc(art.realm)}</div>`;
    box.querySelector('.cult-modal').classList.add('show');
  },

  artFor(level) {
    const lv = (this.data.levels || []).find((x) => x.level === level);
    const realm = lv ? lv.realm : '凡尘';
    const hit = (this.data.realms || []).find((r) => r.realm === realm);
    return Object.assign({ realm }, (hit && hit.art) || {});
  },

  /**
   * 点开一个等级：看到「那一境的你」的肖像、神功与门槛。
   * 未到达的境界也能看（灰一点，标「预览」）——这是最强的升级动机。
   */
  async openLevel(level) {
    if (!this.data) {
      const data = await this.load();
      if (!data) return;
    }
    const d = this.data;
    const lv = (d.levels || []).find((x) => x.level === level);
    if (!lv) return;
    const art = this.artFor(level);
    const reached = lv.reached;
    const current = lv.level === d.profile.level;
    const box = this.modalShell();
    const trial = (d.realms.find((r) => r.realm === lv.realm) || {}).trial || {};
    const gap = Math.max(0, lv.need - d.profile.points);

    box.querySelector('.cult-modal-body').innerHTML = `
      <div class="preview-tag">${current ? '当前境界' : (reached ? '已到达' : '尚未到达 · 预览')}</div>
      ${window.Portrait.render({
        seed: d.user, art, level,
        className: reached ? '' : 'is-locked',
        label: lv.name + ' 的神识画像',
      })}
      <div style="display:flex;justify-content:space-between;font-size:11.5px;color:var(--text-muted);
                  font-family:var(--font-mono);margin-top:6px">
        <span>第 ${lv.level} / ${d.profile.max_level} 境</span>
        <span>${lv.need} 修为</span>
      </div>`;
    box.querySelector('.modal-body').innerHTML = `
      <div class="tagline" style="color:${art.primary}">第 ${lv.level} 境 · ${this.esc(lv.name)}</div>
      <h3>《${this.esc(lv.skill.name)}》</h3>
      <div class="tagline">${this.esc(lv.skill.term)}</div>
      <div class="whisper">${this.esc(art.whisper || '')}</div>
      <div class="modal-block">
        <div class="k">这一境要练的</div>
        <div class="v">${this.esc(lv.skill.desc)}</div>
      </div>
      <div class="modal-block">
        <div class="k">境界试炼</div>
        <div class="v">${trial.objectives ? trial.objectives.map((o) => this.esc(o.text)).join(' · ')
          : '—'} ${trial.reward ? `<span style="color:var(--orange)">（全通 +${trial.reward} 修为）</span>` : ''}</div>
      </div>
      ${reached ? '' : `<div class="modal-locked-note">还差 ${gap} 修为到达此境。最快的路：满星通关一道较难题（+189）。</div>`}
      <div class="modal-actions">
        <a class="cult-btn primary" href="/training">去刷题</a>
        ${current ? '' : `<button class="cult-btn" id="modal-jump">看地图上的位置</button>`}
      </div>`;

    const jump = box.querySelector('#modal-jump');
    if (jump) {
      jump.addEventListener('click', () => {
        box.querySelector('.cult-modal').classList.remove('show');
        const node = document.querySelector(`.map-node[data-level="${lv.level}"]`);
        if (node) node.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
      });
    }
    box.querySelector('.cult-modal').classList.add('show');
  },

  modalShell() {
    let shell = document.getElementById('cult-modal-shell');
    if (shell) return shell;
    shell = document.createElement('div');
    shell.id = 'cult-modal-shell';
    shell.innerHTML = `
      <div class="cult-modal" id="cult-modal">
        <div class="cult-modal-box">
          <button class="close" id="cult-modal-close" title="关闭">×</button>
          <div class="cult-modal-body" style="${this.artStyle(this.data && this.data.art)}"></div>
          <div class="modal-body"></div>
        </div>
      </div>`;
    document.body.appendChild(shell);
    shell.querySelector('#cult-modal-close').addEventListener('click', () => {
      shell.querySelector('.cult-modal').classList.remove('show');
    });
    shell.querySelector('#cult-modal').addEventListener('click', (event) => {
      if (event.target.id === 'cult-modal') shell.querySelector('.cult-modal').classList.remove('show');
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') shell.querySelector('.cult-modal').classList.remove('show');
    });
    return shell;
  },

  // ── 解锁播报 ──────────────────────────────────────────
  /** 装备/试炼是新达成的才播报：见过一次就不再打扰（记在 localStorage）。 */
  celebrate(d) {
    let seen = [];
    try { seen = JSON.parse(localStorage.getItem(this.seenKey) || '[]'); } catch (error) { seen = []; }
    if (!seen.length) {
      // 第一次打开：把现状记为「已知」，只播报服务端刚刚发的试炼奖励
      try { localStorage.setItem(this.seenKey, JSON.stringify(d.equipment.filter((e) => e.unlocked).map((e) => e.id))); } catch (error) {}
    } else {
      const fresh = d.equipment.filter((e) => e.unlocked && seen.indexOf(e.id) < 0);
      fresh.forEach((e) => this.toast(`装备解锁 · ${e.name}`, e.why || e.hint));
      if (fresh.length) {
        try {
          localStorage.setItem(this.seenKey, JSON.stringify(d.equipment.filter((e) => e.unlocked).map((e) => e.id)));
        } catch (error) {}
      }
    }
    (d.granted_trials || []).forEach((t) => {
      this.toast(`试炼通过 · ${t.realm}`, `突破奖励 +${t.reward} 修为`);
    });
    (d.just_unlocked || []).forEach((name) => this.toast(`新装备 · ${name}`, '去装备栏看看'));
  },

  toast(title, subtitle) {
    let box = document.getElementById('cult-unlock-toast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'cult-unlock-toast';
      box.className = 'cult-unlock-toast';
      document.body.appendChild(box);
    }
    const item = document.createElement('div');
    item.className = 'unlock-item';
    item.innerHTML = `${window.Portrait.icon('spark', { size: 20 })}
      <div><div class="t">${this.esc(title)}</div><div class="s">${this.esc(subtitle || '')}</div></div>`;
    box.appendChild(item);
    setTimeout(() => item.remove(), 5200);
  },
};

window.CultivationGame = CultivationGame;

/**
 * 修行阁页面入口。支持 #level-12 / #portrait 这样的锚点：
 * 直接刷新或分享一条链接，也能落在「某一境的你」上面。
 */
document.addEventListener('DOMContentLoaded', async function () {
  const root = document.getElementById('cult-root');
  if (!root) return;
  await CultivationGame.renderInto(root);
  if (window.Cultivation) Cultivation.mount({ float: false });
  const hash = (location.hash || '').replace('#', '');
  const levelHit = hash.match(/^level-(\d+)$/);
  if (levelHit) CultivationGame.openLevel(parseInt(levelHit[1], 10));
  else if (hash === 'portrait' && CultivationGame.data) CultivationGame.zoom(CultivationGame.data.profile.level);
});
