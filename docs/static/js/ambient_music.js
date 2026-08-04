/**
 * ambient_music.js — PyMaster 背景音乐系统
 * 播放下载的 Harmonic Light 氛围音乐 MP3（前 5 分钟）
 */
const AmbientMusic = {
  audio: null,
  playing: false,
  volume: 0.5,

  get storageKey() { return 'pymaster_music_enabled'; },

  get audioSrc() {
    // Use absolute path from root
    const base = document.querySelector('base')?.href || window.location.origin;
    return base + '/static/audio/bgmusic.mp3';
  },

  init() {
    const saved = localStorage.getItem(this.storageKey);
    if (saved === 'true') {
      setTimeout(() => this.play(), 500);
    }
    this._updateToggleUI();
  },

  _ensureAudio() {
    if (!this.audio) {
      this.audio = new Audio();
      this.audio.src = this.audioSrc;
      this.audio.loop = true;
      this.audio.volume = this.volume;
      this.audio.preload = 'auto';
      this.audio.addEventListener('ended', () => {
        // Restart when reaches the 5-min cut point
        if (this.playing) this.audio.currentTime = 0;
      });
    }
    return this.audio;
  },

  play() {
    try {
      const audio = this._ensureAudio();
      audio.volume = this.volume;
      audio.play().then(() => {
        this.playing = true;
        localStorage.setItem(this.storageKey, 'true');
        this._updateToggleUI();
      }).catch(e => {
        console.warn('音乐自动播放被阻止，等待用户交互:', e.message);
      });
    } catch (e) {
      console.warn('音乐播放失败:', e.message);
    }
  },

  stop() {
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
    }
    this.playing = false;
    localStorage.setItem(this.storageKey, 'false');
    this._updateToggleUI();
  },

  toggle() {
    if (this.playing) this.stop();
    else this.play();
  },

  _updateToggleUI() {
    const btn = document.getElementById('music-toggle-btn');
    if (btn) {
      btn.textContent = this.playing ? '🎵' : '🎶';
      btn.title = this.playing ? '关闭背景音乐' : '开启背景音乐';
      btn.style.color = this.playing ? 'var(--cyan, #00d4ff)' : 'var(--text-muted, #666)';
    }
  }
};

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', () => AmbientMusic.init());
