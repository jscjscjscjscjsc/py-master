/* ==========================================================================
   PyMaster · 五分钟图文讲解播放器
   一节讲解 = N 个镜头；每个镜头 = 一张漫画插画 + 一段 edge-tts 口播 + 讲义要点。
   播放时按镜头推进，口播结束自动翻页；讲义里当前句按字数比例高亮。
   ========================================================================== */
(function () {
  'use strict';

  var state = {
    chapterId: null,
    kpIndex: null,
    kpTitle: '',
    data: null,
    scene: 0,
    playing: false,
    autoNext: true,
    speed: 1,
    audio: null,
    elapsedBefore: 0,
    sentenceTimer: null,
    pollTimer: null,
    jobId: null
  };

  var el = {};
  var KIND_LABEL = {
    hook: '开场', concept: '概念', code: '代码',
    compare: '对比', pitfall: '踩坑', summary: '总结'
  };

  function $(id) { return document.getElementById(id); }

  function fmt(seconds) {
    seconds = Math.max(0, Math.round(seconds || 0));
    var m = Math.floor(seconds / 60);
    var s = seconds % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function totalOf(data) {
    return data.scenes.reduce(function (sum, s) { return sum + (s.audio_seconds || 0); }, 0);
  }

  function startOf(data, index) {
    var sum = 0;
    for (var i = 0; i < index; i++) { sum += data.scenes[i].audio_seconds || 0; }
    return sum;
  }

  /* ── 构建界面骨架 ─────────────────────────────────────── */
  function buildSkeleton() {
    if (el.overlay) { return; }
    var overlay = document.createElement('div');
    overlay.className = 'nr-overlay';
    overlay.id = 'nr-overlay';
    overlay.innerHTML = [
      '<div class="nr-top">',
      '  <div class="nr-brand"><span class="nr-brand-dot"></span>5 分钟图文讲解</div>',
      '  <div class="nr-top-title" id="nr-top-title"></div>',
      '  <div class="nr-counter" id="nr-counter">0 / 0</div>',
      '  <button class="nr-icon-btn" id="nr-close">✕ 退出</button>',
      '</div>',
      '<div id="nr-content" style="flex:1;display:flex;flex-direction:column;min-height:0"></div>'
    ].join('');
    document.body.appendChild(overlay);
    el.overlay = overlay;
    el.content = $('nr-content');
    el.topTitle = $('nr-top-title');
    el.counter = $('nr-counter');
    $('nr-close').addEventListener('click', close);
  }

  function stageMarkup() {
    return [
      '<div class="nr-stage">',
      '  <div class="nr-scene" id="nr-scene">',
      '    <img id="nr-image" alt="讲解配图">',
      '    <div class="nr-scene-badge"><span class="nr-kind" id="nr-kind"></span>',
      '      <span id="nr-scene-title"></span></div>',
      '  </div>',
      '  <div class="nr-script">',
      '    <div class="nr-script-head">',
      '      <div class="nr-script-kicker" id="nr-kicker">镜头讲义</div>',
      '      <div class="nr-script-title" id="nr-title"></div>',
      '    </div>',
      '    <div class="nr-caption" id="nr-caption"></div>',
      '    <div class="nr-script-body">',
      '      <div class="nr-narration" id="nr-narration"></div>',
      '      <div class="nr-code" id="nr-code" style="display:none">',
      '        <div class="nr-code-head"><span>代码演示</span><span>点击可选中复制</span></div>',
      '        <pre><code id="nr-code-body"></code></pre>',
      '      </div>',
      '    </div>',
      '  </div>',
      '</div>',
      '<div class="nr-bar">',
      '  <div class="nr-progress" id="nr-progress">',
      '    <div class="nr-progress-fill" id="nr-progress-fill"></div>',
      '    <div class="nr-progress-marks" id="nr-progress-marks"></div>',
      '  </div>',
      '</div>',
      '<div class="nr-controls">',
      '  <button class="nr-btn" id="nr-prev">◀ 上一镜头</button>',
      '  <button class="nr-btn nr-btn-main" id="nr-play">▶ 播放</button>',
      '  <button class="nr-btn" id="nr-next">下一镜头 ▶</button>',
      '  <span class="nr-time" id="nr-time">0:00 / 0:00</span>',
      '  <span class="nr-spacer"></span>',
      '  <select class="nr-speed" id="nr-speed">',
      '    <option value="0.75">0.75×</option>',
      '    <option value="1" selected>1.0×</option>',
      '    <option value="1.25">1.25×</option>',
      '    <option value="1.5">1.5×</option>',
      '  </select>',
      '  <label class="nr-toggle"><input type="checkbox" id="nr-auto" checked>自动连播</label>',
      isStatic() ? '' : '  <button class="nr-btn" id="nr-done">✓ 学完这节</button>',
      '</div>',
      '<div class="nr-strip" id="nr-strip"></div>'
    ].join('');
  }

  /* ── 打开 / 渲染 ──────────────────────────────────────── */
  function open(chapterId, kpIndex, kpTitle) {
    buildSkeleton();
    state.chapterId = chapterId;
    state.kpIndex = kpIndex;
    state.kpTitle = kpTitle || '';
    state.scene = 0;
    state.data = null;
    el.overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    el.topTitle.innerHTML = '正在载入 <strong>' + escapeHtml(state.kpTitle) + '</strong>';
    el.counter.textContent = '…';
    el.content.innerHTML = '<div class="nr-empty"><div class="nr-build-bar"><i></i></div>' +
      '<p>正在取讲解…</p></div>';
    fetchNarration();
  }

  function escapeHtml(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // 静态展示（GitHub Pages）没有 Flask 后端，讲解数据改为读本地 JSON；
  // 页面里只要设置 window.PYMASTER_STATIC = true 即可切换，不必维护两份代码。
  function isStatic() { return Boolean(window.PYMASTER_STATIC); }

  function narrationUrl(chapterId, kpIndex) {
    return isStatic()
      ? 'data/narrations/' + chapterId + '_' + kpIndex + '.json'
      : '/api/narration/' + chapterId + '/' + kpIndex;
  }

  function fetchNarration() {
    fetch(narrationUrl(state.chapterId, state.kpIndex))
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (res.available) {
          state.data = res.narration;
          renderPlayer();
        } else {
          renderMissing();
        }
      })
      .catch(function () { renderMissing('网络异常，请稍后重试'); });
  }

  function renderMissing(message) {
    var staticMode = isStatic();
    el.content.innerHTML = [
      '<div class="nr-empty">',
      '  <div class="nr-empty-icon">🎬</div>',
      '  <h3>' + (staticMode ? '这一节讲解暂未收录到在线预览' : '这节讲解还在制作中') + '</h3>',
      '  <p id="nr-missing-msg">' + escapeHtml(message ||
           (staticMode
             ? '在线预览只收录了少量样例讲解。完整讲解请在本地运行 PyMaster：'
               + '讲解由大模型撰写分镜、本地程序化作图、edge-tts 合成口播，全部可离线复现。'
             : '五分钟图文讲解由大模型现场撰写分镜、生成配图并合成口播，一节需要 3–5 分钟。')) + '</p>',
      staticMode ? '' :
        '  <button class="nr-btn nr-btn-main" id="nr-generate">⚡ 现在为这一节生成讲解</button>',
      staticMode ? '' : '  <div class="nr-build-bar" id="nr-build-bar" style="display:none"><i></i></div>',
      staticMode ? '' : '  <div class="nr-build-log" id="nr-build-log" style="display:none"></div>',
      '</div>'
    ].join('');
    el.counter.textContent = '—';
    var button = $('nr-generate');
    if (button) { button.addEventListener('click', requestBuild); }
  }

  function requestBuild() {
    var button = $('nr-generate');
    button.disabled = true;
    button.textContent = '正在排队…';
    fetch('/api/narration/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: state.chapterId, kp_index: state.kpIndex })
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.success && res.status !== 'running' && res.status !== 'already') {
        $('nr-missing-msg').textContent = res.message || '生成失败';
        button.disabled = false;
        button.textContent = '⚡ 重新尝试';
        return;
      }
      if (res.status === 'already') { fetchNarration(); return; }
      state.jobId = res.job_id;
      $('nr-build-bar').style.display = 'block';
      $('nr-build-log').style.display = 'block';
      logLine(res.message || '已开始生成');
      pollJob();
    }).catch(function () {
      button.disabled = false;
      button.textContent = '⚡ 重新尝试';
    });
  }

  function logLine(text) {
    var log = $('nr-build-log');
    if (!log) { return; }
    log.textContent += (log.textContent ? '\n' : '') + text;
    log.scrollTop = log.scrollHeight;
  }

  function pollJob() {
    clearTimeout(state.pollTimer);
    fetch('/api/narration/job/' + state.jobId)
      .then(function (r) { return r.json(); })
      .then(function (job) {
        if (job.message) { logLine(job.message); }
        if (job.status === 'done') {
          $('nr-build-bar').style.display = 'none';
          logLine('✓ 生成完成，正在打开…');
          setTimeout(fetchNarration, 700);
          return;
        }
        if (job.status === 'error') {
          $('nr-build-bar').style.display = 'none';
          var button = $('nr-generate');
          if (button) { button.disabled = false; button.textContent = '⚡ 重新尝试'; }
          return;
        }
        state.pollTimer = setTimeout(pollJob, 2500);
      })
      .catch(function () { state.pollTimer = setTimeout(pollJob, 4000); });
  }

  function renderPlayer() {
    el.content.innerHTML = stageMarkup();
    var data = state.data;
    el.topTitle.innerHTML = '第 ' + state.chapterId + ' 章 · <strong>' +
      escapeHtml(data.kp_title) + '</strong>';
    el.counter.textContent = '共 ' + data.scene_count + ' 镜头 · ' +
      fmt(totalOf(data));

    el.scene = $('nr-scene');
    el.image = $('nr-image');
    el.kind = $('nr-kind');
    el.sceneTitle = $('nr-scene-title');
    el.title = $('nr-title');
    el.caption = $('nr-caption');
    el.narration = $('nr-narration');
    el.code = $('nr-code');
    el.codeBody = $('nr-code-body');
    el.progress = $('nr-progress');
    el.fill = $('nr-progress-fill');
    el.marks = $('nr-progress-marks');
    el.time = $('nr-time');
    el.play = $('nr-play');
    el.strip = $('nr-strip');

    renderStrip();
    renderMarks();
    bindControls();
    goto(0, false);
  }

  function renderStrip() {
    el.strip.innerHTML = state.data.scenes.map(function (scene, index) {
      return '<div class="nr-thumb" data-index="' + index + '" title="' +
        escapeHtml(scene.title) + '"><img loading="lazy" src="/static/' +
        escapeHtml(scene.image) + '" alt=""><span>' + (index + 1) + '</span></div>';
    }).join('');
    el.strip.querySelectorAll('.nr-thumb').forEach(function (node) {
      node.addEventListener('click', function () {
        goto(parseInt(node.dataset.index, 10), state.playing);
      });
    });
  }

  function renderMarks() {
    var total = totalOf(state.data) || 1;
    var html = '';
    state.data.scenes.forEach(function (scene) {
      var at = startOf(state.data, scene.id - 1) / total * 100;
      html += '<span class="nr-mark" data-at="' + at + '" style="left:' + at + '%"></span>';
    });
    el.marks.innerHTML = html;
  }

  function bindControls() {
    $('nr-prev').addEventListener('click', function () { goto(state.scene - 1, state.playing); });
    $('nr-next').addEventListener('click', function () { goto(state.scene + 1, state.playing); });
    el.play.addEventListener('click', toggle);
    $('nr-auto').addEventListener('change', function (e) { state.autoNext = e.target.checked; });
    $('nr-speed').addEventListener('change', function (e) {
      state.speed = parseFloat(e.target.value);
      if (state.audio) { state.audio.playbackRate = state.speed; }
    });
    var doneBtn = $('nr-done');
    if (doneBtn) { doneBtn.addEventListener('click', markDone); }
    el.progress.addEventListener('click', function (e) {
      var ratio = (e.clientX - el.progress.getBoundingClientRect().left) /
        el.progress.offsetWidth;
      var target = ratio * totalOf(state.data);
      var acc = 0;
      for (var i = 0; i < state.data.scenes.length; i++) {
        acc += state.data.scenes[i].audio_seconds || 0;
        if (target <= acc) { goto(i, state.playing); return; }
      }
      goto(state.data.scenes.length - 1, state.playing);
    });
    if (!state.keysBound) {
      document.addEventListener('keydown', onKey);
      state.keysBound = true;
    }
  }

  function onKey(e) {
    if (!el.overlay || !el.overlay.classList.contains('is-open')) { return; }
    if (e.target && /INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) { return; }
    if (e.key === 'Escape') { close(); }
    else if (e.key === ' ') { e.preventDefault(); toggle(); }
    else if (e.key === 'ArrowRight') { goto(state.scene + 1, state.playing); }
    else if (e.key === 'ArrowLeft') { goto(state.scene - 1, state.playing); }
  }

  /* ── 镜头切换与播放 ───────────────────────────────────── */
  function goto(index, autoplay) {
    var scenes = state.data.scenes;
    if (index < 0 || index >= scenes.length) { return; }
    stopAudio();
    state.scene = index;
    var scene = scenes[index];

    el.scene.classList.add('is-swapping');
    var preload = new Image();
    preload.onload = function () {
      el.image.src = preload.src;
      el.scene.classList.remove('is-swapping');
    };
    preload.src = '/static/' + scene.image;
    if (preload.complete) { el.image.src = preload.src; el.scene.classList.remove('is-swapping'); }

    el.kind.textContent = KIND_LABEL[scene.type] || '讲解';
    el.kind.className = 'nr-kind nr-kind-' + (scene.type || 'concept');
    el.sceneTitle.textContent = scene.title || '';
    el.title.textContent = scene.title || state.data.title;
    el.caption.textContent = scene.caption || '';
    renderNarration(scene.narration || '');
    if (scene.code) {
      el.code.style.display = 'block';
      el.codeBody.textContent = scene.code;
    } else {
      el.code.style.display = 'none';
    }

    el.strip.querySelectorAll('.nr-thumb').forEach(function (node) {
      node.classList.toggle('is-active', parseInt(node.dataset.index, 10) === index);
    });
    var active = el.strip.querySelector('.nr-thumb.is-active');
    if (active && active.scrollIntoView) {
      active.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
    }

    el.counter.textContent = (index + 1) + ' / ' + scenes.length + ' · ' +
      fmt(totalOf(state.data));
    updateTime(index, 0);
    el.play.textContent = autoplay ? '⏸ 暂停' : '▶ 播放';
    state.playing = false;
    if (autoplay) { play(); }
  }

  function renderNarration(text) {
    // 按句号类标点切句，播放时按字数比例逐句高亮
    var parts = [];
    var buffer = '';
    for (var i = 0; i < text.length; i++) {
      buffer += text[i];
      if ('。！？；!?;'.indexOf(text[i]) >= 0 && buffer.trim()) {
        parts.push(buffer);
        buffer = '';
      }
    }
    if (buffer.trim()) { parts.push(buffer); }
    if (!parts.length) { parts = [text]; }
    el.narration.innerHTML = parts.map(function (sentence) {
      return '<span class="nr-sent">' + escapeHtml(sentence) + '</span>';
    }).join('');
  }

  function toggle() { state.playing ? pause() : play(); }

  function play() {
    var scene = state.data.scenes[state.scene];
    if (!scene || !scene.audio_url) { return; }
    if (!state.audio || state.audio.dataset.scene !== String(scene.id)) {
      state.audio = new Audio(scene.audio_url);
      state.audio.dataset.scene = String(scene.id);
      state.audio.playbackRate = state.speed;
      state.audio.addEventListener('timeupdate', onTimeUpdate);
      state.audio.addEventListener('ended', onEnded);
      state.audio.addEventListener('error', function () { state.playing = false; syncPlayButton(); });
    }
    state.audio.playbackRate = state.speed;
    state.playing = true;
    state.audio.play().catch(function () { state.playing = false; syncPlayButton(); });
    syncPlayButton();
    startSentenceTimer();
  }

  function pause() {
    state.playing = false;
    if (state.audio) { state.audio.pause(); }
    clearInterval(state.sentenceTimer);
    syncPlayButton();
  }

  function stopAudio() {
    clearInterval(state.sentenceTimer);
    if (state.audio) {
      state.audio.pause();
      state.audio.removeEventListener('timeupdate', onTimeUpdate);
      state.audio.removeEventListener('ended', onEnded);
      state.audio = null;
    }
    state.playing = false;
  }

  function syncPlayButton() {
    if (el.play) { el.play.textContent = state.playing ? '⏸ 暂停' : '▶ 播放'; }
  }

  function onTimeUpdate() {
    if (!state.audio) { return; }
    updateTime(state.scene, state.audio.currentTime || 0);
  }

  function onEnded() {
    if (!state.autoNext) { state.playing = false; syncPlayButton(); return; }
    if (state.scene + 1 < state.data.scenes.length) {
      goto(state.scene + 1, true);
    } else {
      state.playing = false;
      syncPlayButton();
      updateTime(state.scene, state.data.scenes[state.scene].audio_seconds || 0);
      awardCompletion();
    }
  }

  // 整节讲解播完给一次修为奖励。服务端按 (章节, 知识点) 去重，
  // 反复看同一节不会重复刷分，所以这里放心每次都报。
  function awardCompletion() {
    if (state.awarded) { return; }
    state.awarded = true;
    fetch('/api/cultivation/award', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason: 'narration', ref: state.chapterId + '_' + state.kpIndex })
    }).then(function (r) { return r.json(); }).then(function (data) {
      if (!data || !data.success) { return; }
      if (window.Cultivation) {
        if (data.awarded) Cultivation.applySettlement(data);
        else if (data.profile) { Cultivation.profile = data.profile; Cultivation.render({}); }
      }
    }).catch(function () {});
  }

  function updateTime(index, offset) {
    var total = totalOf(state.data) || 1;
    var current = startOf(state.data, index) + offset;
    el.time.textContent = fmt(current) + ' / ' + fmt(total);
    var ratio = Math.min(1, current / total);
    el.fill.style.width = (ratio * 100) + '%';
    el.marks.querySelectorAll('.nr-mark').forEach(function (mark) {
      mark.classList.toggle('is-done', parseFloat(mark.dataset.at) <= ratio * 100 + 0.01);
    });
  }

  function startSentenceTimer() {
    clearInterval(state.sentenceTimer);
    var nodes = el.narration.querySelectorAll('.nr-sent');
    if (nodes.length < 2) { return; }
    var lengths = Array.prototype.map.call(nodes, function (n) { return n.textContent.length || 1; });
    var totalLen = lengths.reduce(function (a, b) { return a + b; }, 0);
    var duration = state.data.scenes[state.scene].audio_seconds || 1;
    var offsets = [];
    var acc = 0;
    lengths.forEach(function (len) {
      offsets.push({ start: acc / totalLen * duration, end: (acc + len) / totalLen * duration });
      acc += len;
    });
    state.sentenceTimer = setInterval(function () {
      if (!state.audio) { return; }
      var t = state.audio.currentTime || 0;
      var active = 0;
      for (var i = 0; i < offsets.length; i++) {
        if (t >= offsets[i].start) { active = i; }
      }
      nodes.forEach(function (node, i) {
        node.style.background = i === active ? 'rgba(184, 136, 59, 0.28)' : 'transparent';
      });
    }, 220);
  }

  function markDone() {
    fetch('/api/complete-kp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: state.chapterId, kp_index: state.kpIndex })
    }).then(function () {
      var button = $('nr-done');
      if (button) { button.textContent = '✓ 已标记完成'; }
      if (typeof showToast === 'function') { showToast('已标记为学完', 'success'); }
    }).catch(function () {});
  }

  function close() {
    clearTimeout(state.pollTimer);
    stopAudio();
    if (el.overlay) { el.overlay.classList.remove('is-open'); }
    document.body.style.overflow = '';
  }

  window.NarrationPlayer = { open: open, close: close, state: state };
})();
