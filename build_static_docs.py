"""Build the GitHub Pages showcase into docs/ from the current Flask UI."""
import json
import re
import shutil
from pathlib import Path

import app as pymaster

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'


def static_html(text):
    replacements = {
        'href="/static/': 'href="static/',
        'src="/static/': 'src="static/',
        "url('/static/": "url('static/",
        'href="/dashboard"': 'href="index.html"',
        'href="/playground"': 'href="playground.html"',
        'href="/canvas"': 'href="canvas.html"',
        "window.location.href='/canvas'": "window.location.href='canvas.html'",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_page(client, route, destination):
    response = client.get(route)
    if response.status_code != 200:
        raise RuntimeError(f'{route} returned {response.status_code}')
    (DOCS / destination).write_text(static_html(response.get_data(as_text=True)), encoding='utf-8')


def build():
    DOCS.mkdir(exist_ok=True)
    legacy_page = DOCS / 'chapter.html'
    if legacy_page.exists():
        legacy_page.unlink()
    shutil.copytree(ROOT / 'static', DOCS / 'static', dirs_exist_ok=True)
    client = pymaster.app.test_client()
    write_page(client, '/dashboard', 'index.html')
    write_page(client, '/stars', 'stars.html')
    write_page(client, '/canvas', 'canvas.html')
    write_page(client, '/playground', 'playground.html')
    for chapter_id in range(1, 10):
        write_page(client, f'/chapter/{chapter_id}', f'chapter-{chapter_id}.html')

    stars_file = DOCS / 'stars.html'
    stars = stars_file.read_text(encoding='utf-8')
    stars = stars.replace('data-universe-url="/api/knowledge-universe"', 'data-universe-url="data/knowledge-universe.json"')
    stars = stars.replace('data-dashboard-url="/dashboard"', 'data-dashboard-url="index.html"')
    stars_file.write_text(stars, encoding='utf-8')

    universe = client.get('/api/knowledge-universe').get_json()
    for galaxy in universe['galaxies']:
        for star in galaxy['stars']:
            star['url'] = re.sub(r'^/chapter/(\d+)', r'chapter-\1.html', star['url'])
    (DOCS / 'data').mkdir(exist_ok=True)
    (DOCS / 'data' / 'knowledge-universe.json').write_text(
        json.dumps(universe, ensure_ascii=False, indent=2), encoding='utf-8')

    star_script = DOCS / 'static' / 'js' / 'knowledge_stars.js'
    source = star_script.read_text(encoding='utf-8')
    source = source.replace("location.assign('/dashboard')", "location.assign(document.body.dataset.dashboardUrl||'index.html')")
    source = source.replace("else location.assign('/dashboard')", "else location.assign(document.body.dataset.dashboardUrl||'index.html')")
    star_script.write_text(source, encoding='utf-8')
    (DOCS / '.nojekyll').touch()
    print('Built GitHub Pages:', DOCS)


if __name__ == '__main__':
    build()
