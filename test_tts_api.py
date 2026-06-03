"""Test Doubao TTS with different cluster values"""
import json, urllib.request, urllib.error, uuid, base64

APP_ID = "3689913526"
TOKEN = "G7D1NW8dhQzW7PeS9RVjRNfoZZjbqYiB"
AUTH = "Bearer; " + TOKEN
text = "你好同学们，今天我们来学习Python函数的基础知识，函数是编程中最重要的概念之一。"

clusters = [
    "volcano_tts", "volc_tts", "doubao_tts",
    "volcano_tts_zh", "volcano_ich", "volcano_mega",
    "seed_tts", "speech_tts",
]

for cluster in clusters:
    payload = {
        "app": {"appid": APP_ID, "token": TOKEN, "cluster": cluster},
        "user": {"uid": "test"},
        "audio": {"voice_type": "zh_female_tianmei", "encoding": "mp3", "speed_ratio": 1.0},
        "request": {"reqid": str(uuid.uuid4()), "text": text, "text_type": "plain", "operation": "query"}
    }
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": AUTH}
    try:
        req = urllib.request.Request("https://openspeech.bytedance.com/api/v1/tts", data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        code = result.get("code", -1)
        msg = result.get("message", "")[:120]
        print(f"cluster={cluster}: code={code}, msg={msg}")
        if code == 3000:
            data_b64 = result.get("data", "")
            if data_b64:
                audio = base64.b64decode(data_b64)
                out = f"C:/Users/Administrator/python_tutor/data/audio_cache/{cluster}.mp3"
                with open(out, "wb") as f: f.write(audio)
                print(f"  >>> SUCCESS! {len(audio)} bytes saved to {cluster}.mp3")
    except urllib.error.HTTPError as e:
        print(f"cluster={cluster}: HTTP {e.code} - {e.read().decode('utf-8', errors='replace')[:200]}")
    except Exception as e:
        print(f"cluster={cluster}: Error: {e}")
