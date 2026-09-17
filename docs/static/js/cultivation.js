/**
 * cultivation.js — 修为等级：全局悬浮等级条
 *
 * 它挂在每一个页面上（仪表盘 / 章节页 / 教练页 / 刷题页），
 * 所以只做一件事：拉一次 /api/cultivation/profile，把等级条画出来。
 * 加分不在这里算——加分全部由服务端结算，前端只负责「展示 + 升级动画」。
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
    dock.classList.toggle('collapsed', this.collapsed);
    const peak = Math.round(profile.progress);
    dock.innerHTML = this.collapsed ? `
      <div class="cult-head" title="修为：${profile.name}（${profile.points} 分）">
        <div class="cult-orb">${this.orbGlyph(profile.level)}</div>
      </div>` : `
      <div class="cult-head">
        <div class="cult-orb">${this.orbGlyph(profile.level)}</div>
        <div>
          <div class="cult-name">${this.esc(profile.name)}</div>
          <div class="cult-points">${profile.points} 点修为</div>
        </div>
        <button class="cult-toggle" id="cult-toggle" title="收起">▾</button>
      </div>
      <div class="cult-bar"><i style="width:${peak}%"></i></div>
      <div class="cult-next">
        ${profile.is_max ? '<span>已至巅峰 · 道祖之境</span>'
          : `<span>下一境：${this.esc(profile.next_name)}</span><span>还差 <b>${profile.to_next}</b></span>`}
      </div>
      <div class="cult-actions">
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
    dock.addEventListener('click', () => {
      if (!this.collapsed) return;
      this.collapsed = false;
      try { localStorage.setItem(this.storageKey, '0'); } catch (e) {}
      this.render(options);
    });
  },

  /** 把等级条渲染进指定容器（仪表盘里用） */
  renderInline(container, profile) {
    if (!container || !profile) return;
    container.innerHTML = `
      <div class="cult-inline">
        <div class="row1">
          <span class="lv">${this.orbGlyph(profile.level)} ${this.esc(profile.name)}</span>
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

  orbGlyph(level) {
    if (level >= 28) return '🌌';
    if (level >= 25) return '⚡';
    if (level >= 22) return '👑';
    if (level >= 19) return '🔥';
    if (level >= 16) return '💫';
    if (level >= 13) return '🌟';
    if (level >= 10) return '💎';
    if (level >= 7) return '🟡';
    if (level >= 4) return '🔵';
    return '🟢';
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },

  /**
   * 结算提示：任何一次加分都会带回来 profile。
   * 升级了就弹一条醒目的提示，没升级就只更新等级条。
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

    if (levelUp) {
      this.toast(`✦ 突破！${profile.name}`,
        `当前修为 ${profile.points} 点${gained ? ` · 本次 +${gained}` : ''}`, 4600);
    } else if (gained > 0) {
      this.toast(`修为 +${gained}`, profile.is_max ? '' : `距 ${profile.next_name} 还差 ${profile.to_next} 点`, 2400);
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
