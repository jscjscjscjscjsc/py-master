"""把新版 14 天教材的新章节并入现有课程数据。

背景
----
新版《14 天课程编排方案》改写了大部分章节，并新增了两批：
  · 第 41 章 LangFlow（Day14 的收尾，主线二）
  · 第 51–59 章 AI 工程化（40 天体系的完整版，原来的 37–40 只有 4 章）

同时新版**主动删掉**了一些与主线无关的章节（工程/全栈/综合实战等）。
按用户"不太相关的可以放到后面去"的要求，这里采取**合并**而非替换：
  · 已有章：用新版教材的内容刷新（教材是源头）
  · 新章：追加进来
  · 旧的、新版不再覆盖的章：原样保留，由 restructure 排到"进阶选修"

用法：
    python tools/merge_new_courseware.py --check   # 只看会改什么
    python tools/merge_new_courseware.py           # 执行（自动备份）
"""
import argparse
import importlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / 'data' / 'courses.json'
sys.path.insert(0, str(ROOT / 'tools'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    import migrate_courseware as m
    importlib.reload(m)

    fresh = {c['id']: c for c in m.build()}
    current = json.loads(COURSES.read_text(encoding='utf-8'))
    current_map = {c['id']: c for c in current}

    added = sorted(set(fresh) - set(current_map))
    updated = sorted(set(fresh) & set(current_map))
    kept = sorted(set(current_map) - set(fresh))

    print('合并新版教材')
    print('=' * 62)
    print(f'  新增章节 {len(added)} 个: {added}')
    print(f'  用新版刷新 {len(updated)} 个')
    print(f'  旧版保留   {len(kept)} 个: {kept}')
    print()

    # 逐章对比，只说变化大的
    for cid in updated:
        n_new = len(fresh[cid].get('knowledge_points', []))
        n_old = len(current_map[cid].get('knowledge_points', []))
        if n_new != n_old:
            print(f"  ch{cid:>2} 知识点 {n_old} → {n_new}"
                  f"  ({current_map[cid]['title'][:24]})")

    if args.check:
        print('\n--check：未写入')
        return 0

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = COURSES.with_suffix(f'.before-merge-{stamp}.json')
    shutil.copy2(COURSES, backup)
    print(f'\n已备份到 {backup.name}')

    # 合并：旧章保留其原有 order（由 restructure 统一重排），新章先排到最后
    merged = []
    for c in current:
        cid = c['id']
        if cid in fresh:
            # 用新版内容替换正文/知识点/练习，但保留旧版的展示字段
            new_c = dict(fresh[cid])
            new_c['order'] = c.get('order')
            new_c['stage'] = c.get('stage')
            new_c['stage_description'] = c.get('stage_description')
            merged.append(new_c)
        else:
            merged.append(c)
    base = max((c.get('order') or 0) for c in merged) if merged else 0
    for i, cid in enumerate(added, 1):
        c = dict(fresh[cid])
        c['order'] = base + i
        merged.append(c)

    COURSES.write_text(json.dumps(merged, ensure_ascii=False, indent=2),
                       encoding='utf-8')
    tot_kp = sum(len(c.get('knowledge_points', [])) for c in merged)
    tot_ex = sum(len(c.get('exercises', [])) for c in merged)
    print(f'已合并：{len(merged)} 章 / {tot_kp} 个知识点 / {tot_ex} 道练习')
    print('下一步跑：python tools/restructure_courses.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
