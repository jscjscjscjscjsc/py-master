/**
 * tools/shoot_setup.mjs —— 给《大模型添加说明书和教程.md》拍配置页截图。
 *
 * 复用 tools/shoot.mjs 的 CDP 手法，但只截「模型配置页」这一个页面，
 * 两个平台各一张，输出到 logs/shots/setup/。
 *
 * 用法：node tools/shoot_setup.mjs <平台目录> <端口> <输出名>
 * 例：  node tools/shoot_setup.mjs "AI Master 学习平台" 5178 aimaster-setup
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'logs', 'shots', 'setup');
const PORT = 9401;
const EDGE = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].find((p) => existsSync(p));

const [, , base, name] = process.argv;
if (!base || !name) {
  console.error('用法: node tools/shoot_setup.mjs <base url> <输出名>');
  process.exit(1);
}

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
      setTimeout(() => {
        if (this.pending.has(id)) { this.pending.delete(id); reject(new Error('CDP timeout: ' + method)); }
      }, 40000);
    });
  }
}

async function connect(url, tries = 40) {
  for (let i = 0; i < tries; i += 1) {
    try {
      const list = await (await fetch(url + '/json/list')).json();
      const target = list.find((t) => t.type === 'page');
      if (target) {
        const ws = new WebSocket(target.webSocketDebuggerUrl);
        await new Promise((res, rej) => {
          ws.addEventListener('open', res, { once: true });
          ws.addEventListener('error', rej, { once: true });
        });
        return new CDP(ws);
      }
    } catch (e) { /* 浏览器没起来 */ }
    await sleep(400);
  }
  throw new Error('连不上调试端口');
}

async function main() {
  if (!EDGE) { console.error('找不到 Edge'); process.exit(1); }
  mkdirSync(OUT, { recursive: true });
  const profile = join(process.env.TEMP || '/tmp', 'setup_cdp_' + name);
  const child = spawn(EDGE, [
    '--headless=new', '--no-sandbox', '--disable-gpu-sandbox',
    '--enable-unsafe-swiftshader', '--hide-scrollbars', '--no-first-run',
    '--disable-extensions', '--disable-features=Translate',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile,
    '--window-size=1500,1200', 'about:blank',
  ], { stdio: 'ignore' });

  try {
    const cdp = await connect('http://127.0.0.1:' + PORT);
    await cdp.send('Page.enable');
    await cdp.send('Network.enable');
    const root = base.replace(/\/$/, '');

    // 配置向导的「模型表单」只在已登录时才显示，否则停在第一步的注册表单。
    // 先在同源里注册一个临时账号拿到会话 Cookie，截到的才是真实第二步。
    await cdp.send('Page.navigate', { url: root + '/login' });
    await sleep(1500);
    await cdp.send('Runtime.evaluate', {
      expression: `(async () => {
        for (const path of ['/api/register', '/api/login']) {
          try {
            const r = await fetch(path, { method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username: '__shot__', password: 'shot123456' }) });
            const d = await r.json();
            if (d && d.success) return 'ok';
          } catch (e) { /* 下一个 */ }
        }
        return 'fail';
      })()`,
      awaitPromise: true, returnByValue: true,
    });

    const url = root + '/setup';
    await cdp.send('Page.navigate', { url });
    // 等渲染稳定：连续三次 readyState=complete 再静置
    let stable = 0;
    for (let i = 0; i < 60; i += 1) {
      const { result } = await cdp.send('Runtime.evaluate', {
        expression: 'document.readyState', returnByValue: true,
      });
      stable = result.value === 'complete' ? stable + 1 : 0;
      if (stable >= 3) break;
      await sleep(250);
    }
    await sleep(1600);
    const shot = await cdp.send('Page.captureScreenshot', {
      format: 'png', captureBeyondViewport: true,
    });
    writeFileSync(join(OUT, name + '.png'), Buffer.from(shot.data, 'base64'));
    console.log('OK -> ' + join(OUT, name + '.png'));
  } finally {
    child.kill();
  }
}

main().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
