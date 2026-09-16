/* ============================================================
   PyMaster — Main JavaScript
   ============================================================ */

// ==================== Particle System ====================
(function() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let animationId;
  const PARTICLE_COUNT = 80;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  class Particle {
    constructor() {
      this.reset();
      this.y = Math.random() * canvas.height;
      this.opacity = Math.random() * 0.5 + 0.1;
    }
    reset() {
      this.x = Math.random() * canvas.width;
      this.y = -10;
      this.size = Math.random() * 2 + 0.5;
      this.speed = Math.random() * 0.6 + 0.2;
      this.opacity = Math.random() * 0.5 + 0.1;
      this.wobble = Math.random() * Math.PI * 2;
      this.wobbleSpeed = (Math.random() - 0.5) * 0.02;
      this.wobbleAmp = Math.random() * 0.5;
    }
    update() {
      this.y += this.speed;
      this.wobble += this.wobbleSpeed;
      this.x += Math.sin(this.wobble) * this.wobbleAmp;
      if (this.y > canvas.height + 10) {
        this.reset();
        this.y = -10;
      }
    }
    draw(ctx) {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      const color = this.size > 1.5 ? '0, 212, 255' : '163, 113, 247';
      ctx.fillStyle = `rgba(${color}, ${this.opacity})`;
      ctx.fill();
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size * 2.5, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color}, ${this.opacity * 0.15})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push(new Particle());
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => { p.update(); p.draw(ctx); });
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 212, 255, ${0.04 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    animationId = requestAnimationFrame(animate);
  }
  animate();
})();

// ==================== Toast ====================
function showToast(message, type) {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3000);
}

// ==================== Auth Page Logic ====================
(function() {
  const tabBtns = document.querySelectorAll('.auth-tab');
  if (!tabBtns.length) return;
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      tabBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      const target = this.dataset.tab;
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      if (target === 'login') loginForm.classList.add('active');
      else registerForm.classList.add('active');
    });
  });

  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    if (!username || !password) { showToast('请填写用户名和密码', 'error'); return; }
    try {
      const res = await fetch('/api/login', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) { showToast('登录成功！正在跳转...', 'success'); setTimeout(() => { window.location.href = '/dashboard'; }, 600); }
      else showToast(data.message, 'error');
    } catch (err) { showToast('网络错误，请稍后重试', 'error'); }
  });

  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-password-confirm').value;
    if (!username || !password || !confirm) { showToast('请填写所有字段', 'error'); return; }
    if (username.length < 3) { showToast('用户名至少3个字符', 'error'); return; }
    if (password.length < 6) { showToast('密码至少6个字符', 'error'); return; }
    if (password !== confirm) { showToast('两次输入的密码不一致', 'error'); return; }
    try {
      const res = await fetch('/api/register', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) { showToast('注册成功！请登录', 'success'); tabBtns[0].click(); document.getElementById('login-username').value = username; registerForm.reset(); }
      else showToast(data.message, 'error');
    } catch (err) { showToast('网络错误，请稍后重试', 'error'); }
  });
})();

// ==================== Chapter Page Logic ====================
(function() {
  const tabs = document.querySelectorAll('.section-tab');
  if (!tabs.length) return;
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');
      const target = this.dataset.panel;
      document.getElementById('knowledge-panel').classList.toggle('active', target === 'knowledge');
      const ep = document.getElementById('exercise-panel');
      if (ep) ep.classList.toggle('active', target === 'exercise');
    });
  });
})();

function toggleKP(header) {
  const item = header.parentElement;
  item.classList.toggle('open');
}

// ==================== Learning System ====================

// --- Choice Exercise ---
function submitChoiceEx(btn, chapterId, kpIndex, exIndex) {
  const card = btn.closest('.kp-exercise');
  const selected = card.querySelector('.ex-option.selected');
  if (!selected) { showToast('请先选择一个答案', 'error'); return; }
  if (card.dataset.exSubmitted === 'true') { showToast('已完成此题', 'error'); return; }

  const optionsDiv = card.querySelector('.ex-options');
  const correctIdx = parseInt(optionsDiv.dataset.correct);
  const chosenIdx = parseInt(selected.dataset.opt);
  const allOpts = card.querySelectorAll('.ex-option');
  const question = card.querySelector('.ex-question')?.textContent || '';
  const optLabels = ['A','B','C','D'];

  card.dataset.exSubmitted = 'true';
  btn.disabled = true;

  allOpts.forEach((opt, i) => {
    opt.style.pointerEvents = 'none';
    if (i === correctIdx) opt.classList.add('correct');
  });

  const correctAnswer = optLabels[correctIdx];
  const userAnswer = optLabels[chosenIdx];

  if (chosenIdx === correctIdx) {
    selected.classList.add('correct');
    showToast('✅ 回答正确！', 'success');
    fetch('/api/submit-answer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex, ex_index: exIndex,
        correct: true, question, user_answer: userAnswer, correct_answer: correctAnswer })
    });
    checkKPCompletion(chapterId, kpIndex, card);
  } else {
    selected.classList.add('wrong');
    showToast('❌ 回答错误，已记录到错题本', 'error');
    fetch('/api/submit-answer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex, ex_index: exIndex,
        correct: false, question, user_answer: userAnswer, correct_answer: correctAnswer })
    });
  }
}

function showExAnswer(btn) {
  const card = btn.closest('.kp-exercise');
  const answerDiv = card.querySelector('.ex-answer');
  const optionsDiv = card.querySelector('.ex-options');

  // 选择题才需要顺带标出正确选项。教材原题（open 型）没有选项，
  // 这里以前直接读 dataset 会抛错，表现为"查看参考答案"点了没反应。
  if (optionsDiv) {
    const correctIdx = parseInt(optionsDiv.dataset.correct, 10);
    if (card.dataset.exSubmitted !== 'true') {
      card.querySelectorAll('.ex-option').forEach((opt, i) => {
        opt.style.pointerEvents = 'none';
        if (i === correctIdx) opt.classList.add('correct');
      });
    }
  }
  const opening = answerDiv.style.display === 'none';
  answerDiv.style.display = opening ? 'block' : 'none';
  btn.textContent = opening ? '收起参考答案' : '查看参考答案';
}

/* ── 教材原题的"文字作答"与 AI 批改 ────────────────────────
   题干、参考答案、解析都从 DOM 读取，不往 onclick 属性里塞长文本：
   参考答案动辄上千字，塞进属性既臃肿又容易被引号截断。 */

function toggleTextAnswer(btn) {
  const card = btn.closest('.kp-exercise');
  const box = card.querySelector('.ex-text-answer');
  if (!box) return;
  const opening = box.style.display === 'none';
  box.style.display = opening ? 'block' : 'none';
  btn.textContent = opening ? '收起作答区' : '✍️ 文字作答';
  if (opening) {
    const input = box.querySelector('.ex-text-input');
    if (input) input.focus();
  }
}

async function submitTextAnswer(btn) {
  const card = btn.closest('.kp-exercise');
  const box = card.querySelector('.ex-text-answer');
  const input = box.querySelector('.ex-text-input');
  const result = box.querySelector('.ex-ai-result');
  const answer = (input.value || '').trim();

  if (answer.length < 4) {
    showToast('先写下你的作答再提交', 'error');
    return;
  }

  const questionEl = card.querySelector('.ex-question');
  const question = questionEl ? questionEl.innerText : '';
  const answerNodes = card.querySelectorAll('.ex-answer .answer-text');
  const reference = answerNodes[0] ? answerNodes[0].innerText : '';
  const explanation = answerNodes[1] ? answerNodes[1].innerText : '';

  btn.disabled = true;
  btn.textContent = 'AI 批改中…';
  result.style.display = 'block';
  result.innerHTML = '<div class="ex-ai-pending">正在对照参考答案批改，请稍候…</div>';

  try {
    const res = await fetch('/api/score-answer', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer, reference, explanation })
    });
    const data = await res.json();
    if (!data.success) {
      result.innerHTML = '<div class="ex-ai-pending">批改失败：' +
        escapeHtml(data.message || '请稍后重试') + '</div>';
      return;
    }
    const score = Math.max(0, Math.min(100, data.score || 0));
    const tone = score >= 85 ? 'good' : (score >= 60 ? 'ok' : 'bad');
    result.innerHTML =
      '<div class="ex-ai-score ' + tone + '">AI 评分：<strong>' + score + '</strong> / 100</div>' +
      (data.feedback ? '<div class="ex-ai-line"><b>评语：</b>' + escapeHtml(data.feedback) + '</div>' : '') +
      (data.strengths ? '<div class="ex-ai-line"><b>答得好的地方：</b>' + escapeHtml(data.strengths) + '</div>' : '') +
      (data.weaknesses ? '<div class="ex-ai-line"><b>可以补充：</b>' + escapeHtml(data.weaknesses) + '</div>' : '') +
      '<div class="ex-ai-hint">对照下面的参考答案再检查一遍，印象更深。</div>';
    if (score >= 60) {
      const answerDiv = card.querySelector('.ex-answer');
      if (answerDiv) answerDiv.style.display = 'block';
    }
  } catch (e) {
    result.innerHTML = '<div class="ex-ai-pending">网络异常，批改失败，请重试。</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = '重新提交批改';
  }
}

// --- Code Exercise (CodeMirror Enhanced Editor) ---
let codeExState = { chapterId: null, kpIndex: null, exIndex: null };
let codeMirrorEditor = null;
let codeExLintTimer = null;

function initCodeMirror() {
  const textarea = document.getElementById('code-ex-editor');
  if (!textarea || codeMirrorEditor) return;
  codeMirrorEditor = CodeMirror.fromTextArea(textarea, {
    mode: 'python',
    theme: 'material-darker',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    styleActiveLine: true,
    viewportMargin: Infinity,
    extraKeys: {
      'Ctrl-/': cm => cm.toggleComment({ indent: true }),
      'Cmd-/': cm => cm.toggleComment({ indent: true }),
      Tab: cm => cm.execCommand('insertTab'),
      Enter: cm => { cm.execCommand('newlineAndIndent'); runLintCheck(); },
    }
  });
  codeMirrorEditor.setSize('100%', '100%');
  // Debounced lint on change
  codeMirrorEditor.on('change', () => {
    clearTimeout(codeExLintTimer);
    codeExLintTimer = setTimeout(runLintCheck, 800);
  });
  // Fix: prevent delete/backspace from triggering browser back
  codeMirrorEditor.getInputField().addEventListener('keydown', e => {
    if (e.key === 'Backspace' || e.key === 'Delete') e.stopPropagation();
  });
}

async function runLintCheck() {
  if (!codeMirrorEditor) return;
  const code = codeMirrorEditor.getValue();
  const errEl = document.getElementById('code-ex-lint-errors');
  if (!code.trim()) { if (errEl) errEl.textContent = ''; return; }
  try {
    const res = await fetch('/api/lint-code', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });
    const data = await res.json();
    if (!data.success) return;
    // Clear old lint markers
    codeMirrorEditor.clearGutter('CodeMirror-lint-markers');
    if (errEl) errEl.textContent = '';
    if (data.errors && data.errors.length > 0) {
      if (errEl) errEl.textContent = `⚠️ ${data.errors.length} 个语法错误`;
      data.errors.forEach(err => {
        const lineIdx = Math.max(0, err.line - 1);
        const msg = err.message;
        const marker = document.createElement('div');
        marker.className = 'CodeMirror-lint-marker-error';
        marker.title = msg;
        codeMirrorEditor.setGutterMarker(lineIdx, 'CodeMirror-lint-markers', marker);
        codeMirrorEditor.addLineClass(lineIdx, 'wrap', 'cm-lint-error-line');
      });
    }
  } catch (_) {}
}

function openCodeEx(chapterId, kpIndex, exIndex, prompt, starter) {
  codeExState = { chapterId, kpIndex, exIndex };
  const promptEl = document.getElementById('code-ex-prompt');
  promptEl.textContent = '📝 ' + prompt;
  document.getElementById('code-ex-output').innerHTML = '';
  document.getElementById('code-ex-status').textContent = '';
  const errEl = document.getElementById('code-ex-lint-errors');
  if (errEl) errEl.textContent = '';
  const jjArea = document.getElementById('code-ex-jj-area');
  if (jjArea) jjArea.style.display = 'none';
  document.getElementById('code-ex-modal').classList.add('active');
  document.body.style.overflow = 'hidden';

  if (!codeMirrorEditor) initCodeMirror();
  // 教材原题会把题目要点作为注释预置进来，避免学生打开编辑器只看到一片空白
  codeMirrorEditor.setValue((starter && starter.trim())
    ? starter.replace(/\s*$/, '\n')
    : '# 在这里编写你的 Python 代码\n');
  codeMirrorEditor.clearHistory();
  codeMirrorEditor.focus();
  // 光标落到文件末尾，学生直接开始敲代码
  codeMirrorEditor.setCursor(codeMirrorEditor.lineCount(), 0);
  codeMirrorEditor.clearGutter('CodeMirror-lint-markers');
  codeMirrorEditor.eachLine(l => codeMirrorEditor.removeLineClass(l, 'wrap', 'cm-lint-error-line'));
  setTimeout(runLintCheck, 500);
}

function closeCodeEx() {
  document.getElementById('code-ex-modal').classList.remove('active');
  document.body.style.overflow = '';
}

function saveCodeAsPy() {
  if (!codeMirrorEditor) return;
  const code = codeMirrorEditor.getValue();
  const blob = new Blob([code], { type: 'text/x-python' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `pymaster_ch${codeExState.chapterId}_kp${codeExState.kpIndex}.py`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('💾 代码已保存为 .py 文件', 'success');
}

async function runCodeEx() {
  if (!codeMirrorEditor) return;
  const output = document.getElementById('code-ex-output');
  const status = document.getElementById('code-ex-status');
  const code = codeMirrorEditor.getValue().trim();

  if (!code) { showToast('请先编写代码', 'error'); return; }

  status.textContent = '运行中...';
  status.style.color = 'var(--text-muted)';
  output.innerHTML = '<div style="color:var(--text-muted);">运行中...</div>';

  try {
    const res = await fetch('/api/run-code', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code })
    });
    const data = await res.json();

    if (data.success && data.exit_code === 0) {
      output.innerHTML = '<div style="color:var(--green);">✅ 运行成功！\n\n' + escapeHtml(data.output) + '</div>';
      status.textContent = '⏳ AI评分中...';
      status.style.color = 'var(--cyan)';

      const kpItem = document.querySelector(`.kp-item[data-kp-index="${codeExState.kpIndex}"]`);
      const kpTitle = kpItem ? kpItem.querySelector('.kp-title')?.textContent?.trim() || '' : '';
      const promptText = document.getElementById('code-ex-prompt')?.textContent?.replace('💡 ', '') || '';

      let score = 70, feedback = '', strengths = '', weaknesses = '';
      try {
        const scoreRes = await fetch('/api/score-code', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            kp_title: kpTitle, code, output: data.output,
            prompt: promptText
          })
        });
        const scoreData = await scoreRes.json();
        if (scoreData.success) {
          score = scoreData.score;
          feedback = scoreData.feedback;
          strengths = scoreData.strengths;
          weaknesses = scoreData.weaknesses;
        }
      } catch (e) {}

      showScoreAnimation(score, feedback, strengths, weaknesses);

      if (score >= 60) {
        status.textContent = `✅ ${score}分 通过！`;
        status.style.color = 'var(--green)';
        showToast(`🎉 AI评分 ${score}分，知识点已标记完成`, 'success');

        fetch('/api/submit-answer', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chapter_id: codeExState.chapterId,
            kp_index: codeExState.kpIndex, ex_index: codeExState.exIndex,
            correct: true, question: '代码练习: ' + codeExState.chapterId + '_' + codeExState.kpIndex,
            user_answer: '代码运行成功', correct_answer: '代码运行成功' })
        });

        await completeKP(codeExState.chapterId, codeExState.kpIndex);

        const card = document.querySelector(
          `.kp-item[data-kp-index="${codeExState.kpIndex}"] .kp-exercise[data-ex-idx="${codeExState.exIndex}"]`
        );
        if (card) {
          card.dataset.exSubmitted = 'true';
          const resultDiv = card.querySelector('.code-result');
          if (resultDiv) resultDiv.style.display = 'block';
          const btn = card.querySelector('.btn-code-ex');
          if (btn) { btn.textContent = `✅ ${score}分`; btn.disabled = true; btn.style.opacity = '0.6'; }
          checkKPCompletion(codeExState.chapterId, codeExState.kpIndex, card);
        }

        const totalKPs = document.querySelectorAll('.kp-item').length;
        if (codeExState.kpIndex >= totalKPs - 1) {
          checkChapterComplete(codeExState.chapterId);
        }

        setTimeout(closeCodeEx, 2000);
      } else {
        status.textContent = `❌ ${score}分 未通过`;
        status.style.color = 'var(--red)';
        showToast(`AI评分 ${score}分，未达到60分及格线，请完善代码后重试`, 'error');
      }
    } else {
      let errMsg = data.error || data.output || '执行出错';
      output.innerHTML = '<div style="color:var(--red);">❌ 执行失败\n\n' + escapeHtml(errMsg) + '</div>';
      status.textContent = '❌ 执行失败';
      status.style.color = 'var(--red)';
    }
  } catch (err) {
    output.innerHTML = '<div style="color:var(--red);">❌ 网络错误: ' + err.message + '</div>';
    status.textContent = '❌ 错误';
    status.style.color = 'var(--red)';
  }
}

// --- KP Completion ---
async function completeKP(chapterId, kpIndex) {
  try {
    await fetch('/api/complete-kp', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex })
    });
  } catch (e) {}
}

function checkKPCompletion(chapterId, kpIndex, exerciseCard) {
  const kpItem = exerciseCard.closest('.kp-item');
  const allExercises = kpItem.querySelectorAll('.kp-exercise');
  let allDone = true;

  allExercises.forEach(ex => {
    if (ex.dataset.exSubmitted !== 'true') allDone = false;
  });

  if (allDone) {
    // Also update server-side completed_kps
    completeKP(chapterId, kpIndex);
    kpItem.classList.add('completed');
    // Add done badge
    let badge = kpItem.querySelector('.kp-done-badge');
    if (!badge) {
      const actions = kpItem.querySelector('.kp-actions');
      if (actions) {
        badge = document.createElement('span');
        badge.className = 'kp-done-badge';
        badge.textContent = '✅ 已完成';
        actions.appendChild(badge);
      }
    }
    // Update the indicator
    const indicator = kpItem.querySelector('.kp-indicator');
    if (indicator) indicator.textContent = '✅';

    // Unlock next KP
    const nextItem = kpItem.nextElementSibling;
    if (nextItem && nextItem.classList.contains('kp-item')) {
      nextItem.classList.remove('locked');
      nextItem.classList.add('unlocked');
      const nextHeader = nextItem.querySelector('.kp-header');
      if (nextHeader) {
        const titleSpan = nextHeader.querySelector('.kp-title span:first-child');
        if (titleSpan) titleSpan.style.color = 'var(--cyan)';
        const lockIcon = nextHeader.querySelector('.kp-indicator');
        if (lockIcon && lockIcon.textContent === '🔒') lockIcon.textContent = '▼';
      }
      const lockOverlay = nextItem.querySelector('.kp-locked-overlay');
      if (lockOverlay) lockOverlay.remove();
      // Show real content (already in DOM, just hidden)
      const bodyInner = nextItem.querySelector('.kp-body-inner');
      if (bodyInner) bodyInner.style.display = '';
      // Fix header onclick so it toggles instead of showing locked toast
      if (nextHeader) nextHeader.onclick = function() { toggleKP(this); };
    }

    showToast('🎉 恭喜完成本知识点！', 'success');

    // Check if ALL exercises across the chapter are submitted → trigger chapter-end CG
    const allExList = document.querySelectorAll('.kp-exercise');
    const allExercisesDone = allExList.length > 0 && Array.from(allExList).every(ex => ex.dataset.exSubmitted === 'true');
    if (allExercisesDone) {
      checkChapterComplete(chapterId);
    }
  }
}

// --- Chapter Completion → 星辰启示 CG ---
function checkChapterComplete(chapterId) {
  // 判断是否最后一个 KP 被完成（做完最后一题就触发星辰启示 CG 跳转）
  const allKpItems = document.querySelectorAll('.kp-item');
  if (allKpItems.length === 0) return;

  const lastKpItem = allKpItems[allKpItems.length - 1];
  const isLastKpCompleted = lastKpItem.classList.contains('completed');

  if (isLastKpCompleted) {
    showToast('🌌 最后一题完成！即将进入星辰启示...', 'success');
    setTimeout(() => {
      window.location.href = '/static/revelation_cg.html?ch=' + chapterId;
    }, 1500);
  }
}

// --- Favorites ---
async function toggleFav(chapterId, exIndex, question) {
  try {
    const res = await fetch('/api/toggle-favorite', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, ex_index: exIndex, question })
    });
    const data = await res.json();
    if (data.success) {
      const stars = document.querySelectorAll('.btn-fav-star');
      stars.forEach(s => {
        if (s.closest('[data-ex-idx]')?.dataset.exIdx === String(exIndex)) {
          s.textContent = data.is_favorite ? '⭐' : '☆';
          s.title = data.is_favorite ? '取消收藏' : '收藏';
        }
      });
      showToast(data.is_favorite ? '⭐ 已收藏' : '取消收藏', 'success');
    }
  } catch (e) {}
}

async function showFavorites() {
  const modal = document.getElementById('fav-modal');
  const list = document.getElementById('fav-list');
  if (!modal || !list) return;

  try {
    const res = await fetch('/api/user');
    const data = await res.json();
    const favs = data.favorites || [];

    if (favs.length === 0) {
      list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">📭 还没有收藏的题目</div>';
    } else {
      list.innerHTML = favs.map(f =>
        `<div class="fav-item">
          <span class="fav-icon">⭐</span>
          <span class="fav-text">${escapeHtml(f.question.substring(0, 60))}${f.question.length > 60 ? '...' : ''}</span>
        </div>`
      ).join('');
    }
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  } catch (e) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--red);">加载失败</div>';
    modal.classList.add('active');
  }
}

// --- Wrong Answer Book ---
async function showWrongBook() {
  const modal = document.getElementById('wrong-modal');
  const list = document.getElementById('wrong-list');
  if (!modal || !list) return;

  try {
    const res = await fetch('/api/user');
    const data = await res.json();
    const wrong = data.wrong_answers || [];

    if (wrong.length === 0) {
      list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">🎉 暂无错题，继续保持！</div>';
    } else {
      list.innerHTML = wrong.map((w, i) =>
        `<div class="wrong-item">
          <div class="wrong-question">${escapeHtml(w.question.substring(0, 80))}</div>
          <div class="wrong-detail">
            <span class="wrong-tag wrong-user">你的答案: ${escapeHtml(w.user_answer || '代码练习')}</span>
            <span class="wrong-tag wrong-correct">正确答案: ${escapeHtml(w.correct_answer || '运行成功')}</span>
          </div>
          <button class="btn-wrong-dismiss" onclick="dismissWrong(${i})">✕ 移除</button>
        </div>`
      ).join('');
    }
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  } catch (e) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--red);">加载失败</div>';
    modal.classList.add('active');
  }
}

async function dismissWrong(index) {
  try {
    await fetch('/api/clear-wrong', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ indices: [index] })
    });
    showToast('错题已移除', 'success');
    showWrongBook();
  } catch (e) {}
}

// --- Notes ---
function toggleNotes(btn) {
  const editor = btn.parentElement.querySelector('.kp-notes-editor');
  if (editor) {
    const isVisible = editor.style.display !== 'none';
    editor.style.display = isVisible ? 'none' : 'block';
    btn.textContent = isVisible ? '📝 我的笔记' : '📝 收起笔记';

    // Load existing note + file list
    if (!isVisible) {
      const textarea = editor.querySelector('.kp-notes-textarea');
      const kpKey = textarea.dataset.kpKey;
      loadNote(kpKey, textarea);
      loadNoteFiles(editor);
    }
  }
}

async function loadNote(kpKey, textarea) {
  try {
    const res = await fetch('/api/user');
    const data = await res.json();
    const notes = data.notes || {};
    const note = notes[kpKey];
    if (typeof note === 'string') {
      textarea.value = note;
    } else if (note && note.content) {
      textarea.value = note.content;
    }
  } catch (e) {}
}

async function saveNote(chapterId, kpIndex, btn) {
  const editor = btn.closest('.kp-notes-editor');
  const textarea = editor.querySelector('.kp-notes-textarea');
  const hint = editor.querySelector('.notes-saved-hint');
  const content = textarea.value;

  try {
    const res = await fetch('/api/save-note', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex, content })
    });
    const data = await res.json();
    if (data.success) {
      if (hint) { hint.style.display = 'inline'; setTimeout(() => { hint.style.display = 'none'; }, 2000); }
      showToast('📝 笔记已保存', 'success');
    }
  } catch (e) {
    showToast('保存失败', 'error');
  }
}

// --- Note Files ---

const FILE_ICONS = {
  txt: '📄', py: '🐍', md: '📝',
  docx: '📘', doc: '📘',
  xlsx: '📊', xls: '📊',
  pptx: '📽️', ppt: '📽️',
  pdf: '📕',
  jpg: '🖼️', jpeg: '🖼️', png: '🖼️',
  gif: '🖼️', bmp: '🖼️',
  html: '🌐', css: '🎨', js: '🖥️',
  json: '⚙️', xml: '⚙️',
};
const FILE_ICON_DEFAULT = '📎';

function getFileIcon(ext) { return FILE_ICONS[ext] || FILE_ICON_DEFAULT; }

async function loadNoteFiles(editor) {
  const textarea = editor.querySelector('.kp-notes-textarea');
  const kpKey = textarea.dataset.kpKey;
  const parts = kpKey.split('_');
  if (parts.length < 2) return;
  const chapterId = parts[0], kpIndex = parts[1];

  try {
    const res = await fetch('/api/note-files/list', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex })
    });
    const data = await res.json();
    if (!data.success) return;
    const files = data.note && data.note.files ? data.note.files : [];
    renderNoteFiles(editor, files, chapterId, kpIndex);
  } catch (e) {}
}

function renderNoteFiles(editor, files, chapterId, kpIndex) {
  const container = editor.querySelector('.note-files-list');
  if (!container) return;
  if (!files || files.length === 0) {
    container.style.display = 'none';
    return;
  }
  container.style.display = 'block';
  let html = '<div class="note-files-header">📎 关联文件</div>';
  files.forEach(f => {
    const icon = getFileIcon(f.type);
    html += '<div class="note-file-item">';
    html += '<span class="note-file-icon">' + icon + '</span>';
    html += '<span class="note-file-name" title="' + escapeHtml(f.path) + '">' + escapeHtml(f.name) + '</span>';
    html += '<span class="note-file-actions">';
    html += '<button class="btn-nf-open" onclick="openNoteFile(\'' + escapeHtml(f.path) + '\')" title="打开文件">📝 打开</button>';
    html += '<button class="btn-nf-remove" onclick="removeNoteFile(' + chapterId + ', ' + kpIndex + ', \'' + escapeHtml(f.path) + '\', this)" title="从列表中移除">✕</button>';
    html += '</span>';
    html += '</div>';
  });
  container.innerHTML = html;
}

async function createNoteTxt(chapterId, kpIndex) {
  try {
    const res = await fetch('/api/note-files/create-txt', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex })
    });
    const data = await res.json();
    if (data.success) {
      let msg = '📄 TXT 文件已创建';
      if (data.is_desktop && data.opened) {
        msg += '，正在用记事本打开';
      } else if (!data.is_desktop) {
        msg += '（网页版仅保存到服务器）';
      }
      showToast(msg, 'success');
      // Reload file list
      const editor = document.querySelector('.kp-notes-editor[style*="block"]') ||
                     document.querySelector('.kp-notes-editor');
      if (editor && editor.style.display !== 'none') {
        loadNoteFiles(editor);
      }
    } else {
      showToast('创建失败: ' + (data.error || ''), 'error');
    }
  } catch (e) {
    showToast('创建失败: ' + e.message, 'error');
  }
}

async function addLocalFile(chapterId, kpIndex) {
  try {
    const res = await fetch('/api/note-files/add', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex })
    });
    const data = await res.json();
    if (data.success && data.file) {
      showToast('📂 文件已打开并关联到笔记', 'success');
      // Reload file list
      const editor = document.querySelector('.kp-notes-editor[style*="block"]') ||
                     document.querySelector('.kp-notes-editor');
      if (editor && editor.style.display !== 'none') {
        loadNoteFiles(editor);
      }
    } else if (data.success && !data.file) {
      // User cancelled dialog
    } else if (data.error === 'desktop_only') {
      showToast('💻 此功能仅在桌面版可用', 'success');
    } else {
      showToast('操作失败: ' + (data.error || ''), 'error');
    }
  } catch (e) {
    showToast('操作失败: ' + e.message, 'error');
  }
}

async function openNoteFile(filePath) {
  try {
    const res = await fetch('/api/note-files/open', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath })
    });
    const data = await res.json();
    if (data.success) {
      showToast('📝 正在打开文件...', 'success');
    } else {
      showToast('打开失败: ' + (data.error || ''), 'error');
    }
  } catch (e) {
    showToast('打开失败: ' + e.message, 'error');
  }
}

async function removeNoteFile(chapterId, kpIndex, filePath, btn) {
  try {
    const res = await fetch('/api/note-files/remove', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, kp_index: kpIndex, file_path: filePath })
    });
    const data = await res.json();
    if (data.success) {
      showToast('已从列表移除', 'success');
      // Reload file list from parent editor
      const editor = btn ? btn.closest('.kp-notes-editor') : null;
      if (editor) loadNoteFiles(editor);
    }
  } catch (e) {
    showToast('移除失败', 'error');
  }
}

// --- Mode Toggle ---
async function toggleMode() {
  const checkbox = document.getElementById('mode-toggle');
  const label = document.getElementById('mode-label');
  const newMode = checkbox.checked ? 'all_unlocked' : 'explore';

  try {
    const res = await fetch('/api/set-mode', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: newMode })
    });
    const data = await res.json();
    if (data.success) {
      label.textContent = newMode === 'all_unlocked' ? '🔓 全部解锁' : '🔒 探索模式';
      showToast(newMode === 'all_unlocked' ? '🔓 已切换为全部解锁模式' : '🔒 已切换为探索模式', 'success');
      // Reload to refresh chapter lock states
      setTimeout(() => location.reload(), 800);
    }
  } catch (e) {}
}

// --- Modal helpers ---
function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Close modals on Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeModal('fav-modal');
    closeModal('wrong-modal');
    const codeEx = document.getElementById('code-ex-modal');
    if (codeEx && codeEx.classList.contains('active')) closeCodeEx();
  }
  // Left/Right arrow for comic
  const comicOverlay = document.getElementById('comic-overlay');
  if (comicOverlay && comicOverlay.classList.contains('active')) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); navigateComic(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); navigateComic(1); }
  }
});

// ---- Exercise option click (inside chapter page) ----
(function() {
  document.addEventListener('click', function(e) {
    const opt = e.target.closest('.ex-option');
    if (!opt) return;
    const card = opt.closest('.kp-exercise');
    if (!card || card.dataset.exSubmitted === 'true') return;
    card.querySelectorAll('.ex-option').forEach(o => o.classList.remove('selected'));
    opt.classList.add('selected');
  });
})();

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ==================== Comic Viewer ====================
let comicState = {
  panels: [], currentPanel: 0, chapterId: null, kpIndex: null, kpTitle: null
};

async function openComic(chapterId, kpIndex, kpTitle) {
  comicState.chapterId = chapterId; comicState.kpIndex = kpIndex; comicState.kpTitle = kpTitle; comicState.currentPanel = 0;
  const overlay = document.getElementById('comic-overlay');
  const panelsContainer = document.getElementById('comic-panels');
  const nav = document.getElementById('comic-nav');
  const bottom = document.getElementById('comic-bottom');
  const settingsHint = document.getElementById('comic-settings-hint');
  const autoPlayWrap = document.getElementById('comic-autoplay-wrap');
  const badge = document.getElementById('comic-badge');
  panelsContainer.innerHTML = `<div class="comic-loading"><div class="loading-spinner"></div><p>正在生成漫画讲解...</p><p class="loading-sub">蛇蛇老师和同学正在创作中 🎨</p></div>`;
  nav.style.display = 'none'; bottom.style.display = 'none'; autoPlayWrap.style.display = 'none'; settingsHint.style.display = 'none';
  overlay.classList.add('active'); document.body.style.overflow = 'hidden';
  try {
    const res = await fetch(`/api/comic/${chapterId}/${kpIndex}`);
    const data = await res.json();
    if (!data.success) { panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 ${data.message || '生成失败，请稍后重试'}</p></div>`; return; }
    const comic = data.comic; comicState.panels = comic.panels;
    document.getElementById('comic-title').textContent = comic.title;
    badge.textContent = `共 ${comic.total_panels} 格`;
    renderComicPanels(); nav.style.display = 'flex'; bottom.style.display = 'flex';
    document.getElementById('comic-autoplay-wrap').style.display = 'flex';
    if (!comic.has_api) settingsHint.style.display = 'block';
  } catch (err) { panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 网络错误，请稍后重试</p></div>`; }
}

function renderComicPanels() {
  const container = document.getElementById('comic-panels');
  container.innerHTML = comicState.panels.map((p, i) => {
    const charClass = `${p.character}-panel`;
    return `<div class="comic-panel ${charClass}" data-panel="${i}" style="display:${i === comicState.currentPanel ? 'flex' : 'none'};animation-delay:${i * 0.05}s">
      <div class="comic-avatar">${p.avatar}</div>
      <div class="comic-bubble">
        <div class="bubble-name">${p.character_name}<button class="btn-voice" data-panel-idx="${i}" onclick="event.stopPropagation();speakPanel(${i})" title="🔊 语音播报">🔊</button></div>
        <div class="bubble-text">${escapeHtml(p.dialog)}</div>
        <div class="bubble-expression">${getExpressionEmoji(p.expression)} ${getExpressionLabel(p.expression)}</div>
        ${p.knowledge_bite ? `<span class="bubble-knowledge">💡 ${escapeHtml(p.knowledge_bite)}</span>` : ''}
      </div>
      <div class="comic-scene">📍 ${getSceneEmoji(p.scene)} ${getSceneLabel(p.scene)}</div>
    </div>`;
  }).join('');
  updateComicNav();
}

// ==================== Voice / TTS ====================
let currentSpeech = null, isSpeaking = false, cachedChineseVoices = [];

function initVoices() {
  const loadVoices = () => {
    const all = speechSynthesis.getVoices();
    cachedChineseVoices = all.filter(v => v.lang.startsWith('zh') || v.lang === 'zh-CN' || v.lang === 'zh-TW');
    if (cachedChineseVoices.length === 0) cachedChineseVoices = all.filter(v => v.name.includes('Chinese') || v.name.includes('Microsoft Huihui') || v.name.includes('Microsoft Kangkang') || v.name.includes('Yaoyao') || v.name.includes('Tingting'));
  };
  loadVoices(); speechSynthesis.onvoiceschanged = loadVoices;
}
if (typeof speechSynthesis !== 'undefined') initVoices();

function speakPanel(panelIdx) {
  const panel = comicState.panels[panelIdx]; if (!panel) return;
  if (isSpeaking) { stopSpeak(); if (currentSpeech && currentSpeech._panelIdx === panelIdx) { currentSpeech = null; updateAllVoiceButtons(); return; } }
  const text = panel.dialog.replace(/[\u{1F000}-\u{1FFFF}]/gu,'').replace(/[\u{1F300}-\u{1F9FF}]/gu,'').replace(/[☀-➿]/gu,'').replace(/\*\*/g,'').replace(/`/g,'').replace(/<[^>]+>/g,'').replace(/\s+/g,' ').trim();
  if (!text || text.length < 2) return;
  const utterance = new SpeechSynthesisUtterance(text); utterance.lang = 'zh-CN'; utterance.volume = 1.0;
  switch(panel.character){case'student':utterance.rate=1.2;utterance.pitch=1.3;break;case'narrator':utterance.rate=0.9;utterance.pitch=0.95;break;default:utterance.rate=1.0;utterance.pitch=1.05;break;}
  const voices = speechSynthesis.getVoices();
  if (voices.length > 0 && cachedChineseVoices.length === 0) cachedChineseVoices = voices.filter(v => v.lang.startsWith('zh') || v.lang === 'zh-CN' || v.lang === 'zh-TW' || v.name.includes('Chinese') || v.name.includes('Huihui') || v.name.includes('Kangkang') || v.name.includes('Yaoyao'));
  if (cachedChineseVoices.length > 0) { if (panel.character === 'student') { const female = cachedChineseVoices.find(v => v.name.includes('female')||v.name.includes('Female')||v.name.includes('Huihui')||v.name.includes('Yaoyao')||v.name.includes('Tingting')); utterance.voice = female || cachedChineseVoices[0]; } else { const male = cachedChineseVoices.find(v => v.name.includes('male')||v.name.includes('Male')||v.name.includes('Kangkang')); utterance.voice = male || cachedChineseVoices[0]; } }
  utterance._panelIdx = panelIdx; tryServerTTS(panelIdx, text, panel.character);
}

async function tryServerTTS(panelIdx, text, character) {
  const panel = comicState.panels[panelIdx]; const chId = comicState.chapterId; const kpId = comicState.kpIndex; const pId = panel.panel_id;
  try {
    const statusRes = await fetch('/api/tts/status'); const statusData = await statusRes.json();
    if (!statusData.edge_tts_available && !statusData.doubao_available) { const u = new SpeechSynthesisUtterance(text); u.lang='zh-CN'; u._panelIdx=panelIdx; speakWithBrowserTTS(u,panelIdx); return; }
    const url = `/api/tts/panel/${chId}/${kpId}/${pId}`; const audio = new Audio(url); audio._panelIdx = panelIdx;
    audio.onplay = () => { isSpeaking=true; currentSpeech=audio; updateAllVoiceButtons(); };
    audio.onended = () => { isSpeaking=false; currentSpeech=null; updateAllVoiceButtons(); const autoPlay=document.getElementById('comic-autoplay'); if(autoPlay&&autoPlay.checked){const next=panelIdx+1;if(next<comicState.panels.length){setTimeout(()=>{navigateComic(1);setTimeout(()=>speakPanel(next),500);},600);}} };
    audio.onerror = () => { isSpeaking=false; currentSpeech=null; const u=new SpeechSynthesisUtterance(text); u.lang='zh-CN'; u._panelIdx=panelIdx; speakWithBrowserTTS(u,panelIdx); };
    audio.play().catch(() => { const u=new SpeechSynthesisUtterance(text); u.lang='zh-CN'; u._panelIdx=panelIdx; speakWithBrowserTTS(u,panelIdx); });
  } catch(e) { const u=new SpeechSynthesisUtterance(text); u.lang='zh-CN'; u._panelIdx=panelIdx; speakWithBrowserTTS(u,panelIdx); }
}

function speakWithBrowserTTS(utterance, panelIdx) {
  utterance.onstart = () => { isSpeaking=true; currentSpeech=utterance; updateAllVoiceButtons(); };
  utterance.onend = () => { isSpeaking=false; currentSpeech=null; updateAllVoiceButtons(); const next=panelIdx+1; if(next<comicState.panels.length){const ap=document.getElementById('comic-autoplay'); if(ap&&ap.checked){setTimeout(()=>{navigateComic(1);setTimeout(()=>speakPanel(next),400);},600);}} };
  utterance.onerror = (e) => { if(e.error!=='interrupted')console.warn('TTS error:',e.error); isSpeaking=false; currentSpeech=null; updateAllVoiceButtons(); };
  speechSynthesis.speak(utterance);
}

function stopSpeak() { speechSynthesis.cancel(); if(currentSpeech){if(currentSpeech instanceof Audio){currentSpeech.pause();currentSpeech.currentTime=0;}} isSpeaking=false; currentSpeech=null; updateAllVoiceButtons(); const ap=document.getElementById('comic-autoplay'); if(ap&&ap.checked)ap.checked=false; }
function updateAllVoiceButtons() { document.querySelectorAll('.btn-voice').forEach(b=>{const i=parseInt(b.dataset.panelIdx);const a=currentSpeech&&currentSpeech._panelIdx===i;b.classList.toggle('speaking',a);b.textContent=a?'🔊':'🔊';b.title=a?'⏹ 停止':'🔊 语音播报';}); }
function updateComicNav() { document.getElementById('comic-prev').disabled=comicState.currentPanel<=0; document.getElementById('comic-next').disabled=comicState.currentPanel>=comicState.panels.length-1; document.getElementById('comic-counter').textContent=`${comicState.currentPanel+1} / ${comicState.panels.length}`; }
function navigateComic(delta) { const n=comicState.currentPanel+delta; if(n<0||n>=comicState.panels.length)return; const ce=document.querySelector(`.comic-panel[data-panel="${comicState.currentPanel}"]`); if(ce)ce.style.display='none'; comicState.currentPanel=n; const ne=document.querySelector(`.comic-panel[data-panel="${n}"]`); if(ne){ne.style.display='flex';ne.style.animation='none';ne.offsetHeight;ne.animation='panelSlideIn 0.4s ease both';} updateComicNav(); document.querySelector('.comic-container').scrollTo({top:ne.offsetTop-100,behavior:'smooth'}); }
function restartComic() { comicState.currentPanel=0; document.querySelectorAll('.comic-panel').forEach((e,i)=>{e.style.display=i===0?'flex':'none';}); updateComicNav(); document.querySelector('.comic-container').scrollTo({top:0,behavior:'smooth'}); }
function closeComic() { stopSpeak(); document.getElementById('comic-autoplay').checked=false; document.getElementById('comic-overlay').classList.remove('active'); document.body.style.overflow=''; comicState.panels=[]; comicState.currentPanel=0; }

// ==================== Comic Settings ====================
function showComicSettings() { document.getElementById('comic-settings-modal').style.display='flex'; }
function closeComicSettings() { document.getElementById('comic-settings-modal').style.display='none'; }
async function saveComicConfig() {
  const k=document.getElementById('comic-api-key').value.trim(); const b=document.getElementById('comic-api-base').value.trim(); const m=document.getElementById('comic-model').value.trim();
  if(!k){showToast('请填写 API Key','error');return;}
  try{const r=await fetch('/api/comic/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({api_key:k,api_base:b,model:m||'gpt-4o'})});const d=await r.json();if(d.success){showToast('配置已保存！','success');closeComicSettings();document.getElementById('comic-settings-hint').style.display='none';}else showToast('配置保存失败','error');}catch(e){showToast('网络错误','error');}
}

// ==================== Comic Helpers ====================
function getExpressionEmoji(e){const m={'explaining':'📝','thinking':'🤔','surprised':'😮','happy':'😊','questioning':'🙋','excited':'🤩','inspired':'💡'};return m[e]||'💬';}
function getExpressionLabel(e){const m={'explaining':'认真讲解中','thinking':'思考中','surprised':'感到惊讶','happy':'开心','questioning':'举手提问','excited':'兴奋','inspired':'恍然大悟'};return m[e]||e;}
function getSceneEmoji(s){const m={'classroom':'🏫','coding_lab':'💻','thought_bubble':'💭','whiteboard':'📋','computer_screen':'🖥️'};return m[s]||'📍';}
function getSceneLabel(s){const m={'classroom':'教室','coding_lab':'编程实验室','thought_bubble':'思考','whiteboard':'白板','computer_screen':'电脑屏幕'};return m[s]||s;}

// ==================== Mindmap ====================
let mindmapInstance = null, mindmapSvg = null;
async function openMindmap() {
  const overlay=document.getElementById('mindmap-overlay'); overlay.classList.add('active'); document.body.style.overflow='hidden';
  const mdData=document.getElementById('mindmap-data'); if(!mdData)return;
  const svg=document.getElementById('mindmap-svg'); svg.innerHTML='';
  try{const{Transformer}=window.markmap;const{Markmap}=window.markmap;const t=new Transformer();const{root}=t.transform(mdData.textContent);mindmapInstance=Markmap.create(svg,{autoFit:true,colorFreezeLevel:2,duration:600,maxInitialScale:1.2,pan:true,zoom:true},root);mindmapSvg=svg;mindmapInstance.fit();}catch(e){svg.innerHTML='<div style="color:var(--text-secondary);text-align:center;padding:60px;">思维导图加载失败，请刷新重试</div>';}
}
function closeMindmap(){document.getElementById('mindmap-overlay').classList.remove('active');document.body.style.overflow='';}
function mindmapZoomIn(){if(mindmapInstance)mindmapInstance.rescale(1.3);}
function mindmapZoomOut(){if(mindmapInstance)mindmapInstance.rescale(0.7);}
function mindmapReset(){if(mindmapInstance)mindmapInstance.fit();}
function mindmapExpandAll(){if(mindmapInstance){mindmapInstance.setData(mindmapInstance.state.data);mindmapInstance.fit();}}
function mindmapCollapseAll(){if(!mindmapInstance)return;const cn=(n)=>{if(n.c){n.p={...n.p,f:true};n.c.forEach(cn);}};try{const d=JSON.parse(JSON.stringify(mindmapInstance.state.data));d.p={...d.p,f:true};if(d.c)d.c.forEach(cn);mindmapInstance.setData(d);}catch(e){}}

// ==================== JJ老师 AI Chat ====================
let jjCodeContext = '';
function toggleJJChat(){const o=document.getElementById('jj-chat-overlay');if(o)o.classList.toggle('active');if(o&&o.classList.contains('active')){setTimeout(()=>document.getElementById('jj-input').focus(),200);loadAIQuota();}}
function askJJAboutExercise(question){jjCodeContext=question;const o=document.getElementById('jj-chat-overlay');if(o)o.classList.add('active');const i=document.getElementById('jj-input');if(i){i.value='这道题我不太懂，能帮我分析一下吗？';i.focus();}loadAIQuota();}
async function loadAIQuota() {
  const el = document.getElementById('jj-quota'); if (!el) return;
  try {
    const r = await fetch('/api/ai-quota'); const d = await r.json();
    if (!d.success) return;
    if (d.is_unlimited) { el.textContent = '∞ 无限'; el.style.color = 'var(--green)'; }
    else { el.textContent = '📊 ' + d.remaining + '/' + d.limit; el.style.color = d.remaining <= 2 ? 'var(--orange)' : 'var(--text-muted)'; }
  } catch(e) { el.textContent = ''; }
}
// 把学生「在页面上做到哪、答错什么、正在写什么代码」一起带给后端，
// AI 才知道自己在给谁讲、讲到哪一步，而不是对着空气回答。
function collectJJPageContext(extra) {
  const page = { chapter_id: typeof CHAPTER_ID !== 'undefined' ? CHAPTER_ID : '',
                 chapter_title: typeof CHAPTER_TITLE !== 'undefined' ? CHAPTER_TITLE : '' };
  const items = Array.from(document.querySelectorAll('.kp-item'));
  if (items.length) {
    page.kp_total = items.length;
    page.kp_done = typeof COMPLETED_KPS !== 'undefined'
      ? COMPLETED_KPS.filter(k => String(k).indexOf(String(CHAPTER_ID) + '_') === 0).length
      : items.filter(i => i.classList.contains('completed')).length;
    // 优先取正在编辑的那个知识点，否则取第一个没做完的
    let node = null;
    if (typeof codeExState !== 'undefined' && codeExState && codeExState.chapterId != null) {
      node = document.querySelector('.kp-item[data-kp-index="' + codeExState.kpIndex + '"]');
    }
    if (!node) node = items.find(i => !i.classList.contains('completed')) || items[0];
    const titleEl = node && node.querySelector('.kp-title');
    if (titleEl) page.kp_title = titleEl.textContent.replace(/\s+/g, ' ').trim().slice(0, 80);
  }
  if (typeof CHAPTER_WRONG !== 'undefined' && Array.isArray(CHAPTER_WRONG)) {
    page.wrong = CHAPTER_WRONG.slice(-5).map(w => ({ question: (w && w.question) || '', user_answer: (w && w.user_answer) || '' }));
  }
  return Object.assign(page, extra || {});
}

// 统一的流式问答：AI 助教对话和代码讲评共用同一条链路
async function streamJJAnswer(payload, handlers) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);
  let answer = '', done = false;
  try {
    const response = await fetch('/api/ask-jj-stream', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload), signal: controller.signal
    });
    if (!response.ok) { const error = await response.json(); throw Error(error.error || '请求失败'); }
    const reader = response.body.getReader(), decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const chunk = await reader.read();
      buffer += decoder.decode(chunk.value || new Uint8Array(), { stream: !chunk.done });
      const frames = buffer.split('\n\n'); buffer = frames.pop();
      for (const frame of frames) {
        if (!frame.startsWith('data: ')) continue;
        const event = JSON.parse(frame.slice(6));
        if (event.type === 'delta') { answer += event.text; handlers.onDelta(answer); }
        if ((event.type === 'status' || event.type === 'switch') && !answer) handlers.onStatus(event.message);
        if (event.type === 'error') throw Error(event.message);
        if (event.type === 'done') done = true;
      }
      if (chunk.done) break;
    }
    if (!done) throw Error('连接提前结束，请重试。');
    handlers.onDone(answer);
    return { ok: true, answer };
  } catch (error) {
    const message = (answer ? answer + '\n\n' : '') +
      (error.name === 'AbortError' ? '响应超时，请重试。' : error.message);
    handlers.onError(message);
    return { ok: false, error: message };
  } finally { clearTimeout(timer); }
}

async function sendJJMessage() {
  const input=document.getElementById('jj-input'), btn=document.getElementById('jj-send-btn'), messages=document.getElementById('jj-messages'), typing=document.getElementById('jj-typing');
  const question=input.value.trim(); if(!question || btn.disabled) return;
  const user=document.createElement('div'); user.className='msg user'; user.textContent=question; messages.appendChild(user);
  const reply=document.createElement('div'); reply.className='msg jj'; reply.setAttribute('aria-live','polite'); reply.textContent='正在思考…'; messages.appendChild(reply);
  input.value=''; btn.disabled=true; typing.style.display='none';
  const context=jjCodeContext;
  const scroll=()=>{messages.scrollTop=messages.scrollHeight;};
  try {
    const result = await streamJJAnswer({
      question, context,
      chapter_id: typeof CHAPTER_ID!=='undefined'?CHAPTER_ID:'',
      page: collectJJPageContext()
    }, {
      onDelta: (text) => { reply.textContent=text; scroll(); },
      onStatus: (msg) => { reply.textContent=msg; scroll(); },
      onDone: (text) => { reply.innerHTML=formatJJAnswer(text); jjCodeContext=''; loadAIQuota(); scroll(); },
      onError: (msg) => { reply.textContent=msg; input.value=question; scroll(); }
    });
    if (!result.ok) return;
  } finally { btn.disabled=false; input.focus(); }
}

function formatJJAnswer(text){return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code>$2</code></pre>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>');}

// ==================== JJ Auto Chapter Guide & Completion ====================

async function autoJJChapterGuide() {
  // Avoid consuming model quota on every reload or CG replay.
  const guideKey = 'pymaster.guide.' + CHAPTER_ID;
  try { if(sessionStorage.getItem(guideKey)) return; sessionStorage.setItem(guideKey,'1'); } catch(e) {}
  // Check if this chapter has any progress — if no KPs completed, it's a fresh start
  const hasAnyProgress = COMPLETED_KPS.some(k => k.startsWith(CHAPTER_ID + '_'));
  if (hasAnyProgress) return;
  if (typeof CHAPTER_KP_TITLES === 'undefined') return;

  try {
    const res = await fetch('/api/jj-chapter-guide', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: CHAPTER_ID, chapter_title: CHAPTER_TITLE, kp_titles: CHAPTER_KP_TITLES })
    });
    const data = await res.json();
    if (!data.success) return;

    // Show JJ chat with the guide
    const msgDiv = document.getElementById('jj-messages');
    const typing = document.getElementById('jj-typing');
    const jjBtn = document.getElementById('btn-jj-float');
    if (msgDiv) {
      const guideMsg = document.createElement('div');
      guideMsg.className = 'msg jj';
      guideMsg.innerHTML = '🎯 <strong>章节学习指引</strong><br><br>' + formatJJAnswer(data.answer);
      msgDiv.appendChild(guideMsg);
      msgDiv.scrollTop = msgDiv.scrollHeight;
      // Auto-open JJ chat
      const overlay = document.getElementById('jj-chat-overlay');
      if (overlay && !overlay.classList.contains('active')) {
        overlay.classList.add('active');
      }
    }
  } catch (e) {}
}

async function autoJJChapterComplete() {
  if (typeof CHAPTER_KP_TITLES === 'undefined') return;

  try {
    const res = await fetch('/api/jj-chapter-complete', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chapter_id: CHAPTER_ID, chapter_title: CHAPTER_TITLE,
        kp_titles: CHAPTER_KP_TITLES,
        wrong_answers: typeof CHAPTER_WRONG !== 'undefined' ? CHAPTER_WRONG : []
      })
    });
    const data = await res.json();
    if (!data.success) return;

    const msgDiv = document.getElementById('jj-messages');
    if (msgDiv) {
      const completeMsg = document.createElement('div');
      completeMsg.className = 'msg jj';
      completeMsg.innerHTML = '🎉 <strong>章节完成！</strong><br><br>' + formatJJAnswer(data.answer);
      msgDiv.appendChild(completeMsg);
      msgDiv.scrollTop = msgDiv.scrollHeight;
      // Auto-open JJ chat
      const overlay = document.getElementById('jj-chat-overlay');
      if (overlay && !overlay.classList.contains('active')) {
        overlay.classList.add('active');
      }
    }
  } catch (e) {}
}

// Check if this chapter is fully completed (all KPs done)
function isChapterComplete() {
  const totalKPs = document.querySelectorAll('.kp-item').length;
  const completedKPs = document.querySelectorAll('.kp-item.completed').length;
  return totalKPs > 0 && completedKPs >= totalKPs;
}

// ==================== User Mindmap (My Mindmap) — Mind Elixir ====================
let myMindmapInstance = null;

async function openMyMindmap() {
  const overlay = document.getElementById('my-mindmap-overlay');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  const container = document.getElementById('mind-elixir-container');
  if (!container) return;

  // Destroy any existing instance
  if (myMindmapInstance) {
    myMindmapInstance.destroy();
    myMindmapInstance = null;
  }

  // Create MindElixir instance
  myMindmapInstance = new MindElixir({
    el: container,
    direction: MindElixir.SIDE,
    editable: true,
    contextMenu: true,
    toolBar: true,
    keypress: true,
    theme: MindElixir.DARK_THEME,
    overflowHidden: false
  });

  try {
    const res = await fetch('/api/mindmap/get?chapter_id=' + CHAPTER_ID);
    const data = await res.json();
    let initData = null;

    if (data.success && data.content) {
      try {
        const parsed = JSON.parse(data.content);
        if (parsed && parsed.nodeData) initData = parsed;
      } catch (e) {}
    }

    if (!initData) {
      initData = {
        nodeData: MindElixir.new(CHAPTER_TITLE || '我的思维导图').nodeData,
        arrows: [],
        summaries: [],
        meta: {}
      };
    }

    myMindmapInstance.init(initData);
    setTimeout(() => { try { myMindmapInstance.toCenter(); } catch(e) {} }, 200);
  } catch (e) {
    const initData = {
      nodeData: MindElixir.new(CHAPTER_TITLE || '我的思维导图').nodeData,
      arrows: [],
      summaries: [],
      meta: {}
    };
    myMindmapInstance.init(initData);
  }
}

function closeMyMindmap() {
  document.getElementById('my-mindmap-overlay').classList.remove('active');
  document.body.style.overflow = '';
  if (myMindmapInstance) {
    myMindmapInstance.destroy();
    myMindmapInstance = null;
  }
}

async function myMindmapSave() {
  if (!myMindmapInstance) { showToast('请先打开思维导图编辑器', 'error'); return; }
  try {
    const data = myMindmapInstance.getData();
    const content = JSON.stringify(data);
    const res = await fetch('/api/mindmap/save', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: CHAPTER_ID, content })
    });
    const result = await res.json();
    if (result.success) showToast('\U0001f4be 思维导图已保存！', 'success');
    else showToast('保存失败', 'error');
  } catch (e) { showToast('网络错误', 'error'); }
}

function myMindmapFit() {
  if (myMindmapInstance) {
    try { myMindmapInstance.toCenter(); } catch(e) {}
  }
}

function myMindmapUpload() {
  document.getElementById('my-mindmap-file-input').click();
}

function myMindmapLoadFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const data = JSON.parse(e.target.result);
      if (data && data.nodeData) {
        if (myMindmapInstance) {
          myMindmapInstance.init(data);
          showToast('\U0001f4c2 思维导图已加载', 'success');
        } else {
          showToast('请先打开思维导图编辑器', 'error');
        }
      } else {
        showToast('无效的思维导图 JSON 格式', 'error');
      }
    } catch (err) {
      showToast('文件格式有误，请上传有效的 JSON 文件', 'error');
    }
  };
  reader.readAsText(file, 'UTF-8');
  event.target.value = '';
}

async function myMindmapDelete() {
  if (!confirm('确定删除自定义思维导图？')) return;
  try {
    const res = await fetch('/api/mindmap/delete', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: CHAPTER_ID })
    });
    const data = await res.json();
    if (data.success) {
      if (myMindmapInstance) {
        const defaultData = {
          nodeData: MindElixir.new(CHAPTER_TITLE || '我的思维导图').nodeData,
          arrows: [],
          summaries: [],
          meta: {}
        };
        myMindmapInstance.init(defaultData);
      }
      showToast('已删除', 'success');
    }
  } catch (e) {}
}

// ==================== Fireworks System ====================
let fireworksAnimId = null;

function startFireworks(mode) {
  const canvas = document.getElementById('fireworks-canvas');
  if (!canvas) return;
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  const ctx = canvas.getContext('2d');

  const isFull = mode === 'full';
  const particles = [];
  const rockets = [];
  const colors = ['#ff6b6b', '#ffd700', '#00d4ff', '#a371f7', '#3fb950', '#ff6b9d', '#ff9f43'];

  function createBurst(x, y) {
    const count = isFull ? 80 : 25;
    const color = colors[Math.floor(Math.random() * colors.length)];
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 / count) * i + (Math.random() - 0.5) * 0.5;
      const speed = (Math.random() * 3 + 2) * (isFull ? 1.5 : 1);
      particles.push({
        x, y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1,
        decay: 0.015 + Math.random() * 0.01,
        size: Math.random() * 3 + 1,
        color
      });
    }
  }

  function createRocket() {
    const x = isFull
      ? Math.random() * canvas.width
      : (Math.random() < 0.5 ? Math.random() * canvas.width * 0.15 : canvas.width - Math.random() * canvas.width * 0.15);
    const targetY = isFull
      ? Math.random() * canvas.height * 0.5 + canvas.height * 0.1
      : Math.random() * canvas.height * 0.4 + canvas.height * 0.1;
    rockets.push({
      x, y: canvas.height, targetY, speed: 3 + Math.random() * 3, trail: []
    });
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Rockets
    for (let i = rockets.length - 1; i >= 0; i--) {
      const r = rockets[i];
      r.trail.push({ x: r.x, y: r.y });
      if (r.trail.length > 10) r.trail.shift();
      r.y -= r.speed;
      r.x += (Math.random() - 0.5) * 0.6;

      // Draw trail
      for (let j = 0; j < r.trail.length; j++) {
        const alpha = j / r.trail.length;
        ctx.fillStyle = 'rgba(255,255,255,' + (alpha * 0.5) + ')';
        ctx.beginPath();
        ctx.arc(r.trail[j].x, r.trail[j].y, 1.5 * alpha, 0, Math.PI * 2);
        ctx.fill();
      }

      if (r.y <= r.targetY) {
        createBurst(r.x, r.y);
        rockets.splice(i, 1);
      }
    }

    // Particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.04;
      p.vx *= 0.99;
      p.life -= p.decay;

      if (p.life <= 0) { particles.splice(i, 1); continue; }

      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();

      ctx.globalAlpha = p.life * 0.2;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    // Launch rockets
    if (isFull) {
      if (Math.random() < 0.08) createRocket();
      if (Math.random() < 0.05) createRocket();
    } else {
      if (Math.random() < 0.03) createRocket();
    }

    if (rockets.length > 0 || particles.length > 0) {
      fireworksAnimId = requestAnimationFrame(animate);
    }
  }

  // Initial burst
  for (let i = 0; i < (isFull ? 5 : 2); i++) {
    setTimeout(createRocket, i * 200);
  }

  if (fireworksAnimId) cancelAnimationFrame(fireworksAnimId);
  animate();
}

function stopFireworks() {
  if (fireworksAnimId) {
    cancelAnimationFrame(fireworksAnimId);
    fireworksAnimId = null;
  }
  const canvas = document.getElementById('fireworks-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
}

function createConfetti(count) {
  const colors = ['#ff6b6b', '#ffd700', '#00d4ff', '#a371f7', '#3fb950', '#ff6b9d', '#ff9f43'];
  for (let i = 0; i < count; i++) {
    const el = document.createElement('div');
    el.className = 'confetti-piece';
    el.style.cssText = 'left:' + (Math.random() * 100) + 'vw;' +
      'background:' + colors[Math.floor(Math.random() * colors.length)] + ';' +
      'width:' + (Math.random() * 8 + 4) + 'px;' +
      'height:' + (Math.random() * 8 + 4) + 'px;' +
      'animation-duration:' + (2 + Math.random() * 2) + 's;' +
      'animation-delay:' + (Math.random() * 2) + 's;' +
      'border-radius:' + (Math.random() > 0.5 ? '50%' : '2px') + ';';
    document.body.appendChild(el);
    setTimeout(function() { if (el.parentNode) el.remove(); }, 5000);
  }
}

// ==================== Score Animation ====================
function showScoreAnimation(score, feedback, strengths, weaknesses) {
  const overlay = document.getElementById('score-overlay');
  const scoreNum = document.getElementById('score-number');
  const scoreLabel = document.getElementById('score-label');
  const feedbackEl = document.getElementById('score-feedback');
  const strengthsEl = document.getElementById('score-strengths');
  const weaknessesEl = document.getElementById('score-weaknesses');
  const quoteEl = document.getElementById('score-quote');
  const card = document.getElementById('score-card');

  if (!overlay) return;

  // Reset
  overlay.classList.remove('active');
  card.className = 'score-card';
  scoreNum.className = 'score-number';
  document.body.classList.remove('screen-shake');
  stopFireworks();
  document.querySelectorAll('.confetti-piece').forEach(function(el) { el.remove(); });

  // Set content
  feedbackEl.textContent = feedback || '';
  strengthsEl.textContent = strengths ? '✅ ' + strengths : '';
  weaknessesEl.textContent = weaknesses ? '❌ ' + weaknesses : '';

  var quoteText = '';
  var labelText = 'AI 评分';

  if (score >= 40 && score < 80) {
    scoreNum.className = 'score-number pass';
    labelText = '✅ 通过！再接再厉';
    var quotes = [
      '“成功是衰倒九次，爬起来十次。” — 香港俗语',
      '“不积步跬，无以至千里。” — 茀子',
      '“Practice makes perfect.” — 熟能生巧',
      '“每一次练习都是向大师脉进的一步。”',
      '“坚持是成功的另一个名字。”',
      '“Rome was not built in a day.”'
    ];
    quoteText = quotes[Math.floor(Math.random() * quotes.length)];
    setTimeout(function() { startFireworks('edge'); }, 300);

  } else if (score >= 80 && score < 95) {
    scoreNum.className = 'score-number medium';
    card.classList.add('glow');
    labelText = '🌟 才华横溢！';
    var poems = [
      '「心有灵狐一点通，学贯东西自不同。\n  代码如诗写乾坄，智慧光芒照苍穹。」',
      '「笔落惊风雨，码成泣鬼神。\n  逻辑如丝织锦绣，思维似剑破迷津。」',
      '「少年负壮气，奋烈自有时。\n  编程之道通天地，智慧之花绽满枝。」',
      '「博学之，审问之，慎思之，明辨之，積行之。」\n  —— 《礼记·中庸》',
      '「问渠哪得清如许，为有源头活水来。」\n  —— 朱熹《观书有感》'
    ];
    quoteText = poems[Math.floor(Math.random() * poems.length)];
    document.body.classList.add('screen-shake');
    setTimeout(function() { startFireworks('edge'); }, 300);

  } else if (score >= 95) {
    scoreNum.className = 'score-number winner';
    card.classList.add('glow');
    labelText = '🏆 绝世天才！';
    var praises = [
      '「此曲只应天上有，人间能得几回闻！」\n  你的代码如诗如画，堪称编程艺术的巅峰之作！',
      '「会当凌绝顶，一览众山小！」\n  你已站在编程之巅，让人叹为观止！',
      '「天纵之才，旷世难逢！」\n  你的逻辑思维和代码能力，已达到超凡入圣的境界！',
      '「春风得意马蹄急，一日看尽长安花！」\n  完美的解答，令人拍案叫绝！',
      '「大鹏一日同风起，扶摇直上九万里！」\n  你的编程天赋，正如大鹏展翅，不可限量！'
    ];
    quoteText = praises[Math.floor(Math.random() * praises.length)];
    setTimeout(function() { startFireworks('full'); }, 300);
    setTimeout(function() { createConfetti(50); }, 500);
    var confettiInterval = setInterval(function() {
      if (!overlay.classList.contains('active')) {
        clearInterval(confettiInterval);
        return;
      }
      createConfetti(15);
    }, 1500);
  }

  quoteEl.textContent = quoteText;
  scoreLabel.textContent = labelText;

  // Show overlay
  overlay.classList.add('active');
  scoreNum.textContent = '0';
  scoreNum.classList.add('pop');

  // Animate score counting up
  var duration = 1000;
  var startTime = Date.now();
  function animateScore() {
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(eased * score);
    scoreNum.textContent = current;
    if (progress < 1) {
      requestAnimationFrame(animateScore);
    } else {
      scoreNum.textContent = score;
    }
  }
  animateScore();
}

function closeScoreOverlay() {
  const overlay = document.getElementById('score-overlay');
  if (overlay) overlay.classList.remove('active');
  document.body.classList.remove('screen-shake');
  stopFireworks();
  document.querySelectorAll('.confetti-piece').forEach(function(el) { el.remove(); });
}

// ── JJ老师 for Code Editor ──
async function askJJAboutCode() {
  const output = document.getElementById('code-ex-output');
  const jjArea = document.getElementById('code-ex-jj-area');
  const jjContent = document.getElementById('code-ex-jj-content');
  if (!jjArea || !jjContent) return;

  // 代码要从 CodeMirror 实例取：它替换了 #code-ex-editor，那个 textarea 已隐藏且不再同步
  const code = codeMirrorEditor ? codeMirrorEditor.getValue().trim() : '';
  if (!code) { showToast('请先编写代码再请教JJ老师', 'error'); return; }

  // Get output text, stripping HTML tags
  const outputText = output ? output.textContent?.trim() || '（还没运行过）' : '（还没运行过）';
  const exercise = (document.getElementById('code-ex-prompt')?.textContent || '').replace('📝 ', '').trim();
  const context = '【学生代码】\n```python\n' + code + '\n```\n【运行输出】\n' + outputText;

  jjArea.style.display = 'block';
  jjContent.innerHTML = '<div style="color:var(--text-muted);padding:8px;">⏳ JJ老师正在看你的代码…</div>';
  jjArea.scrollTop = 0;

  await streamJJAnswer({
    question: '请帮我看看这段 Python 代码写得怎么样：有错误就指出错在哪、怎么改；没错就说说哪里写得好、哪里可以更规范。',
    context,
    chapter_id: codeExState.chapterId,
    page: collectJJPageContext({ exercise, code, output: outputText })
  }, {
    // 流式渲染，先把话显示出来，学生不用等整段生成完
    onDelta: (text) => { jjContent.textContent = text; jjArea.scrollTop = jjArea.scrollHeight; },
    onStatus: (msg) => { jjContent.innerHTML = '<div style="color:var(--text-muted);padding:8px;">' + escapeHtml(msg) + '</div>'; },
    onDone: (text) => { jjContent.innerHTML = formatJJAnswer(text); jjArea.scrollTop = jjArea.scrollHeight; },
    onError: (msg) => { jjContent.innerHTML = '<div style="color:var(--orange);padding:8px;">❌ ' + escapeHtml(msg) + '</div>'; }
  });
}
document.addEventListener('DOMContentLoaded', function() {
  // JJ Chapter Guide for first-time chapter visit
  if (typeof CHAPTER_ID !== 'undefined') {
    autoJJChapterGuide();
  }
});

// ==================== Theme Toggle ====================
(function() {
  const KEY = 'pymaster_theme';
  function paintThemeButton() {
    const btn = document.querySelector('.btn-theme-toggle');
    if (!btn) return;
    const light = document.documentElement.getAttribute('data-theme') === 'light';
    const glyph = btn.querySelector('.theme-glyph');
    if (glyph) glyph.textContent = light ? '☀' : '☾';
    btn.setAttribute('aria-pressed', light ? 'true' : 'false');
  }
  const saved = localStorage.getItem(KEY);
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
  }
  window.setTimeout(paintThemeButton, 0);
})();
function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    localStorage.setItem('pymaster_theme', 'dark');
  } else {
    html.setAttribute('data-theme', 'light');
    localStorage.setItem('pymaster_theme', 'light');
  }
  const btn = document.querySelector('.btn-theme-toggle');
  if (btn) {
    const glyph = btn.querySelector('.theme-glyph');
    const light = html.getAttribute('data-theme') === 'light';
    if (glyph) glyph.textContent = light ? '☀' : '☾';
    btn.setAttribute('aria-pressed', light ? 'true' : 'false');
  }
}
// ==================== Glossary ====================
async function showGlossary() {
  const modal = document.getElementById('glossary-modal');
  const list = document.getElementById('glossary-list');
  if (!modal || !list) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">加载中...</div>';
  try {
    const res = await fetch('/api/glossary');
    const data = await res.json();
    if (!data.success) throw new Error(data.message);
    list.innerHTML = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;">';
    data.terms.forEach(function(term) {
      list.innerHTML += '<div class="glossary-item" onclick="toggleGlossaryTerm(this)" style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:10px;padding:12px 14px;cursor:pointer;transition:all 0.2s ease;">' +
        '<div style="display:flex;align-items:center;gap:8px;">' +
        '<span style="color:var(--cyan);font-weight:600;font-size:14px;">' + escapeHtml(term.term) + '</span>' +
        '<span style="color:var(--text-muted);font-size:11px;">' + escapeHtml(term.en || '') + '</span>' +
        '</div>' +
        '<div class="glossary-desc" style="display:none;margin-top:8px;padding-top:8px;border-top:1px solid var(--border-subtle);color:var(--text-secondary);font-size:13px;line-height:1.6;">' + escapeHtml(term.desc) + '</div>' +
        '</div>';
    });
    list.innerHTML += '</div>';
  } catch (e) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--red);">加载失败，请刷新重试</div>';
  }
}
function toggleGlossaryTerm(el) {
  const desc = el.querySelector('.glossary-desc');
  if (desc) desc.style.display = desc.style.display === 'none' ? 'block' : 'none';
}
// ==================== Close modals by clicking overlay ====================
document.addEventListener('click', function(e) {
  if (e.target.closest('.modal-overlay') && !e.target.closest('.modal-container')) {
    document.querySelectorAll('.modal-overlay.active').forEach(m => { m.classList.remove('active'); document.body.style.overflow = ''; });
  }
  if (e.target.closest('.code-ex-overlay') && !e.target.closest('.code-ex-container')) {
    closeCodeEx();
  }
});
