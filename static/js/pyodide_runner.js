/* ============================================================
   pyodide_runner.js — 在浏览器里真跑 Python（在线演示站用）
   ------------------------------------------------------------
   在线站点没有后端，原来刷题中心进去只弹一句「要本地部署」。
   但判题的输入全是静态的：题库 + 判题脚本。少的只是一个能跑
   Python 的地方 —— Pyodide（编译成 WebAssembly 的 CPython）正好补这一环。

   设计要点
   --------
   1. **判题脚本与后端共用同一份**（data/qbank/harness.py）。
      两边各写一套脚本，迟早会出现"本地判过、在线判不过"，
      而学生无从判断该信哪个。
   2. **懒加载**：Pyodide 运行时约 10MB，只在学生第一次点「运行」时才下载。
      不会因为要上刷题页就先让他等半分钟。
   3. **诚实降级**：Pyodide 核心只有标准库。用到 pandas / requests 的题
      会明确告知"这道题要在本地跑"，而不是抛一堆 ModuleNotFoundError。
   4. **超时保护**：死循环在浏览器里会把标签页卡死，用 Web Worker 隔离，
      超时就终止 worker（重新起一个很便宜）。
   ============================================================ */
(function () {
  'use strict';

  const PYODIDE_VERSION = 'v0.26.4';
  const BASE = 'https://cdn.jsdelivr.net/pyodide/' + PYODIDE_VERSION + '/full/';
  const RUN_TIMEOUT_MS = 20000;

  // 有些镜像在国内更快；按顺序试，第一个成功就记住
  const MIRRORS = [
    BASE,
    'https://npmmirror.com/mirrors/pyodide/' + PYODIDE_VERSION + '/full/',
  ];

  // 这些库在 Pyodide 里需要额外下载大包（或根本装不上），直接说明白
  const HEAVY_LIBS = ['pandas', 'numpy', 'matplotlib', 'requests', 'flask',
                      'fastapi', 'openai', 'sqlite3', 'torch', 'sklearn'];

  const state = {
    worker: null,
    ready: false,
    loading: null,      // 加载中的 Promise
    harness: null,      // 判题脚本源码
    baseIndex: 0,
  };

  function detectHeavyLib(code) {
    for (const lib of HEAVY_LIBS) {
      const re = new RegExp('(^|[^\\w.])(' + lib + ')([^\\w]|$)');
      if (re.test(code)) return lib;
    }
    return null;
  }

  /** 取判题脚本（与后端同一份） */
  async function loadHarness() {
    if (state.harness !== null) return state.harness;
    try {
      const res = await fetch('data/qbank/harness.py');
      state.harness = res.ok ? await res.text() : '';
    } catch (e) {
      state.harness = '';
    }
    return state.harness;
  }

  /** 起一个 Worker：Pyodide 跑在里面，卡死也不影响页面 */
  function createWorker() {
    const src = `
      let pyodide = null;
      let booting = null;

      async function boot(bases) {
        if (pyodide) return;
        if (booting) return booting;
        booting = (async () => {
          let lastErr = null;
          for (const base of bases) {
            try {
              importScripts(base + 'pyodide.js');
              pyodide = await loadPyodide({ indexURL: base });
              return;
            } catch (e) { lastErr = e; }
          }
          throw lastErr || new Error('Pyodide 加载失败');
        })();
        return booting;
      }

      self.onmessage = async (event) => {
        const msg = event.data || {};
        if (msg.type === 'boot') {
          try {
            await boot(msg.bases);
            self.postMessage({ type: 'ready' });
          } catch (e) {
            self.postMessage({ type: 'boot-error', error: String(e && e.message || e) });
          }
          return;
        }
        if (msg.type === 'run') {
          try {
            await boot(msg.bases);
            // 把判题脚本与三个入参写成虚拟文件，然后执行它 ——
            // 完全复刻后端子进程的调用方式（argv 传参、结果写文件）
            pyodide.FS.writeFile('/harness.py', msg.harness, { encoding: 'utf8' });
            pyodide.FS.writeFile('/payload.json', JSON.stringify({
              cells: msg.cells, checks: msg.checks || [],
            }), { encoding: 'utf8' });
            pyodide.FS.writeFile('/out.json', '{}', { encoding: 'utf8' });
            pyodide.FS.mkdirTree('/figs');

            const argv = ['/harness.py', '/payload.json', '/out.json', '/figs'];
            // 传 argv 给判题脚本。注意：pyodide.globals.set 收 JS 数组即可，
            // 它自己会转成 Python list；**不要再调 .to_py()** —— 那是反方向
            // （Python→JS）的方法，调用会抛
            // "'list' object has no attribute 'to_py'"。
            pyodide.globals.set('__argv', argv);
            await pyodide.runPythonAsync('import sys; sys.argv = __argv');
            await pyodide.runPythonAsync(
              'exec(compile(open("/harness.py", encoding="utf-8").read(), "/harness.py", "exec"))'
            );
            const out = pyodide.FS.readFile('/out.json', { encoding: 'utf8' });
            self.postMessage({ type: 'result', payload: out });
          } catch (e) {
            self.postMessage({ type: 'run-error', error: String(e && e.message || e) });
          }
        }
      };
    `;
    const blob = new Blob([src], { type: 'application/javascript' });
    const worker = new Worker(URL.createObjectURL(blob));
    return worker;
  }

  /** 确保 worker 与 Pyodide 都就绪 */
  function ensureReady(onStatus) {
    if (state.ready && state.worker) return Promise.resolve();
    if (state.loading) return state.loading;

    // 注意：这里**不能**在 async IIFE 里 `return state.loading` ——
    // 那会让 Promise 返回自己，运行时抛 "Chaining cycle detected"。
    // 直接构造 Promise 赋值给 state.loading，再单独返回它。
    state.loading = new Promise((resolve, reject) => {
      if (!state.worker) state.worker = createWorker();
      const bases = MIRRORS.slice(state.baseIndex);
      const timer = setTimeout(
        () => {
          state.loading = null;
          reject(new Error('运行环境加载超时（首次约需 10–30 秒，取决于网速）'));
        }, 120000);
      const onMsg = (e) => {
        const d = e.data || {};
        if (d.type === 'ready') {
          clearTimeout(timer);
          state.worker.removeEventListener('message', onMsg);
          state.ready = true;
          resolve();
        } else if (d.type === 'boot-error') {
          clearTimeout(timer);
          state.worker.removeEventListener('message', onMsg);
          state.loading = null;
          reject(new Error(d.error || '运行环境加载失败'));
        }
      };
      state.worker.addEventListener('message', onMsg);
      state.worker.postMessage({ type: 'boot', bases });
      if (onStatus) onStatus('正在准备浏览器内的 Python 运行环境（首次约 10–30 秒）…');
    });
    return state.loading;
  }

  /** 复合判题：执行源码，返回与后端相同结构的结果 */
  async function run(cells, checks, onStatus) {
    const codeAll = (cells || []).join('\n');
    const heavy = detectHeavyLib(codeAll);
    if (heavy) {
      return {
        ok: false,
        unavailable: true,
        error: '这道题用到了 ' + heavy + '，浏览器内的 Python 只带标准库，装不了它。\n'
             + '课程正文、练习解析、AI 答疑在在线站都能用；需要跑第三方库的题目请下载本地完整版。',
      };
    }

    await ensureReady(onStatus);
    const harness = await loadHarness();
    if (!harness) {
      return { ok: false, unavailable: true, error: '判题脚本没有随站点导出，请下载本地版。' };
    }
    if (onStatus) onStatus('运行中…');

    const worker = state.worker;
    const result = await new Promise((resolve) => {
      const timer = setTimeout(() => {
        // 超时：直接换掉 worker（Pyodide 卡在死循环里没法中断）
        worker.terminate();
        state.worker = null;
        state.ready = false;
        state.loading = null;
        resolve({ ok: false, timeout: true,
                  error: '运行超时（20 秒）。死循环或等待输入都会这样。' });
      }, RUN_TIMEOUT_MS);

      const onMsg = (e) => {
        const d = e.data || {};
        if (d.type === 'result') {
          clearTimeout(timer); worker.removeEventListener('message', onMsg);
          let parsed = null;
          try { parsed = JSON.parse(d.payload); } catch (err) {}
          resolve(parsed ? { ok: true, data: parsed }
                         : { ok: false, error: '结果解析失败' });
        } else if (d.type === 'run-error') {
          clearTimeout(timer); worker.removeEventListener('message', onMsg);
          resolve({ ok: false, error: d.error });
        }
      };
      worker.addEventListener('message', onMsg);
      worker.postMessage({ type: 'run', bases: MIRRORS.slice(state.baseIndex),
                           harness, cells, checks });
    });
    return result;
  }

  window.PyRunner = {
    run,
    isAvailable: () => typeof Worker !== 'undefined' && typeof Blob !== 'undefined',
    warmUp: (onStatus) => ensureReady(onStatus),
  };
})();
