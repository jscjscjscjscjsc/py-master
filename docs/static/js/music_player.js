/**
 * music_player.js — 学习背景音乐（多曲目 · 播放 / 暂停 / 上一首 / 下一首）
 *
 * 设计上只做三件事，但每件都得做对：
 *
 * 1. **不自动出声**。浏览器的自动播放策略会拦截没有用户交互的 play()，
 *    所以默认「记忆上次状态但只在用户点过之后才播」，被拦截时静默降级，
 *    绝不弹报错——背景音乐不该打断学习。
 * 2. **跨页面不中断**。用 localStorage 记住曲目与进度（秒），
 *    换页时从上次的位置接着放，而不是每次从头开始。
 * 3. **不抢注意力**。控制条平时是收起的，只留一个小音符按钮；
 *    悬停/点击才展开曲目名与进度。
 *
 * 同时兼容旧接口 AdaptiveMusic/AmbientMusic.toggle()，
 * 老页面上的「音乐」按钮不用改一行代码也能用。
 */
const PyMusic = {
  audio: null,
  tracks: [],
  index: 0,
  ready: false,
  enabled: false,
  expanded: false,
  volume: 0.45,

  KEYS: {
    enabled: 'pymaster_music_enabled',
    index: 'pymaster_music_index',
    volume: 'pymaster_music_volume',
    position: 'pymaster_music_position',
  },

  fallbackTracks: [
    { file: 'calm-morning.mp3', title: '清晨的书桌', artist: 'PyMaster', mood: '安静' },
    { file: 'warm-sunlight.mp3', title: '暖阳', artist: 'PyMaster', mood: '温暖' },
  ],

  init(options = {}) {
    if (this.ready) return;
    this.ready = true;
    try {
      this.enabled = localStorage.getItem(this.KEYS.enabled) === '1';
      this.index = Number(localStorage.getItem(this.KEYS.index) || 0) || 0;
      const saved = parseFloat(localStorage.getItem(this.KEYS.volume));
      if (!Number.isNaN(saved)) this.volume = Math.min(1, Math.max(0, saved));
    } catch (error) { /* 隐私模式下 localStorage 不可用，用默认值 */ }

    this.mount();
    this.loadPlaylist(options.playlistUrl || this.staticAsset('audio/playlist.json'));
  },

  async loadPlaylist(url) {
    let tracks = this.fallbackTracks;
    try {
      const response = await fetch(url);
      const data = await response.json();
      if (Array.isArray(data) && data.length) tracks = data;
      else if (data && Array.isArray(data.tracks) && data.tracks.length) tracks = data.tracks;
    } catch (error) {
      tracks = this.fallbackTracks;
    }
    this.tracks = tracks;
    if (this.index >= this.tracks.length) this.index = 0;
    this.renderTrack();
    if (this.enabled) {
      // 记忆里是开着的：尝试续播，被浏览器拦了就算了（不弹提示）
      const restored = await this.play({ resume: true, silent: true });
      if (!restored) this.renderState();
    } else {
      this.renderState();
    }
  },

  ensureAudio() {
    if (this.audio) return this.audio;
    const audio = new Audio();
    audio.preload = 'auto';
    audio.volume = this.volume;
    audio.addEventListener('ended', () => this.next());
    audio.addEventListener('timeupdate', () => {
      this.renderProgress();
      // 每 5 秒记一次进度就够了，太频繁会拖慢页面
      if (Math.floor(audio.currentTime) % 5 === 0) {
        try { localStorage.setItem(this.KEYS.position, String(Math.floor(audio.currentTime))); } catch (e) {}
      }
    });
    audio.addEventListener('error', () => {
      this.setStatus('这首曲子加载失败，换下一首');
      setTimeout(() => this.next(), 900);
    });
    this.audio = audio;
    return audio;
  },

  mount() {
    if (document.getElementById('pymusic-dock')) return;
    // 开场动画页与登录页只要音乐，不要浮窗（body 上加 data-no-music-dock 即可）
    if (document.body && document.body.dataset && document.body.dataset.noMusicDock !== undefined) return;
    const dock = document.createElement('div');
    dock.id = 'pymusic-dock';
    dock.className = 'pymusic-dock';
    dock.innerHTML = `
      <button class="pymusic-glyph" id="pymusic-toggle" title="学习背景音乐">
        <span id="pymusic-glyph-icon">♪</span>
      </button>
      <div class="pymusic-panel" id="pymusic-panel">
        <div class="pymusic-head">
          <span class="pymusic-title" id="pymusic-title">准备播放</span>
          <button class="pymusic-close" id="pymusic-close" title="收起">✕</button>
        </div>
        <div class="pymusic-meta" id="pymusic-meta">轻松学习 · 专注不打扰</div>
        <div class="pymusic-bar"><i id="pymusic-progress"></i></div>
        <div class="pymusic-controls">
          <button id="pymusic-prev" title="上一首">⏮</button>
          <button id="pymusic-play" class="primary" title="播放 / 暂停">▶</button>
          <button id="pymusic-next" title="下一首">⏭</button>
          <span class="pymusic-vol-wrap" title="音量">
            🔊<input type="range" id="pymusic-volume" min="0" max="100" value="${Math.round(this.volume * 100)}">
          </span>
        </div>
      </div>`;
    document.body.appendChild(dock);

    const bind = (id, handler) => {
      const node = document.getElementById(id);
      if (node) node.addEventListener('click', handler);
    };
    bind('pymusic-toggle', () => this.togglePanel());
    bind('pymusic-close', () => this.togglePanel(false));
    bind('pymusic-play', () => (this.playing() ? this.pause() : this.play()));
    bind('pymusic-next', () => this.next());
    bind('pymusic-prev', () => this.prev());
    const volume = document.getElementById('pymusic-volume');
    if (volume) {
      volume.addEventListener('input', () => {
        this.volume = Number(volume.value) / 100;
        if (this.audio) this.audio.volume = this.volume;
        try { localStorage.setItem(this.KEYS.volume, String(this.volume)); } catch (e) {}
      });
    }
  },

  togglePanel(force) {
    const panel = document.getElementById('pymusic-panel');
    if (!panel) return;
    const open = force === undefined ? !this.expanded : !!force;
    this.expanded = open;
    panel.classList.toggle('open', open);
  },

  playing() {
    return !!(this.audio && !this.audio.paused && !this.audio.ended);
  },

  track() {
    return this.tracks[this.index] || { title: '背景音乐', artist: '' };
  },

  // 在线演示站平铺在 docs/ 下，绝对路径 /static/... 会 404
  staticAsset(path) {
    return (window.PYMASTER_STATIC ? 'static/' : '/static/') + path;
  },

  currentSrc() {
    const track = this.track();
    return this.staticAsset('audio/' + (track.file || ''));
  },

  async play(options = {}) {
    if (!this.tracks.length) return false;
    const audio = this.ensureAudio();
    const wantSrc = this.currentSrc();
    if (audio.getAttribute('src') !== wantSrc) {
      audio.setAttribute('src', wantSrc);
      if (options.resume) {
        let position = 0;
        try { position = Number(localStorage.getItem(this.KEYS.position) || 0) || 0; } catch (e) { position = 0; }
        if (position > 3) {
          audio.addEventListener('loadedmetadata', function once() {
            audio.removeEventListener('loadedmetadata', once);
            if (position < audio.duration - 4) audio.currentTime = position;
          });
        }
      }
    }
    audio.volume = this.volume;
    try {
      await audio.play();
      this.enabled = true;
      try { localStorage.setItem(this.KEYS.enabled, '1'); } catch (e) {}
      this.setStatus('');
      this.renderState();
      return true;
    } catch (error) {
      this.enabled = false;
      try { localStorage.setItem(this.KEYS.enabled, '0'); } catch (e) {}
      this.renderState();
      if (!options.silent) this.setStatus('浏览器拦下了自动播放，点一下 ▶ 试试');
      return false;
    }
  },

  pause() {
    if (this.audio) this.audio.pause();
    this.enabled = false;
    try { localStorage.setItem(this.KEYS.enabled, '0'); } catch (e) {}
    this.renderState();
  },

  /** 老页面调用的是 AmbientMusic.toggle()，这里保持同名同行为 */
  toggle() {
    if (this.playing()) this.pause();
    else this.play();
    this.togglePanel(true);
  },

  next() {
    if (!this.tracks.length) return;
    this.index = (this.index + 1) % this.tracks.length;
    this.switchTo();
  },

  prev() {
    if (!this.tracks.length) return;
    this.index = (this.index - 1 + this.tracks.length) % this.tracks.length;
    this.switchTo();
  },

  switchTo() {
    try { localStorage.setItem(this.KEYS.index, String(this.index)); } catch (e) {}
    try { localStorage.setItem(this.KEYS.position, '0'); } catch (e) {}
    if (this.audio) {
      this.audio.setAttribute('src', this.currentSrc());
      this.audio.currentTime = 0;
    }
    this.renderTrack();
    if (this.playing() || this.enabled) this.play();
    else this.play();   // 手动切歌视为明确的播放意图
  },

  renderTrack() {
    const title = document.getElementById('pymusic-title');
    const meta = document.getElementById('pymusic-meta');
    const track = this.track();
    if (title) title.textContent = track.title || '背景音乐';
    if (meta) meta.textContent = [track.artist, track.mood].filter(Boolean).join(' · ') || '轻松学习 · 专注不打扰';
  },

  renderProgress() {
    if (!this.audio || !this.audio.duration) return;
    const bar = document.getElementById('pymusic-progress');
    if (bar) bar.style.width = (this.audio.currentTime / this.audio.duration * 100).toFixed(2) + '%';
  },

  renderState() {
    const isPlaying = this.playing();
    const play = document.getElementById('pymusic-play');
    const glyph = document.getElementById('pymusic-glyph-icon');
    if (play) play.textContent = isPlaying ? '⏸' : '▶';
    if (glyph) {
      glyph.textContent = isPlaying ? '♫' : '♪';
      glyph.style.color = isPlaying ? 'var(--cyan, #00d4ff)' : 'var(--text-muted, #6e7681)';
    }
    const dock = document.getElementById('pymusic-dock');
    if (dock) dock.classList.toggle('playing', isPlaying);
    // 老页面上的按钮（如果存在）也跟着变
    const legacy = document.getElementById('music-toggle-btn');
    if (legacy) {
      legacy.textContent = isPlaying ? '🎵' : '🎶';
      legacy.title = isPlaying ? '关闭背景音乐' : '开启背景音乐';
    }
  },

  setStatus(message) {
    const meta = document.getElementById('pymusic-meta');
    if (meta && message) meta.textContent = message;
    else if (meta) this.renderTrack();
  },
};

// 老代码里到处是 AmbientMusic.toggle()，保留这个别名以免改动老页面
window.PyMusic = PyMusic;
window.AmbientMusic = {
  toggle: () => PyMusic.toggle(),
  play: () => PyMusic.play(),
  stop: () => PyMusic.pause(),
  init: () => PyMusic.init(),
};

document.addEventListener('DOMContentLoaded', () => {
  if (!window.__pymusicAutoInitDisabled) PyMusic.init();
});
