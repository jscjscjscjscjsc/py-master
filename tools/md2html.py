"""教材 Markdown → 富文本 HTML 转换器。

只服务于本课程的课件格式：标题、代码块（含 mermaid）、GFM 表格、
引用块、嵌套列表、行内格式与 ✅❌⚠ 这类教学标记。
刻意不引入第三方 Markdown 库，避免给学生环境增加安装负担。
"""
import html as _html
import re

_FENCE_RE = re.compile(r'^```(\w*)\s*$')
_HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')
_LIST_RE = re.compile(r'^(\s*)([-*+]|\d+[.)])\s+(.*)$')
_HR_RE = re.compile(r'^\s*(-{3,}|\*{3,}|_{3,})\s*$')
_TABLE_SEP_RE = re.compile(r'^\|[\s:\-|]+\|$')

# 教学标记 → 视觉样式，让"必须掌握/常见坑/提示"在页面上能一眼区分
_CALLOUTS = (
    (('❌', '⛔'), 'md-bad'),
    (('✅',), 'md-good'),
    (('⚠️', '⚠', '❗'), 'md-warn'),
    (('💡', '🔑', '🧠', '🎯', '🔍'), 'md-tip'),
    (('📌', '📝', '🚀', '⚡', '🔧', '📊', '🎬', '⭐', '🎨', '🏆', '📈'), 'md-note'),
)


def _inline(text):
    """处理行内格式；代码片段先摘出来，避免其中的 * _ 被误判为强调。"""
    codes = []

    def stash(match):
        codes.append(match.group(1))
        return f'\x00{len(codes) - 1}\x00'

    text = re.sub(r'`([^`]+)`', stash, text)
    text = _html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
                  r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)

    def restore(match):
        raw = _html.escape(codes[int(match.group(1))], quote=False)
        return f'<code class="md-inline">{raw}</code>'

    return re.sub(r'\x00(\d+)\x00', restore, text)


def _callout_class(text):
    stripped = text.lstrip('* ')
    for marks, cls in _CALLOUTS:
        if stripped.startswith(marks):
            return cls
    return None


def _paragraph(text):
    cls = _callout_class(text)
    if cls:
        return f'<p class="md-callout {cls}">{_inline(text)}</p>'
    return f'<p>{_inline(text)}</p>'


def _split_row(line):
    row = line.strip()
    if row.startswith('|'):
        row = row[1:]
    if row.endswith('|'):
        row = row[:-1]
    return [cell.strip().replace('\\|', '|') for cell in row.split('|')]


def _render_table(rows, aligns):
    head, body = rows[0], rows[1:]
    parts = ['<div class="md-table-wrap"><table class="md-table"><thead><tr>']
    for idx, cell in enumerate(head):
        align = aligns[idx] if idx < len(aligns) else ''
        style = f' style="text-align:{align}"' if align else ''
        parts.append(f'<th{style}>{_inline(cell)}</th>')
    parts.append('</tr></thead><tbody>')
    for row in body:
        parts.append('<tr>')
        for idx, cell in enumerate(row):
            align = aligns[idx] if idx < len(aligns) else ''
            style = f' style="text-align:{align}"' if align else ''
            parts.append(f'<td{style}>{_inline(cell)}</td>')
        parts.append('</tr>')
    parts.append('</tbody></table></div>')
    return ''.join(parts)


def _parse_aligns(sep_line):
    aligns = []
    for cell in _split_row(sep_line):
        left, right = cell.startswith(':'), cell.endswith(':')
        if left and right:
            aligns.append('center')
        elif right:
            aligns.append('right')
        else:
            aligns.append('')
    return aligns


def _list_tree(items):
    """items: [(indent, ordered, text)] → 嵌套树，用缩进判定层级。"""
    root = {'indent': -1, 'ordered': False, 'text': '', 'children': []}
    stack = [root]
    for indent, ordered, text in items:
        node = {'indent': indent, 'ordered': ordered, 'text': text, 'children': []}
        while len(stack) > 1 and stack[-1]['indent'] >= indent:
            stack.pop()
        stack[-1]['children'].append(node)
        stack.append(node)
    return root


def _render_list(node):
    out = []
    current = None
    for child in node['children']:
        tag = 'ol' if child['ordered'] else 'ul'
        if tag != current:
            if current:
                out.append(f'</{current}>')
            out.append(f'<{tag}>')
            current = tag
        nested = _render_list(child)
        out.append(f'<li>{_inline(child["text"])}{nested}</li>')
    if current:
        out.append(f'</{current}>')
    return ''.join(out)


def md_to_html(md, min_heading=2):
    """转换 Markdown 正文。min_heading 以下级别的标题会被保留为对应 HTML 标题。"""
    lines = md.replace('\r\n', '\n').split('\n')
    out = []
    i, total = 0, len(lines)

    while i < total:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        fence = _FENCE_RE.match(stripped)
        if fence:
            lang = fence.group(1)
            i += 1
            buf = []
            while i < total and not lines[i].strip().startswith('```'):
                buf.append(lines[i])
                i += 1
            i += 1
            code = _html.escape('\n'.join(buf))
            if lang in ('mermaid', 'text'):
                out.append(f'<div class="md-figure"><pre class="md-diagram">{code}</pre></div>')
            else:
                label = lang or 'code'
                out.append(
                    f'<div class="md-codeblock" data-lang="{label}">'
                    f'<div class="md-codebar"><span class="md-codelang">{label}</span>'
                    f'<button type="button" class="md-copy" onclick="copyBlock(this)">复制</button></div>'
                    f'<pre><code class="language-{label}">{code}</code></pre></div>')
            continue

        if _HR_RE.match(line):
            i += 1
            continue

        heading = _HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level >= min_heading:
                out.append(f'<h{level} class="md-h">{_inline(text)}</h{level}>')
            i += 1
            continue

        if stripped.startswith('|') and i + 1 < total and _TABLE_SEP_RE.match(lines[i + 1].strip()):
            aligns = _parse_aligns(lines[i + 1])
            rows = [_split_row(stripped)]
            i += 2
            while i < total and lines[i].strip().startswith('|'):
                rows.append(_split_row(lines[i]))
                i += 1
            out.append(_render_table(rows, aligns))
            continue

        if stripped.startswith('>'):
            buf = []
            while i < total and (lines[i].strip().startswith('>') or not lines[i].strip()):
                if not lines[i].strip():
                    if i + 1 < total and lines[i + 1].strip().startswith('>'):
                        buf.append('')
                        i += 1
                        continue
                    break
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]))
                i += 1
            out.append(f'<blockquote class="md-quote">{md_to_html(chr(10).join(buf), min_heading)}</blockquote>')
            continue

        if _LIST_RE.match(line):
            items = []
            pending_text = None
            while i < total:
                current = lines[i]
                if not current.strip():
                    look = i + 1
                    while look < total and not lines[look].strip():
                        look += 1
                    if look < total and _LIST_RE.match(lines[look]):
                        i = look
                        continue
                    break
                match = _LIST_RE.match(current)
                if match:
                    indent = len(match.group(1).replace('\t', '    '))
                    ordered = match.group(2)[0].isdigit()
                    items.append((indent, ordered, match.group(3).strip()))
                    pending_text = items[-1]
                    i += 1
                    continue
                if current.startswith(('  ', '\t')) and pending_text is not None:
                    i += 1
                    continue
                break
            out.append(_render_list(_list_tree(items)))
            continue

        buf = []
        while i < total:
            current = lines[i]
            if not current.strip() or _LIST_RE.match(current) or _HEADING_RE.match(current):
                break
            if current.strip().startswith(('|', '>')) or _FENCE_RE.match(current.strip()):
                break
            buf.append(current.strip())
            i += 1
        if buf:
            out.append(_paragraph(' '.join(buf)))

    return '\n'.join(out)


def html_to_text(html_text):
    """从 HTML 抽回纯文本，供大模型生成讲解稿时复用。

    代码块会被保留成 fenced 形式——讲解稿要能引用具体代码，
    否则模型只能泛泛而谈。
    """
    text = re.sub(r'<(script|style).*?</\1>', ' ', html_text, flags=re.S)

    def keep_code(match):
        lang = match.group(1) or 'text'
        body = re.sub(r'<[^>]+>', '', match.group(2))
        return f'\n```{lang}\n{_html.unescape(body).strip()}\n```\n'

    text = re.sub(r'<div class="md-codeblock" data-lang="([^"]*)">.*?<pre><code[^>]*>(.*?)</code></pre>.*?</div>',
                  keep_code, text, flags=re.S)
    text = re.sub(r'<pre[^>]*>(.*?)</pre>',
                  lambda m: '\n```text\n' + _html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() + '\n```\n',
                  text, flags=re.S)
    text = re.sub(r'<(h[1-6])[^>]*>(.*?)</\1>',
                  lambda m: f'\n{"#" * int(m.group(1)[1])} {m.group(2)}\n', text, flags=re.S)
    text = re.sub(r'<li[^>]*>', '\n- ', text)
    text = re.sub(r'<(tr|p|div|table|thead|tbody|ul|ol|blockquote)[^>]*>', '\n', text)
    text = re.sub(r'</(td|th)>', ' | ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = _html.unescape(text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
