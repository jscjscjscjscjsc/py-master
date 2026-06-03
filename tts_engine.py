"""
PyMaster TTS Engine — Edge-TTS (primary) + Doubao TTS (legacy) integration.
Converts comic character dialogs to spoken Chinese audio.

Edge-TTS: Free, no API key, excellent Chinese neural voices via Microsoft Edge.
DoubaoTTS: ByteDance Volcengine TTS (requires credentials, may expire).
BrowserTTS: Client-side SpeechSynthesis fallback.
"""
import os
import json
import hashlib
import asyncio
import subprocess
import re
import uuid
import base64
import urllib.request
import urllib.parse


# ================================================================
# Edge-TTS Engine — FREE, high-quality Chinese neural voices
# ================================================================

class EdgeTTS:
    """Microsoft Edge TTS — free, no API key needed, best Chinese quality."""

    # Character voice presets (all zh-CN neural voices)
    VOICES = {
        "teacher": {
            "voice": "zh-CN-YunxiNeural",    # Male, bright, clear — perfect for teaching
            "label": "蛇蛇老师 - 云希(男声)",
            "rate": "+5%",
            "pitch": "+0Hz",
        },
        "student": {
            "voice": "zh-CN-XiaoxiaoNeural", # Female, warm, lively — perfect for student
            "label": "小码 - 晓晓(女声)",
            "rate": "+10%",
            "pitch": "+2Hz",
        },
        "narrator": {
            "voice": "zh-CN-YunyangNeural",  # Male, professional, calm — perfect for narration
            "label": "旁白君 - 云扬(男声)",
            "rate": "-5%",
            "pitch": "-1Hz",
        }
    }

    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "audio_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)

    def is_available(self) -> bool:
        """Edge-TTS is always available once installed."""
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def _clean_text(self, text: str) -> str:
        """Clean text for TTS: remove emoji and formatting, keep Chinese/English/punctuation."""
        text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
        text = re.sub(r'[☀-➿]', '', text)
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'`', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def synthesize(self, text: str, character: str = "teacher") -> bytes:
        """Convert text to speech using Edge-TTS. Returns MP3 audio bytes."""
        voice_config = self.VOICES.get(character, self.VOICES["teacher"])
        text = self._clean_text(text)
        if not text or len(text) < 2:
            return b""

        # Cache key
        cache_key = hashlib.md5(
            f"{text}_{voice_config['voice']}".encode("utf-8")
        ).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"edge_{cache_key}.mp3")
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        try:
            audio = asyncio.run(self._synthesize_async(text, voice_config, cache_path))
            return audio
        except Exception as e:
            print(f"[EdgeTTS] Error: {e}")
            return b""

    async def _synthesize_async(self, text: str, voice_config: dict, cache_path: str) -> bytes:
        """Async synthesis using edge-tts library."""
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            voice_config["voice"],
            rate=voice_config.get("rate", "+0%"),
            pitch=voice_config.get("pitch", "+0Hz"),
        )
        await communicate.save(cache_path)

        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()
        return b""

    def synthesize_panel(self, panel: dict) -> bytes:
        """Synthesize speech for a comic panel."""
        character = panel.get("character", "teacher")
        return self.synthesize(panel.get("dialog", ""), character)


# ================================================================
# Doubao TTS — ByteDance Volcengine (legacy, may require API changes)
# ================================================================

class DoubaoTTS:
    """Doubao TTS client using Volcengine Speech API."""

    VOICES = {
        "teacher": {
            "voice_type": "zh_male_qingrun",
            "label": "蛇蛇老师 - 男声清润",
            "speed": 1.0,
            "volume": 1.0,
        },
        "student": {
            "voice_type": "zh_female_tianmei",
            "label": "小码 - 女声甜美",
            "speed": 1.15,
            "volume": 1.0,
        },
        "narrator": {
            "voice_type": "zh_male_story",
            "label": "旁白君 - 男声故事",
            "speed": 0.95,
            "volume": 0.9,
        }
    }

    def __init__(self, app_id=None, access_token=None, secret_key=None, cache_dir=None):
        self.app_id = app_id or os.environ.get("DOUBAO_APP_ID", "")
        self.access_token = access_token or os.environ.get("DOUBAO_ACCESS_TOKEN", "")
        self.secret_key = secret_key or os.environ.get("DOUBAO_SECRET_KEY", "")
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "audio_cache"
        )
        os.makedirs(self.cache_dir, exist_ok=True)

    def is_available(self) -> bool:
        return bool(self.app_id and self.access_token)

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'[\U0001F000-\U0001FFFF]', '', text)
        text = re.sub(r'[\U0001F300-\U0001F9FF]', '', text)
        text = re.sub(r'[☀-➿]', '', text)
        text = re.sub(r'\*\*', '', text)
        text = re.sub(r'`', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def synthesize(self, text: str, character: str = "teacher") -> bytes:
        voice_config = self.VOICES.get(character, self.VOICES["teacher"])
        text = self._clean_text(text)
        if not text or len(text) < 2:
            return b""

        cache_key = hashlib.md5(
            f"{text}_{voice_config['voice_type']}".encode("utf-8")
        ).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"doubao_{cache_key}.mp3")
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        if not self.is_available():
            return b""

        try:
            audio = self._call_api(text, voice_config)
            if audio:
                with open(cache_path, "wb") as f:
                    f.write(audio)
            return audio
        except Exception as e:
            print(f"[DoubaoTTS] API error: {e}")
            return b""

    def synthesize_panel(self, panel: dict) -> bytes:
        character = panel.get("character", "teacher")
        return self.synthesize(panel.get("dialog", ""), character)

    def _call_api(self, text: str, voice_config: dict) -> bytes:
        voice_type = voice_config["voice_type"]
        speed = voice_config["speed"]
        volume = voice_config["volume"]

        payload = {
            "app": {"appid": self.app_id, "token": self.access_token, "cluster": "volcano_tts"},
            "user": {"uid": "pymaster_user"},
            "audio": {"voice_type": voice_type, "encoding": "mp3", "speed_ratio": speed, "volume_ratio": volume},
            "request": {"reqid": str(uuid.uuid4()), "text": text, "text_type": "plain", "operation": "query"}
        }

        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer; {self.access_token}"}

        try:
            req = urllib.request.Request(
                "https://openspeech.bytedance.com/api/v1/tts", data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 3000:
                data = result.get("data", "")
                if data:
                    return base64.b64decode(data)
        except Exception as e:
            print(f"[DoubaoTTS] API: {e}")
        return b""


# ================================================================
# Browser TTS helper (zero-config client-side fallback)
# ================================================================

class BrowserTTS:
    """Helper for browser-side SpeechSynthesis TTS."""

    @staticmethod
    def get_voice_config(character: str) -> dict:
        configs = {
            "teacher": {"lang": "zh-CN", "rate": 1.0, "pitch": 1.05},
            "student": {"lang": "zh-CN", "rate": 1.15, "pitch": 1.3},
            "narrator": {"lang": "zh-CN", "rate": 0.9, "pitch": 0.95},
        }
        return configs.get(character, configs["teacher"])
