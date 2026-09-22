/* ============================================================
   static_qbank.js — 在线演示站的刷题数据层
   ------------------------------------------------------------
   在线站没有后端，`/api/training/*` 全部落空。这一层把它们接到
   导出好的静态 JSON 上；判题则交给 pyodide_runner.js（浏览器内真跑 Python）。

   与本地版的分工（诚实告知，不假装能用）
   ------------------------------------
     能用：选题 → 看题面 → 写代码 → 运行 → 判题 → 看解析 → 查看参考答案
     不能用：成绩保存、错题本、修为积分、组卷考试（这些要写数据库）
   所以在静态模式下：
     · 进度一律按"未通关"显示，但会明确说明"本机演示不记分"
     · 组卷/交卷接口返回人话提示，而不是让页面卡在加载中
   ============================================================ */
(function () {
  'use strict';

  if (!window.PYMASTER_STATIC) return;

  const cache = { catalog: null, briefs: null, details: {}, harness: null };

  async function getJSON(path) {
    try {
      const res = await fetch(path);
      if (!res.ok) return null;
      return await res.json();
    } catch (e) {
      return null;
    }
  }

  async function detail(id) {
    if (cache.details[id]) return cache.details[id];
    const data = await getJSON('data/qbank/details/' + encodeURIComponent(id) + '.json');
    if (data) cache.details[id] = data;
    return data;
  }

  /** 把判题结果整理成与后端 /api/training/run-cell 相同的返回体 */
  function shapeRunResult(runData, active, checks) {
    const results = (runData && runData.results) || [];
    const last = results[active] || { stdout: '', error: '', ok: true };
    const checkCell = results[checks && checks.length ? results.length - 1 : -1];
    const out = {
      success: true,
      ok: last.ok !== false,
      stdout: last.stdout || '',
      error: last.error || '',
      elapsed: 0,
      results: results,
    };
    if (checks && checks.length) {
      out.checks_run = !!(checkCell && checkCell.index === results.length - 1);
      out.checks_passed = out.checks_run && checkCell.ok !== false;
      if (!out.checks_passed && checkCell && checkCell.error) {
        out.check_error = checkCell.error;
      }
    }
    return out;
  }

  const api = {
    /** 判题：跑代码，必要时带断言 */
    async runCell({ cells, active, checks, onStatus }) {
      const r = await window.PyRunner.run(cells, checks || [], onStatus);
      if (r.unavailable) return { success: false, error: r.error, unavailable: true };
      if (r.timeout) return { success: false, error: r.error, timeout: true };
      if (!r.ok) return { success: false, error: r.error || '运行失败' };
      return shapeRunResult(r.data, active, checks);
    },

    /** 运行（不带断言） */
    async run(cells, active) {
      return api.runCell({ cells, active, checks: [] });
    },
  };

  // ── 接管 /api/training/* ──────────────────────────────
  // main.js / training.js 用的是裸 fetch，这里在全局层拦一层，
  // 它们的代码一行都不用改。
  const realFetch = window.fetch.bind(window);
  const NOT_SAVED = '在线演示站不保存成绩（没有数据库）。'
                  + '想记录进度、攒修为、用错题本，请下载本地完整版。';

  window.fetch = async function (input, init) {
    const raw = typeof input === 'string' ? input : (input && input.url) || '';
    let path = raw;
    try { path = new URL(raw, location.href).pathname; } catch (e) {}
    if (!path.startsWith('/api/training/')) {
      return realFetch(input, init);
    }

    const url = new URL(raw, location.href);
    const method = ((init && init.method) || 'GET').toUpperCase();

    // 目录
    if (path === '/api/training/catalog') {
      if (!cache.catalog) cache.catalog = getJSON('data/qbank/catalog.json');
      const data = await cache.catalog;
      return json(data || { success: false, error: '题库目录未导出' });
    }

    // 题目列表
    if (path === '/api/training/questions') {
      if (!cache.briefs) cache.briefs = getJSON('data/qbank/briefs.json');
      const all = await cache.briefs;
      if (!all) return json({ success: false, error: '题库未导出', questions: [] });
      let items = all.questions || [];
      const chapters = (url.searchParams.get('chapters') || '')
        .split(',').map((s) => s.trim()).filter(Boolean);
      const track = url.searchParams.get('track') || '';
      const difficulty = url.searchParams.get('difficulty') || '';
      const keyword = (url.searchParams.get('q') || '').trim().toLowerCase();
      const only = url.searchParams.get('only') || '';
      if (chapters.length) {
        items = items.filter((q) => chapters.includes(String(q.chapter_id)));
      }
      if (track) items = items.filter((q) => (q.track || 'course') === track);
      if (difficulty) items = items.filter((q) => String(q.difficulty) === difficulty);
      if (keyword) {
        items = items.filter((q) =>
          (q.title || '').toLowerCase().includes(keyword) ||
          (q.tags || []).join(' ').toLowerCase().includes(keyword));
      }
      if (only === 'unsolved') items = items.filter((q) => !q.solved);
      if (only === 'wrong') items = items.filter((q) => q.wrong > 0);
      const limit = parseInt(url.searchParams.get('limit') || '200', 10) || 200;
      return json({ success: true, questions: items.slice(0, limit), count: items.length });
    }

    // 单题详情
    const qMatch = path.match(/^\/api\/training\/question\/(.+)$/);
    if (qMatch) {
      const data = await detail(decodeURIComponent(qMatch[1]));
      return json(data || { success: false, message: '这道题没有随站点导出' });
    }

    // 需要写数据的接口：明确说清
    if (path === '/api/training/draft' || path === '/api/training/attempt') {
      return json({ success: true, saved: false, message: NOT_SAVED });
    }
    if (path === '/api/training/exam' || path.startsWith('/api/training/exam/')) {
      return json({ success: false, message: '实战组卷需要成绩库，在线演示站不可用。' + NOT_SAVED });
    }
    if (path === '/api/training/ai-help') {
      return json({ success: false, error: 'AI 答疑需要后端与大模型密钥，请下载本地完整版。' });
    }
    if (path === '/api/training/run-cell') {
      // 由 training.js 直接走 PyRunner，这里只兜底
      return json({ success: false, error: '请通过页面的运行按钮执行。' });
    }

    return json({ success: false, message: '在线演示站不支持这个操作。' + NOT_SAVED });
  };

  function json(payload, status) {
    return new Response(JSON.stringify(payload), {
      status: status || 200,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  }

  // 暴露给训练页面直接用（判题要带断言，走内部通道更直接）
  window.StaticQBank = api;
})();
