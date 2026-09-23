/**
 * tools/shoot_setup_server.mjs —— 学生视角的「绑定自己的模型」页截图。
 *
 * 服务器模式下这页和本地版不一样（文案、当前来源、保存去向都变了），
 * 要看的就是这几处真的说清楚了：学生得知道自己填的 Key 存在哪、
 * 会不会被别人看到、不填会怎样。
 *
 * 用法：node tools/shoot_setup_server.mjs http://127.0.0.1:5056
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'logs', 'shots', 'setup-server');
const PORT = 9413;
const EDGE = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].find((p) => existsSync(p));

const base = (process.argv[2] || 'http://127.0.0.1:5056').replace(/\/$/, '');
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
        await new Promise((res, rej) => {
          ws.addEventListener('open', res, { once: true });
          ws.addEventListener('error', rej, { once: true });
        });
        return new CDP(ws);
      }
    } catch (e) { /* 未就绪 */ }
    await sleep(400);
  }
  throw new Error('连不上调试端口');
}

async function main() {
  mkdirSync(OUT, { recursive: true });
  const profile = join(process.env.TEMP || '/tmp', 'setup_srv_profile');
  const child = spawn(EDGE, [
    '--headless=new', '--no-sandbox', '--enable-unsafe-swiftshader', '--hide-scrollbars',
    '--no-first-run', '--disable-extensions', '--disable-features=Translate',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile,
    '--window-size=1500,1200', 'about:blank',
  ], { stdio: 'ignore' });

  try {
    const cdp = await connect('http://127.0.0.1:' + PORT);
    await cdp.send('Page.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride',
      { width: 1500, height: 1200, deviceScaleFactor: 1, mobile: false });

    console.log('[1] 注册一个学生账号');
    await cdp.send('Page.navigate', { url: base + '/setup' });
    await sleep(1600);
    const reg = await cdp.send('Runtime.evaluate', {
      expression: `(async () => {
        const r = await fetch('/api/register', { method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ username:'截图学生' + Date.now().toString().slice(-4), password:'shot123456' }) });
        return await r.json();
      })()`, awaitPromise: true, returnByValue: true,
    });
    console.log('    ', JSON.stringify(reg.result.value).slice(0, 120));

    console.log('[2] 打开模型配置页');
    await cdp.send('Page.navigate', { url: base + '/setup' });
    let stable = 0;
    for (let i = 0; i < 60; i += 1) {
      const { result } = await cdp.send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
      stable = result.value === 'complete' ? stable + 1 : 0;
      if (stable >= 3) break;
      await sleep(220);
    }
    await sleep(2000);
    const info = await cdp.send('Runtime.evaluate', {
      expression: `({ host: (document.getElementById('cur-host')||{}).textContent,
                      lead: (document.querySelector('.pane.active .lead')||{}).innerText })`,
      returnByValue: true,
    });
    console.log('    ', JSON.stringify(info.result.value).slice(0, 300));

    let s = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    writeFileSync(join(OUT, '10-student-bind.png'), Buffer.from(s.data, 'base64'));
    console.log('  ->', join(OUT, '10-student-bind.png'));

    console.log('[3] 手机宽度');
    await cdp.send('Emulation.setDeviceMetricsOverride',
      { width: 414, height: 950, deviceScaleFactor: 2, mobile: true });
    await sleep(1600);
    s = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    writeFileSync(join(OUT, '11-student-bind-mobile.png'), Buffer.from(s.data, 'base64'));
    console.log('  ->', join(OUT, '11-student-bind-mobile.png'));
  } finally {
    child.kill();
  }
}

main().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
