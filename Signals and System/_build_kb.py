#!/usr/bin/env python3
"""Build the Signals and System knowledge base from notes."""

import os
import re
import shutil

BASE = r"D:\DOC\Notes\Signals and System"
NOTES_DIR = os.path.join(BASE, "notes")
KB_IMAGES_DIR = os.path.join(BASE, "images")
NOTE_IMAGES_DIR = os.path.join(NOTES_DIR, "images")

CHAPTERS = [
    (1, "1.基本概念.md", "基本概念", "01-基本概念", None, None),
    (2, "2.时域分析.md", "连续时间系统时域分析", "02-连续时间系统时域分析", None, None),
    (3, "3.傅里叶变换.md", "傅里叶变换", "03-傅里叶变换", None, None),
    (4, "4.拉普拉斯变换.md", "拉普拉斯变换", "04-拉普拉斯变换", None, None),
    (5, "5.频域分析.md", "频域分析", "05-频域分析", None, None),
    (6, "7.离散时域.md", "Z变换", "06-Z变换", None, None),
    (7, "6.Z变换.md", "离散时间系统时域分析", "07-离散时间系统时域分析", None, None),
    (8, "8.FFT.md", "FFT与DFT", "08-FFT与DFT", None, "# 系统状态变量分析"),
    (9, "8.FFT.md", "系统状态变量分析", "09-系统状态变量分析", "# 系统状态变量分析", None),
]


def sanitize(title):
    return title.replace('/', '或').replace('\\', '或').replace(':', '：').replace('*', '×').replace('?', '？').replace('"', "'").replace('<', '＜').replace('>', '＞').replace('|', '—').strip()


def read_file_section(filepath, split_start=None, split_end=None):
    """Read lines from a note file for a specific chapter section."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    result = []
    active = split_start is None
    for line in lines:
        s = line.strip()
        if split_end and s == split_end:
            break
        if split_start and s == split_start:
            active = True
            continue
        if active:
            result.append(line)
    return result


def is_h1(s):
    """True if s is a level-1 heading (not ##)."""
    return s.startswith('# ') and not s.startswith('## ')


def is_h2(s):
    """True if s is a level-2 heading (not ###)."""
    return s.startswith('## ') and not s.startswith('### ')


def parse_kps(lines, ch_num, ch_name):
    """
    Split note lines into knowledge points.

    Steps:
    1. Skip the first line if it's the chapter title (#).
    2. Divide remaining lines into sections at every # heading.
    3. Within each section, if there are ## headings, split further:
       - Content before the first ## -> KP with section title
       - Each ## subsection -> individual KP
    4. Sections without ## headings -> single KP.
    """
    kps = []
    counter = 0

    # Skip chapter title
    if lines and is_h1(lines[0].strip()):
        lines = lines[1:]

    # --- Divide into sections at # headings ---
    sections = []          # [(title_str, [content_lines])]
    cur_sec_title = None
    cur_sec_lines = []

    for line in lines:
        stripped = line.strip()
        if is_h1(stripped):
            if cur_sec_title is not None:
                sections.append((cur_sec_title, cur_sec_lines))
            elif cur_sec_lines:
                # Lines before the very first # heading -> overview section
                sections.append((ch_name, cur_sec_lines))
            cur_sec_title = stripped[2:].strip()
            cur_sec_lines = []
        else:
            cur_sec_lines.append(line)

    # Flush last section
    if cur_sec_lines:
        sections.append((cur_sec_title or ch_name, cur_sec_lines))

    # --- Process each section ---
    def add_kp(title, content_lines):
        nonlocal counter
        counter += 1
        kps.append({
            "id": f"{ch_num}.{counter}",
            "title": title,
            "safe_title": sanitize(title),
            "lines": [f"# {title}\n"] + content_lines,
        })

    for sec_title, sec_lines in sections:
        has_sub = any(is_h2(l.strip()) for l in sec_lines)

        if not has_sub:
            add_kp(sec_title, sec_lines)
            continue

        # Split at ## headings
        preamble = []
        subs = []          # [(sub_title, [sub_lines])]
        cur_sub = None

        for line in sec_lines:
            stripped = line.strip()
            if is_h2(stripped):
                if cur_sub is not None:
                    subs.append(cur_sub)
                cur_sub = [stripped[3:].strip(), []]
            elif cur_sub is not None:
                cur_sub[1].append(line)
            else:
                preamble.append(line)

        if cur_sub is not None:
            subs.append(cur_sub)

        # Preamble KP (content before first ##)
        if preamble and any(l.strip() for l in preamble):
            add_kp(sec_title, preamble)

        # Subsection KPs
        for sub_title, sub_lines in subs:
            add_kp(sub_title, sub_lines)

    return kps


def process_images(kps, ch_num):
    """Replace image references and copy source images."""
    pat = re.compile(r'!\[(.*?)\]\(images/(\d+)/(.+?)\)')
    ok = True
    for kp in kps:
        seq = 0
        for j, line in enumerate(kp["lines"]):
            m = pat.match(line.rstrip())
            if m:
                src_ch = m.group(2)
                src_name = m.group(3)
                seq += 1
                kp_seq = kp["id"].split('.')[1]
                new_name = f"{ch_num}.{kp_seq}_{seq:03d}.png"
                kp["lines"][j] = f"![[Signals and System/images/{new_name}]]\n"

                src_path = os.path.join(NOTE_IMAGES_DIR, src_ch, src_name)
                dst_path = os.path.join(KB_IMAGES_DIR, new_name)
                if os.path.exists(src_path):
                    if not os.path.exists(dst_path):
                        shutil.copy2(src_path, dst_path)
                else:
                    print(f"    WARNING: Image not found: {src_path}")
                    ok = False
    return ok


def process_chapter(ch_num, ch_name, note_file, dir_name, split_start, split_end):
    note_path = os.path.join(NOTES_DIR, note_file)
    target_dir = os.path.join(BASE, dir_name)

    print(f"\n{'='*60}")
    print(f"Chapter {ch_num}: {ch_name}  <-- {note_file}")

    lines = read_file_section(note_path, split_start, split_end)
    if not lines:
        print("  No content.")
        return []

    kps = parse_kps(lines, ch_num, ch_name)
    if not kps:
        print("  No KPs.")
        return []

    os.makedirs(KB_IMAGES_DIR, exist_ok=True)
    process_images(kps, ch_num)

    os.makedirs(target_dir, exist_ok=True)

    for i, kp in enumerate(kps):
        if i > 0:
            p = kps[i-1]
            prev_link = f"[[{p['id']} {p['safe_title']}.md|{p['title']}]]"
        else:
            prev_link = "无（本章第一个知识点）"

        if i < len(kps)-1:
            n = kps[i+1]
            nxt_link = f"[[{n['id']} {n['safe_title']}.md|{n['title']}]]"
        else:
            nxt_link = "无（本章最后一个知识点）"

        fname = f"{kp['id']} {kp['safe_title']}.md"
        fpath = os.path.join(target_dir, fname)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(f"tags: [ss, ss-ch{ch_num}, {ch_name}]\n")
            f.write("---\n\n")
            f.writelines(kp["lines"])
            f.write("\n---\n\n")
            f.write("## 链接到\n\n")
            f.write(f"- 上一个知识点：{prev_link}\n")
            f.write(f"- 下一个知识点：{nxt_link}\n")

        print(f"  [{kp['id']}] {fname}")

    # Hub
    hub_name = f"{sanitize(ch_name)}.md"
    hub_path = os.path.join(target_dir, hub_name)
    with open(hub_path, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write(f"tags: [ss, moc, ss-ch{ch_num}]\n")
        f.write(f"aliases: [第{ch_num}章, {ch_name}]\n")
        f.write("---\n")
        f.write(f"# 第{ch_num}章 {ch_name}\n\n## 本章知识点\n\n")
        for kp in kps:
            f.write(f"- [[{kp['id']} {kp['safe_title']}.md|{kp['title']}]]\n")
        f.write("\n---\n\n[[../Signals and System|← 返回 Signals and System 总览]]\n")
    print(f"  Hub: {hub_name}  ({len(kps)} KPs)")
    return kps


def main():
    # Clear images
    if os.path.exists(KB_IMAGES_DIR):
        for f in os.listdir(KB_IMAGES_DIR):
            p = os.path.join(KB_IMAGES_DIR, f)
            if os.path.isfile(p) and f.lower().endswith('.png'):
                os.remove(p)
    os.makedirs(KB_IMAGES_DIR, exist_ok=True)
    print("Images cleared.")

    # Clear old KB files
    for ch_num in range(1, 10):
        d = {c[0]: c for c in CHAPTERS}[ch_num][3]
        dpath = os.path.join(BASE, d)
        if os.path.exists(dpath):
            cnt = 0
            for f in os.listdir(dpath):
                p = os.path.join(dpath, f)
                if os.path.isfile(p) and f.endswith('.md'):
                    os.remove(p)
                    cnt += 1
            if cnt:
                print(f"Cleared {cnt} from {d}/")

    total = 0
    for cfg in CHAPTERS:
        ch_num, note_file, ch_name, dir_name, split_start, split_end = cfg
        kps = process_chapter(ch_num, ch_name, note_file, dir_name, split_start, split_end)
        total += len(kps)

    ic = len([f for f in os.listdir(KB_IMAGES_DIR) if f.endswith('.png')])
    print(f"\n{'='*60}")
    print(f"Done! {total} KPs, {ic} images.")


if __name__ == "__main__":
    main()
