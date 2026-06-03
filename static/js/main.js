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
      // Glow
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
    particles.forEach(p => {
      p.update();
      p.draw(ctx);
    });
    // Draw connections between close particles
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

  setTimeout(() => {
    if (toast.parentNode) toast.remove();
  }, 3000);
}

// ==================== Auth Page Logic ====================
(function() {
  const tabBtns = document.querySelectorAll('.auth-tab');
  if (!tabBtns.length) return;

  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  // Tab switching
  tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      tabBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      const target = this.dataset.tab;
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      if (target === 'login') {
        loginForm.classList.add('active');
      } else {
        registerForm.classList.add('active');
      }
    });
  });

  // Login
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
      showToast('请填写用户名和密码', 'error');
      return;
    }

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) {
        showToast('登录成功！正在跳转...', 'success');
        setTimeout(() => { window.location.href = '/dashboard'; }, 600);
      } else {
        showToast(data.message, 'error');
      }
    } catch (err) {
      showToast('网络错误，请稍后重试', 'error');
    }
  });

  // Register
  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-password-confirm').value;

    if (!username || !password || !confirm) {
      showToast('请填写所有字段', 'error');
      return;
    }
    if (username.length < 3) {
      showToast('用户名至少3个字符', 'error');
      return;
    }
    if (password.length < 6) {
      showToast('密码至少6个字符', 'error');
      return;
    }
    if (password !== confirm) {
      showToast('两次输入的密码不一致', 'error');
      return;
    }

    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (data.success) {
        showToast('注册成功！请登录', 'success');
        // Switch to login tab
        tabBtns[0].click();
        document.getElementById('login-username').value = username;
        registerForm.reset();
      } else {
        showToast(data.message, 'error');
      }
    } catch (err) {
      showToast('网络错误，请稍后重试', 'error');
    }
  });
})();

// ==================== Chapter Page Logic ====================
// Section tab switching
(function() {
  const tabs = document.querySelectorAll('.section-tab');
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      tabs.forEach(t => t.classList.remove('active'));
      this.classList.add('active');

      const target = this.dataset.panel;
      document.getElementById('knowledge-panel').classList.toggle('active', target === 'knowledge');
      document.getElementById('exercise-panel').classList.toggle('active', target === 'exercise');
    });
  });
})();

// Knowledge point accordion
function toggleKP(header) {
  const item = header.parentElement;
  item.classList.toggle('open');

  // Track progress when opening
  if (item.classList.contains('open') && typeof CHAPTER_ID !== 'undefined') {
    const index = parseInt(item.dataset.kpIndex);
    updateProgress('knowledge', index);
  }
}

// Mark knowledge point as done
function markDone(btn, type, index) {
  const item = btn.closest('.kp-item');
  const isDone = btn.classList.contains('done');

  if (isDone) {
    btn.classList.remove('done');
    btn.textContent = '✓ 标记为已掌握';
    item.classList.remove('completed');
  } else {
    btn.classList.add('done');
    btn.textContent = '✓ 已掌握';
    item.classList.add('completed');
  }
  updateProgress(type, index);
}

async function updateProgress(type, index) {
  if (typeof CHAPTER_ID === 'undefined') return;
  try {
    await fetch('/api/progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: CHAPTER_ID, type: type, index: index })
    });
  } catch (e) {
    // silent fail
  }
}

// Exercise — select option
(function() {
  document.querySelectorAll('.ex-option').forEach(opt => {
    opt.addEventListener('click', function() {
      const card = this.closest('.exercise-card');
      // Only allow selection if not already submitted
      if (card.dataset.submitted === 'true') return;

      card.querySelectorAll('.ex-option').forEach(o => o.classList.remove('selected'));
      this.classList.add('selected');
    });
  });
})();

// Exercise — submit answer
function submitAnswer(btn, correctIndex) {
  const card = btn.closest('.exercise-card');
  const selected = card.querySelector('.ex-option.selected');

  if (!selected) {
    showToast('请先选择一个答案', 'error');
    return;
  }

  if (card.dataset.submitted === 'true') {
    showToast('你已经提交过了', 'error');
    return;
  }

  card.dataset.submitted = 'true';
  btn.disabled = true;

  const chosenIndex = parseInt(selected.dataset.opt);
  const allOptions = card.querySelectorAll('.ex-option');

  allOptions.forEach((opt, i) => {
    opt.style.pointerEvents = 'none';
    if (i === correctIndex) {
      opt.classList.add('correct');
    }
  });

  if (chosenIndex === correctIndex) {
    selected.classList.add('correct');
    showToast('回答正确！🎉', 'success');

    const exIndex = parseInt(card.dataset.exIndex);
    updateProgress('exercise', exIndex);
  } else {
    selected.classList.add('wrong');
    showToast('回答错误，请查看解析', 'error');
  }
}

// Exercise — show explanation
function showExplanation(btn, correctIndex) {
  const card = btn.closest('.exercise-card');
  const answerDiv = card.querySelector('.ex-answer');

  // Auto-select correct option
  if (card.dataset.submitted !== 'true') {
    card.querySelectorAll('.ex-option').forEach((opt, i) => {
      opt.style.pointerEvents = 'none';
      if (i === correctIndex) {
        opt.classList.add('correct');
      }
    });
  }

  answerDiv.classList.toggle('visible');
  btn.textContent = answerDiv.classList.contains('visible') ? '收起解析' : '查看解析';
}

// ==================== Comic Viewer ====================
let comicState = {
  panels: [],
  currentPanel: 0,
  chapterId: null,
  kpIndex: null,
  kpTitle: null
};

async function openComic(chapterId, kpIndex, kpTitle) {
  comicState.chapterId = chapterId;
  comicState.kpIndex = kpIndex;
  comicState.kpTitle = kpTitle;
  comicState.currentPanel = 0;

  const overlay = document.getElementById('comic-overlay');
  const panelsContainer = document.getElementById('comic-panels');
  const nav = document.getElementById('comic-nav');
  const bottom = document.getElementById('comic-bottom');
  const settingsHint = document.getElementById('comic-settings-hint');
  const autoPlayWrap = document.getElementById('comic-autoplay-wrap');
  const badge = document.getElementById('comic-badge');

  // Reset UI
  panelsContainer.innerHTML = `
    <div class="comic-loading">
      <div class="loading-spinner"></div>
      <p>正在生成漫画讲解...</p>
      <p class="loading-sub">蛇蛇老师和同学正在创作中 🎨</p>
    </div>
  `;
  nav.style.display = 'none';
  bottom.style.display = 'none';
  autoPlayWrap.style.display = 'none';
  settingsHint.style.display = 'none';

  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  try {
    const res = await fetch(`/api/comic/${chapterId}/${kpIndex}`);
    const data = await res.json();

    if (!data.success) {
      panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 ${data.message || '生成失败，请稍后重试'}</p></div>`;
      return;
    }

    const comic = data.comic;
    comicState.panels = comic.panels;

    // Update header
    document.getElementById('comic-title').textContent = comic.title;
    badge.textContent = `共 ${comic.total_panels} 格`;

    renderComicPanels();
    nav.style.display = 'flex';
    bottom.style.display = 'flex';
    document.getElementById('comic-autoplay-wrap').style.display = 'flex';

    // Show settings hint if no API configured
    if (!comic.has_api) {
      settingsHint.style.display = 'block';
    }
  } catch (err) {
    panelsContainer.innerHTML = `<div class="comic-loading"><p>😔 网络错误，请稍后重试</p></div>`;
  }
}

function renderComicPanels() {
  const container = document.getElementById('comic-panels');
  const panels = comicState.panels;

  container.innerHTML = panels.map((p, i) => {
    const charClass = `${p.character}-panel`;
    return `
      <div class="comic-panel ${charClass}" data-panel="${i}" style="display:${i === comicState.currentPanel ? 'flex' : 'none'}; animation-delay:${i * 0.05}s">
        <div class="comic-avatar">${p.avatar}</div>
        <div class="comic-bubble">
          <div class="bubble-name">
            ${p.character_name}
            <button class="btn-voice" data-panel-idx="${i}" onclick="event.stopPropagation(); speakPanel(${i})" title="🔊 语音播报">
              🔊
            </button>
          </div>
          <div class="bubble-text">${escapeHtml(p.dialog)}</div>
          <div class="bubble-expression">${getExpressionEmoji(p.expression)} ${getExpressionLabel(p.expression)}</div>
          ${p.knowledge_bite ? `<span class="bubble-knowledge">💡 ${escapeHtml(p.knowledge_bite)}</span>` : ''}
        </div>
        <div class="comic-scene">📍 ${getSceneEmoji(p.scene)} ${getSceneLabel(p.scene)}</div>
      </div>
    `;
  }).join('');

  updateComicNav();
}

// ==================== Voice / TTS 语音播报 ====================
let currentSpeech = null;
let isSpeaking = false;
let cachedChineseVoices = [];

// Preload voices on page load (Chrome loads them async)
function initVoices() {
  const loadVoices = () => {
    const all = speechSynthesis.getVoices();
    cachedChineseVoices = all.filter(v =>
      v.lang.startsWith('zh') || v.lang === 'zh-CN' || v.lang === 'zh-TW'
    );
    // Also check for voices with Chinese names
    if (cachedChineseVoices.length === 0) {
      cachedChineseVoices = all.filter(v =>
        v.name.includes('Chinese') || v.name.includes('Microsoft Huihui') ||
        v.name.includes('Microsoft Kangkang') || v.name.includes('Yaoyao') ||
        v.name.includes('Tingting')
      );
    }
    if (cachedChineseVoices.length > 0) {
      console.log('[TTS] Found', cachedChineseVoices.length, 'Chinese voices:',
        cachedChineseVoices.map(v => v.name).join(', '));
    }
  };
  loadVoices();
  speechSynthesis.onvoiceschanged = loadVoices;
}

// Initialize voices as soon as possible
if (typeof speechSynthesis !== 'undefined') {
  initVoices();
}

function speakPanel(panelIdx) {
  const panel = comicState.panels[panelIdx];
  if (!panel) return;

  // If already speaking, stop
  if (isSpeaking) {
    stopSpeak();
    if (currentSpeech && currentSpeech._panelIdx === panelIdx) {
      currentSpeech = null;
      updateAllVoiceButtons();
      return;
    }
  }

  // Clean text: remove ONLY emoji and formatting — keep ALL Chinese and text
  const text = panel.dialog
    .replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
    .replace(/[\u{1F300}-\u{1F9FF}]/gu, '')
    .replace(/[☀-➿]/gu, '')
    .replace(/\*\*/g, '')
    .replace(/`/g, '')
    .replace(/<[^>]+>/g, '')
    .replace(/\s+/g, ' ')
    .trim();

  if (!text || text.length < 2) {
    console.warn('[TTS] Empty text after cleaning, original:', panel.dialog.substring(0, 50));
    return;
  }
  console.log('[TTS] Speaking:', text.substring(0, 80) + '...');

  const utterance = new SpeechSynthesisUtterance(text);

  // Force Chinese language
  utterance.lang = 'zh-CN';
  utterance.volume = 1.0;

  // Character-specific voice settings
  switch (panel.character) {
    case 'student':
      utterance.rate = 1.2;
      utterance.pitch = 1.3;
      break;
    case 'narrator':
      utterance.rate = 0.9;
      utterance.pitch = 0.95;
      break;
    case 'teacher':
    default:
      utterance.rate = 1.0;
      utterance.pitch = 1.05;
      break;
  }

  // Pick a Chinese voice
  const voices = speechSynthesis.getVoices();
  if (voices.length > 0 && cachedChineseVoices.length === 0) {
    // Re-cache if needed
    cachedChineseVoices = voices.filter(v =>
      v.lang.startsWith('zh') || v.lang === 'zh-CN' || v.lang === 'zh-TW' ||
      v.name.includes('Chinese') || v.name.includes('Huihui') ||
      v.name.includes('Kangkang') || v.name.includes('Yaoyao')
    );
  }

  if (cachedChineseVoices.length > 0) {
    if (panel.character === 'student') {
      const female = cachedChineseVoices.find(v =>
        v.name.includes('female') || v.name.includes('Female') ||
        v.name.includes('Huihui') || v.name.includes('Yaoyao') ||
        v.name.includes('Tingting')
      );
      utterance.voice = female || cachedChineseVoices[0];
    } else {
      const male = cachedChineseVoices.find(v =>
        v.name.includes('male') || v.name.includes('Male') ||
        v.name.includes('Kangkang')
      );
      utterance.voice = male || cachedChineseVoices[0];
    }
  }
  // If no Chinese voice found, just use lang='zh-CN' without setting a specific voice
  // This tells the browser to use its built-in Chinese TTS engine

  utterance._panelIdx = panelIdx;

  // Try server-side Edge-TTS first (best Chinese quality), fall back to browser
  tryServerTTS(panelIdx, text, panel.character);
}

async function tryServerTTS(panelIdx, text, character) {
  const panel = comicState.panels[panelIdx];
  const chId = comicState.chapterId;
  const kpId = comicState.kpIndex;
  const pId = panel.panel_id;

  try {
    const statusRes = await fetch('/api/tts/status');
    const statusData = await statusRes.json();
    if (!statusData.edge_tts_available && !statusData.doubao_available) {
      // Fall back to browser TTS when no server TTS available
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance._panelIdx = panelIdx;
      speakWithBrowserTTS(utterance, panelIdx);
      return;
    }

    const url = `/api/tts/panel/${chId}/${kpId}/${pId}`;
    const audio = new Audio(url);
    audio._panelIdx = panelIdx;

    audio.onplay = () => {
      isSpeaking = true;
      currentSpeech = audio;
      updateAllVoiceButtons();
    };
    audio.onended = () => {
      isSpeaking = false;
      currentSpeech = null;
      updateAllVoiceButtons();
      const autoPlay = document.getElementById('comic-autoplay');
      if (autoPlay && autoPlay.checked) {
        const nextIdx = panelIdx + 1;
        if (nextIdx < comicState.panels.length) {
          setTimeout(() => {
            navigateComic(1);
            setTimeout(() => speakPanel(nextIdx), 500);
          }, 600);
        }
      }
    };
    audio.onerror = () => {
      console.warn('[TTS] Server audio failed, falling back to browser');
      isSpeaking = false;
      currentSpeech = null;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance._panelIdx = panelIdx;
      speakWithBrowserTTS(utterance, panelIdx);
    };

    audio.play().catch(() => {
      // Audio play failed, use browser TTS
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance._panelIdx = panelIdx;
      speakWithBrowserTTS(utterance, panelIdx);
    });
  } catch (e) {
    console.warn('[TTS] Server check failed:', e);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'zh-CN';
    utterance._panelIdx = panelIdx;
    speakWithBrowserTTS(utterance, panelIdx);
  }
}

function speakWithBrowserTTS(utterance, panelIdx) {
  // Events
  utterance.onstart = () => {
    isSpeaking = true;
    currentSpeech = utterance;
    updateAllVoiceButtons();
  };
  utterance.onend = () => {
    isSpeaking = false;
    currentSpeech = null;
    updateAllVoiceButtons();
    // Auto-advance to next panel
    const nextIdx = panelIdx + 1;
    if (nextIdx < comicState.panels.length) {
      const autoPlay = document.getElementById('comic-autoplay');
      if (autoPlay && autoPlay.checked) {
        setTimeout(() => {
          navigateComic(1);
          setTimeout(() => speakPanel(nextIdx), 400);
        }, 600);
      }
    }
  };
  utterance.onerror = (e) => {
    if (e.error !== 'interrupted') {
      console.warn('TTS error:', e.error);
    }
    isSpeaking = false;
    currentSpeech = null;
    updateAllVoiceButtons();
  };

  speechSynthesis.speak(utterance);
}

function stopSpeak() {
  speechSynthesis.cancel();
  if (currentSpeech) {
    if (currentSpeech instanceof Audio) {
      currentSpeech.pause();
      currentSpeech.currentTime = 0;
    }
  }
  isSpeaking = false;
  currentSpeech = null;
  updateAllVoiceButtons();
  // Reset autoplay if stopping
  const autoPlay = document.getElementById('comic-autoplay');
  if (autoPlay && autoPlay.checked) {
    autoPlay.checked = false;
  }
}

function updateAllVoiceButtons() {
  document.querySelectorAll('.btn-voice').forEach(btn => {
    const idx = parseInt(btn.dataset.panelIdx);
    const isActive = currentSpeech && currentSpeech._panelIdx === idx;
    btn.classList.toggle('speaking', isActive);
    btn.textContent = isActive ? '🔊' : '🔊';
    btn.title = isActive ? '⏹ 停止' : '🔊 语音播报';
  });
}

function updateComicNav() {
  const prevBtn = document.getElementById('comic-prev');
  const nextBtn = document.getElementById('comic-next');
  const counter = document.getElementById('comic-counter');
  const total = comicState.panels.length;
  const current = comicState.currentPanel + 1;

  counter.textContent = `${current} / ${total}`;
  prevBtn.disabled = current <= 1;
  nextBtn.disabled = current >= total;
}

function navigateComic(delta) {
  const newIdx = comicState.currentPanel + delta;
  if (newIdx < 0 || newIdx >= comicState.panels.length) return;

  // Hide current panel
  const currentEl = document.querySelector(`.comic-panel[data-panel="${comicState.currentPanel}"]`);
  if (currentEl) currentEl.style.display = 'none';

  // Show new panel
  comicState.currentPanel = newIdx;
  const newEl = document.querySelector(`.comic-panel[data-panel="${newIdx}"]`);
  if (newEl) {
    newEl.style.display = 'flex';
    newEl.style.animation = 'none';
    newEl.offsetHeight; // reflow
    newEl.style.animation = 'panelSlideIn 0.4s ease both';
  }

  updateComicNav();

  // Scroll to panel top
  document.querySelector('.comic-container').scrollTo({
    top: newEl.offsetTop - 100,
    behavior: 'smooth'
  });
}

function restartComic() {
  comicState.currentPanel = 0;
  document.querySelectorAll('.comic-panel').forEach((el, i) => {
    el.style.display = i === 0 ? 'flex' : 'none';
  });
  updateComicNav();
  document.querySelector('.comic-container').scrollTo({ top: 0, behavior: 'smooth' });
}

function closeComic() {
  stopSpeak();
  document.getElementById('comic-autoplay').checked = false;
  document.getElementById('comic-overlay').classList.remove('active');
  document.body.style.overflow = '';
  comicState.panels = [];
  comicState.currentPanel = 0;
}

// Close comic with Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    const overlay = document.getElementById('comic-overlay');
    if (overlay.classList.contains('active')) {
      closeComic();
    }
    const settings = document.getElementById('comic-settings-modal');
    if (settings.style.display === 'flex') {
      closeComicSettings();
    }
  }
  // Left/Right arrow navigation
  if (e.key === 'ArrowLeft') {
    const overlay = document.getElementById('comic-overlay');
    if (overlay.classList.contains('active')) {
      e.preventDefault();
      navigateComic(-1);
    }
  }
  if (e.key === 'ArrowRight') {
    const overlay = document.getElementById('comic-overlay');
    if (overlay.classList.contains('active')) {
      e.preventDefault();
      navigateComic(1);
    }
  }
});

// ==================== Comic Settings ====================
function showComicSettings() {
  document.getElementById('comic-settings-modal').style.display = 'flex';
}

function closeComicSettings() {
  document.getElementById('comic-settings-modal').style.display = 'none';
}

async function saveComicConfig() {
  const apiKey = document.getElementById('comic-api-key').value.trim();
  const apiBase = document.getElementById('comic-api-base').value.trim();
  const model = document.getElementById('comic-model').value.trim();

  if (!apiKey) {
    showToast('请填写 API Key', 'error');
    return;
  }

  try {
    const res = await fetch('/api/comic/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey, api_base: apiBase, model: model || 'gpt-4o' })
    });
    const data = await res.json();
    if (data.success) {
      showToast('配置已保存！下次讲解将使用 AI 生成', 'success');
      closeComicSettings();
      document.getElementById('comic-settings-hint').style.display = 'none';
    } else {
      showToast('配置保存失败', 'error');
    }
  } catch (err) {
    showToast('网络错误', 'error');
  }
}

// ==================== Comic Helpers ====================
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML.replace(/\n/g, '<br>');
}

function getExpressionEmoji(expr) {
  const map = {
    'explaining': '📝', 'thinking': '🤔', 'surprised': '😮',
    'happy': '😊', 'questioning': '🙋', 'excited': '🤩', 'inspired': '💡'
  };
  return map[expr] || '💬';
}

function getExpressionLabel(expr) {
  const map = {
    'explaining': '认真讲解中', 'thinking': '思考中', 'surprised': '感到惊讶',
    'happy': '开心', 'questioning': '举手提问', 'excited': '兴奋', 'inspired': '恍然大悟'
  };
  return map[expr] || expr;
}

function getSceneEmoji(scene) {
  const map = {
    'classroom': '🏫', 'coding_lab': '💻', 'thought_bubble': '💭',
    'whiteboard': '📋', 'computer_screen': '🖥️'
  };
  return map[scene] || '📍';
}

function getSceneLabel(scene) {
  const map = {
    'classroom': '教室', 'coding_lab': '编程实验室', 'thought_bubble': '思考',
    'whiteboard': '白板', 'computer_screen': '电脑屏幕'
  };
  return map[scene] || scene;
}

// ==================== Mindmap ====================
let mindmapInstance = null;
let mindmapSvg = null;

async function openMindmap() {
  const overlay = document.getElementById('mindmap-overlay');
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';

  const mdData = document.getElementById('mindmap-data');
  if (!mdData) return;

  const svg = document.getElementById('mindmap-svg');
  svg.innerHTML = '';

  try {
    const { Transformer } = window.markmap;
    const { Markmap } = window.markmap;

    const transformer = new Transformer();
    const { root } = transformer.transform(mdData.textContent);

    mindmapInstance = Markmap.create(svg, {
      autoFit: true,
      colorFreezeLevel: 2,
      duration: 600,
      maxInitialScale: 1.2,
      pan: true,
      zoom: true,
    }, root);

    mindmapSvg = svg;
    mindmapInstance.fit();
  } catch(e) {
    console.error('[Mindmap] Render error:', e);
    svg.innerHTML = '<div style=\"color:var(--text-secondary);text-align:center;padding:60px;\">思维导图加载失败，请刷新重试</div>';
  }
}

function closeMindmap() {
  document.getElementById('mindmap-overlay').classList.remove('active');
  document.body.style.overflow = '';
}

function mindmapZoomIn() {
  if (mindmapInstance) mindmapInstance.rescale(1.3);
}

function mindmapZoomOut() {
  if (mindmapInstance) mindmapInstance.rescale(0.7);
}

function mindmapReset() {
  if (mindmapInstance) mindmapInstance.fit();
}

function mindmapExpandAll() {
  if (mindmapInstance) {
    mindmapInstance.setData(mindmapInstance.state.data);
    mindmapInstance.fit();
  }
}

function mindmapCollapseAll() {
  if (!mindmapInstance) return;
  const collapseNode = (node) => {
    if (node.c) {
      node.p = { ...node.p, f: true };
      node.c.forEach(collapseNode);
    }
  };
  try {
    const data = JSON.parse(JSON.stringify(mindmapInstance.state.data));
    data.p = { ...data.p, f: true };
    if (data.c) data.c.forEach(collapseNode);
    mindmapInstance.setData(data);
  } catch(e) {}
}

// ==================== JJ老师 AI Chat ====================
let jjCodeContext = '';

function toggleJJChat() {
  const overlay = document.getElementById('jj-chat-overlay');
  if (overlay) overlay.classList.toggle('active');
  if (overlay && overlay.classList.contains('active')) {
    setTimeout(() => document.getElementById('jj-input').focus(), 200);
  }
}

function askJJAboutExercise(question) {
  jjCodeContext = question;
  const overlay = document.getElementById('jj-chat-overlay');
  if (overlay) overlay.classList.add('active');
  // Pre-fill question
  const input = document.getElementById('jj-input');
  if (input) { input.value = '这道题我不太懂，能帮我分析一下吗？'; input.focus(); }
}

async function sendJJMessage() {
  const input = document.getElementById('jj-input');
  const btn = document.getElementById('jj-send-btn');
  const messagesDiv = document.getElementById('jj-messages');
  const typingDiv = document.getElementById('jj-typing');
  const question = (input.value || '').trim();

  if (!question || btn.disabled) return;

  // Add user message
  const userMsg = document.createElement('div');
  userMsg.className = 'msg user';
  userMsg.textContent = question;
  messagesDiv.appendChild(userMsg);
  input.value = '';
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  // Show typing
  btn.disabled = true;
  typingDiv.style.display = 'block';
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  try {
    const body = { question: question };
    if (jjCodeContext) { body.context = jjCodeContext; jjCodeContext = ''; }

    const res = await fetch('/api/ask-jj', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    typingDiv.style.display = 'none';

    const jjMsg = document.createElement('div');
    jjMsg.className = 'msg jj';
    if (data.success) {
      jjMsg.innerHTML = formatJJAnswer(data.answer);
    } else {
      jjMsg.textContent = '😔 ' + (data.error || '出错了，请稍后重试');
    }
    messagesDiv.appendChild(jjMsg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  } catch(e) {
    typingDiv.style.display = 'none';
    const errMsg = document.createElement('div');
    errMsg.className = 'msg jj';
    errMsg.textContent = '😔 网络错误，请检查网络连接后重试';
    messagesDiv.appendChild(errMsg);
  } finally {
    btn.disabled = false;
    input.focus();
  }
}

function formatJJAnswer(text) {
  // Convert markdown code blocks to HTML
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // Code blocks
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Newlines
    .replace(/\n/g, '<br>');
  return html;
}
