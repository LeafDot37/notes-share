#!/usr/bin/env python3
"""
Comprehensive script to reorder/rename files and update all internal links
in the Signals and System subject.
Processes chapters in order so cross-chapter links update correctly.
"""

import os
import re
import urllib.parse
import sys

BASE = r"D:/DOC/Signals and System"

# ============================================================
# DEFINITIONS: each chapter entry is (dir_name, hub_file, old_order, new_order)
# ============================================================
chapters = [
    # Chapter 01 - keep as-is
    ("01-基本概念", "01-基本概念.md", None, None),
    # Chapter 02 - needs reorder
    ("02-连续时间系统时域分析", "02-连续时间系统时域分析.md",
     ["2.1 冲激响应与阶跃响应.md", "2.2 卷积性质.md", "2.3 卷积概念与图解.md",
      "2.4 卷积求全响应.md", "2.5 线性系统时域模拟.md", "2.6 经典微分方程求解.md",
      "2.7 跳变求法与换路定理.md", "2.8 零输入零状态响应.md"],
     ["2.1 经典微分方程求解.md", "2.2 零输入零状态响应.md", "2.3 冲激响应与阶跃响应.md",
      "2.4 跳变求法与换路定理.md", "2.5 卷积概念与图解.md", "2.6 卷积性质.md",
      "2.7 卷积求全响应.md", "2.8 线性系统时域模拟.md"]),
    # Chapter 03 - needs reorder
    ("03-傅里叶变换", "03-傅里叶变换.md",
     ["3.1 傅里叶变换定义.md", "3.2 傅里叶变换的性质.md", "3.3 傅里叶级数.md",
      "3.4 典型周期信号的傅里叶级数.md", "3.5 典型非周期信号的傅里叶变换.md",
      "3.6 卷积特性与频率响应.md", "3.7 吉布斯现象.md", "3.8 周期信号的傅里叶变换.md",
      "3.9 抽样定理.md", "3.10 波形对称性与傅里叶系数.md", "3.11 能量谱与功率谱.md",
      "3.12 频谱与带宽.md"],
     ["3.1 傅里叶级数.md", "3.2 典型周期信号的傅里叶级数.md",
      "3.3 波形对称性与傅里叶系数.md", "3.4 傅里叶变换定义.md",
      "3.5 典型非周期信号的傅里叶变换.md", "3.6 周期信号的傅里叶变换.md",
      "3.7 傅里叶变换的性质.md", "3.8 卷积特性与频率响应.md",
      "3.9 频谱与带宽.md", "3.10 能量谱与功率谱.md", "3.11 抽样定理.md",
      "3.12 吉布斯现象.md"]),
    # Chapter 04 - needs reorder
    ("04-拉普拉斯变换", "04-拉普拉斯变换.md",
     ["4.1 常用拉普拉斯变换对.md", "4.2 拉普拉斯变换定义.md",
      "4.3 拉普拉斯变换收敛域.md", "4.4 拉普拉斯变换的性质.md",
      "4.5 拉普拉斯逆变换.md", "4.6 滤波器类型.md",
      "4.7 用拉普拉斯变换分析电路.md", "4.8 系统函数H(s).md",
      "4.9 系统因果性与稳定性.md", "4.10 零极点分布与时域特性.md",
      "4.11 零极点分布与频响特性.md"],
     ["4.1 拉普拉斯变换定义.md", "4.2 拉普拉斯变换收敛域.md",
      "4.3 常用拉普拉斯变换对.md", "4.4 拉普拉斯变换的性质.md",
      "4.5 拉普拉斯逆变换.md", "4.6 系统函数H(s).md",
      "4.7 用拉普拉斯变换分析电路.md", "4.8 系统因果性与稳定性.md",
      "4.9 零极点分布与时域特性.md", "4.10 零极点分布与频响特性.md",
      "4.11 滤波器类型.md"]),
    # Chapter 05 - keep as-is
    ("05-频域分析", "05-频域分析.md", None, None),
    # Chapter 06 - needs reorder
    ("06-Z变换", "06-Z变换.md",
     ["6.1 z变换定义与收敛域.md", "6.2 z变换的性质.md", "6.3 z变换解差分方程.md",
      "6.4 z平面与s平面的映射关系.md", "6.5 典型序列的z变换.md",
      "6.6 数字滤波器.md", "6.7 离散时间傅里叶变换DTFT.md",
      "6.8 离散系统系统函数.md", "6.9 离散系统频率响应.md", "6.10 逆z变换.md"],
     ["6.1 z变换定义与收敛域.md", "6.2 典型序列的z变换.md",
      "6.3 z变换的性质.md", "6.4 逆z变换.md", "6.5 z变换解差分方程.md",
      "6.6 z平面与s平面的映射关系.md", "6.7 离散时间傅里叶变换DTFT.md",
      "6.8 离散系统系统函数.md", "6.9 离散系统频率响应.md",
      "6.10 数字滤波器.md"]),
    # Chapter 07 - needs reorder
    ("07-离散时间系统时域分析", "07-离散时间系统时域分析.md",
     ["7.1 单位样值响应.md", "7.2 卷积和.md", "7.3 差分方程的经典求解.md",
      "7.4 常用典型序列.md", "7.5 离散信号的运算.md", "7.6 离散时间信号与序列.md",
      "7.7 离散时间系统与差分方程.md", "7.8 零输入零状态响应离散.md"],
     ["7.1 离散时间信号与序列.md", "7.2 常用典型序列.md",
      "7.3 离散信号的运算.md", "7.4 离散时间系统与差分方程.md",
      "7.5 差分方程的经典求解.md", "7.6 零输入零状态响应离散.md",
      "7.7 单位样值响应.md", "7.8 卷积和.md"]),
    # Chapter 08 - keep as-is (already correct)
    ("08-FFT与DFT", "08-FFT与DFT.md", None, None),
    # Chapter 09 - keep as-is
    ("09-系统状态变量分析", "09-系统状态变量分析.md", None, None),
]


def extract_topic(filename):
    """Extract topic from a numbered filename like 'X.Y Topic.md' -> 'Topic'"""
    # Remove .md extension
    name = filename[:-3] if filename.endswith('.md') else filename
    # Remove leading 'X.Y ' pattern (digits.digits space)
    m = re.match(r'^\d+\.\d+\s+(.*)', name)
    if m:
        return m.group(1)
    return name


def url_encode_filename(filename):
    """URL-encode a filename for markdown links: spaces->%20, Chinese chars->encoded"""
    # Encode each path component separately so / stays intact
    parts = filename.split('/')
    encoded = []
    for p in parts:
        # Quote everything except safe chars; safe='' means encode everything that isn't alphanumeric
        # But we need to keep . for extension and () for filenames that might contain them
        encoded.append(urllib.parse.quote(p, safe='().-'))
    return '/'.join(encoded)


def old_to_new_url(old_filename, new_filename):
    """Convert a filename in a markdown link: old syntax -> new syntax.

    Returns both the new display text and the new URL-encoded filename.

    For within-chapter prev/next links like:
      [2.5 线性系统时域模拟](2.5%20%E7%BA%BF%E6%80%A7%E7%B3%BB%E7%BB%9F%E6%97%B6%E5%9F%9F%E6%A8%A1%E6%8B%9F.md)

    The display text was "2.5 线性系统时域模拟" and the URL was "2.5%20... .md"
    After rename, both need updating.
    """
    # The new display text should be "X.Y Topic" where X.Y is the new number
    new_display = new_filename[:-3]  # Remove .md
    new_url = url_encode_filename(new_filename)
    return new_display, new_url


# ============================================================
# STEP 1: Build all mappings
# ============================================================
print("=" * 60)
print("STEP 1: Building filename mappings...")
print("=" * 60)

# old_to_new[(dir, old_filename)] = new_filename
old_to_new = {}
# topic_to_new[(dir, topic_name)] = new_filename (for cross-chapter refs)
topic_to_new = {}
# Also collect old numbered filenames per dir for pattern matching
old_filenames_per_dir = {}
new_filenames_per_dir = {}

for ch in chapters:
    ch_dir, hub_file, old_order, new_order = ch
    ch_path = os.path.join(BASE, ch_dir)

    if old_order is not None and new_order is not None:
        # Needs reorder
        for old_fn, new_fn in zip(old_order, new_order):
            old_to_new[(ch_dir, old_fn)] = new_fn
            topic = extract_topic(new_fn)
            topic_to_new[(ch_dir, topic)] = new_fn
        old_filenames_per_dir[ch_dir] = set(old_order)
    else:
        # Keep as-is - still register current filenames for topic lookups
        current_files = [f for f in os.listdir(ch_path) if f.endswith('.md') and f != hub_file]
        old_filenames_per_dir[ch_dir] = set(current_files)
        for fn in current_files:
            topic = extract_topic(fn)
            topic_to_new[(ch_dir, topic)] = fn

    new_filenames_per_dir[ch_dir] = set()
    if new_order is not None:
        new_filenames_per_dir[ch_dir] = set(new_order)
    else:
        # Keep current files
        current_files = [f for f in os.listdir(ch_path) if f.endswith('.md') and f != hub_file]
        new_filenames_per_dir[ch_dir] = set(current_files)

print(f"  Old->new mappings: {len(old_to_new)}")
print(f"  Topic->new mappings: {len(topic_to_new)}")


# ============================================================
# STEP 2: Rename files
# ============================================================
print()
print("=" * 60)
print("STEP 2: Renaming files...")
print("=" * 60)

for ch in chapters:
    ch_dir, hub_file, old_order, new_order = ch
    if old_order is None or new_order is None:
        print(f"  [{ch_dir}] No rename needed")
        continue

    ch_path = os.path.join(BASE, ch_dir)
    print(f"  [{ch_dir}] Renaming {len(old_order)} files...")

    for old_fn, new_fn in zip(old_order, new_order):
        old_path = os.path.join(ch_path, old_fn)
        new_path = os.path.join(ch_path, new_fn)

        if not os.path.exists(old_path):
            print(f"    WARNING: {old_path} does not exist, skipping")
            continue
        if os.path.exists(new_path) and old_fn != new_fn:
            print(f"    WARNING: {new_path} already exists, skipping")
            continue

        os.rename(old_path, new_path)
        print(f"    {old_fn} -> {new_fn}")


# ============================================================
# STEP 3: Update links in ALL markdown files
# ============================================================
print()
print("=" * 60)
print("STEP 3: Updating links in all markdown files...")
print("=" * 60)

# Collect all markdown files to process
all_md_files = []

# Main root file
root_file = os.path.join(BASE, "Signals and System.md")
if os.path.exists(root_file):
    all_md_files.append(("", "Signals and System.md"))  # (dir, filename) - root

# Files in chapter directories
for ch in chapters:
    ch_dir, hub_file, _, _ = ch
    ch_path = os.path.join(BASE, ch_dir)
    if not os.path.isdir(ch_path):
        continue
    for f in sorted(os.listdir(ch_path)):
        if f.endswith('.md'):
            all_md_files.append((ch_dir, f))

# Files in notes directory
notes_dir = os.path.join(BASE, "notes")
if os.path.isdir(notes_dir):
    for f in sorted(os.listdir(notes_dir)):
        if f.endswith('.md'):
            all_md_files.append(("notes", f))


def replace_links_in_content(content, current_dir):
    """Replace all old filenames with new filenames in the content.

    Patterns to handle:
    1. Hub wiki-links: [[chapter-dir/X.Y Topic|Topic]]
    2. Prev/next (within-chapter): [X.Y Topic](X.Y%20Topic.md)
    3. Cross-chapter markdown links: [Topic](chapter-dir/Topic.md)
    4. Cross-chapter wiki-links: [[chapter-dir/Topic|Name]]
    """

    def update_wiki_link(match):
        """Update [[dir/filename|display]] pattern"""
        full = match.group(0)
        dir_name = match.group(1)
        filename = match.group(2)
        display = match.group(3)

        # Check if this filename has a topic-only name (no X.Y prefix) in a cross-chapter ref
        if (dir_name, filename) in old_to_new:
            new_fn = old_to_new[(dir_name, filename)]
            if new_fn != filename:
                return f'[[{dir_name}/{new_fn}|{display}]]'

        # Check if it's a topic-only reference (cross-chapter wiki-link)
        topic = extract_topic(filename)
        if filename == topic:  # No number prefix, so it's topic-only
            if (dir_name, topic) in topic_to_new:
                new_fn = topic_to_new[(dir_name, topic)]
                if new_fn != filename:
                    return f'[[{dir_name}/{new_fn}|{display}]]'

        return full

    def update_markdown_link(match):
        """Update [text](path) pattern for cross-chapter refs with topic-only names.
        Only handles links that reference other chapters (cross-chapter)."""
        full = match.group(0)
        text = match.group(1)
        path = match.group(2)

        # Only process if path doesn't contain %20 and looks like a cross-chapter ref
        # Format: chapter-dir/filename.md
        if '/' not in path:
            return full  # Within-chapter link, handled separately

        parts = path.split('/')
        if len(parts) != 2:
            return full

        dir_part = parts[0]
        fn_part = parts[1]

        # Remove .md for comparison
        fn_without_ext = fn_part[:-3] if fn_part.endswith('.md') else fn_part

        # Decode URL encoding if present
        try:
            fn_decoded = urllib.parse.unquote(fn_without_ext)
        except:
            fn_decoded = fn_without_ext

        # Check if this matches a topic name
        if (dir_part, fn_decoded) in topic_to_new:
            new_fn = topic_to_new[(dir_part, fn_decoded)]
            if new_fn != fn_decoded:
                # URL-encode the new filename for the markdown link
                new_url = url_encode_filename(f'{dir_part}/{new_fn}')
                return f'[{text}]({new_url})'

        return full

    def update_prev_next_link(match):
        """Update prev/next markdown links within same chapter.
        Pattern: [X.Y Topic](X.Y%20Topic.md) where the link is to a file in the same dir."""
        full = match.group(0)
        text = match.group(1)  # X.Y Topic
        url = match.group(2)   # X.Y%20Topic.md

        # Decode URL to get the actual filename
        decoded_url = urllib.parse.unquote(url)

        # Check against all old filenames across all dirs
        for (ch_dir, old_fn), new_fn in old_to_new.items():
            if decoded_url == old_fn or decoded_url == old_fn.replace(' ', '%20'):
                # This link needs updating
                new_text = new_fn[:-3]  # Remove .md
                new_url = url_encode_filename(new_fn)
                return f'[{new_text}]({new_url})'

        return full

    # Process hub wiki-links: [[dir/filename|display]]
    content = re.sub(
        r'\[\[(\d{2}-[^/]+)/([^|]+)\|([^\]]+)\]\]',
        update_wiki_link,
        content
    )

    # Process cross-chapter markdown links: [text](dir/filename.md)
    content = re.sub(
        r'\[([^\]]+)\]\((\d{2}-[^/]+/[^)]+\.md)\)',
        update_markdown_link,
        content
    )

    # Process prev/next links within same chapter
    # Pattern: [X.Y Topic](X.Y%20Topic.md) at the bottom of atomic notes
    content = re.sub(
        r'\[(\d+\.\d+\s+[^\]]+)\]\(([^)]+\.md)\)',
        update_prev_next_link,
        content
    )

    # Also handle wiki-links that might not have been caught by the previous hub pattern
    # e.g., [[dir/Topic]] (without display text) - less likely but handle it
    # [[dir/Topic]] - wiki-link without display text
    def update_wiki_link_simple(match):
        full = match.group(0)
        dir_name = match.group(1)
        filename = match.group(2)

        # Check old_to_new
        if (dir_name, filename) in old_to_new:
            return f'[[{dir_name}/{old_to_new[(dir_name, filename)]}]]'

        # Check topic_to_new
        topic = extract_topic(filename)
        if filename == topic and (dir_name, topic) in topic_to_new:
            return f'[[{dir_name}/{topic_to_new[(dir_name, topic)]}]]'

        return full

    content = re.sub(
        r'\[\[(\d{2}-[^/]+)/([^|\]]+)\]\]',
        update_wiki_link_simple,
        content
    )

    return content


# Process each file
files_updated = 0
total_changes = 0

for ch_dir, filename in all_md_files:
    filepath = os.path.join(BASE, ch_dir, filename) if ch_dir else os.path.join(BASE, filename)

    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pass current_dir to help determine link types
    content = replace_links_in_content(content, ch_dir)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        files_updated += 1
        print(f"  UPDATED: {ch_dir}/{filename}" if ch_dir else f"  UPDATED: {filename}")

print(f"\nTotal files updated: {files_updated}")

# ============================================================
# VERIFICATION
# ============================================================
print()
print("=" * 60)
print("VERIFICATION: Checking renamed files...")
print("=" * 60)

for ch in chapters:
    ch_dir, hub_file, _, new_order in ch
    ch_path = os.path.join(BASE, ch_dir)

    if new_order is not None:
        # Check new files exist
        all_ok = True
        for fn in new_order:
            fp = os.path.join(ch_path, fn)
            if not os.path.exists(fp):
                print(f"  MISSING: {ch_dir}/{fn}")
                all_ok = False
        if all_ok:
            print(f"  [{ch_dir}] All files present OK")
    else:
        print(f"  [{ch_dir}] No changes (kept as-is)")

# Check for any old files that might still exist (sanity check)
print()
print("Sanity check for orphaned old filenames...")
for ch in chapters:
    ch_dir, hub_file, old_order, _ = ch
    if old_order is None:
        continue
    ch_path = os.path.join(BASE, ch_dir)
    for fn in old_order:
        if os.path.exists(os.path.join(ch_path, fn)):
            print(f"  WARNING: Old file still exists: {ch_dir}/{fn}")

# Check cross-chapter link updates
print()
print("Cross-chapter reference check (sampling files)...")
sample_cross_refs = [
    ("02-连续时间系统时域分析", "2.8 零输入零状态响应.md", "零输入零状态响应离散", "07-离散时间系统时域分析"),
    ("07-离散时间系统时域分析", "7.8 零输入零状态响应离散.md", "零输入零状态响应", "02-连续时间系统时域分析"),
    ("02-连续时间系统时域分析", "2.6 经典微分方程求解.md", "差分方程的经典求解", "07-离散时间系统时域分析"),
    ("01-基本概念", "1.1 信号分类.md", "离散时间信号与序列", "07-离散时间系统时域分析"),
    ("03-傅里叶变换", "3.9 抽样定理.md", "抽样信号恢复", "05-频域分析"),
    ("04-拉普拉斯变换", "4.3 拉普拉斯变换收敛域.md", "z变换定义与收敛域", "06-Z变换"),
]

for ch_dir, filename, topic, target_dir in sample_cross_refs:
    filepath = os.path.join(BASE, ch_dir, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        c = f.read()

    # Check if the link now contains the numbered filename
    if (target_dir, topic) in topic_to_new:
        expected_fn = topic_to_new[(target_dir, topic)]
        # Check for the numbered filename in the content
        if expected_fn in c:
            print(f"  OK: {ch_dir}/{filename} -> ref to {target_dir}/{expected_fn}")
        else:
            # Check if topic name still appears as a bare file reference (without number)
            pattern_bare = f'({target_dir}/{topic}.md)'
            pattern_wiki = f'[[{target_dir}/{topic}|'
            pattern_bare_enc = f'({target_dir}/{urllib.parse.quote(topic, safe="")}.md)'

            if pattern_bare in c or pattern_wiki in c or pattern_bare_enc in c:
                print(f"  STILL_BARE: {ch_dir}/{filename} -> ref to {target_dir}/{topic} (expected {expected_fn})")
            else:
                print(f"  NOT_FOUND: {ch_dir}/{filename} -> looking for {target_dir}/{expected_fn}")

# Quick verification of hub files
print()
print("Hub file verification...")
for ch in chapters:
    ch_dir, hub_file, _, new_order in ch
    hub_path = os.path.join(BASE, ch_dir, hub_file)
    if not os.path.exists(hub_path):
        print(f"  MISSING HUB: {hub_path}")
        continue
    with open(hub_path, 'r', encoding='utf-8') as f:
        c = f.read()

    files_to_check = new_order if new_order else old_filenames_per_dir.get(ch_dir, set())
    missing = []
    for fn in sorted(files_to_check):
        if fn not in c:
            missing.append(fn)
    if missing:
        print(f"  HUB [{ch_dir}]: Missing links for: {missing}")
    else:
        print(f"  HUB [{ch_dir}]: All links correct ({len(files_to_check)} entries)")

print()
print("=" * 60)
print("DONE! Script completed successfully.")
print("=" * 60)
