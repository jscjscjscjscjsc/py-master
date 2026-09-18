/**
 * progress.js — 学习仪表盘：分章节进度 + 错题分类 + 刷题进度
 *
 * 这个页面的价值全在「一眼看出该补哪儿」，所以：
 * - 每个数字都要能点进去（错题直接跳到那道题）；
 * - 课程章节与算法专题分开呈现，但共用同一套进度结构；
 * - 没有数据时给出「下一步做什么」而不是空白表格。
 */
const ProgressPage = {
  data: null,

  async init() {
    const data = await fetch('/api/progress/overview').then((r) => r.json()).catch(() => null);
    if (!data || !data.success) {
      document.getElementById('dash-root').innerHTML =
        '<div class="empty-note">仪表盘数据加载失败，刷新页面重试。</div>';
      return;
    }
    this.data = data;
    this.render();
  },

  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  },

  stars(count, max) {
    const filled = Math.round((count / Math.max(1, max)) * 5);
    return [1, 2, 3, 4, 5].map((n) => (n <= filled ? '★' : '<span class="off">★</span>')).join('');
  },

  /** 一行章节进度。课程章节比算法专题多两列（知识点数、知识点进度）。 */
  row(c, isCourse) {
    const wrongColor = c.q_wrong ? 'var(--red)' : 'var(--text-muted)';
    const cells = [];
    if (isCourse) {
      cells.push(`<td class="num">${c.kp_done}/${c.kp_total}</td>`);
      cells.push(`<td><div style="display:flex;align-items:center;gap:8px">
          <div class="mini-bar learn"><i style="width:${c.kp_progress}%"></i></div>
          <span class="num">${c.kp_progress}%</span></div></td>`);
    } else {
      cells.push(`<td class="num">${c.q_total}</td>`);
    }
    cells.push(`<td><div style="display:flex;align-items:center;gap:8px">
        <div class="mini-bar"><i style="width:${c.q_progress}%"></i></div>
        <span class="num">${c.q_solved}/${c.q_total}</span></div></td>`);
    cells.push(`<td class="stars">${this.stars(c.stars, c.max_stars)}<span class="num" style="color:var(--text-muted);margin-left:5px">${c.stars}/${c.max_stars}</span></td>`);
    cells.push(`<td class="num" style="color:${wrongColor}">${c.q_wrong}</td>`);
    cells.push(`<td><div style="display:flex;align-items:center;gap:8px">
        <div class="mini-bar"><i style="width:${c.learn_progress}%"></i></div>
        <span class="num">${c.learn_progress}%</span></div></td>`);
    const link = c.wrong_ids && c.wrong_ids.length
      ? `<a href="/training?q=${encodeURIComponent(c.wrong_ids[0])}">重做错题</a>`
      : `<a href="/training?chapters=${c.id}">去刷题</a>`;
    cells.push(`<td>${link}</td>`);
    return `<tr><td class="name">${this.esc(c.title)}</td>${cells.join('')}</tr>`;
  },

  /**
   * 修行卡：仪表盘上的「用户画像」区域。
   * 左边是这一境的神识画像，右边是等级 / 战力 / 突破进度 / 试炼，
   * 下面一排是可点开的境界阶梯——点任一境都能看到那一境的肖像与神功。
   */
  renderCultivationCard(profile) {
    if (!profile) return '';
    const art = profile.art || {};
    const trial = profile.trial;
    const ladder = (profile.levels || []).map((lv) => {
      const realmArt = (profile.realm_art || {})[lv.name.split('·')[0]] || {};
      const color = realmArt.primary || '#00d4ff';
      const state = lv.level === profile.level ? ' current' : (lv.level < profile.level ? ' done' : '');
      const seal = window.Portrait
        ? window.Portrait.sigil(realmArt.glyph || 'seed', { size: 20, className: 'pm-sigil' })
        : '';
      return `<button class="cult-step${state}" data-level="${lv.level}" title="${this.esc(lv.name)}"
        style="--pm-primary:${color}">${seal}<span>${this.esc(lv.name)}</span></button>`;
    }).join('');

    return `
      <div class="profile-card" style="--pm-primary:${art.primary || '#00d4ff'};--pm-aura:${art.aura || '#fff'}">
        <div class="profile-portrait" id="dash-portrait" title="点击放大法相">
          ${window.Portrait ? window.Portrait.render({
            seed: this.data.user || '', art, level: profile.level,
            label: '神识画像', className: 'dash-portrait-svg',
          }) : ''}
          <div class="zoom-hint">点击放大</div>
        </div>
        <div class="profile-main">
          <div class="profile-title">
            <span class="seal">${window.Portrait ? window.Portrait.sigil(art.glyph || 'seed', { size: 30, className: 'pm-sigil is-current' }) : ''}</span>
            <span class="nm" style="color:${art.primary || 'var(--cyan)'}">${this.esc(profile.name)}</span>
            <span class="tag">第 ${profile.level} / ${profile.max_level} 境</span>
          </div>
          <div class="profile-whisper">${this.esc(art.whisper || '')}</div>
          <div class="profile-power">
            <b>${profile.power || 0}</b><span>战力</span>
            <span class="sep">·</span>
            <span>${profile.points} 修为</span>
            <span class="sep">·</span>
            <span>装备 ${profile.equipment_unlocked || 0}/${profile.equipment_total || 0}</span>
          </div>
          <div class="cult-bar" style="margin-top:10px">
            <i style="width:${Math.round(profile.progress)}%"></i></div>
          <div class="cult-next">
            ${profile.is_max ? '<span>已至巅峰</span>'
              : `<span>下一境：${this.esc(profile.next_name)}</span><span>还差 <b>${profile.to_next}</b> 点</span>`}
          </div>
          ${trial ? `
          <div class="profile-trial">
            <span>${this.esc(trial.realm)}·试炼</span>
            <div class="mini-bar"><i style="width:${trial.progress}%"></i></div>
            <span class="num">${trial.progress}%</span>
          </div>` : ''}
          <div class="profile-actions">
            <a class="cult-btn primary" href="/cultivation">进入修行阁</a>
            <button class="cult-btn" id="dash-open-level">查看本境详情</button>
          </div>
        </div>
        <div class="profile-ladder">${ladder}</div>
      </div>`;
  },

  bindCultivationCard() {
    const profile = this.data && this.data.profile;
    if (!profile) return;
    const open = (level) => {
      if (window.CultivationGame) {
        window.CultivationGame.load().then((data) => {
          if (data) window.CultivationGame.openLevel(level);
        });
      } else {
        window.location.href = '/cultivation';
      }
    };
    const detail = document.getElementById('dash-open-level');
    if (detail) detail.addEventListener('click', () => open(profile.level));
    const portrait = document.getElementById('dash-portrait');
    if (portrait) portrait.addEventListener('click', () => open(profile.level));
    document.querySelectorAll('.cult-step[data-level]').forEach((el) => {
      el.addEventListener('click', () => open(parseInt(el.dataset.level, 10)));
    });
  },

  render() {
    const d = this.data;
    const t = d.totals;
    const root = document.getElementById('dash-root');

    root.innerHTML = `
      <div class="section-title">修为等级 <span class="line"></span>
        <span class="sub">刷题升境界、拿神功；较难题解锁装备；十境试炼全通再给突破奖励</span></div>
      <div id="cult-inline">${this.renderCultivationCard(d.profile)}</div>

      <div class="section-title">总览 <span class="line"></span></div>
      <div class="dash-grid">
        <div class="dash-card cyan">
          <div class="k">题库掌握度</div>
          <div class="v">${t.mastery}<small>%</small></div>
          <div class="bar"><i style="width:${t.mastery}%"></i></div>
          <div class="k" style="margin-top:8px">已通关 ${t.solved} / ${t.questions} 题</div>
        </div>
        <div class="dash-card green">
          <div class="k">星级合计</div>
          <div class="v">${t.stars}<small>/ ${t.max_stars}</small></div>
          <div class="bar"><i style="width:${Math.round(t.stars / Math.max(1, t.max_stars) * 100)}%"></i></div>
          <div class="k" style="margin-top:8px">一次做对才能拿满星</div>
        </div>
        <div class="dash-card orange">
          <div class="k">累计作答</div>
          <div class="v">${t.attempted}<small>次</small></div>
          <div class="bar"><i style="width:${Math.min(100, t.attempted)}%"></i></div>
          <div class="k" style="margin-top:8px">通关率 ${t.accuracy}%</div>
        </div>
        <div class="dash-card purple">
          <div class="k">错题待攻克</div>
          <div class="v">${t.wrong}<small>题</small></div>
          <div class="bar"><i style="width:${Math.min(100, t.wrong * 5)}%"></i></div>
          <div class="k" style="margin-top:8px">实战组卷 ${t.exams} 次</div>
        </div>
      </div>

      <div class="section-title">课程章节进度 <span class="line"></span>
        <span class="sub">知识点学习 + 配套刷题，两条线都要看</span></div>
      <div class="table-wrap">
        <table class="progress-table">
          <thead><tr>
            <th>章节</th><th>知识点</th><th>知识点进度</th>
            <th>刷题进度</th><th>星级</th><th>错题</th><th>综合</th><th></th>
          </tr></thead>
          <tbody>
            ${d.course_chapters.map((c) => this.row(c, true)).join('') ||
              '<tr><td colspan="8"><div class="empty-note">题库里还没有课程配套题。</div></td></tr>'}
          </tbody>
        </table>
      </div>

      <div class="section-title">算法与数据结构 <span class="line"></span>
        <span class="sub">按专题统计，从复杂度基础到动态规划</span></div>
      <div class="table-wrap">
        <table class="progress-table">
          <thead><tr>
            <th>专题</th><th>题量</th><th>刷题进度</th><th>星级</th><th>错题</th><th>综合</th><th></th>
          </tr></thead>
          <tbody>
            ${d.algo_chapters.map((c) => this.row(c, false)).join('') ||
              '<tr><td colspan="7"><div class="empty-note">题库里还没有算法题。</div></td></tr>'}
          </tbody>
        </table>
      </div>

      <div class="section-title">错题本（按章节分类） <span class="line"></span>
        <span class="sub">点题目直接回去重做</span></div>
      <div id="wrong-book">
        ${d.wrong_groups.length ? d.wrong_groups.map((g) => `
          <div class="wrong-group">
            <div class="wrong-group-head">
              <span>${this.esc(g.title)}</span>
              <span class="count">${g.items.length} 题</span>
              <span style="margin-left:auto;font-size:11.5px;color:var(--text-muted)">
                ${g.track === 'algorithm' ? '算法专题' : '课程配套'}
              </span>
            </div>
            ${g.items.map((item) => `
              <div class="wrong-item">
                <div class="t">
                  <div><span class="diff d${item.difficulty}">${item.difficulty === 1 ? '简单' : item.difficulty === 2 ? '中等' : '较难'}</span>
                    ${this.esc(item.title)} ${item.solved ? '<span style="color:var(--green);font-size:11px">（已补做）</span>' : ''}</div>
                  ${item.last_error ? `<div class="err">${this.esc(item.last_error.slice(0, 160))}</div>` : ''}
                </div>
                <a class="go" href="/training?q=${encodeURIComponent(item.question_id)}">去重做 →</a>
              </div>`).join('')}
          </div>`).join('') : '<div class="empty-note">还没有刷题错题。做题时报错或反复修改的题目会自动记到这里。</div>'}
      </div>

      ${Object.keys(d.textbook_wrong).length ? `
      <div class="section-title">教材练习错题 <span class="line"></span>
        <span class="sub">来自章节页的练习题</span></div>
      <div class="wrong-book" id="textbook-wrong">
        ${Object.entries(d.textbook_wrong).map(([cid, items]) => `
          <div class="wrong-group">
            <div class="wrong-group-head"><span>第 ${this.esc(cid)} 章</span>
              <span class="count">${items.length} 题</span></div>
            ${items.slice(0, 12).map((item) => `
              <div class="wrong-item"><div class="t">
                <div>${this.esc(item.question || '')}</div>
                <div class="err">你的答案：${this.esc(item.user_answer || '（空）')}</div>
              </div></div>`).join('')}
          </div>`).join('')}
      </div>` : ''}

      ${d.exams && d.exams.length ? `
      <div class="section-title">实战组卷记录 <span class="line"></span></div>
      <div class="table-wrap">
        <table class="progress-table">
          <thead><tr><th>时间</th><th>题量</th><th>得分</th><th>状态</th><th></th></tr></thead>
          <tbody>
            ${d.exams.map((e) => `<tr>
              <td class="num">${this.esc(e.created_at || '')}</td>
              <td>${e.count} 题</td>
              <td class="num">${e.score === null ? '-' : e.score}</td>
              <td>${e.status === 'finished' ? '已交卷' : `进行中 ${e.done}/${e.count}`}</td>
              <td>${e.review ? '已批卷' : ''}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>` : ''}

      <div class="section-title">最近的修为变化 <span class="line"></span></div>
      <div class="points-log">
        ${(d.recent_points || []).length ? d.recent_points.map((p) => `
          <div class="points-row">
            <span class="when">${this.esc(p.ts || '')}</span>
            <span class="what">${this.esc(p.note || p.reason)}</span>
            <span class="plus">+${p.delta}</span>
          </div>`).join('') : '<div class="empty-note">还没有加分记录。去刷一道题试试。</div>'}
      </div>`;

    // 修行卡自带画像与等级信息，只有画像脚本缺席时才退回旧的等级条
    if (window.Cultivation && (!window.Portrait || !d.profile.art)) {
      Cultivation.renderInline(document.getElementById('cult-inline'), d.profile);
    } else {
      this.bindCultivationCard();
    }
  },
};

window.ProgressPage = ProgressPage;

document.addEventListener('DOMContentLoaded', async () => {
  await ProgressPage.init();
  // 页内已有等级条，关掉左下角浮窗，避免遮挡表格首列
  if (window.Cultivation) Cultivation.mount({ float: false });
});
