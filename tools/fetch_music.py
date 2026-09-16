"""抓取并处理学习背景音乐。

曲源用的是 Kevin MacLeod（incompetech.com）的 CC-BY 4.0 作品：
免费、可商用、可再分发，只要保留署名——CREDITS 会一并生成。

为什么要自己转码，而不是直接用下载到的文件：
原曲每首 3–14 MB，六首加起来 50 MB 上下，塞进安装包太重。
统一裁到 2 分钟、96 kbps 立体声、首尾各加 1.5 秒淡入淡出，
六首合计约 9 MB，音质对「背景音乐」这个用途完全够。

依赖：`pip install imageio-ffmpeg`（自带 ffmpeg 可执行文件，不需要单独装）。
用法：
    python tools/fetch_music.py            # 抓取并生成 static/audio/
    python tools/fetch_music.py --check    # 只检查现有文件是否齐全
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT, 'static', 'audio')
CACHE_DIR = os.path.join(ROOT, 'data', 'music_cache')

BASE_URL = 'https://incompetech.com/music/royalty-free/mp3-royaltyfree/'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')

# 选曲标准：节奏在 70–110 BPM 之间、以自然乐器为主、没有人声歌词——
# 有人唱的歌会跟「边听边想」抢注意力，这也是自习室一般放器乐的原因。
TRACKS = [
    {'source': 'Life of Riley', 'file': 'lively-steps.mp3', 'title': '悠然时光',
     'artist': 'Kevin MacLeod', 'mood': '轻快 · 打开思路'},
    {'source': 'Carefree', 'file': 'carefree.mp3', 'title': '无忧',
     'artist': 'Kevin MacLeod', 'mood': '明亮 · 心情上浮'},
    {'source': 'Happy Alley', 'file': 'happy-alley.mp3', 'title': '快乐小巷',
     'artist': 'Kevin MacLeod', 'mood': '俏皮 · 短小的快乐'},
    {'source': 'Heartwarming', 'file': 'warm-sunlight.mp3', 'title': '暖阳',
     'artist': 'Kevin MacLeod', 'mood': '温暖 · 适合长时间写代码'},
    {'source': 'Deliberate Thought', 'file': 'calm-morning.mp3', 'title': '沉思',
     'artist': 'Kevin MacLeod', 'mood': '安静 · 进入心流'},
    {'source': 'Wallpaper', 'file': 'wallpaper.mp3', 'title': '壁纸',
     'artist': 'Kevin MacLeod', 'mood': '极简 · 几乎感觉不到它'},
]

LICENSE = 'CC BY 4.0（Kevin MacLeod / incompetech.com）'
CLIP_SECONDS = 120
BITRATE = '96k'


def ffmpeg_path():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        found = shutil.which('ffmpeg')
        if found:
            return found
    raise SystemExit('没找到 ffmpeg。请先 `pip install imageio-ffmpeg`，或把 ffmpeg 加进 PATH。')


def download(track):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cached = os.path.join(CACHE_DIR, track['source'].replace(' ', '_') + '.mp3')
    if os.path.exists(cached) and os.path.getsize(cached) > 200_000:
        return cached
    url = BASE_URL + urllib.parse.quote(track['source']) + '.mp3'
    request = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(request, timeout=90) as response, open(cached, 'wb') as handle:
        shutil.copyfileobj(response, handle)
    return cached


def transcode(ffmpeg, source, target):
    """裁到 CLIP_SECONDS 秒 + 1.5 秒淡入淡出 + 96k 立体声。"""
    fade_out_start = CLIP_SECONDS - 2
    command = [
        ffmpeg, '-y', '-loglevel', 'error',
        '-i', source,
        '-t', str(CLIP_SECONDS),
        '-af', f'afade=t=in:st=0:d=1.5,afade=t=out:st={fade_out_start}:d=2',
        '-ac', '2', '-ar', '44100', '-b:a', BITRATE,
        target,
    ]
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='只检查文件是否齐全')
    args = parser.parse_args()

    os.makedirs(AUDIO_DIR, exist_ok=True)
    if args.check:
        missing = [t['file'] for t in TRACKS
                   if not os.path.exists(os.path.join(AUDIO_DIR, t['file']))]
        if missing:
            print('缺少音乐文件：' + ', '.join(missing))
            return 1
        print(f'音乐文件齐全（{len(TRACKS)} 首）。')
        return 0

    ffmpeg = ffmpeg_path()
    print(f'使用 ffmpeg：{ffmpeg}')
    playlist = []
    for track in TRACKS:
        target = os.path.join(AUDIO_DIR, track['file'])
        try:
            source = download(track)
            transcode(ffmpeg, source, target)
            size = os.path.getsize(target) / 1024 / 1024
            print(f'  ✓ {track["title"]:<8} {track["file"]:<20} {size:.2f} MB')
        except Exception as exc:
            print(f'  ✗ {track["title"]} 处理失败：{exc}')
            continue
        playlist.append({
            'file': track['file'],
            'title': track['title'],
            'artist': track['artist'],
            'mood': track['mood'],
            'license': LICENSE,
            'source': track['source'],
        })

    with open(os.path.join(AUDIO_DIR, 'playlist.json'), 'w', encoding='utf-8') as handle:
        json.dump(playlist, handle, ensure_ascii=False, indent=1)

    with open(os.path.join(AUDIO_DIR, 'CREDITS.md'), 'w', encoding='utf-8') as handle:
        handle.write('# 背景音乐版权与来源\n\n')
        handle.write('全部曲目来自 [incompetech.com](https://incompetech.com)，'
                     '作者 Kevin MacLeod，授权 **Creative Commons: By Attribution 4.0**'
                     '（CC BY 4.0），允许免费使用、修改与再分发，需保留署名。\n\n')
        handle.write('| 曲目 | 原名 | 用途 |\n|---|---|---|\n')
        for item in playlist:
            handle.write(f'| {item["title"]} | {item["source"]} | {item["mood"]} |\n')
        handle.write('\n处理方式：截取前 120 秒，首尾淡入淡出，转码为 96 kbps 立体声 MP3。\n')

    total = sum(os.path.getsize(os.path.join(AUDIO_DIR, t['file']))
                for t in TRACKS if os.path.exists(os.path.join(AUDIO_DIR, t['file'])))
    print(f'\n完成：{len(playlist)} 首，合计 {total / 1024 / 1024:.1f} MB')
    print(f'已写入 {os.path.join(AUDIO_DIR, "playlist.json")} 与 CREDITS.md')
    return 0


if __name__ == '__main__':
    sys.exit(main())
