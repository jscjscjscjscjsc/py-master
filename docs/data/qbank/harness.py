
import json, sys, io, os, traceback, contextlib

# 公网部署时给这个子进程套上资源上限：CPU 15 秒、地址空间 512MB、
# 线程/进程数 64。防的是死循环或疯狂吃内存把服务器拖垮（Linux 生效）。
if os.environ.get('PYMASTER_SAFE_MODE', '').strip().lower() in ('1', 'true', 'yes', 'on'):
    try:
        import resource as _r
        _r.setrlimit(_r.RLIMIT_CPU, (15, 15))
        _c = 512 * 1024 * 1024
        _r.setrlimit(_r.RLIMIT_AS, (_c, _c))
        _r.setrlimit(_r.RLIMIT_NPROC, (64, 64))
    except Exception:
        pass

payload = json.load(open(sys.argv[1], 'r', encoding='utf-8'))
cells = payload.get('cells') or []
out_path = sys.argv[2]
fig_dir = sys.argv[3]

results = []
globs = {'__name__': '__main__'}

def clean_tb(exc):
    """只保留用户代码块里的帧，行号天然对应代码块内的真实行号。"""
    frames = traceback.extract_tb(exc.__traceback__)
    user = [f for f in frames if str(f.filename).startswith('<cell')]
    if not user:
        user = frames[-1:]
    lines = []
    for f in user:
        loc = os.path.basename(f.filename).replace('<cell ', 'Cell ').replace('>', '')
        lines.append('%s, 第 %d 行：%s' % (loc, f.lineno, (f.line or '').strip()))
    lines.append('%s: %s' % (type(exc).__name__, exc))
    return '\n'.join(lines)

for index, src in enumerate(cells):
    record = {'index': index, 'stdout': '', 'error': '', 'ok': True, 'stderr': ''}
    buf = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            exec(compile(src, '<cell %d>' % (index + 1), 'exec'), globs)
    except SystemExit:
        pass
    except BaseException as exc:
        record['ok'] = False
        record['error'] = clean_tb(exc)
        record['stdout'] = buf.getvalue()
        record['stderr'] = err.getvalue()
        results.append(record)
        break
    record['stdout'] = buf.getvalue()
    record['stderr'] = err.getvalue()
    results.append(record)

# 判题断言作为最后一个「代码块」执行：先把学生所有代码块的输出与源码注入进去，
# 断言里就能用 _out（全部输出）和 _src（全部源码）来检查，不必跑第二遍。
checks = payload.get('checks') or []
if checks and all(r['ok'] for r in results):
    globs['_out'] = ''.join(r.get('stdout', '') for r in results)
    globs['_src'] = '\n'.join(cells)
    record = {'index': len(cells), 'stdout': '', 'error': '', 'ok': True, 'stderr': ''}
    buf = io.StringIO()
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            exec(compile('\n'.join(checks), '<cell %d>' % (len(cells) + 1), 'exec'), globs)
    except BaseException as exc:
        record['ok'] = False
        record['error'] = clean_tb(exc)
    record['stdout'] = buf.getvalue()
    record['stderr'] = err.getvalue()
    results.append(record)

figures = []
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for num in plt.get_fignums():
        name = 'fig_%d.png' % num
        path = os.path.join(fig_dir, name)
        plt.figure(num).savefig(path, dpi=110, bbox_inches='tight', facecolor='white')
        figures.append(path)
    plt.close('all')
except Exception:
    pass

with open(out_path, 'w', encoding='utf-8') as fh:
    json.dump({'results': results, 'figures': figures}, fh, ensure_ascii=False)
