/**
 * tools/shoot_chip.mjs —— 验证「AI 功能未开启」提示条在真实页面上渲染正确。
 * 会先登录、跳过模型配置，再截首页右下角，确认提示条可见且不挡内容。
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'logs', 'shots', 'setup');
const PORT = 9411;
const EDGE = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].find((p) => existsSync(p));

const [, , base, name] = process.argv;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

class CDP {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.pending = new Map();
    ws.addEventListener('message', (e) => {
      const m = JSON.parse(e.data);
      if (m.id && this.pending.has(m.id)) {
        const { resolve, reject } = this.pending.get(m.id);
        this.pending.delete(m.id);
        m.error ? reject(new Error(m.error.message)) : resolve(m.result);
      }
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      setTimeout(() => { if (this.pending.has(id)) { this.pending.delete(id); reject(new Error('timeout ' + method)); } }, 40000);
    });
  }
}

async function connect(url, tries = 40) {
  for (let i = 0; i < tries; i += 1) {
    try {
      const list = await (await fetch(url + '/json/list')).json();
      const t = list.find((x) => x.type === 'page');
      if (t) {
        const ws = new WebSocket(t.webSocketDebuggerUrl);
        await new Promise((res, rej) => { ws.addEventListener('open', res, { once: true }); ws.addEventListener('error', rej, { once: true }); });
        return new CDP(ws);
      }
    } catch (e) { /* 未就绪 */ }
    await sleep(400);
  }
  throw new Error('连不上调试端口');
}

async function main() {
  mkdirSync(OUT, { recursive: true });
  const profile = join(process.env.TEMP || '/tmp', 'chip_cdp_' + name);
  const child = spawn(EDGE, [
    '--headless=new', '--no-sandbox', '--enable-unsafe-swiftshader', '--hide-scrollbars',
    '--no-first-run', '--disable-extensions', '--disable-features=Translate',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile,
    '--window-size=1440,900', 'about:blank',
  ], { stdio: 'ignore' });
  try {
    const cdp = await connect('http://127.0.0.1:' + PORT);
    await cdp.send('Page.enable');
    await cdp.send('Network.enable');
    const root = base.replace(/\/$/, '');

    // 注册 + 走「跳过配置」这条路 —— 只有这样 dashboard 才打得开，
    // 而 configured 仍是 false，提示条才会出现。
    // （按 reopen 清掉跳过标记是不行的：那样会被重定向回 /setup，
    //   而提示条在配置页上是故意隐藏的。）
    await cdp.send('Page.navigate', { url: root + '/setup' });
    await sleep(1500);
    const setup = await cdp.send('Runtime.evaluate', {
      expression: `(async () => {
        let ok = false;
        for (const p of ['/api/register', '/api/login']) {
          const r = await fetch(p, { method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ username:'__chip__', password:'chip123456' }) });
          const d = await r.json().catch(()=>({}));
          if (d && d.success) { ok = true; break; }
        }
        await fetch('/api/setup/skip', { method:'POST', headers:{'Content-Type':'application/json'}, body:'{}' });
        return ok;
      })()`, awaitPromise: true, returnByValue: true,
    });
    console.log('准备状态:', setup.result.value);

    await cdp.send('Page.navigate', { url: root + '/dashboard' });
    let stable = 0;
    for (let i = 0; i < 60; i += 1) {
      const { result } = await cdp.send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
      stable = result.value === 'complete' ? stable + 1 : 0;
      if (stable >= 3) break;
      await sleep(250);
    }
    await sleep(2500);

    // 探针：提示条在不在、位置如何、有没有盖住内容
    const probe = await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const el = document.getElementById('ai-notice-chip');
        if (!el) return { found: false };
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return { found: true, text: el.innerText.replace(/\\s+/g,' ').trim(),
                 rect: {top: r.top, left: r.left, w: r.width, h: r.height},
                 display: cs.display, opacity: cs.opacity, zIndex: cs.zIndex };
      })()`, returnByValue: true,
    });
    console.log('提示条探针:', JSON.stringify(probe.result.value));

    // 只截右下角区域，看清提示条实际观感
    const shot = await cdp.send('Page.captureScreenshot', {
      format: 'png',
      clip: { x: 900, y: 620, width: 540, height: 280, scale: 2 },
    });
    writeFileSync(join(OUT, name + '.png'), Buffer.from(shot.data, 'base64'));
    console.log('OK -> ' + join(OUT, name + '.png'));

    // 再截整页，确认不遮挡主要内容
    const full = await cdp.send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(join(OUT, name + '-full.png'), Buffer.from(full.data, 'base64'));
  } finally {
    child.kill();
  }
}

main().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
