/**
 * cultivation.js — 修为等级：全局悬浮等级条
 *
 * 它挂在每一个页面上（仪表盘 / 章节页 / 教练页 / 刷题页），
 * 所以只做一件事：拉一次 /api/cultivation/profile，把等级条画出来。
 * 加分不在这里算——加分全部由服务端结算，前端只负责「展示 + 升级动画」。
 *
 * 图形一律是矢量法印（Prtrait.sigil），不用 emoji：
 * 同一个境界在任何系统、任何字体下都是同一枚印记，而不是一个彩色圆点。
 * portrait.js 没加载时退回一个内联的极简法环，绝不出现空白或报错。
 *
 * 任何拿不到数据的情况（游客、接口报错、网络断）都静默降级，
 * 绝不因为一个装饰性的组件让整页报错。
 */
const Cultivation = {
  profile: null,
  collapsed: false,

  storageKey: 'pymaster_cult_collapsed',

  init() {
    try { this.collapsed = localStorage.getItem(this.storageKey) === '1'; } catch (e) { this.collapsed = false; }
  },

  async mount(options = {}) {
    this.init();
    try {
      const response = await fetch('/api/cultivation/profile');
      const data = await response.json();
      if (!data || !data.success) return null;
      this.profile = data.profile;
    } catch (error) {
      return null;
    }
    if (this.profile && this.profile.is_guest && !options.showForGuest) return null;
    // float:false 用于「页面自己已经画了等级条」的场景（如学习仪表盘），
    // 否则左下角的浮窗会盖住表格第一列。
    if (options.float !== false) this.render(options);
    return this.profile;
  },

  render(options = {}) {
    const profile = this.profile;
    if (!profile) return;
    let dock = document.getElementById('cultivation-dock');
    if (!dock) {
      dock = document.createElement('div');
      dock.id = 'cultivation-dock';
      dock.className = 'cultivation-dock';
      document.body.appendChild(dock);
    }
    const art = profile.art || {};
    dock.classList.toggle('collapsed', this.collapsed);
    if (art.primary) dock.style.setProperty('--pm-primary', art.primary);
    const peak = Math.round(profile.progress);
    const trialLine = profile.trial
      ? `<div class="cult-trial">${this.esc(profile.trial.realm)}试炼
          <b>${profile.trial.progress}%</b></div>` : '';
    dock.innerHTML = this.collapsed ? `
      <div class="cult-head" title="修为：${profile.name}（战力 ${profile.power || 0}）">
        <div class="cult-orb">${this.orbHtml(profile)}</div>
      </div>` : `
      <div class="cult-head">
        <div class="cult-orb">${this.orbHtml(profile)}</div>
        <div>
          <div class="cult-name">${this.esc(profile.name)}</div>
          <div class="cult-points">${profile.points} 点修为 · 战力 <b>${profile.power || 0}</b></div>
        </div>
        <button class="cult-toggle" id="cult-toggle" title="收起">▾</button>
      </div>
      <div class="cult-bar"><i style="width:${peak}%"></i></div>
      <div class="cult-next">
        ${profile.is_max ? '<span>已至巅峰 · 道祖之境</span>'
          : `<span>下一境：${this.esc(profile.next_name)}</span><span>还差 <b>${profile.to_next}</b></span>`}
      </div>
      ${trialLine}
      <div class="cult-actions">
        <a href="/cultivation">修行阁</a>
        <a href="/training">刷题</a>
        <a href="/progress">仪表盘</a>
      </div>`;

    const toggle = document.getElementById('cult-toggle');
    if (toggle) {
      toggle.addEventListener('click', (event) => {
        event.stopPropagation();
        this.collapsed = true;
        try { localStorage.setItem(this.storageKey, '1'); } catch (e) {}
        this.render(options);
      });
    }
    dock.addEventListener('click', (event) => {
      if (event.target.closest('a')) return;
      if (this.collapsed) {
        this.collapsed = false;
        try { localStorage.setItem(this.storageKey, '0'); } catch (e) {}
        this.render(options);
        return;
      }
      // 点法印/名字：能开等级详情就开，否则去修行阁
      if (event.target.closest('.cult-head')) this.openHere();
    });
  },

  /** 有修行阁脚本就弹等级详情，没有就跳页——两种都是可用的正反馈。 */
  openHere() {
    const profile = this.profile;
    if (!profile) return;
    if (window.CultivationGame) {
      CultivationGame.load().then((data) => { if (data) CultivationGame.openLevel(profile.level); });
    } else {
      window.location.href = '/cultivation';
    }
  },

  /** 把等级条渲染进指定容器（仪表盘里用） */
  renderInline(container, profile) {
    if (!container || !profile) return;
    const art = profile.art || {};
    if (art.primary) container.style.setProperty('--pm-primary', art.primary);
    container.innerHTML = `
      <div class="cult-inline">
        <div class="row1">
          <span class="lv">${this.orbHtml(profile, 34)} ${this.esc(profile.name)}</span>
          <span class="pt"><b>${profile.points}</b> / ${profile.is_max ? profile.points : profile.next_need} 修为</span>
        </div>
        <div class="cult-bar"><i style="width:${Math.round(profile.progress)}%"></i></div>
        <div class="cult-next">
          ${profile.is_max ? '<span>已至巅峰</span>' : `<span>下一境：${this.esc(profile.next_name)}</span><span>还差 <b>${profile.to_next}</b> 点</span>`}
        </div>
        <div class="cult-ladder">
          ${(profile.levels || []).map((lv) => `<span class="cult-step${lv.level === profile.level ? ' current' : (lv.level < profile.level ? ' done' : '')}">${this.esc(lv.name)}</span>`).join('')}
        </div>
      </div>`;
  },

  /**
   * 境界法印。有 portrait.js 就用真正的法印（十境各不相同），
   * 否则退回到一个同心法环——它仍然不是 emoji，只是没有纹样而已。
   */
  orbHtml(profile, size = 30) {
    const art = profile.art || {};
    const glyph = art.glyph || 'seed';
    if (window.Portrait) {
      return `<span class="cult-sigil" style="color:${art.primary || 'var(--cyan)'}">
        ${window.Portrait.sigil(glyph, { size: size - 4, seed: profile.name || glyph })}</span>`;
    }
    const color = art.primary || '#00d4ff';
    return `<span class="cult-sigil" style="color:${color}">
      <svg width="${size - 6}" height="${size - 6}" viewBox="-12 -12 24 24" fill="none"
           stroke="currentColor" stroke-width="1.5">
        <circle cx="0" cy="0" r="9"/><circle cx="0" cy="0" r="3.4"/>
      </svg></span>`;
  },


  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  /**
   * 结算提示：任何一次加分都会带回来 profile。
   * 升级了就弹一条醒目的提示（并报出这一境新得的神功），
   * 顺带播报装备数量变化——这是「刷题 → 修为 → 神功/装备」闭环的收口。
   */
  applySettlement(settlement) {
    if (!settlement) return;
    const profile = settlement.profile || (settlement.settle && settlement.settle.profile);
    if (!profile) return;
    const before = this.profile;
    this.profile = profile;
    this.render({ compact: true });

    const levelUp = settlement.level_up
      || (settlement.settle && settlement.settle.profile && before
          && settlement.settle.profile.level > before.level);
    const gained = settlement.awarded || settlement.points
      || (settlement.settle && settlement.settle.points) || 0;
    const skill = profile.skill ? `得《${profile.skill.name}》` : '';

    if (levelUp && window.CultivationGame) {
      // 修行阁在场时用它统一的解锁播报，避免两套提示叠在一起
      CultivationGame.toast(`突破 · ${profile.name}`, skill || `战力 ${profile.power || 0}`);
    } else if (levelUp) {
      this.toast(`突破 · ${profile.name}`, `${skill}${skill ? ' · ' : ''}当前修为 ${profile.points} 点`, 4600);
    } else if (gained > 0) {
      this.toast(`修为 +${gained}`, profile.is_max ? '' : `距 ${profile.next_name} 还差 ${profile.to_next} 点`, 2400);
    }

    if (before && typeof profile.equipment_unlocked === 'number'
        && typeof before.equipment_unlocked === 'number'
        && profile.equipment_unlocked > before.equipment_unlocked) {
      const delta = profile.equipment_unlocked - before.equipment_unlocked;
      this.toast(`装备解锁 +${delta}`, '去修行阁看是哪一件', 4200);
    }
  },

  toast(title, subtitle, ms = 2600) {
    let box = document.getElementById('cult-toast');
    if (!box) {
      box = document.createElement('div');
      box.id = 'cult-toast';
      box.className = 'cult-toast';
      document.body.appendChild(box);
    }
    box.innerHTML = this.esc(title) + (subtitle ? `<small>${this.esc(subtitle)}</small>` : '');
    box.classList.add('show');
    clearTimeout(this._timer);
    this._timer = setTimeout(() => box.classList.remove('show'), ms);
  },
};

window.Cultivation = Cultivation;
