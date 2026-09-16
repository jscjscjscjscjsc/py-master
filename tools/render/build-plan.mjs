/**
 * 讲解配图 · 渲染计划生成器（Node 端只负责把 visual 规格编译成 HTML）
 *
 * 真正的截图交给 tools/render/render_plan.py 用 Python Playwright 完成：
 * 本机 Python Playwright 的 Chromium 已经就绪，不必再装一套 Node 版浏览器。
 * 这样分工只有一个渲染器、一份真相，也不引入额外依赖。
 *
 * 用法
 *   node build-plan.mjs --sheet                # 生成样张计划（各 layout 一张，供人工审阅）
 *   node build-plan.mjs                        # 为 narrations.json 里所有镜头生成计划
 *   node build-plan.mjs --chapter 5            # 只做某章
 *   node build-plan.mjs --chapter 5 --force    # 已存在的也重画
 */
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderScene } from './visuals.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '..', '..');
const NARRATIONS = join(ROOT, 'data', 'narrations.json');
const OUT_DIR = join(ROOT, 'static', 'narrations');
const PLAN = join(HERE, 'build-plan.json');
const REL = OUT_DIR.replace(/\\/g, '/');

function arg(name, fallback = null) {
  const i = process.argv.indexOf('--' + name);
  if (i === -1) return fallback;
  const next = process.argv[i + 1];
  return next && !next.startsWith('--') ? next : true;
}

/** 老数据没有 visual 规格时，用口播文本兜一张概念卡，保证渲染不中断 */
export function fallbackVisual(scene) {
  const sentences = String(scene.narration || '').split(/[。！？；]/).filter((s) => s.trim());
  return {
    layout: scene.type === 'summary' ? 'summary' : 'concept',
    title: scene.title || '',
    bullets: sentences.slice(0, 3).map((s) => s.trim().slice(0, 22)),
    highlight: scene.caption || '',
    code: scene.code || '',
  };
}

const SHEET_SAMPLES = [
  { layout: 'hook', title: '配置被改的小悲剧', question: '默认收货地址被顺手加了一项，程序就崩了？',
    bullets: [{ icon: '⚠', text: '坐标、RGB、日期这类固定组合最怕被改' }] },
  { layout: 'concept', title: '元组是"只读列表"', subtitle: '用圆括号创建，功能几乎和列表一样',
    bullets: [
      { icon: '①', text: '能索引、能切片、能遍历' },
      { icon: '②', text: '能算长度、能判断成员' },
      { icon: '③', text: '唯一区别：创建后不能修改' },
    ],
    highlight: '功能一样 → 差别只在"能不能改"' },
  { layout: 'code', title: '创建元组并取值',
    code: 'point = (3, 5)\nrgb = (255, 0, 0)\n\nprint(point[0])\nprint(rgb[-1])\nprint(len(point))',
    output: '3\n0\n2',
    bullets: [{ icon: '💡', text: '索引、负索引、长度，用法与列表完全一致' }] },
  { layout: 'compare', title: '列表 vs 元组',
    left: { label: '列表 list', lines: ['中括号创建', '可以修改', '适合会变的数据'] },
    right: { label: '元组 tuple', lines: ['圆括号创建', '不能修改', '适合固定组合'] },
    highlight: '数量会变 → 列表；固定组合 → 元组' },
  { layout: 'pitfall', title: '单元素陷阱',
    wrong: '单个元素直接加括号，Python 把它当成运算优先级的小括号',
    wrong_code: "t = (1)\nprint(type(t))\n# <class 'int'>",
    right_answer: '单元素元组必须留一个尾逗号',
    right_code: "t = (1,)\nprint(type(t))\n# <class 'tuple'>",
    highlight: '逗号才是元组的灵魂，括号有时可以省' },
  { layout: 'summary', title: '三条必须记住的结论',
    bullets: ['元组是只读列表，单元素必须加逗号', '解包是高频技巧，交换变量就靠它', '不可变指的是引用不能换'] },
  { layout: 'flow', title: '二分查找的执行流程',
    steps: ['确定左右边界', '取中间位置比较', '失败就缩小一半范围', '命中目标或边界交叉'],
    highlight: '每次排除一半 → 100 万条数据最多比 20 次' },
];

function sheetPlan() {
  return SHEET_SAMPLES.map((spec, i) => ({
    out: `${REL}/_preview/${String(i + 1).padStart(2, '0')}-${spec.layout}.jpg`,
    html: renderScene(spec, {
      chapterTitle: '数据结构（上）：列表与元组',
      sceneNo: i + 1, sceneTotal: SHEET_SAMPLES.length,
    }),
  }));
}

function narrationPlan() {
  if (!existsSync(NARRATIONS)) {
    console.error('找不到 data/narrations.json');
    process.exit(1);
  }
  const data = JSON.parse(readFileSync(NARRATIONS, 'utf-8'));
  const onlyChapter = arg('chapter');
  const onlyKey = arg('key');
  const force = Boolean(arg('force'));
  const jobs = [];

  for (const key of Object.keys(data)) {
    const narration = data[key];
    if (onlyKey && key !== String(onlyKey)) continue;
    if (onlyChapter && narration.chapter_id !== Number(onlyChapter)) continue;
    for (const scene of narration.scenes) {
      const name = `s${String(scene.id).padStart(2, '0')}.jpg`;
      const out = `${REL}/${narration.chapter_id}_${narration.kp_index}/${name}`;
      if (!force && existsSync(out)) continue;
      const visual = scene.visual || fallbackVisual(scene);
      jobs.push({
        key, sceneId: scene.id, out,
        image: `narrations/${narration.chapter_id}_${narration.kp_index}/${name}`,
        html: renderScene(visual, {
          chapterTitle: narration.chapter_title,
          sceneNo: scene.id, sceneTotal: narration.scene_count,
        }),
      });
    }
  }
  return jobs;
}

const plan = arg('sheet') ? sheetPlan() : narrationPlan();
writeFileSync(PLAN, JSON.stringify(plan), 'utf-8');
console.log(`渲染计划：${plan.length} 张 -> tools/render/build-plan.json`);
if (!plan.length) console.log('（没有待渲染的图，可能都已存在；加 --force 可重画）');
