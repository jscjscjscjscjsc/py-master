/**
 * canvas_presets.js — Pre-made Python memory model diagrams
 * Each preset is a function that returns an array of path objects
 * compatible with the canvas drawing engine.
 */

var CANVAS_PRESETS = {};

// ── Helper function to draw a labeled box ──
function _box(x, y, w, h, label, color) {
  var paths = [];
  paths.push({
    type: 'rect',
    color: color || '#00d4ff',
    width: 2,
    points: [{x: x, y: y}, {x: x + w, y: y + h}]
  });
  paths.push({
    type: 'text',
    text: label,
    x: x + 8,
    y: y + 22,
    color: color || '#00d4ff',
    font: '14px sans-serif'
  });
  return paths;
}

function _arrow(x1, y1, x2, y2, color) {
  return [{
    type: 'arrow',
    color: color || '#a371f7',
    width: 2,
    points: [{x: x1, y: y1}, {x: x2, y: y2}]
  }];
}

function _label(text, x, y, color, size) {
  return [{
    type: 'text',
    text: text,
    x: x,
    y: y,
    color: color || '#8b949e',
    font: (size || 13) + 'px sans-serif'
  }];
}

// ── 1. 函数栈调用图 ──
CANVAS_PRESETS.stack = function() {
  var p = [];

  // Title
  p = p.concat(_label('📚 函数栈调用过程', 50, 30, '#00d4ff', 20));

  // Stack frame: main()
  p = p.concat(_label('栈顶', 350, 55, '#a371f7', 12));
  p = p.concat(_box(50, 70, 300, 45, 'main() 栈帧\n  局部变量: total = 15', '#3fb950'));
  p.push({type: 'arrow', color: '#3fb950', width: 2, points: [{x: 130, y: 115}, {x: 130, y: 140}]});

  // Stack frame: func_a()
  p = p.concat(_box(50, 140, 300, 45, 'func_a() 栈帧\n  局部变量: x = 5, y = 10', '#00d4ff'));
  p.push({type: 'arrow', color: '#00d4ff', width: 2, points: [{x: 130, y: 185}, {x: 130, y: 210}]});

  // Stack frame: func_b()
  p = p.concat(_box(50, 210, 300, 45, 'func_b() 栈帧\n  局部变量: a = 3, b = 7', '#ff6b9d'));
  p.push({type: 'arrow', color: '#ff6b9d', width: 2, points: [{x: 130, y: 255}, {x: 130, y: 280}]});

  // Stack bottom
  p = p.concat(_label('⬆ 栈底', 50, 295, '#6e7681', 12));

  // Call arrows on the right
  p.push({type: 'arrow', color: '#a371f7', width: 2, points: [{x: 420, y: 92}, {x: 420, y: 162}]});
  p = p.concat(_label('func_a() 被 main() 调用', 430, 125, '#a371f7', 12));

  p.push({type: 'arrow', color: '#a371f7', width: 2, points: [{x: 420, y: 185}, {x: 420, y: 232}]});
  p = p.concat(_label('func_b() 被 func_a() 调用', 430, 210, '#a371f7', 12));

  return p;
};

// ── 2. 变量引用/对象实体模型 ──
CANVAS_PRESETS.reference = function() {
  var p = [];

  p = p.concat(_label('🔗 变量引用与对象实体', 50, 30, '#00d4ff', 20));

  // Variable names (stack/reference area)
  p = p.concat(_label('变量区（栈/引用）', 50, 65, '#a371f7', 14));
  p = p.concat(_box(50, 80, 180, 35, 'a  →  [地址 0x100]', '#3fb950'));
  p = p.concat(_box(50, 130, 180, 35, 'b  →  [地址 0x100]', '#00d4ff'));

  // Arrow from a and b to the list object
  p.push({type: 'arrow', color: '#3fb950', width: 2, points: [{x: 230, y: 97}, {x: 320, y: 180}]});
  p.push({type: 'arrow', color: '#00d4ff', width: 2, points: [{x: 230, y: 147}, {x: 320, y: 190}]});

  // Object region (heap)
  p = p.concat(_label('对象区（堆）', 300, 65, '#a371f7', 14));
  p = p.concat(_box(300, 80, 200, 160, '列表对象 [1, 2, 3]  @ 0x100\n  ┌───┬───┬───┐\n  │ 1 │ 2 │ 3 │\n  └───┴───┴───┘\n  引用计数: 2', '#ff6b9d'));

  // Note about aliasing
  p = p.concat(_label('⚠️ a 和 b 指向同一个列表对象', 300, 270, '#d29922', 13));
  p = p.concat(_label('修改 a[0] 也会影响 b，这叫"别名"', 300, 290, '#8b949e', 12));

  // Right side — immutable example
  p = p.concat(_label('不可变对象示例:', 50, 340, '#a371f7', 14));
  p = p.concat(_box(50, 355, 150, 30, 's = "hello"', '#3fb950'));
  p.push({type: 'arrow', color: '#3fb950', width: 2, points: [{x: 200, y: 370}, {x: 280, y: 370}]});
  p = p.concat(_box(280, 355, 120, 30, 'str "hello"', '#ff6b9d'));

  p = p.concat(_box(50, 400, 150, 30, 's = "world"  # 重新赋值', '#00d4ff'));
  p.push({type: 'arrow', color: '#00d4ff', width: 2, points: [{x: 200, y: 415}, {x: 280, y: 415}]});
  p = p.concat(_box(280, 400, 120, 30, 'str "world"  (新对象)', '#ff6b9d'));

  p = p.concat(_label('字符串不可变，每次修改都创建新对象', 50, 460, '#d29922', 12));

  return p;
};

// ── 3. 字典内部结构 ──
CANVAS_PRESETS.dict = function() {
  var p = [];

  p = p.concat(_label('📖 字典内部结构（哈希表）', 50, 30, '#00d4ff', 20));

  // Hash table array
  p = p.concat(_label('哈希表数组（稀疏存储）', 50, 60, '#a371f7', 14));

  var rows = [
    {idx: 0, hash: '...', empty: true},
    {idx: 1, hash: '0x1A3F', key: '"name"', val: '"Alice"'},
    {idx: 2, hash: '...', empty: true},
    {idx: 3, hash: '0x7B2D', key: '"age"', val: '25'},
    {idx: 4, hash: '0xC4E8', key: '"city"', val: '"北京"'},
    {idx: 5, hash: '...', empty: true},
    {idx: 6, hash: '...', empty: true},
    {idx: 7, hash: '...', empty: true},
  ];

  var yStart = 80;
  var rowH = 32;
  rows.forEach(function(r, i) {
    var y = yStart + i * rowH;
    var color = r.empty ? '#21262d' : '#1a1e2b';
    p.push({type: 'rect', color: r.empty ? '#30363d' : '#3fb950', width: 1, points: [{x: 50, y: y}, {x: 400, y: y + rowH}]});
    if (!r.empty) {
      var txt = '[' + r.idx + ']  hash=' + r.hash + '  键: ' + r.key + ' → 值: ' + r.val;
      p = p.concat(_label(txt, 58, y + 20, r.key === '"age"' ? '#ff6b9d' : '#00d4ff', 12));
    } else {
      p = p.concat(_label('[' + r.idx + ']  empty', 58, y + 20, '#6e7681', 12));
    }
  });

  // Collision chain
  p = p.concat(_label('冲突链:', 50, yStart + rows.length * rowH + 10, '#d29922', 13));
  p = p.concat(_label('当两个键的哈希值相同时，用链表/开放寻址解决', 50, yStart + rows.length * rowH + 30, '#8b949e', 12));

  // Key features
  p = p.concat(_label('✨ 字典特性:', 50, yStart + rows.length * rowH + 60, '#a371f7', 14));
  p = p.concat(_label('• O(1) 平均查找时间（最坏 O(n)）', 50, yStart + rows.length * rowH + 82, '#8b949e', 12));
  p = p.concat(_label('• Python 3.7+ 保持插入顺序', 50, yStart + rows.length * rowH + 100, '#8b949e', 12));
  p = p.concat(_label('• 键必须是不可变类型（字符串、数字、元组）', 50, yStart + rows.length * rowH + 118, '#8b949e', 12));

  return p;
};

// ── 4. 函数对象在内存中 ──
CANVAS_PRESETS.func_obj = function() {
  var p = [];

  p = p.concat(_label('⚙️ 函数对象在内存中的结构', 50, 30, '#00d4ff', 20));

  // Python code
  p = p.concat(_label('源代码定义:', 50, 60, '#a371f7', 14));
  p = p.concat(_label('def add(a, b):', 50, 80, '#3fb950', 14));
  p = p.concat(_label('    return a + b', 50, 97, '#3fb950', 14));
  p = p.concat(_label('', 50, 110, '#8b949e', 12));

  // Function object in memory
  p = p.concat(_label('函数对象（堆中）', 300, 60, '#a371f7', 14));

  // The big box showing function object internals
  p = p.concat(_box(300, 75, 250, 180, '', '#ff6b9d'));
  p = p.concat(_label('函数对象: add @ 0x200', 312, 95, '#ff6b9d', 13));

  var fields = [
    '__code__        → 代码对象 @ 0x300',
    '__name__        → "add"',
    '__defaults__    → None',
    '__globals__     → 全局命名空间',
    '__closure__     → None',
    '__annotations__ → {}',
  ];

  fields.forEach(function(f, i) {
    var color = f.indexOf('__code__') >= 0 ? '#00d4ff' : '#8b949e';
    p = p.concat(_label(f, 315, 118 + i * 20, color, 12));
  });

  // Arrow: __code__ → code object
  p.push({type: 'arrow', color: '#00d4ff', width: 2, points: [{x: 480, y: 175}, {x: 300, y: 330}]});

  // Code object
  p = p.concat(_label('代码对象 @ 0x300', 50, 280, '#a371f7', 14));
  p = p.concat(_box(50, 295, 230, 140, '', '#00d4ff'));

  var codeFields = [
    'co_argcount:    2',
    'co_varnames:    (a, b)',
    'co_code:        |LOAD_FAST|',
    '               |LOAD_FAST|',
    '               |BINARY_ADD|',
    '               |RETURN_VALUE|',
    'co_consts:     (None,)',
    'co_filename:   "demo.py"',
  ];
  codeFields.forEach(function(f, i) {
    p = p.concat(_label(f, 62, 315 + i * 16, i === 1 ? '#ff6b9d' : '#8b949e', 12));
  });

  // Stack execution
  p = p.concat(_label('调用后 → 栈帧执行:', 50, 470, '#a371f7', 14));
  p = p.concat(_box(50, 488, 250, 40, 'add(3, 5) → 栈帧创建 → 执行 → 返回 8', '#3fb950'));

  p.push({type: 'arrow', color: '#3fb950', width: 2, points: [{x: 170, y: 435}, {x: 170, y: 488}]});
  p = p.concat(_label('函数调用时创建栈帧', 180, 460, '#8b949e', 12));

  return p;
};

// ── Loader function ──
function loadCanvasPreset(name, callback) {
  if (CANVAS_PRESETS[name]) {
    var paths = CANVAS_PRESETS[name]();
    if (typeof callback === 'function') callback(paths);
  }
}
