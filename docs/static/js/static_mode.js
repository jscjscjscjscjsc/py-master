/* 在线演示站（GitHub Pages）适配层。
 *
 * 导出的静态站没有后端：课程正文、讲解样例、星海图这些"读数据"的功能照常，
 * 而 AI 答疑、账号与学习记录、在线判题、代码运行必须跑 Flask 才有意义。
 * 这里把那些请求接住并给出人话提示——不能让页面停在"加载中"或者弹一堆 404，
 * 那看起来就像平台坏了。
 *
 * 只有 build_static_docs.py 导出的页面会加载本文件；本地部署不加载，
 * 平台行为与原来完全一致。
 */
(function () {
  window.PYMASTER_STATIC = true;

  // ── 后端路由 → 同名静态页 ─────────────────────────────
  var PAGE_MAP = {
    '/dashboard': 'index.html',
    '/playground': 'playground.html',
    '/canvas': 'canvas.html',
    '/stars': 'stars.html',
    '/update': 'update.html',
    '/intro': 'intro.html',
    // 刷题中心现在也能在线用：题库随站点导出，判题交给浏览器里的
    // Python（Pyodide），整条链路（选题→写码→运行→判题→看解析）都走得通
    '/training': 'training.html'
  };
  // 这些页面依赖后端才有意义，在线站不导出
  var BACKEND_ONLY = {
    '/coach': '星辰教练要接大模型，需本地部署',
    '/progress': '学习仪表盘读的是你的本地学习记录',
    '/cultivation': '修行阁读的是你的本地修为与作答档案',
    '/login': '账号要存在本地数据库里',
    '/logout': '账号要存在本地数据库里',
    '/setup': '模型密钥只存在你自己电脑上',
    '/admin': '管理后台需本地部署'
  };

  function pathOf(path) {
    return String(path || '').split('?')[0].split('#')[0].replace(/\/+$/, '') || '/';
  }

  window.pmStaticUrl = function (path) {
    var clean = pathOf(path);
    if (PAGE_MAP[clean]) return PAGE_MAP[clean];
    var chapter = clean.match(/^\/chapter\/(\d+)$/);
    return chapter ? 'chapter-' + chapter[1] + '.html' : null;
  };

  // 跳转到后端路由：能映射到静态页就过去，否则给出提示
  window.pmGo = function (path) {
    var url = window.pmStaticUrl(path);
    if (url) { window.location.href = url; return true; }
    window.pmStaticNotice(BACKEND_ONLY[pathOf(path)]);
    return false;
  };

  window.pmStaticNotice = function (extra) {
    var text = extra || '这个功能需要本地部署后才能用';
    if (typeof window.showToast === 'function') {
      window.showToast('🧪 在线演示站：' + text, 'info');
      return;
    }
    var el = document.getElementById('pm-static-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'pm-static-toast';
      el.style.cssText = 'position:fixed;left:50%;bottom:36px;transform:translateX(-50%);' +
        'background:#161b22;border:1px solid #00d4ff55;color:#cfe3ff;padding:12px 20px;' +
        'border-radius:10px;z-index:99999;font-size:14px;max-width:80vw;text-align:center;';
      document.body.appendChild(el);
    }
    el.textContent = '🧪 在线演示站：' + text;
    clearTimeout(el._pmTimer);
    el._pmTimer = setTimeout(function () { el.remove(); }, 3600);
  };

  // ── 接住后端请求 ──────────────────────────────────────
  function jsonResponse(payload, status) {
    return new Response(JSON.stringify(payload), {
      status: status || 200,
      headers: { 'Content-Type': 'application/json; charset=utf-8' }
    });
  }

  var GUEST = {
    username: 'guest', mode: 'all_unlocked', completed_kps: [],
    completed_exercises: [], favorites: [], wrong_answers: [], notes: {}
  };
  var CHATTY = ['/api/ask-jj', '/api/score-code', '/api/score-answer', '/api/chapter-agent',
                '/api/coach/chat', '/api/training/ai-help', '/api/jj-chapter'];
  var RUNNER = ['/api/run-code', '/api/lint-code', '/api/training/', '/api/narration/', '/api/tts/'];

  function degrade(path) {
    if (path === '/api/user') return jsonResponse(GUEST);
    if (path === '/api/glossary') return null;  // 走本地 JSON，见下
    if (path === '/api/ai-quota') {
      return jsonResponse({ success: false, error: '在线演示站不含 AI 额度' });
    }
    for (var i = 0; i < CHATTY.length; i++) {
      if (path.indexOf(CHATTY[i]) === 0) {
        return jsonResponse({ success: false, error:
          '在线演示站不接大模型。下载本地版并填入自己的模型密钥，就能用 JJ 老师答疑和 AI 批改。' });
      }
    }
    for (var j = 0; j < RUNNER.length; j++) {
      if (path.indexOf(RUNNER[j]) === 0) {
        return jsonResponse({ success: false, error:
          '运行代码 / 在线判题需要在本地部署后使用（演示站没有 Python 执行环境）。' });
      }
    }
    return jsonResponse({ success: false, error:
      '在线演示站没有后端，收藏、错题、进度、笔记这类要存数据的功能请在本地版使用。' });
  }

  var realFetch = window.fetch ? window.fetch.bind(window) : null;
  window.fetch = function (input, init) {
    var raw = typeof input === 'string' ? input : (input && input.url) || '';
    var path = raw;
    try { path = new URL(raw, window.location.href).pathname; } catch (e) {}
    var api = path.match(/\/api\/.*$/);
    if (!api) return realFetch ? realFetch(input, init) : Promise.reject(new Error('no fetch'));
    var apiPath = api[0];

    if (apiPath === '/api/glossary') {
      // 术语表是纯静态数据，导出了就照常用
      return realFetch('data/glossary.json', init).then(function (res) {
        if (res.ok) return res;
        return realFetch(input, init);
      }).catch(function () { return realFetch(input, init); });
    }
    return Promise.resolve(degrade(apiPath));
  };

  // ── 兜底：任何指向后端路由的链接都不要跳出站点 ─────────
  document.addEventListener('click', function (event) {
    var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (!href.startsWith('/') || href.startsWith('//')) return;
    var target = window.pmStaticUrl(href);
    event.preventDefault();
    if (target) { window.location.href = target; return; }
    window.pmStaticNotice(BACKEND_ONLY[pathOf(href)]);
  }, true);

  // ── 顶部说明条：让访客知道"在线能做什么" ──────────────
  function banner() {
    if (sessionStorage.getItem('pm-static-banner') === 'off') return;
    var bar = document.createElement('div');
    bar.id = 'pm-static-banner';
    bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:99998;display:flex;' +
      'gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;padding:10px 46px 10px 18px;' +
      'background:linear-gradient(90deg,#0b1220ee,#0e1a2aee);border-top:1px solid #00d4ff44;' +
      'color:#cfe3ff;font-size:13.5px;line-height:1.6;backdrop-filter:blur(6px);';
    bar.innerHTML = '<span>🧪 <b>在线演示站</b>：课程正文、讲解样例、星海图、' +
      '<b>刷题中心（可直接运行与判题）</b>都能用；' +
      '<b>AI 答疑 / 成绩保存 / 修为积分</b>需要下载本地版</span>' +
      '<button style="background:#00d4ff22;border:1px solid #00d4ff55;color:#9fd9ff;' +
      'border-radius:8px;padding:4px 12px;cursor:pointer;font-size:13px;">知道了</button>';
    bar.querySelector('button').onclick = function () {
      sessionStorage.setItem('pm-static-banner', 'off');
      bar.remove();
    };
    document.body.appendChild(bar);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', banner);
  } else {
    banner();
  }
})();
