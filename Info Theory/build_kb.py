#!/usr/bin/env python3
"""Build Knowledge Base for Info Theory from note files."""

import os
import re
import shutil

BASE_DIR = r"D:\DOC\Notes\Info Theory"
NOTES_DIR = os.path.join(BASE_DIR, "notes")
IMAGES_DIR = os.path.join(NOTES_DIR, "images")
OUTPUT_IMAGES_DIR = os.path.join(BASE_DIR, "images")

# ============================================================
# STRUCTURE DEFINITION
# ============================================================
# Each chapter: {
#   "num": str (chapter number),
#   "dir": str (directory name),
#   "title": str (display title),
#   "file": str (note filename),
#   "kps": [{"id": str (e.g. "1.1"), "name": str}, ...],
#   "categories": [str] (optional category names for reference),
# }

CHAPTERS = [
    {
        "num": "01", "dir": "01-信息度量", "title": "信息度量",
        "file": "1.信息度量.md", "abbrev": "度量",
        "kps": [
            {"id": "1.1", "name": "自信息量"},
            {"id": "1.2", "name": "联合自信息量"},
            {"id": "1.3", "name": "条件自信息量"},
            {"id": "1.4", "name": "互信息量"},
            {"id": "1.5", "name": "信息熵（平均自信息量）"},
            {"id": "1.6", "name": "联合熵（平均联合自信息量）"},
            {"id": "1.7", "name": "条件熵（平均条件自信息量）"},
            {"id": "1.8", "name": "互信息（平均互信息量）"},
            {"id": "1.9", "name": "相对熵（KL散度）"},
            {"id": "1.10", "name": "交叉熵"},
        ],
    },
    {
        "num": "02", "dir": "02-相关数学", "title": "相关数学",
        "file": "2.相关数学.md", "abbrev": "数学",
        "kps": [
            {"id": "2.1", "name": "函数凹凸性"},
            {"id": "2.2", "name": "Jensen不等式"},
            {"id": "2.3", "name": "log-sum不等式"},
            {"id": "2.4", "name": "KL散度凹凸性（凸）"},
            {"id": "2.5", "name": "熵的凹凸性（凹）"},
            {"id": "2.6", "name": "互信息的凹凸性"},
        ],
    },
    {
        "num": "03", "dir": "03-离散信源", "title": "离散信源",
        "file": "3.离散信源.md", "abbrev": "信源",
        "kps": [
            {"id": "3.1", "name": "信源"},
            {"id": "3.2", "name": "概念"},
            {"id": "3.3", "name": "压缩方式"},
            {"id": "3.4", "name": "概念"},
            {"id": "3.5", "name": "平稳马尔可夫信源"},
        ],
    },
    {
        "num": "04", "dir": "04-编码", "title": "编码",
        "file": "4.编码.md", "abbrev": "编码",
        "kps": [
            {"id": "4.1", "name": "定长编码"},
            {"id": "4.2", "name": "D进制编码"},
            {"id": "4.3", "name": "二分分布"},
            {"id": "4.4", "name": "Kraft-McMillan不等式"},
            {"id": "4.5", "name": "编码长度"},
        ],
    },
    {
        "num": "05", "dir": "05-数据处理", "title": "数据处理",
        "file": "5.数据处理.md", "abbrev": "数据",
        "kps": [
            {"id": "5.1", "name": "马尔可夫过程"},
            {"id": "5.2", "name": "数据处理不等式（DPI）"},
            {"id": "5.3", "name": "充分统计量"},
            {"id": "5.4", "name": "Fano不等式"},
        ],
    },
    {
        "num": "06", "dir": "06-通信系统", "title": "通信系统",
        "file": "6.通信系统.md", "abbrev": "通信",
        "kps": [
            {"id": "6.1", "name": "概述"},
            {"id": "6.2", "name": "理论模型"},
            {"id": "6.3", "name": "噪声信道编码定理"},
            {"id": "6.4", "name": "信道容量"},
            {"id": "6.5", "name": "联合典型集"},
            {"id": "6.6", "name": "噪声信道编码定理证明"},
        ],
    },
    {
        "num": "07", "dir": "07-连续分布", "title": "连续分布",
        "file": "7.连续分布.md", "abbrev": "连续",
        "kps": [
            {"id": "7.1", "name": "量化"},
            {"id": "7.2", "name": "高斯分布"},
            {"id": "7.3", "name": "高斯信道"},
            {"id": "7.4", "name": "并行高斯信道"},
        ],
    },
    {
        "num": "08", "dir": "08-零空间及汉明码", "title": "零空间及汉明码",
        "file": "8.零空间.md", "abbrev": "零空间",
        "kps": [
            {"id": "8.1", "name": "GF(2)域零空间"},
            {"id": "8.2", "name": "编码方式"},
            {"id": "8.3", "name": "汉明码"},
        ],
    },
    {
        "num": "09", "dir": "09-率失真", "title": "率失真",
        "file": "9.率失真.md", "abbrev": "率失真",
        "kps": [
            {"id": "9.1", "name": "率失真函数"},
            {"id": "9.2", "name": "证明"},
        ],
    },
    {
        "num": "10", "dir": "10-分离编码", "title": "分离编码",
        "file": "10.分离编码.md", "abbrev": "分离",
        "kps": [
            {"id": "10.1", "name": "分离编码"},
            {"id": "10.2", "name": "联合编码"},
        ],
    },
]


def read_file(filepath):
    """Read a file and return its lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def find_headings(lines):
    """Find all heading positions in lines.
    Returns list of (line_index, level, title_text).
    """
    headings = []
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n').rstrip('\r')
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((i, level, title))
    return headings


def extract_content(lines, start_line, end_line):
    """Extract content between start_line and end_line."""
    return ''.join(lines[start_line:end_line]).strip()


def extract_kp_content(filepath, kp_list):
    """
    Extract content for each knowledge point from the note file.

    Rules:
    - First # heading is file title
    - # headings after file title are categories (or knowledge points if no ## children)
    - ## headings are knowledge points
    - Text under # category before first ## goes to first ## of that category
    - ### subsections remain with their parent ##

    Returns: list of (kp_id, content_string)
    """
    lines = read_file(filepath)
    headings = find_headings(lines)

    if not headings:
        return []

    # First heading is file title
    file_title = headings[0][2]
    remaining_headings = headings[1:]

    if not remaining_headings:
        return []

    # Build a structure: for each heading after file title, determine if it's
    # a category or a knowledge point
    structured_kps = []  # list of {"heading_idx": int, "type": "kp"|"cat", ...}

    # We need to process remaining_headings to figure out the hierarchy.
    # Since all knowledge points are defined by either # (no ## children) or ##,
    # we can process sequentially.

    idx = 0
    while idx < len(remaining_headings):
        line_num, level, title = remaining_headings[idx]

        if level == 2:
            # Direct knowledge point (##)
            structured_kps.append({
                "type": "kp",
                "level": 2,
                "title": title,
                "line_num": line_num,
                "heading_idx": idx,
                "extra_start": None,  # category overview start line (if applicable)
            })
            idx += 1

        elif level == 1:
            # Could be category (has ## children) or standalone knowledge point
            has_children = False
            j = idx + 1
            while j < len(remaining_headings):
                if remaining_headings[j][1] == 1:
                    break
                if remaining_headings[j][1] == 2:
                    has_children = True
                    break
                j += 1

            if has_children:
                # This is a category. Its ## children are knowledge points.
                j = idx + 1
                first_child = True
                while j < len(remaining_headings):
                    if remaining_headings[j][1] == 1:
                        break
                    if remaining_headings[j][1] == 2:
                        child_line, _, child_title = remaining_headings[j]
                        extra_start = line_num + 1 if first_child else None
                        structured_kps.append({
                            "type": "kp",
                            "level": 2,
                            "title": child_title,
                            "line_num": child_line,
                            "heading_idx": j,
                            "extra_start": extra_start,
                        })
                        first_child = False
                    j += 1
                idx = j
            else:
                # No ## children: this # is itself a knowledge point
                structured_kps.append({
                    "type": "kp",
                    "level": 1,
                    "title": title,
                    "line_num": line_num,
                    "heading_idx": idx,
                    "extra_start": None,
                })
                idx += 1
        else:
            # Level 3+ (###, ####, ...): sub-sections within a KP, skip
            idx += 1

    # Check for file title intro content (content between file title and first heading)
    if structured_kps:
        first_kp_line = structured_kps[0]["line_num"]
        if first_kp_line > 1:
            ft_intro = extract_content(lines, 1, first_kp_line)
            if ft_intro:
                # Check if first expected KP matches file title
                if kp_list and kp_list[0]["name"] == file_title:
                    # File title is itself a KP — it takes the intro content AND
                    # the content of the first structured KP (since that's actually
                    # the second KP in the file). We'll handle this by creating
                    # a synthetic entry.
                    pass  # handled below
                else:
                    # File title intro goes as extra content to the first structured KP
                    structured_kps[0]["file_title_extra"] = ft_intro

    # Now extract content for each knowledge point
    results = []
    for i, kp_info in enumerate(structured_kps):
        start_line = kp_info["line_num"]

        # end: next heading at level <= current KP level (stops at ## or # category boundaries)
        # or next structured KP heading, whichever comes first (ensuring we dont bleed into next category)
        kp_level = kp_info["level"]
        end_line = len(lines)
        current_heading_idx = kp_info["heading_idx"]
        # Look in remaining_headings for the next heading at level <= kp_level
        for j in range(current_heading_idx + 1, len(remaining_headings)):
            next_level = remaining_headings[j][1]
            if next_level <= kp_level:
                end_line = remaining_headings[j][0]
                break
        # Also cap at next structured KP's line (safety)
        if i + 1 < len(structured_kps):
            next_kp_line = structured_kps[i + 1]["line_num"]
            if next_kp_line < end_line:
                end_line = next_kp_line

        # Extract content
        content = extract_content(lines, start_line, end_line)

        # If there's extra content from category overview, prepend it
        if kp_info.get("extra_start") is not None:
            extra_end = kp_info["line_num"]
            extra = extract_content(lines, kp_info["extra_start"], extra_end)
            if extra:
                content = extra + '\n\n' + content

        # If there's file title extra (and no category overview extra to avoid duplication), prepend it
        if kp_info.get("file_title_extra") is not None and kp_info.get("extra_start") is None:
            content = kp_info["file_title_extra"] + '\n\n' + content

        results.append({
            "title": kp_info["title"],
            "content": content,
        })

    # Handle the case where file title == first expected KP name.
    # The file title's content (before the first heading) becomes its own KP.
    if kp_list and kp_list[0]["name"] == file_title and remaining_headings:
        ft_line = headings[0][0]  # line 0
        first_kp_line = structured_kps[0]["line_num"] if structured_kps else len(lines)
        ft_content = extract_content(lines, ft_line + 1, first_kp_line)

        if ft_content:
            # Insert the file title KP at position 0
            results.insert(0, {
                "title": file_title,
                "content": ft_content,
            })

    return results


def process_images(content, kp_id, img_counter):
    """Replace image references in content and return updated content + image mapping.

    Original: ![1779351122902](images/1.信息度量/1779351122902.png)
    New: ![[Info Theory/images/1.1_001.png]]

    Returns: (updated_content, image_mapping_list)
    """
    pattern = r'!\[(\d+)\]\(images/([^/]+)/(\d+)\.png\)'

    def replacer(match):
        nonlocal img_counter
        img_counter[0] += 1
        seq = img_counter[0]
        orig_dir = match.group(2)
        orig_file = match.group(3)
        new_name = f"{kp_id}_{seq:03d}.png"

        # Store mapping
        mapping_info = {
            "orig_dir": orig_dir,
            "orig_file": f"{orig_file}.png",
            "new_name": new_name,
        }
        mappings.append(mapping_info)

        return f"![[Info Theory/images/{new_name}]]"

    mappings = []
    img_counter[0] = 0  # Reset counter for this knowledge point
    updated_content = re.sub(pattern, replacer, content)

    return updated_content, mappings


def process_images_in_content(content, kp_id):
    """Process images in content, return updated content and list of (orig_path, dest_filename)."""
    pattern = r'!\[(\d+)\]\(images/([^/]+)/(\d+)\.png\)'

    mappings = []  # (orig_dir, orig_filename, new_filename)
    img_counter = [0]

    def replacer(m):
        img_counter[0] += 1
        seq = img_counter[0]
        orig_dir = m.group(2)
        orig_file = f"{m.group(3)}.png"
        new_name = f"{kp_id}_{seq:03d}.png"
        mappings.append((orig_dir, orig_file, new_name))
        return f"![[Info Theory/images/{new_name}]]"

    updated = re.sub(pattern, replacer, content)
    return updated, mappings


def all_kps_flat():
    """Return flat list of all KPs with their chapter info."""
    result = []
    for ch in CHAPTERS:
        for kp in ch["kps"]:
            result.append({**kp, "ch": ch})
    return result


def get_kp_prev_next(kp_id):
    """Get previous and next knowledge point info."""
    all_kps = all_kps_flat()
    for i, kp in enumerate(all_kps):
        if kp["id"] == kp_id:
            prev_kp = all_kps[i - 1] if i > 0 else None
            next_kp = all_kps[i + 1] if i < len(all_kps) - 1 else None
            return prev_kp, next_kp
    return None, None


def make_kp_filename(kp):
    """Create filename for knowledge point file."""
    safe_name = kp["name"].replace('/', '／').replace('\\', '')
    return f"{kp['id']} {safe_name}.md"


def main():
    # Clean and create output images directory
    if os.path.exists(OUTPUT_IMAGES_DIR):
        shutil.rmtree(OUTPUT_IMAGES_DIR)
    os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)

    # Track all image copy operations for summary
    all_image_mappings = []  # (orig_path, dest_path)

    for ch in CHAPTERS:
        ch_dir = os.path.join(BASE_DIR, ch["dir"])
        os.makedirs(ch_dir, exist_ok=True)

        note_path = os.path.join(NOTES_DIR, ch["file"])
        print(f"\n{'='*60}")
        print(f"Processing: {ch['file']} -> {ch['dir']}")

        # Extract knowledge point content from note file
        results = extract_kp_content(note_path, ch["kps"])

        # Debug: print extracted titles
        print(f"  Extracted KPs: {[r['title'] for r in results]}")
        print(f"  Expected KPs: {[kp['name'] for kp in ch['kps']]}")

        # Map results to our knowledge point structure by position
        # (title matching is unreliable for duplicate names like "概念")
        for i, kp in enumerate(ch["kps"]):
            if i >= len(results):
                print(f"  WARNING: Could not find content for KP {kp['id']} '{kp['name']}'")
                continue

            matched = results[i]
            expected_title = kp["name"]
            actual_title = matched["title"]
            if expected_title != actual_title:
                # Title mismatch warning only
                print(f"  NOTE: KP {kp['id']}: expected '{expected_title}', got '{actual_title}'")

            content = matched["content"]

            # Process images in the content
            updated_content, img_mappings = process_images_in_content(content, kp["id"])

            # Copy images
            for orig_dir, orig_file, new_name in img_mappings:
                src = os.path.join(IMAGES_DIR, orig_dir, orig_file)
                dst = os.path.join(OUTPUT_IMAGES_DIR, new_name)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    all_image_mappings.append((src, dst))
                else:
                    print(f"  WARNING: Image not found: {src}")

            # Get prev/next KPs
            prev_kp, next_kp = get_kp_prev_next(kp["id"])

            # Build frontmatter tags
            ch_num = ch["num"]
            tags = [f"info-theory", f"it-ch{ch_num}"]

            # Build prev/next links
            prev_link = "无"
            if prev_kp:
                prev_ch_dir = prev_kp["ch"]["dir"]
                prev_fn = make_kp_filename(prev_kp)
                prev_link = f"[[Info Theory/{prev_ch_dir}/{prev_fn}|{prev_kp['id']} {prev_kp['name']}]]"

            next_link = "无"
            if next_kp:
                next_ch_dir = next_kp["ch"]["dir"]
                next_fn = make_kp_filename(next_kp)
                next_link = f"[[Info Theory/{next_ch_dir}/{next_fn}|{next_kp['id']} {next_kp['name']}]]"

            # Build the knowledge point file
            kp_filename = make_kp_filename(kp)
            kp_filepath = os.path.join(ch_dir, kp_filename)

            kp_content = f"""---
tags: [{', '.join(tags)}]
---

# {kp['name']}

{updated_content}

## 链接到

- 上一个知识点：{prev_link}
- 下一个知识点：{next_link}
"""
            with open(kp_filepath, 'w', encoding='utf-8') as f:
                f.write(kp_content.lstrip('\n'))

            print(f"  Created: {kp_filepath}")

        # Create chapter hub file
        hub_path = os.path.join(ch_dir, f"{ch['title']}.md")
        hub_kps = []
        for kp in ch["kps"]:
            fn = make_kp_filename(kp)
            hub_kps.append(f"- [[Info Theory/{ch['dir']}/{fn}|{kp['id']} {kp['name']}]]")

        ch_arabic = str(int(ch['num']))
        hub_content = f"""---
tags: [info-theory, moc, it-ch{ch['num']}]
aliases: [第{ch_arabic}章, {ch['title']}]
---
# 第{ch_arabic}章 {ch['title']}

## 本章知识点

{chr(10).join(hub_kps)}

---

[[../Info Theory|← 返回 Info Theory 总览]]
"""
        with open(hub_path, 'w', encoding='utf-8') as f:
            f.write(hub_content.lstrip('\n'))
        print(f"  Created hub: {hub_path}")

    print(f"\n{'='*60}")
    print(f"Total images copied: {len(all_image_mappings)}")
    print(f"Done! Knowledge base rebuilt.")


if __name__ == "__main__":
    main()
