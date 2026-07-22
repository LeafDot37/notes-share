#!/usr/bin/env python3
"""
Re-run to fix prev/next links: the sorting had a critical bug where float("3.10") == 3.1.
Files were renamed correctly already, but prev/next links in notes need fixing.
This reads from the NEW filenames and fixes the prev/next links with correct sorting.
"""

import os
import re
from urllib.parse import quote

base = r"D:/DOC/Discrete Math"

# ============================================================
# Define the rename mappings for each chapter
# ============================================================
chapters = [
    {
        "dir": "01-命题逻辑与一阶逻辑",
        "hub": "01-命题逻辑与一阶逻辑.md",
        "old_to_new": {
            "1.1 一阶逻辑基本概念.md": "1.1 命题基本概念.md",
            "1.2 一阶逻辑推理.md":       "1.2 等值演算.md",
            "1.3 一阶逻辑等值演算.md":   "1.3 范式.md",
            "1.4 命题基本概念.md":       "1.4 推理理论.md",
            "1.5 推理理论.md":           "1.5 一阶逻辑基本概念.md",
            "1.6 等值演算.md":           "1.6 一阶逻辑等值演算.md",
            "1.7 范式.md":               "1.7 一阶逻辑推理.md",
        }
    },
    {
        "dir": "02-集合论与二元关系",
        "hub": "02-集合论与二元关系.md",
        "old_to_new": {
            "2.1 二元关系基本概念.md":   "2.4 二元关系基本概念.md",
            "2.2 二元关系性质.md":       "2.5 二元关系性质.md",
            "2.3 二元关系运算.md":       "2.6 二元关系运算.md",
            "2.4 二元关系闭包.md":       "2.7 二元关系闭包.md",
            "2.5 偏序关系.md":           "2.9 偏序关系.md",
            "2.6 函数.md":               "2.10 函数.md",
            "2.7 等价关系与划分.md":     "2.8 等价关系与划分.md",
            "2.8 集合代数基本概念.md":   "2.1 集合代数基本概念.md",
            "2.9 集合基本运算.md":       "2.2 集合基本运算.md",
            "2.10 集合计数与基数.md":    "2.3 集合计数与基数.md",
        }
    },
    {
        "dir": "03-图论",
        "hub": "03-图论.md",
        "old_to_new": {
            "3.1 二部图.md":                       "3.5 二部图.md",
            "3.2 哈密顿图.md":                     "3.7 哈密顿图.md",
            "3.3 图的基本概念.md":                 "3.1 图的基本概念.md",
            "3.4 平面图.md":                       "3.8 平面图.md",
            "3.5 支配集覆盖集独立集匹配.md":       "3.10 支配集覆盖集独立集匹配.md",
            "3.6 树.md":                           "3.4 树.md",
            "3.7 欧拉图与中国邮路.md":             "3.6 欧拉图与中国邮路.md",
            "3.8 连通性.md":                       "3.3 连通性.md",
            "3.9 通路与回路.md":                   "3.2 通路与回路.md",
            "3.10 顶点着色与边着色.md":            "3.9 顶点着色与边着色.md",
        }
    }
]


def parse_version(fname):
    """Parse 'X.Y ...' into a tuple (X, Y) for proper numeric sorting.
    e.g. '3.10 支配集...' -> (3, 10)
    """
    parts = fname.split(" ")[0].split(".")
    return tuple(int(n) for n in parts)


# ============================================================
# Precompute metadata with CORRECT sorting
# ============================================================

for ch in chapters:
    # Sorted list of new filenames (by section number Y, using tuple comparison)
    ch["new_order"] = sorted(
        ch["old_to_new"].values(),
        key=parse_version
    )
    ch["new_to_old"] = {v: k for k, v in ch["old_to_new"].items()}

    print(f"Chapter {ch['dir']}:")
    for i, fname in enumerate(ch["new_order"]):
        print(f"  [{i+1}] {fname}")
    print()


def url_encode_filename(fname):
    return quote(fname)


# ============================================================
# Fix prev/next links in atomic notes (files already renamed)
# ============================================================

for ch in chapters:
    ch_dir = os.path.join(base, ch["dir"])
    new_order = ch["new_order"]

    # Build correct prev/next mapping
    new_prev_next = {}
    for i, fname in enumerate(new_order):
        prev_name = new_order[i - 1] if i > 0 else None
        next_name = new_order[i + 1] if i < len(new_order) - 1 else None
        new_prev_next[fname] = (prev_name, next_name)

    print(f"\n{'='*60}")
    print(f"Fixing {ch['dir']}")
    print(f"{'='*60}")

    for new_fname in new_order:
        fpath = os.path.join(ch_dir, new_fname)
        if not os.path.exists(fpath):
            print(f"  [SKIP] {new_fname} does not exist")
            continue

        print(f"  [READ]  {new_fname}")
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Build new prev/next lines
        prev_fname, next_fname = new_prev_next[new_fname]

        if prev_fname is None:
            new_prev_line = "- 上一个知识点：无（本章第一个知识点）"
        else:
            prev_display = prev_fname[:-3]
            prev_encoded = url_encode_filename(prev_fname)
            new_prev_line = f"- 上一个知识点：[{prev_display}]({prev_encoded})"

        if next_fname is None:
            new_next_line = "- 下一个知识点：无（本章最后一个知识点）"
        else:
            next_display = next_fname[:-3]
            next_encoded = url_encode_filename(next_fname)
            new_next_line = f"- 下一个知识点：[{next_display}]({next_encoded})"

        # Replace prev/next section
        prev_next_re = re.compile(
            r"^(-\s*上一个知识点：.*)$\n^(-\s*下一个知识点：.*)$",
            re.MULTILINE
        )
        new_prev_next_text = f"{new_prev_line}\n{new_next_line}"
        content, n_subs = prev_next_re.subn(new_prev_next_text, content)

        if n_subs == 0:
            print(f"    [WARN]  Could not find prev/next section")
        else:
            print(f"    [OK]    Updated prev/next")

        # Write back
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)

# ============================================================
# Now also update the display text in hub wiki-links
# The display text (after |) should match the topic name (without X.Y prefix)
# ============================================================

for ch in chapters:
    ch_dir = os.path.join(base, ch["dir"])
    hub_path = os.path.join(ch_dir, ch["hub"])

    if not os.path.exists(hub_path):
        print(f"\n  [HUB]   SKIP: {hub_path} not found")
        continue

    print(f"\n  [HUB]   Updating display text in {ch['hub']}")
    with open(hub_path, 'r', encoding='utf-8') as f:
        hub_content = f.read()

    for new_fname in ch["new_order"]:
        # Extract topic name (everything after "X.Y ")
        topic_name = new_fname[:-3].split(" ", 1)[1]  # "命题基本概念" from "1.1 命题基本概念.md"
        # In the hub, the wiki-link display should be the topic name
        # Pattern: [[dir/X.Y Topic|OLD_DISPLAY]]
        # We need to replace OLD_DISPLAY with topic_name

        # Actually, let's just focus on the wiki-link display text.
        # The hub has entries like:
        #   [[dir/1.1 命题基本概念|SOME_DISPLAY]]
        # We want to replace SOME_DISPLAY with 命题基本概念

        # Find all wiki-links with this filename and correct their display
        # Pattern: [[dir/X.Y Topic|old_display]]
        wiki_pattern = re.escape(f"[[{ch['dir']}/{new_fname[:-3]}|") + r"([^]]+)\]"
        replacement = f"[[{ch['dir']}/{new_fname[:-3]}|{topic_name}]]"
        hub_content, n_subs = re.sub(wiki_pattern, replacement, hub_content)
        if n_subs > 0:
            print(f"    [HUB]  Updated display for {new_fname[:-3]} -> {topic_name} ({n_subs} change(s))")

    with open(hub_path, 'w', encoding='utf-8') as f:
        f.write(hub_content)


# ============================================================
# Verification
# ============================================================
print(f"\n\n{'='*60}")
print("VERIFICATION")
print(f"{'='*60}")

for ch in chapters:
    ch_dir = os.path.join(base, ch["dir"])
    print(f"\n--- {ch['dir']} ---")

    # Check hub file
    hub_path = os.path.join(ch_dir, ch["hub"])
    if os.path.exists(hub_path):
        with open(hub_path, 'r', encoding='utf-8') as f:
            hub_content = f.read()
        print(f"  Hub: {ch['hub']}")
        for line in hub_content.split('\n'):
            if '[[' in line and ch['dir'] in line:
                print(f"    {line.strip()}")

    # Check prev/next for first, middle, last files
    new_order = ch["new_order"]
    check_files = [new_order[0]]
    if len(new_order) > 2:
        mid_idx = len(new_order) // 2
        check_files.append(new_order[mid_idx])
    check_files.append(new_order[-1])

    for fname in check_files:
        fpath = os.path.join(ch_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(
                r"^(-\s*上一个知识点：.*)$\n^(-\s*下一个知识点：.*)$",
                content, re.MULTILINE
            )
            if m:
                print(f"  {fname}:")
                print(f"    {m.group(1)}")
                print(f"    {m.group(2)}")

print(f"\n{'='*60}")
print("DONE - VERIFICATION COMPLETE")
print(f"{'='*60}")
