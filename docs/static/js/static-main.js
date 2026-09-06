/* ============================================================
   PyMaster — Static Main JavaScript (作品展示模式)
   基于 main.js 改造，所有 API 调用替换为提示或本地数据加载
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

// 作品展示模式提示
function showDemoToast(feature) {
  showToast('作品展示模式，' + (feature || '此功能') + '需后端支持', 'error');
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
    showDemoToast('登录功能');
  });

  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    showDemoToast('注册功能');
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

  if (chosenIdx === correctIdx) {
    selected.classList.add('correct');
    showToast('✅ 回答正确！', 'success');
    checkKPCompletion(chapterId, kpIndex, card);
  } else {
    selected.classList.add('wrong');
    showToast('❌ 回答错误', 'error');
  }
}

function showExAnswer(btn) {
  const card = btn.closest('.kp-exercise');
  const answerDiv = card.querySelector('.ex-answer');
  const optionsDiv = card.querySelector('.ex-options');
  const correctIdx = parseInt(optionsDiv.dataset.correct);

  if (card.dataset.exSubmitted !== 'true') {
    card.querySelectorAll('.ex-option').forEach((opt, i) => {
      opt.style.pointerEvents = 'none';
      if (i === correctIdx) opt.classList.add('correct');
    });
  }
  answerDiv.style.display = answerDiv.style.display === 'none' ? 'block' : 'none';
  btn.textContent = answerDiv.style.display === 'block' ? '收起解析' : '查看解析';
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
      Enter: cm => { cm.execCommand('newlineAndIndent'); },
    }
  });
  codeMirrorEditor.setSize('100%', '100%');
  codeMirrorEditor.on('change', () => {
    clearTimeout(codeExLintTimer);
  });
  codeMirrorEditor.getInputField().addEventListener('keydown', e => {
    if (e.key === 'Backspace' || e.key === 'Delete') e.stopPropagation();
  });
}

function openCodeEx(chapterId, kpIndex, exIndex, prompt) {
  codeExState = { chapterId, kpIndex, exIndex };
  document.getElementById('code-ex-prompt').textContent = '💡 ' + prompt;
  document.getElementById('code-ex-output').innerHTML = '';
  document.getElementById('code-ex-status').textContent = '';
  const errEl = document.getElementById('code-ex-lint-errors');
  if (errEl) errEl.textContent = '';
  const jjArea = document.getElementById('code-ex-jj-area');
  if (jjArea) jjArea.style.display = 'none';
  document.getElementById('code-ex-modal').classList.add('active');
  document.body.style.overflow = 'hidden';

  if (!codeMirrorEditor) initCodeMirror();
  codeMirrorEditor.setValue('# 在这里编写你的 Python 代码\n');
  codeMirrorEditor.clearHistory();
  codeMirrorEditor.focus();
  codeMirrorEditor.clearGutter('CodeMirror-lint-markers');
  codeMirrorEditor.eachLine(l => codeMirrorEditor.removeLineClass(l, 'wrap', 'cm-lint-error-line'));
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

async function askJJAboutCode() {
  if (!codeMirrorEditor) return;
  const code = codeMirrorEditor.getValue().trim();
  if (!code) { showToast('请先编写代码', 'error'); return; }
  showDemoToast('AI问答功能');
}

async function runCodeEx() {
  if (!codeMirrorEditor) return;
  showDemoToast('代码运行功能');
}

// --- KP Completion ---
async function completeKP(chapterId, kpIndex) {
  // 作品展示模式：无需后端记录
  return Promise.resolve();
}

function checkKPCompletion(chapterId, kpIndex, exerciseCard) {
  const kpItem = exerciseCard.closest('.kp-item');
  const allExercises = kpItem.querySelectorAll('.kp-exercise');
  let allDone = true;

  allExercises.forEach(ex => {
    if (ex.dataset.exSubmitted !== 'true') allDone = false;
  });

  if (allDone) {
    kpItem.classList.add('completed');
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
    const indicator = kpItem.querySelector('.kp-indicator');
    if (indicator) indicator.textContent = '✅';

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
      const bodyInner = nextItem.querySelector('.kp-body-inner');
      if (bodyInner) bodyInner.style.display = '';
      if (nextHeader) nextHeader.onclick = function() { toggleKP(this); };
    }

    showToast('🎉 恭喜完成本知识点！', 'success');

    const allExList = document.querySelectorAll('.kp-exercise');
    const allExercisesDone = allExList.length > 0 && Array.from(allExList).every(ex => ex.dataset.exSubmitted === 'true');
    if (allExercisesDone) {
      checkChapterComplete(chapterId);
    }
  }
}

// --- Chapter Completion → 星辰启示 CG ---
function checkChapterComplete(chapterId) {
  const allKpItems = document.querySelectorAll('.kp-item');
  if (allKpItems.length === 0) return;

  const lastKpItem = allKpItems[allKpItems.length - 1];
  const isLastKpCompleted = lastKpItem.classList.contains('completed');

  if (isLastKpCompleted) {
    showToast('🌌 最后一题完成！即将进入星辰启示...', 'success');
    setTimeout(() => {
      window.location.href = 'static/revelation_cg.html?ch=' + chapterId;
    }, 1500);
  }
}

// --- Favorites ---
async function toggleFav(chapterId, exIndex, question) {
  showDemoToast('收藏功能');
}

async function showFavorites() {
  const modal = document.getElementById('fav-modal');
  const list = document.getElementById('fav-list');
  if (!modal || !list) return;
  list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">📭 作品展示模式：收藏功能需登录后端支持</div>';
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

// --- Wrong Answer Book ---
async function showWrongBook() {
  const modal = document.getElementById('wrong-modal');
  const list = document.getElementById('wrong-list');
  if (!modal || !list) return;
  list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">🎉 作品展示模式：错题本需登录后端支持</div>';
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
}

async function dismissWrong(index) {
  showDemoToast('错题管理功能');
}

// --- Notes ---
function toggleNotes(btn) {
  const editor = btn.parentElement.querySelector('.kp-notes-editor');
  if (editor) {
    const isVisible = editor.style.display !== 'none';
    editor.style.display = isVisible ? 'none' : 'block';
    btn.textContent = isVisible ? '📝 我的笔记' : '📝 收起笔记';
  }
}

async function loadNote(kpKey, textarea) {
  // 作品展示模式：无后端笔记
}

async function saveNote(chapterId, kpIndex, btn) {
  showDemoToast('笔记保存功能');
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
  // 作品展示模式：无文件关联
}

function renderNoteFiles(editor, files, chapterId, kpIndex) {
  const container = editor.querySelector('.note-files-list');
  if (!container) return;
  container.style.display = 'none';
}

async function createNoteTxt(chapterId, kpIndex) {
  showDemoToast('新建TXT功能');
}

async function addLocalFile(chapterId, kpIndex) {
  showDemoToast('文件关联功能');
}

async function openNoteFile(filePath) {
  showDemoToast('打开文件功能');
}

async function removeNoteFile(chapterId, kpIndex, filePath, btn) {
  showDemoToast('移除文件功能');
}

// --- Mode Toggle ---
async function toggleMode() {
  showToast('作品展示模式：所有章节已解锁', 'success');
}

// --- Modal helpers ---
function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    closeModal('fav-modal');
    closeModal('wrong-modal');
    closeModal('glossary-modal');
    const codeEx = document.getElementById('code-ex-modal');
    if (codeEx && codeEx.classList.contains('active')) closeCodeEx();
  }
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

// 静态模式：从 data/comics.json 加载漫画数据
let _comicsCache = null;
async function _loadComicsData() {
  if (_comicsCache) return _comicsCache;
  try {
    const res = await fetch('data/comics.json');
    _comicsCache = await res.json();
    return _comicsCache;
  } catch (e) {
    return {};
  }
}

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
    const comicsData = await _loadComicsData();
    const key = chapterId + '_' + kpIndex;
    const comic = comicsData[key];
    if (!comic) {
      panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 该知识点的漫画内容暂未准备好</p></div>`;
      return;
    }
    comicState.panels = comic.panels;
    document.getElementById('comic-title').textContent = comic.title || kpTitle;
    badge.textContent = `共 ${comic.panels.length} 格`;
    renderComicPanels(); nav.style.display = 'flex'; bottom.style.display = 'flex';
    document.getElementById('comic-autoplay-wrap').style.display = 'flex';
  } catch (err) {
    panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 漫画加载失败，请稍后重试</p></div>`;
  }
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
  utterance._panelIdx = panelIdx;
  // 静态模式：直接使用浏览器 TTS
  speakWithBrowserTTS(utterance, panelIdx);
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
function closeComic() { stopSpeak(); const ap=document.getElementById('comic-autoplay'); if(ap) ap.checked=false; const ov=document.getElementById('comic-overlay'); if(ov) ov.classList.remove('active'); document.body.style.overflow=''; comicState.panels=[]; comicState.currentPanel=0; }

// ==================== Comic Settings ====================
function showComicSettings() { showDemoToast('API配置功能'); }
function closeComicSettings() { const m=document.getElementById('comic-settings-modal'); if(m) m.style.display='none'; }
async function saveComicConfig() { showDemoToast('API配置功能'); }

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
function toggleJJChat(){const o=document.getElementById('jj-chat-overlay');if(o)o.classList.toggle('active');if(o&&o.classList.contains('active')){setTimeout(()=>{const i=document.getElementById('jj-input'); if(i) i.focus();},200);const el=document.getElementById('jj-quota'); if(el){el.textContent='作品展示模式';el.style.color='var(--text-muted)';}}}
function askJJAboutExercise(question){jjCodeContext=question;const o=document.getElementById('jj-chat-overlay');if(o)o.classList.add('active');const i=document.getElementById('jj-input');if(i){i.value='这道题我不太懂，能帮我分析一下吗？';i.focus();}const el=document.getElementById('jj-quota'); if(el){el.textContent='作品展示模式';el.style.color='var(--text-muted)';}}
async function loadAIQuota() {
  const el = document.getElementById('jj-quota'); if (!el) return;
  el.textContent = '作品展示模式';
  el.style.color = 'var(--text-muted)';
}
async function sendJJMessage() {
  const input=document.getElementById('jj-input');const btn=document.getElementById('jj-send-btn');const msgDiv=document.getElementById('jj-messages');const q=(input.value||'').trim();
  if(!q||btn.disabled)return;
  const u=document.createElement('div');u.className='msg user';u.textContent=q;msgDiv.appendChild(u);input.value='';msgDiv.scrollTop=msgDiv.scrollHeight;
  btn.disabled=true;
  setTimeout(()=>{
    const j=document.createElement('div');
    j.className='msg jj';
    j.innerHTML='👋 作品展示模式下，JJ老师 AI 问答功能不可用。此功能需要后端 AI 接口支持。<br><br>您可以浏览课程内容、做练习题、查看漫画讲解和思维导图。';
    msgDiv.appendChild(j);msgDiv.scrollTop=msgDiv.scrollHeight;
    btn.disabled=false;input.focus();
  },800);
}
function formatJJAnswer(text){return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/```(\w*)\n?([\s\S]*?)```/g,'<pre><code>$2</code></pre>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>');}

// ==================== JJ Auto Chapter Guide & Completion (静态模式：跳过) ====================
async function autoJJChapterGuide() { /* 作品展示模式：跳过 */ }
async function autoJJChapterComplete() { /* 作品展示模式：跳过 */ }

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

  if (myMindmapInstance) {
    myMindmapInstance.destroy();
    myMindmapInstance = null;
  }

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

  // 静态模式：使用默认数据
  const initData = {
    nodeData: MindElixir.new(typeof CHAPTER_TITLE !== 'undefined' ? CHAPTER_TITLE : '我的思维导图').nodeData,
    arrows: [],
    summaries: [],
    meta: {}
  };
  myMindmapInstance.init(initData);
  setTimeout(() => { try { myMindmapInstance.toCenter(); } catch(e) {} }, 200);
}

function closeMyMindmap() {
  const ov=document.getElementById('my-mindmap-overlay'); if(ov) ov.classList.remove('active');
  document.body.style.overflow = '';
  if (myMindmapInstance) {
    myMindmapInstance.destroy();
    myMindmapInstance = null;
  }
}

async function myMindmapSave() {
  showDemoToast('思维导图保存功能');
}

function myMindmapFit() {
  if (myMindmapInstance) { try { myMindmapInstance.toCenter(); } catch(e) {} }
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
          showToast('📂 思维导图已加载', 'success');
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
  showDemoToast('思维导图删除功能');
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
    for (let i = rockets.length - 1; i >= 0; i--) {
      const r = rockets[i];
      r.trail.push({ x: r.x, y: r.y });
      if (r.trail.length > 10) r.trail.shift();
      r.y -= r.speed;
      r.x += (Math.random() - 0.5) * 0.6;
      for (let j = 0; j < r.trail.length; j++) {
        const alpha = j / r.trail.length;
        ctx.fillStyle = 'rgba(255,255,255,' + (alpha * 0.5) + ')';
        ctx.beginPath();
        ctx.arc(r.trail[j].x, r.trail[j].y, 1.5 * alpha, 0, Math.PI * 2);
        ctx.fill();
      }
      if (r.y <= r.targetY) { createBurst(r.x, r.y); rockets.splice(i, 1); }
    }
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx; p.y += p.vy; p.vy += 0.04; p.vx *= 0.99; p.life -= p.decay;
      if (p.life <= 0) { particles.splice(i, 1); continue; }
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = p.life * 0.2;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (isFull) { if (Math.random() < 0.08) createRocket(); if (Math.random() < 0.05) createRocket(); }
    else { if (Math.random() < 0.03) createRocket(); }
    if (rockets.length > 0 || particles.length > 0) { fireworksAnimId = requestAnimationFrame(animate); }
  }
  for (let i = 0; i < (isFull ? 5 : 2); i++) { setTimeout(createRocket, i * 200); }
  if (fireworksAnimId) cancelAnimationFrame(fireworksAnimId);
  animate();
}

function stopFireworks() {
  if (fireworksAnimId) { cancelAnimationFrame(fireworksAnimId); fireworksAnimId = null; }
  const canvas = document.getElementById('fireworks-canvas');
  if (canvas) { const ctx = canvas.getContext('2d'); ctx.clearRect(0, 0, canvas.width, canvas.height); }
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
  if (!overlay) return;
  const scoreNum = document.getElementById('score-number');
  const scoreLabel = document.getElementById('score-label');
  const feedbackEl = document.getElementById('score-feedback');
  const strengthsEl = document.getElementById('score-strengths');
  const weaknessesEl = document.getElementById('score-weaknesses');
  const quoteEl = document.getElementById('score-quote');
  const card = document.getElementById('score-card');

  overlay.classList.remove('active');
  card.className = 'score-card';
  scoreNum.className = 'score-number';
  document.body.classList.remove('screen-shake');
  stopFireworks();
  document.querySelectorAll('.confetti-piece').forEach(function(el) { el.remove(); });

  feedbackEl.textContent = feedback || '';
  strengthsEl.textContent = strengths ? '✅ ' + strengths : '';
  weaknessesEl.textContent = weaknesses ? '❌ ' + weaknesses : '';

  var quoteText = '';
  var labelText = 'AI 评分';

  if (score >= 40 && score < 80) {
    scoreNum.className = 'score-number pass';
    labelText = '✅ 通过！再接再厉';
    var quotes = [
      '"成功是跌倒九次，爬起来十次。" — 香港俗语',
      '"不积跬步，无以至千里。" — 荀子',
      '"Practice makes perfect." — 熟能生巧',
      '"每一次练习都是向大师迈进的一步。"',
      '"坚持是成功的另一个名字。"',
      '"Rome was not built in a day."'
    ];
    quoteText = quotes[Math.floor(Math.random() * quotes.length)];
    setTimeout(function() { startFireworks('edge'); }, 300);
  } else if (score >= 80 && score < 95) {
    scoreNum.className = 'score-number medium';
    card.classList.add('glow');
    labelText = '🌟 才华横溢！';
    var poems = [
      '「心有灵犀一点通，学贯东西自不同。\n  代码如诗写乾坤，智慧光芒照苍穹。」',
      '「笔落惊风雨，码成泣鬼神。\n  逻辑如丝织锦绣，思维似剑破迷津。」',
      '「少年负壮气，奋烈自有时。\n  编程之道通天地，智慧之花绽满枝。」',
      '「博学之，审问之，慎思之，明辨之，笃行之。」\n  —— 《礼记·中庸》',
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
      if (!overlay.classList.contains('active')) { clearInterval(confettiInterval); return; }
      createConfetti(15);
    }, 1500);
  }

  quoteEl.textContent = quoteText;
  scoreLabel.textContent = labelText;
  overlay.classList.add('active');
  scoreNum.textContent = '0';
  scoreNum.classList.add('pop');

  var duration = 1000;
  var startTime = Date.now();
  function animateScore() {
    var elapsed = Date.now() - startTime;
    var progress = Math.min(elapsed / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(eased * score);
    scoreNum.textContent = current;
    if (progress < 1) { requestAnimationFrame(animateScore); }
    else { scoreNum.textContent = score; }
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

document.addEventListener('DOMContentLoaded', function() {
  // 作品展示模式：跳过 JJ 章节引导
});

// ==================== Theme Toggle ====================
(function() {
  const KEY = 'pymaster_theme';
  const saved = localStorage.getItem(KEY);
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    const btn = document.querySelector('.btn-theme-toggle');
    if (btn) btn.textContent = '☀️';
  }
})();
function toggleTheme() {
  const html = document.documentElement;
  const btn = document.querySelector('.btn-theme-toggle');
  const isLight = html.getAttribute('data-theme') === 'light';
  if (isLight) {
    html.removeAttribute('data-theme');
    if (btn) btn.textContent = '🌙';
    localStorage.setItem('pymaster_theme', 'dark');
  } else {
    html.setAttribute('data-theme', 'light');
    if (btn) btn.textContent = '☀️';
    localStorage.setItem('pymaster_theme', 'light');
  }
}

// ==================== Glossary (静态模式：从本地加载) ====================
async function showGlossary() {
  const modal = document.getElementById('glossary-modal');
  const list = document.getElementById('glossary-list');
  if (!modal || !list) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  list.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-muted);">加载中...</div>';
  try {
    const res = await fetch('data/glossary_py.json');
    const terms = await res.json();
    let html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;">';
    terms.forEach(function(term) {
      html += '<div class="glossary-item" onclick="toggleGlossaryTerm(this)" style="background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:10px;padding:12px 14px;cursor:pointer;transition:all 0.2s ease;">' +
        '<div style="display:flex;align-items:center;gap:8px;">' +
        '<span style="color:var(--cyan);font-weight:600;font-size:14px;">' + escapeHtml(term.term) + '</span>' +
        '<span style="color:var(--text-muted);font-size:11px;">' + escapeHtml(term.en || '') + '</span>' +
        '</div>' +
        '<div class="glossary-desc" style="display:none;margin-top:8px;padding-top:8px;border-top:1px solid var(--border-subtle);color:var(--text-secondary);font-size:13px;line-height:1.6;">' + escapeHtml(term.desc) + '</div>' +
        '</div>';
    });
    html += '</div>';
    list.innerHTML = html;
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
