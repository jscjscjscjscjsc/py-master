/**
 * md_lite.js — 极简 Markdown 渲染（教练对话与题面共用）
 *
 * 为什么不用现成的 Markdown 库：题面与回答里 90% 是「段落 + 代码块 + 行内代码 + 列表」，
 * 而完整库要么走 CDN（教室里断网就白屏），要么几百 KB。
 * 这 60 行覆盖了全部实际用到的语法，而且**先转义再渲染**，
 * 任何用户输入都不可能变成可执行标签。
 *
 * 注意：它不认识表格合并、脚注、HTML 内联这些，也不打算认识。
 */
const MdLite = {
  esc(text) {
    return String(text == null ? '' : text)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  },

  toHtml(text) {
    let html = this.esc(text || '');
    const blocks = [];
    // 1. 先把代码块摘出来，避免其中的 # 、* 、` 被后面的规则误伤
    html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, code) => {
      blocks.push('<pre><code>' + code.replace(/\n$/, '') + '</code></pre>');
      return '\u0000CB' + (blocks.length - 1) + '\u0000';
    });
    // 2. 行内代码优先于其它行内标记，同样先摘出来
    const inlines = [];
    html = html.replace(/`([^`\n]+)`/g, (match, code) => {
      inlines.push('<code>' + code + '</code>');
      return '\u0000IC' + (inlines.length - 1) + '\u0000';
    });

    html = html.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(^|[\s(])\*([^*\n]+)\*(?=[\s).,，。]|$)/g, '$1<em>$2</em>');

    // 表格（题干里的对照表用得很多）
    html = html.replace(/(^\|.+\|\s*\n\|[\s:|-]+\|\s*\n(?:\|.*\|\s*\n?)+)/gm, (table) => {
      const lines = table.trim().split('\n');
      const head = lines[0].split('|').slice(1, -1).map((c) => c.trim());
      const rows = lines.slice(2).map((row) => row.split('|').slice(1, -1).map((c) => c.trim()));
      return '<table><thead><tr>' + head.map((c) => '<th>' + c + '</th>').join('')
        + '</tr></thead><tbody>'
        + rows.map((cells) => '<tr>' + cells.map((c) => '<td>' + c + '</td>').join('') + '</tr>').join('')
        + '</tbody></table>\n';
    });

    html = html.replace(/^###\s+(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^##\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^#\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^&gt;\s?(.+)$/gm, '<blockquote>$1</blockquote>');
    html = html.replace(/^\s*[-*+]\s+(.+)$/gm, '<li>$1</li>');
    html = html.replace(/^\s*(\d+)\.\s+(.+)$/gm, '<li>$2</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>)(?!\s*<li>)/g, '<ul>$1</ul>');
    html = html.replace(/(🤔\s*想一想：[^\n<]*)/g, '</p><div class="think-line">$1</div><p>');

    html = html.split(/\n{2,}/).map((para) => {
      const trimmed = para.trim();
      if (!trimmed) return '';
      if (/^<(h3|h4|ul|pre|table|blockquote|div)/.test(trimmed)) return trimmed;
      return '<p>' + trimmed.replace(/\n/g, '<br>') + '</p>';
    }).join('');

    html = html.replace(/\u0000IC(\d+)\u0000/g, (m, i) => inlines[Number(i)]);
    html = html.replace(/\u0000CB(\d+)\u0000/g, (m, i) => blocks[Number(i)]);
    return html;
  },
};

window.MdLite = MdLite;
