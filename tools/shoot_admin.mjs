/**
 * tools/shoot_admin.mjs —— 给管理后台拍真实浏览器截图（每个标签页一张）。
 *
 * 为什么要看截图而不是只看接口返回值：后台是这次交付的门面，
 * 接口通了但页面排版错乱（表格溢出、卡片挤成一列、抽屉被氛围层盖住）
 * 是很容易发生的，只有真渲染一遍才看得出来。
 *
 * 用法：node tools/shoot_admin.mjs http://127.0.0.1:5055
 */
import { spawn } from 'node:child_process';
import { existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, '..', 'logs', 'shots', 'admin');
const PORT = 9412;
const EDGE = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
].find((p) => existsSync(p));

const base = (process.argv[2] || 'http://127.0.0.1:5055').replace(/\/$/, '');
const ADMIN_USER = process.env.ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.ADMIN_PASS || 'admin888';
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

async function waitReady(cdp, ms = 1400) {
  let stable = 0;
  for (let i = 0; i < 60; i += 1) {
    const { result } = await cdp.send('Runtime.evaluate', { expression: 'document.readyState', returnByValue: true });
    stable = result.value === 'complete' ? stable + 1 : 0;
    if (stable >= 3) break;
    await sleep(200);
  }
  await sleep(ms);
}

async function shot(cdp, name, full = true) {
  const params = { format: 'png' };
  if (full) params.captureBeyondViewport = true;
  const r = await cdp.send('Page.captureScreenshot', params);
  const file = join(OUT, name + '.png');
  writeFileSync(file, Buffer.from(r.data, 'base64'));
  console.log('  ->', file);
}

async function main() {
  mkdirSync(OUT, { recursive: true });
  const profile = join(process.env.TEMP || '/tmp', 'admin_cdp_profile');
  const child = spawn(EDGE, [
    '--headless=new', '--no-sandbox', '--enable-unsafe-swiftshader', '--hide-scrollbars',
    '--no-first-run', '--disable-extensions', '--disable-features=Translate',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile,
    '--window-size=1600,1100', 'about:blank',
  ], { stdio: 'ignore' });

  try {
    const cdp = await connect('http://127.0.0.1:' + PORT);
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride',
      { width: 1600, height: 1100, deviceScaleFactor: 1, mobile: false });

    console.log('[1] 打开后台登录页');
    await cdp.send('Page.navigate', { url: base + '/admin/login' });
    await waitReady(cdp, 1200);
    await shot(cdp, '01-login');

    console.log('[2] 登录');
    const login = await cdp.send('Runtime.evaluate', {
      expression: `(async () => {
        const r = await fetch('/admin/login', { method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ username: ${JSON.stringify(ADMIN_USER)}, password: ${JSON.stringify(ADMIN_PASS)} }) });
        return await r.json();
      })()`, awaitPromise: true, returnByValue: true,
    });
    console.log('    登录结果:', JSON.stringify(login.result.value));
    if (!login.result.value || !login.result.value.success) throw new Error('管理员登录失败');

    // 必须真的导航到 /admin：上面那次 fetch 只把会话 Cookie 换回来了，
    // 页面还停在登录页，后面的 .tab 选择器全都找不到。
    await cdp.send('Page.navigate', { url: base + '/admin' });
    await waitReady(cdp, 2600);

    const onAdmin = await cdp.send('Runtime.evaluate', {
      expression: `({ url: location.pathname, tabs: document.querySelectorAll('.tab').length,
                      title: document.querySelector('.admin-top h1') ? document.querySelector('.admin-top h1').innerText : '' })`,
      returnByValue: true,
    });
    console.log('    后台页面:', JSON.stringify(onAdmin.result.value));
    if (!onAdmin.result.value.tabs) throw new Error('没进到后台页面（标签页数量为 0）');

    const panes = [
      ['overview', '02-overview', 2600],
      ['users', '03-users', 2000],
      ['logs', '04-logs', 2000],
      ['whitelist', '05-whitelist', 1600],
      ['settings', '06-settings', 1600],
    ];
    for (const [pane, name, wait] of panes) {
      console.log('[3] 标签页', pane);
      await cdp.send('Runtime.evaluate', {
        expression: `document.querySelector('.tab[data-pane="${pane}"]').click()`,
        returnByValue: true,
      });
      await sleep(wait);
      await shot(cdp, name);
    }

    console.log('[4] 打开第一个用户的详情抽屉');
    const open = await cdp.send('Runtime.evaluate', {
      expression: `(() => {
        const el = document.querySelector('#users-table .username');
        if (!el) return false;
        el.click(); return true;
      })()`, returnByValue: true,
    });
    if (open.result.value) {
      await sleep(2200);
      await shot(cdp, '07-user-drawer');
    } else {
      console.log('    （没有用户可点）');
    }

    console.log('[5] 手机宽度看一眼');
    // 先把抽屉关掉：不然手机上拍到的是抽屉盖着整个页面，
    // 看不到列表本身在窄屏下的表现（这一步要看的就是列表）。
    await cdp.send('Runtime.evaluate', { expression: `closeDrawer()` });
    await cdp.send('Emulation.setDeviceMetricsOverride',
      { width: 414, height: 900, deviceScaleFactor: 2, mobile: true });
    await cdp.send('Runtime.evaluate', { expression: `document.querySelector('.tab[data-pane="overview"]').click()` });
    await sleep(2200);
    await shot(cdp, '08-mobile');

    console.log('[6] 手机宽度下的日志表');
    await cdp.send('Runtime.evaluate', { expression: `document.querySelector('.tab[data-pane="logs"]').click()` });
    await sleep(2200);
    await shot(cdp, '09-mobile-logs');

    console.log('\n全部截图完成 ->', OUT);
  } finally {
    child.kill();
  }
}

main().catch((e) => { console.error('FAIL', e.message); process.exit(1); });
