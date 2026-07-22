#!/usr/bin/env python
"""
Comprehensive reorder and rename script for Data Structures chapters.
Renames files, updates all internal links (hub wiki-links, atomic note prev/next links,
and cross-chapter references) across all .md files in the Data Structures directory.
"""

import os
import sys

BASE = r"D:/DOC/Data Structures"

# =============================================================================
# RENAME PLANS per chapter
# Format: (old_filename, new_filename)
# =============================================================================

CHAPTERS = {
    "01-数据结构概述": {
        "hub": "数据结构概述.md",
        "mapping": [
            ("1.1 抽象数据类型.md", "1.1 抽象数据类型.md"),
            ("1.2 逻辑结构与存储结构.md", "1.2 逻辑结构与存储结构.md"),
        ]
    },
    "02-广义表": {
        "hub": "广义表.md",
        "mapping": [
            ("2.1 子表存储.md", "2.2 子表存储.md"),
            ("2.2 广义表的定义.md", "2.1 广义表的定义.md"),
            ("2.3 表头表尾存储.md", "2.3 表头表尾存储.md"),
        ]
    },
    "03-稀疏矩阵": {
        "hub": "稀疏矩阵.md",
        "mapping": [
            ("3.1 三元组稀疏矩阵.md", "3.1 三元组稀疏矩阵.md"),
            ("3.2 稀疏矩阵转置.md", "3.2 稀疏矩阵转置.md"),
        ]
    },
    "04-队列": {
        "hub": "队列.md",
        "mapping": [
            ("4.1 循环队列.md", "4.2 循环队列.md"),
            ("4.2 链队列.md", "4.3 链队列.md"),
            ("4.3 队列的STL实现.md", "4.4 队列的STL实现.md"),
            ("4.4 队列的基本概念.md", "4.1 队列的基本概念.md"),
        ]
    },
    "05-栈": {
        "hub": "栈.md",
        "mapping": [
            ("5.1 栈的STL实现.md", "5.5 栈的STL实现.md"),
            ("5.2 栈的基本操作.md", "5.2 栈的基本操作.md"),
            ("5.3 栈的基本概念.md", "5.1 栈的基本概念.md"),
            ("5.4 栈的链式存储结构.md", "5.4 栈的链式存储结构.md"),
            ("5.5 栈的顺序存储结构.md", "5.3 栈的顺序存储结构.md"),
        ]
    },
    "06-树": {
        "hub": "树.md",
        "mapping": [
            ("6.1 二叉树的基本概念.md", "6.2 二叉树的基本概念.md"),
            ("6.2 二叉树的存储结构.md", "6.3 二叉树的存储结构.md"),
            ("6.3 二叉树的性质.md", "6.4 二叉树的性质.md"),
            ("6.4 二叉树的相关算法.md", "6.6 二叉树的相关算法.md"),
            ("6.5 二叉树的遍历.md", "6.5 二叉树的遍历.md"),
            ("6.6 哈夫曼树的构造.md", "6.12 哈夫曼树的构造.md"),
            ("6.7 哈夫曼树的相关概念.md", "6.11 哈夫曼树的相关概念.md"),
            ("6.8 哈夫曼编码.md", "6.13 哈夫曼编码.md"),
            ("6.9 树和森林的转换.md", "6.9 树和森林的转换.md"),
            ("6.10 树和森林的遍历.md", "6.10 树和森林的遍历.md"),
            ("6.11 树的基本定义.md", "6.1 树的基本定义.md"),
            ("6.12 树的存储结构.md", "6.8 树的存储结构.md"),
            ("6.13 线索二叉树.md", "6.7 线索二叉树.md"),
        ]
    },
    "07-图": {
        "hub": "图.md",
        "mapping": [
            ("7.1 Dijkstra算法.md", "7.11 Dijkstra算法.md"),
            ("7.2 Floyd算法.md", "7.12 Floyd算法.md"),
            ("7.3 Kruskal算法.md", "7.8 Kruskal算法.md"),
            ("7.4 Prim算法.md", "7.7 Prim算法.md"),
            ("7.5 关键路径.md", "7.10 关键路径.md"),
            ("7.6 图的基本概念.md", "7.1 图的基本概念.md"),
            ("7.7 图的广度优先搜索.md", "7.5 图的广度优先搜索.md"),
            ("7.8 图的深度优先搜索.md", "7.4 图的深度优先搜索.md"),
            ("7.9 图的邻接矩阵存储.md", "7.2 图的邻接矩阵存储.md"),
            ("7.10 图的邻接表存储.md", "7.3 图的邻接表存储.md"),
            ("7.11 拓扑排序.md", "7.9 拓扑排序.md"),
            ("7.12 生成树和最小生成树.md", "7.6 生成树和最小生成树.md"),
        ]
    },
}


def url_encode(s):
    """URL-encode spaces in a filename for markdown link matching."""
    return s.replace(' ', '%20')


def collect_all_md_files():
    """Return list of all .md file paths under BASE."""
    files = []
    for root, dirs, fnames in os.walk(BASE):
        # Skip .git directory
        dirs[:] = [d for d in dirs if d != '.git' and d != '__pycache__']
        for f in fnames:
            if f.endswith('.md'):
                files.append(os.path.join(root, f))
    return files


def rename_files(ch_dir, mapping):
    """
    Rename files in the chapter directory using a temp-name approach
    to avoid conflicts when old->new chains overlap (e.g., A->B while B->C).
    """
    dir_path = os.path.join(BASE, ch_dir)
    temp_phase = []   # (old_name, temp_name)
    final_phase = []  # (temp_name, new_name)

    for old_name, new_name in mapping:
        if old_name == new_name:
            continue
        old_path = os.path.join(dir_path, old_name)
        if not os.path.exists(old_path):
            print(f"  WARNING: File not found: {old_path}")
            continue
        temp_name = old_name + ".rename_tmp"
        temp_path = os.path.join(dir_path, temp_name)
        os.rename(old_path, temp_path)
        print(f"  Renamed: {old_name} -> {temp_name} (temp)")
        temp_phase.append((temp_name, new_name))

    for temp_name, new_name in final_phase + temp_phase:
        # Both final_phase and temp_phase use (temp_name, new_name) pattern
        pass

    for temp_name, new_name in temp_phase:
        temp_path = os.path.join(dir_path, temp_name)
        new_path = os.path.join(dir_path, new_name)
        os.rename(temp_path, new_path)
        print(f"  Renamed: {temp_name} -> {new_name} (final)")


def update_links_in_files(ch_dir, mapping, all_md_files):
    """
    For each old->new rename pair, replace all occurrences of the old filename
    (in all link formats) with the new filename across every .md file.
    """
    for old_name, new_name in mapping:
        if old_name == new_name:
            continue

        old_link = old_name.replace('.md', '')   # e.g., "2.1 子表存储"
        new_link = new_name.replace('.md', '')   # e.g., "2.2 子表存储"
        old_enc = url_encode(old_name)           # e.g., "2.1%20子表存储.md"
        new_enc = url_encode(new_name)           # e.g., "2.2%20子表存储.md"

        # Build all possible link patterns for replacement
        replacements = []

        # Wiki-links with directory: [[ch-dir/old_name|display]] or [[ch-dir/old_name]]
        replacements.append((f'[[{ch_dir}/{old_name}|', f'[[{ch_dir}/{new_name}|'))
        replacements.append((f'[[{ch_dir}/{old_name}]]', f'[[{ch_dir}/{new_name}]]'))
        replacements.append((f'[[{ch_dir}/{old_link}|', f'[[{ch_dir}/{new_link}|'))
        replacements.append((f'[[{ch_dir}/{old_link}]]', f'[[{ch_dir}/{new_link}]]'))

        # Markdown links with directory: ](ch-dir/old_enc) or ](ch-dir/old_name)
        replacements.append((f']({ch_dir}/{old_enc})', f']({ch_dir}/{new_enc})'))
        replacements.append((f']({ch_dir}/{old_name})', f']({ch_dir}/{new_name})'))

        # Relative markdown links (same directory): ](old_enc) or ](old_name)
        replacements.append((f']({old_enc})', f']({new_enc})'))
        replacements.append((f']({old_name})', f']({new_name})'))

        # Relative wiki-links: [[old_link|display]] or [[old_link]]
        replacements.append((f'[[{old_link}|', f'[[{new_link}|'))
        replacements.append((f'[[{old_link}]]', f'[[{new_link}]]'))

        # Also handle the first-link pattern (no display text, no pipe)
        # e.g. [[ch-dir/old_link]] handled above

        for filepath in all_md_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"  ERROR reading {filepath}: {e}")
                continue

            original = content
            for old_pattern, new_pattern in replacements:
                content = content.replace(old_pattern, new_pattern)

            if content != original:
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    rel = os.path.relpath(filepath, BASE)
                    print(f"  Updated: {rel}")
                except Exception as e:
                    print(f"  ERROR writing {filepath}: {e}")


def verify_links(all_md_files, ch_dir, mapping):
    """
    After renaming and link updates, check if any old filenames still appear
    in link contexts within files. Report any remaining old references.
    """
    issues = []
    for old_name, new_name in mapping:
        if old_name == new_name:
            continue
        old_enc = url_encode(old_name)
        old_link = old_name.replace('.md', '')

        for filepath in all_md_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue

            # Check for any remaining patterns with old name
            patterns_to_check = [
                f'[[{ch_dir}/{old_name}',
                f'[[{ch_dir}/{old_link}',
                f']({ch_dir}/{old_enc})',
                f']({ch_dir}/{old_name})',
                f']({old_enc})',
                f']({old_name})',
                f'[[{old_link}]]',
            ]
            for pat in patterns_to_check:
                if pat in content:
                    rel = os.path.relpath(filepath, BASE)
                    issues.append(f"  {rel} still contains: {pat}")

    return issues


def main():
    print("=" * 70)
    print("Data Structures - Reorder, Rename & Link Update Script")
    print("=" * 70)

    all_md_files = collect_all_md_files()
    print(f"\nFound {len(all_md_files)} .md files to scan for link updates.\n")

    ordered_chapters = [
        "01-数据结构概述",
        "02-广义表",
        "03-稀疏矩阵",
        "04-队列",
        "05-栈",
        "06-树",
        "07-图",
    ]

    # Phase 1: Rename files in each chapter
    print("=" * 70)
    print("PHASE 1: FILE RENAMING")
    print("=" * 70)
    for ch_name in ordered_chapters:
        ch_info = CHAPTERS[ch_name]
        mapping = ch_info["mapping"]
        print(f"\n--- Chapter {ch_name} ---")
        rename_files(ch_name, mapping)

    print("\nFile renaming complete.\n")

    # Phase 2: Update links in all files for each chapter
    print("=" * 70)
    print("PHASE 2: LINK UPDATES")
    print("=" * 70)
    for ch_name in ordered_chapters:
        ch_info = CHAPTERS[ch_name]
        mapping = ch_info["mapping"]
        print(f"\n--- Chapter {ch_name} ---")
        update_links_in_files(ch_name, mapping, all_md_files)

    print("\nLink updates complete.\n")

    # Phase 3: Verify - check for any remaining old references
    print("=" * 70)
    print("PHASE 3: VERIFICATION")
    print("=" * 70)
    total_issues = 0
    for ch_name in ordered_chapters:
        ch_info = CHAPTERS[ch_name]
        mapping = ch_info["mapping"]
        issues = verify_links(all_md_files, ch_name, mapping)
        if issues:
            print(f"\nRemaining old references in {ch_name}:")
            for iss in issues:
                print(iss)
                total_issues += 1

    if total_issues == 0:
        print("\nNo remaining old references found -- all links updated cleanly.")
    else:
        print(f"\n{total_issues} remaining old reference(s) found. Review above.")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
