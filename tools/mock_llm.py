"""本地假模型：用来在没有可用额度时验证整条生产链路。

它冒充一个 OpenAI 兼容接口，对 /chat/completions 返回一份格式合法的分镜脚本。
用途是压测并发、验证落盘与渲染，不产生任何外部费用。

    python tools/mock_llm.py 8899        # 起在 8899 端口
    # 另开一个终端，用环境变量把生产脚本指过来：
    PYMASTER_AI_BASE_URL=http://127.0.0.1:8899/v1 ARK_API_KEY=mock \
      PYMASTER_AI_MODEL=mock python build_narrations.py --chapter 9 --limit 3 --kp-workers 3
"""
from __future__ import annotations

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCENES = [
    ('hook', '开场提问', 'file', '文件读取', ['打开文件的三种写法']),
    ('concept', 'open 的三种模式', 'concept', '读模式 r', ['只读打开', '文件不存在会报错', '用完要关闭']),
    ('code', 'with 自动关闭', 'code', 'with 语句', ['离开代码块自动关闭文件']),
    ('compare', 'r 与 w 的区别', 'compare', '读与写', ['r 只读', 'w 会清空原内容']),
    ('flow', '文件读取流程', 'flow', '执行步骤', ['打开', '读取', '关闭']),
    ('pitfall', '忘记关闭文件', 'pitfall', '资源泄漏', ['不用 with 容易忘关']),
    ('summary', '三条结论', 'summary', '记住这些', ['with 最稳', '编码要指定 utf-8', '异常要捕获']),
]


def build_script():
    scenes = []
    for i in range(16):
        kind, title, _ignore, label, lines = SCENES[i % len(SCENES)]
        narration = (f'这里是第 {i + 1} 个镜头的口播稿，用来验证并发生产链路是否正常。'
                     f'我们这节课要讲清楚{label}这件事，'
                     f'要注意的细节包括{lines[0]}，还有{lines[-1]}。'
                     f'把这两点都理解了，这一节的内容就算掌握了，'
                     f'接下来我们看具体的代码怎么写，以及容易踩的坑在哪里。')
        scene = {
            'type': kind,
            'title': f'{title}{i + 1}',
            'narration': narration,
            'caption': f'{label} → 要点 {i + 1}',
            'code': 'with open("demo.txt", encoding="utf-8") as f:\n    print(f.read())' if kind == 'code' else '',
            'visual': {
                'layout': kind if kind in ('hook', 'concept', 'code', 'compare', 'pitfall', 'summary', 'flow') else 'concept',
                'title': f'{title}{i + 1}',
                'subtitle': label,
                'question': f'{label} 到底怎么回事？',
                'mood': 'happy',
                'bullets': [
                    {'icon': '①', 'text': f'{label}的第一点'},
                    {'icon': '②', 'text': '第二个要点'},
                    {'icon': '③', 'text': '第三个要点'},
                ],
                'highlight': f'{label} 的核心结论',
                'steps': ['第一步', '第二步', '第三步'],
                'code': 'nums = [1, 2, 3]\nprint(nums[-1])' if kind == 'code' else '',
                'output': '3' if kind == 'code' else '',
                'wrong': '常见的错误写法',
                'wrong_code': 'f = open("a.txt")\nprint(f.read())',
                'right_answer': '正确做法是配合 with',
                'right_code': 'with open("a.txt") as f:\n    print(f.read())',
                'left': {'label': '写法 A', 'lines': ['第一点', '第二点']},
                'right': {'label': '写法 B', 'lines': ['第三点', '第四点']},
            },
        }
        scenes.append(scene)
    return {'title': '并发链路验证课', 'hook_line': '先把管子通起来', 'scenes': scenes}


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        self.rfile.read(length)
        payload = json.dumps(build_script(), ensure_ascii=False)
        # 按 OpenAI 流式格式返回，和真实接口一致
        body = []
        for i in range(0, len(payload), 400):
            chunk = {'choices': [{'delta': {'content': payload[i:i + 400]}}]}
            body.append(f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n")
        body.append('data: [DONE]\n\n')
        raw = ''.join(body).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
        time.sleep(0.2)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8899
    print(f'假模型已启动：http://127.0.0.1:{port}/v1  （仅用于验证链路，不产生费用）')
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
