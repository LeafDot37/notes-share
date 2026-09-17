#!/usr/bin/env python3
"""Build NLP knowledge base in Notes/NLP from the raw notes (verbatim split).

Mirrors the build method used by other subjects in this vault:
  - Raw long notes stay in <subject>/notes/ (untouched; images referenced with
    markdown-relative `images/<dir>/<file>.png`)
  - Every top-level `# ` heading of the raw notes becomes one chapter folder
  - Every `## ` heading becomes one atomic note (`###` sub-sections stay nested)
  - Body text is copied VERBATIM; the only rewrite is re-pointing images to the
    vault-absolute embed `![[NLP/images/<dir>/<file>.png]]` and copying the png
    under <subject>/images/ (same as Info Theory / Machine Learning notes).
  - Chapter hub files and the subject hub NLP.md are generated for navigation.

Usage:  python build_nlp.py
Input:  notes/*.md and notes/images/**.png   (raw copies, kept as backup)
Output: NN-<章节>/X.Y <知识点>.md, chapter hubs, NLP/images/, NLP.md
"""

import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # Notes/NLP
NOTES_DIR = os.path.join(BASE_DIR, "notes")               # raw notes + their images
SRC_IMAGES_DIR = os.path.join(NOTES_DIR, "images")        # notes/images/<dir>/<file>.png
OUT_IMAGES_DIR = os.path.join(BASE_DIR, "images")         # subject-level copy used by embeds

SUBJECT = "NLP"
SUBJECT_TAG = "nlp"
IMG_RE = re.compile(r'!\[([^\]]*)\]\(images/([^)]+)\)')

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def heading_map(lines):
    """[(line_index, level, title)] for every ATX heading."""
    out = []
    for i, line in enumerate(lines):
        m = re.match(r'^(#{1,6})\s+(.*)$', line.rstrip("\r\n"))
        if m:
            out.append((i, len(m.group(1)), m.group(2).strip()))
    return out


def join_lines(lines):
    return "".join(lines).strip("\n")


def safe_name(name):
    """Filesystem-safe fragment (display text preserved as far as possible)."""
    return (name.replace("/", "／").replace("\\", "")
                .replace(":", "：").replace("|", "｜")
                .replace("*", "＊").replace("?", "？").replace('"', "＂")
                .replace("<", "＜").replace(">", "＞"))


def rel_vault(p):
    """Repo-root-relative posix path for a file under BASE_DIR, no .md suffix
    (matches the current wiki-link convention used across this vault)."""
    r = os.path.relpath(p, BASE_DIR).replace("\\", "/")
    return r[:-3] if r.endswith(".md") else r


def embed_images(text):
    return IMG_RE.sub(lambda m: f"![[{SUBJECT}/images/{m.group(2)}]]", text)


# ---------------------------------------------------------------------------
# 1. parse raw notes -> chapters (per `#`) -> knowledge points (per `##`)
# ---------------------------------------------------------------------------
chapters = []            # {num, title, dirname, kps:[{id,name,body}], hubpath}
all_notes = []           # flat reading order: {id,name,path}

for fn in sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".md")):
    lines = read_lines(os.path.join(NOTES_DIR, fn))
    heads = heading_map(lines)
    # chapter boundaries = level-1 headings
    for ci, (p, _lvl, title) in enumerate([h for h in heads if h[1] == 1]):
        h1_list = [h for h in heads if h[1] == 1]
        nxt_h1 = h1_list[ci + 1][0] if ci + 1 < len(h1_list) else len(lines)
        end = nxt_h1
        # `##` headings strictly inside this chapter
        h2s = [h for h in heads if h[1] == 2 and p < h[0] < end]
        if not h2s:      # chapter with no `##`: whole body is one atomic note
            h2s = [(end, 2, title)]
        intro = join_lines(lines[p + 1:h2s[0][0]])

        ch = {"title": title, "kps": [], "h1_lines": (p, end), "intro": intro}
        for qi, (q, _lv, kname) in enumerate(h2s):
            nxt = h2s[qi + 1][0] if qi + 1 < len(h2s) else end
            ch["kps"].append({"name": kname, "raw": lines[q + 1:nxt]})
        chapters.append(ch)

# number chapters / kps
for ci, ch in enumerate(chapters, start=1):
    ch["num"] = ci
    ch["dirname"] = f"{ci:02d}-{safe_name(ch['title'])}"
    ch["hub"] = os.path.join(BASE_DIR, ch["dirname"],
                             f"{safe_name(ch['title'])}.md")
    for ki, kp in enumerate(ch["kps"], start=1):
        kp["id"] = f"{ci}.{ki}"
        kp["path"] = os.path.join(BASE_DIR, ch["dirname"],
                                  f"{kp['id']} {safe_name(kp['name'])}.md")

for ch in chapters:
    for kp in ch["kps"]:
        all_notes.append({"id": kp["id"], "name": kp["name"],
                          "path": kp["path"], "ch_num": ch["num"]})

# ---------------------------------------------------------------------------
# 2. image pool (files actually sitting under notes/images/)
# ---------------------------------------------------------------------------
pool = {}
for root, _dirs, files in os.walk(SRC_IMAGES_DIR):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), SRC_IMAGES_DIR).replace("\\", "/")
        pool[rel] = os.path.join(root, f)

# ---------------------------------------------------------------------------
# 3. emit atomic notes
# ---------------------------------------------------------------------------
def vault_link(e):
    return f"[[{SUBJECT}/{rel_vault(e['path'])}|{e['id']} {e['name']}]]"

missing = []
for ci, ch in enumerate(chapters, start=1):
    ch_dir = os.path.join(BASE_DIR, ch["dirname"])
    os.makedirs(ch_dir, exist_ok=True)
    for ki, kp in enumerate(ch["kps"], start=1):
        body = join_lines(kp["raw"])
        if ki == 1 and ch["intro"]:
            body = (ch["intro"] + "\n\n" + body) if body else ch["intro"]
        body = embed_images(body)
        for rel_img in set(re.findall(r'!\[\[NLP/images/([^\]|]+)\]\]', body)):
            if rel_img not in pool:
                missing.append(rel_img)
            else:
                dst = os.path.join(OUT_IMAGES_DIR, rel_img)
                if not os.path.exists(dst):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(pool[rel_img], dst)
        e = next(n for n in all_notes if n["id"] == kp["id"])
        prev = all_notes[all_notes.index(e) - 1] if all_notes.index(e) > 0 else None
        nxt = all_notes[all_notes.index(e) + 1] if all_notes.index(e) < len(all_notes) - 1 else None
        prev_txt = vault_link(prev) if prev else "无（本章第一个知识点）"
        nxt_txt = vault_link(nxt) if nxt else "无（本章最后一个知识点）"
        content = (
            f"---\n"
            f"tags: [{SUBJECT_TAG}, {SUBJECT_TAG}-ch{ch['num']}]\n"
            f"---\n\n"
            f"# {kp['name']}\n\n"
            f"{body}\n\n"
            f"## 链接到\n\n"
            f"- 上一个知识点：{prev_txt}\n"
            f"- 下一个知识点：{nxt_txt}\n"
        )
        with open(kp["path"], "w", encoding="utf-8") as f:
            f.write(content)

# ---------------------------------------------------------------------------
# 4. emit chapter hub files
# ---------------------------------------------------------------------------
for ci, ch in enumerate(chapters, start=1):
    items = [f"- [[{SUBJECT}/{rel_vault(kp['path'])}|{kp['id']} {kp['name']}]]"
             for kp in ch["kps"]]
    content = (
        f"---\n"
        f"tags: [{SUBJECT_TAG}, moc, {SUBJECT_TAG}-ch{ch['num']}]\n"
        f"aliases: [第{ch['num']}章, {ch['title']}]\n"
        f"---\n\n"
        f"# 第{ch['num']}章 {ch['title']}\n\n"
        f"## 本章知识点\n\n"
        f"{chr(10).join(items)}\n\n"
        f"---\n\n"
        f"[[../{SUBJECT}|← 返回 {SUBJECT} 总览]]\n"
    )
    with open(ch["hub"], "w", encoding="utf-8") as f:
        f.write(content)

# ---------------------------------------------------------------------------
# 5. emit subject hub NLP.md
# ---------------------------------------------------------------------------
nav_blocks = []
for ch in chapters:
    names = "、".join(kp["name"] for kp in ch["kps"])
    nav_blocks.append(
        f"### [[{SUBJECT}/{ch['dirname']}/{safe_name(ch['title'])}|"
        f"第{ch['num']}章 {ch['title']}]]\n{names}"
    )
nav_text = "\n\n".join(nav_blocks)
content = (
    f"---\n"
    f"created: 2026-09-06\n"
    f"tags: [{SUBJECT_TAG}, map-of-content, root]\n"
    f"---\n\n"
    f"# {SUBJECT}\n\n"
    f"> 自然语言处理：让计算机理解、生成和处理人类语言\n\n"
    f"---\n\n"
    f"## 章节导航\n\n"
    f"{nav_text}\n\n"
    f"[[../index|← 返回 📚 笔记主页]]\n"
)
with open(os.path.join(BASE_DIR, f"{SUBJECT}.md"), "w", encoding="utf-8") as f:
    f.write(content)

# ---------------------------------------------------------------------------
print(f"chapters = {len(chapters)}")
print(f"atomic notes = {len(all_notes)}")
print(f"missing images = {len(missing)} {sorted(set(missing)) if missing else ''}")
for ch in chapters:
    print(f"  ch{ch['num']:>2}  {ch['dirname']:<28} kps={len(ch['kps'])}")
