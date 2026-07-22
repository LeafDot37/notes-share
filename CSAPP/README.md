# CSAPP 知识图谱构建手册

> 本文档记录了从原始笔记到结构化知识图谱的完整构建流程。
> 后续如有类似需求，请参考本文档的步骤和方法。

---

## 目录

1. [概述](#1-概述)
2. [前置条件](#2-前置条件)
3. [构建流程总览](#3-构建流程总览)
4. [详细步骤](#4-详细步骤)
   - [Step 1: 全面调研原始笔记](#step-1-全面调研原始笔记)
   - [Step 2: 创建目录结构](#step-2-创建目录结构)
   - [Step 3: 图片 OCR 处理](#step-3-图片-ocr-处理)
   - [Step 4: 统一标签系统](#step-4-统一标签系统)
   - [Step 5: 重命名导航节点](#step-5-重命名导航节点)
   - [Step 6: 构建辐射树状链接](#step-6-构建辐射树状链接)
   - [Step 7: 配置图谱颜色分组](#step-7-配置图谱颜色分组)
   - [Step 8: 清理与验证](#step-8-清理与验证)
5. [图谱结构规范](#5-图谱结构规范)
6. [目录命名规则](#6-目录命名规则)
7. [标签体系](#7-标签体系)
8. [注意事项与常见问题](#8-注意事项与常见问题)

---

## 1. 概述

本手册描述如何将一组扁平的 CSAPP 学习笔记（10 个 Markdown 文件 + 653 张图片）转化为 Obsidian 知识图谱。

### 核心目标

- **知识原子化**：将每个知识点拆分为独立笔记
- **树状结构**：笔记之间仅保留父子关系（根 → 章节 → 知识点），形成辐射树
- **图谱可视化**：按章节着色，便于 Obsidian 关系图谱阅读
- **图片处理**：OCR 提取文字，无法识别的保留并重命名

### 最终结构

```
CSAPP/
├── CSAPP.md                          ← 根节点（#map-of-content）
├── 01-计算机系统漫游/
│   ├── 计算机系统漫游.md             ← 章节导航节点（#chapter1 #moc）
│   ├── 1.1 抽象层次结构.md           ← 原子笔记（#chapter1）
│   └── 1.2 Amdahl定律.md
├── 02-信息的表示和处理/
│   ├── 信息的表示和处理.md           ← 章节导航节点
│   ├── 2.1 字与字节序.md
│   └── ...
├── images/                           ← 处理后的图片
│   ├── 1/ (ch1_text_001.png, ...)
│   └── ...
├── 知识节点/                        ← 跨章节核心概念（独立节点）
└── notes/                           ← 原始笔记（保留但图谱不引用）
```

---

## 2. 前置条件

### 2.1 环境要求

| 工具 | 用途 | 检查命令 |
|------|------|---------|
| **Python 3** | 运行批量处理脚本 | `python --version` |
| **Tesseract OCR** | 图片文字识别 | `tesseract --version` |
| **Tesseract 语言包** | 中英文识别 | `tesseract --list-langs` (需有 `chi_sim` 和 `eng`) |

### 2.2 Tesseract 安装路径

通常在 `D:\TESSERACT\tesseract` 或系统 PATH 中。

如需安装中文语言包：
```bash
# 下载 chi_sim.traineddata 放入 TESSDATA 目录
# Windows 默认路径: C:\Program Files\Tesseract-OCR\tessdata\
```

### 2.3 Python 依赖

标准库即可（`os`, `re`, `json`, `subprocess`, `shutil`, `tempfile`），无需额外安装。

---

## 3. 构建流程总览

```mermaid
graph LR
    A[原始笔记调研] --> B[创建目录结构]
    B --> C[图片OCR处理]
    C --> D[编写知识节点]
    D --> E[统一标签]
    E --> F[重命名MOC文件]
    F --> G[构建树状链接]
    G --> H[配置图谱颜色]
    H --> I[清理验证]
```

---

## 4. 详细步骤

### Step 1: 全面调研原始笔记

**目标**：了解所有原始笔记的内容、图片数量、笔记结构。

```python
# 使用 Glob 搜索 CSAPP 目录结构
# 使用 Read 读取所有笔记内容
# 统计图片数量和分布
```

**关键发现记录**：
- 原始笔记为 10 个 Markdown 文件（`1.md` ~ `10.md`）
- 共计 653 张 PNG 图片
- 笔记内容是浓缩的要点式记录，非完整教材

### Step 2: 创建目录结构

**目标**：建立知识图谱的物理目录框架。

```bash
mkdir -p \
  "01-计算机系统漫游" \
  "02-信息的表示和处理" \
  "03-程序的机器级表示" \
  "04-处理器体系结构" \
  "05-优化程序性能" \
  "06-存储器层次结构" \
  "07-链接" \
  "08-异常控制流" \
  "09-虚拟内存" \
  "10-系统级IO" \
  "知识节点" \
  "images/1" "images/2" ... "images/10"
```

**目录命名规则**：`<两位数字>-<中文章节名>`，保持排序一致性。

### Step 3: 图片 OCR 处理

**目标**：对每张图片进行文字识别，判断能否用文本替代，不能替代的用描述性名称重命名。

**Python 实现要点**：

```python
def safe_ocr(image_path):
    """使用临时文件避免 Windows 编码问题"""
    import tempfile
    tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w', encoding='utf-8')
    tmp_path = tmp.name
    tmp.close()
    
    base = tmp_path.replace('.txt', '')
    subprocess.run(["tesseract", image_path, base, "-l", "chi_sim+eng", "--psm", "6"],
                   capture_output=True, timeout=30)
    
    # 读取结果
    with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read().strip()
    
    # 如文字太少，尝试纯英文识别
    if len(text) < 10:
        subprocess.run(["tesseract", image_path, base, "-l", "eng", "--psm", "6"],
                       capture_output=True, timeout=30)
        with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read().strip()
    
    os.unlink(tmp_path)
    return text
```

**分类逻辑**：
- 文字量 ≥ 5 行有意义的句子 → 标记为"可替换为文字"
- 架构图/流程图（有框线字符 `│└├─┌┐┘└┃` 等）→ 保留图片
- 文字过少或无文字 → 保留图片

**图片重命名规则**：
- 可替换图片：`chX_text_XXX.png`（文字已被提取到笔记中）
- 保留图片：从 OCR 结果中提取英文关键词作为文件名
- 所有图片复制到 `images/<章节号>/` 目录

**处理结果**：653 张图片，约 98% 可替换，约 2% 保留为图片。

> ⚠️ **编码问题**：Windows 环境下 `subprocess.run` 的 `capture_output=True, text=True` 会使用 GBK 编码导致 UnicodeDecodeError。**必须使用临时文件方式**来避免此问题。

### Step 4: 统一标签系统

**目标**：为所有笔记添加统一标签，使 Obsidian 图谱能按章节着色。

**规范**：
- 每篇笔记必须有 `tags` 字段
- 标签使用全小写格式（`csapp` 而非 `CSAPP`）
- 原子笔记 → `[chapter<数字>, csapp, ...]`
- 章节导航节点 → `[csapp, moc, chapter<数字>]`
- 根节点 → `[csapp, map-of-content, root]`
- 知识节点 → `[csapp, knowledge-node, core-concept]`

**自动修复脚本逻辑**：
```python
# 1. 读取 frontmatter
# 2. 解析已有 tags
# 3. 统一大小写（CSAPP → csapp）
# 4. 确保 chapterX 存在
# 5. 去重
# 6. 写回文件
```

**验证标准**：每章的 MOC + 所有原子笔记都应包含对应的 `chapter<数字>` 标签。

### Step 5: 重命名导航节点

**目标**：将 `_moc.md` 重命名为有意义的名称，使 Obsidian 图谱中节点可读。

**重命名映射**：

| 原路径 | 新路径 |
|--------|--------|
| `CSAPP/_moc.md` | `CSAPP/CSAPP.md` |
| `CSAPP/01-计算机系统漫游/_moc.md` | `CSAPP/01-计算机系统漫游/计算机系统漫游.md` |
| `CSAPP/02-信息的表示和处理/_moc.md` | `CSAPP/02-信息的表示和处理/信息的表示和处理.md` |
| ... | ... |

**同时更新所有引用**：
```python
# 对所有 .md 文件搜索 CSAPP/XX-章节/_moc 替换为 CSAPP/XX-章节/章节名
# 包括带别名格式 别名
# 注意表格中的转义管道符 \\|
```

> ⚠️ **Obsidian wiki-link 格式**：链接格式为 `路径/文件名`（不加 `.md` 后缀）。表格中管道符需转义为 `\|`。

### Step 6: 构建辐射树状链接

**目标**：建立单向父子关系的树状结构，去除所有平级和跨章节链接。

**最终链接规则**：

| 来源 | 去向 | 关系 | 数量 |
|------|------|------|:----:|
| `CSAPP.md` (根) | 10 个章节导航节点 | 父→子 | 10 |
| 每个章节导航节点 | CSAPP 根节点 | 子→父（回链）| 10 |
| 每个章节导航节点 | 下属的所有原子笔记 | 父→子 | 165 |
| 原子笔记 | 无 | 叶子节点 | 0 |

**操作方法**：
1. **原子笔记** → 移除所有 wiki-link（`re.sub(r'\[\[([^\]]*)\]\]', '', content)`），只保留 `frontmatter`
2. **章节导航节点** → 重写内容，只链接自己的原子笔记 + 回链 CSAPP
3. **根节点** → 重写内容，只链接 10 个章节导航节点

```python
# 关键模式：原子笔记清除所有链接
# 只操作 frontmatter 之外的正文部分
parts = content.split('---', 2)
if len(parts) >= 3:
    body = re.sub(r'\[\[([^\]]*)\]\]', '', parts[2])
    body = re.sub(r'\n{3,}', '\n\n', body)
    content = f"---{parts[1]}---{body}\n"
```

### Step 7: 配置图谱颜色分组

**目标**：在 Obsidian 的 `graph.json` 中预设颜色分组，用户打开图谱即可看到着色。

**配置文件位置**：`.obsidian/graph.json`

```json
{
  "colorGroups": [
    {"query": "tag:#chapter1", "color": {"a": 1, "rgb": 14895979}},
    {"query": "tag:#chapter2", "color": {"a": 1, "rgb": 15769162}},
    // ... 10 个章节
    {"query": "tag:#knowledge-node", "color": {"a": 1, "rgb": 16777215}},
    {"query": "tag:#moc", "color": {"a": 0.4, "rgb": 10526880}}
  ],
  "showArrow": true,
  "showTags": true,
  "showAttachments": false
}
```

**颜色值计算**：
```python
# RGB 转 Obsidian 整数格式
rgb_value = red * 65536 + green * 256 + blue
# 例如 #e34b6b (红) = 0xe3*65536 + 0x4b*256 + 0x6b = 14895979
```

**推荐颜色方案**（10 章 + 知识节点 + MOC）：

| 标签 | 颜色 | RGB | 整数值 |
|------|------|-----|--------|
| `#chapter1` | 🔴 红 | `#e34b6b` | 14895979 |
| `#chapter2` | 🟠 橙 | `#f09e4a` | 15769162 |
| `#chapter3` | 🟡 黄 | `#f5d442` | 16110658 |
| `#chapter4` | 🟢 绿 | `#4caf50` | 5025616 |
| `#chapter5` | 🔵 蓝 | `#2196f3` | 2201331 |
| `#chapter6` | 🟣 紫 | `#9c27b0` | 10233776 |
| `#chapter7` | 🟤 棕 | `#795548` | 7951688 |
| `#chapter8` | 🩶 灰 | `#607d8b` | 6323595 |
| `#chapter9` | 🔷 靛 | `#3f51b5` | 4149685 |
| `#chapter10` | 🩵 青 | `#00bcd4` | 48340 |
| `#knowledge-node` | ⚪ 白 | `#ffffff` | 16777215 |
| `#moc` | ◻️ 浅灰(透明度0.4) | `#a0a0a0` | 10526880 |

### Step 8: 清理与验证

**最终验证标准**：

```python
link_types = {
    "csapp_to_chapter": 10,   # CSAPP → 10章节
    "chapter_to_csapp": 10,   # 10章节 → CSAPP
    "chapter_to_note": 165,   # 10章 → 165原子笔记
    "note_links": 0,          # 原子笔记不能有链接
    "other_links": 0          # 无其他类型链接
}
```

**清理临时文件**：
```bash
rm -f process_images*.py fix_graph*.py rebuild_links.py image_processing_report.json
```

---

## 5. 图谱结构规范

### 5.1 节点类型

| 类型 | frontmatter 示例 | 出链规则 |
|------|-----------------|---------|
| **根节点** (CSAPP.md) | `tags: [csapp, map-of-content, root]` | 仅指向10个章节节点 |
| **章节导航** | `tags: [csapp, moc, chapter1]` | 指向下属知识点 + 回链CSAPP |
| **原子笔记** | `tags: [chapter1, csapp, ...]` | **无出链** |
| **知识节点** | `tags: [csapp, knowledge-node, core-concept]` | 无出链（如需使用单独添加） |

### 5.2 绝对规范

1. **原子笔记不能有任何 wiki-link**（图谱中作为叶子节点）
2. **所有链接均为单向父子关系**（无兄弟链接、无跨章节链接）
3. **章节流向不通过链接表达**（章节之间没有连接）
4. **CSAPP.md 与章节节点双向连接**（CSAPP→章节，章节→CSAPP）

---

## 6. 目录命名规则

```
CSAPP/
├── <两位数字>-<章节中文名>/      ← 目录名
│   ├── <章节中文名>.md           ← 导航节点（原名 _moc.md）
│   ├── <序号>.<小节号> <标题>.md ← 原子笔记
│   └── ...
├── 知识节点/                     ← 跨章节概念
│   └── <概念名>.md
└── images/                       ← 处理后的图片
    └── <章节号>/
        ├── ch<章节号>_text_<序号>.png    ← 可替换的图片
        └── <描述性英文名>.png             ← 保留的图片（如架构图）
```

**文件命名要点**：
- 导航节点名 = 章节中文名（如 `计算机系统漫游.md`）
- 原子笔记以序号开头（如 `2.3 整型数表示.md`），便于排序
- 不使用 `_moc.md` 作为文件名（图谱中不可读）

---

## 7. 标签体系

### 7.1 标签类型

| 标签前缀 | 用途 | 应用范围 |
|---------|------|---------|
| `chapter<数字>` | 按章节分组 | 所有笔记 |
| `moc` | 标记为导航节点 | 仅章节导航节点 |
| `knowledge-node` | 跨章节核心概念 | 仅知识节点 |
| `csapp` | 统一命名空间 | 所有笔记 |
| `map-of-content` | 标记为根节点 | 仅 CSAPP.md |

### 7.2 写回规范

```yaml
# 根节点
tags: [csapp, map-of-content, root]

# 章节导航节点
tags: [csapp, moc, chapter1]

# 原子笔记（Ch1示例）
tags: [chapter1, csapp, 计算机系统, 抽象, 层次结构]

# 知识节点
tags: [csapp, knowledge-node, core-concept]
```

### 7.3 标签修复脚本逻辑

```python
def normalize_tags(line, chapter_tag):
    # 1. 统一大小写: CSAPP → csapp
    # 2. 确保 chapter<数字> 存在且为第一个
    # 3. 确保 csapp 存在
    # 4. 去重保留顺序
    # 5. 处理空标签（补充默认值）
    pass
```

---

## 8. 注意事项与常见问题

### 8.1 Windows 编码问题 ⚠️

**问题**：Python 在 Windows 上使用 `print()` 输出 Unicode 会报 `UnicodeEncodeError: 'gbk' codec can't encode character`。

**原因**：Windows 终端默认使用 GBK 编码，不支持某些 Unicode 字符。

**解决方案**：
- 不使用 emoji 和特殊符号（如 `✓`, `✗`, `→`）
- 使用纯 ASCII 替代（如 `OK`, `DONE`, `->`）
- 或者将输出重定向到文件

### 8.2 Tesseract OCR 编码问题

**问题**：`subprocess.run(capture_output=True, text=True)` 在 Windows 上会因 GBK 解码失败崩溃。

**原因**：Tesseract 输出 UTF-8 文本，但 Python 用系统默认编码（GBK）解码。

**解决方案**：使用临时文件接收 OCR 结果，而非标准输出管道。

```python
# 正确方式
tmp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
tmp_path = tmp.name
tmp.close()

subprocess.run(["tesseract", image_path, tmp_path.replace('.txt', ''),
                "-l", "chi_sim+eng"])
with open(tmp_path, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()
os.unlink(tmp_path)
```

### 8.3 wiki-link 表格转义

**问题**：Markdown 表格中的 `|` 需要转义为 `\|`，导致直接替换失效。

**解决方案**：同时匹配 `别名` 和 `别名` 两种格式。

### 8.4 图片重命名的中文问题

**问题**：OCR 提取的中文文字作为文件名会导致路径问题。

**解决方案**：只提取英文关键词作为重命名的依据，中文字符剔除。

### 8.5 重复运行的风险

**风险**：多次运行原子笔记清理脚本会反复修改文件，虽然幂等但浪费时间。

**预防**：在操作前检查是否需要处理（如 `if ' grep -v "导航节点文件名"
```

### 图谱验证
```bash
# 统计链接分布
python -c "
import os, re
stats = {}
for root, dirs, files in os.walk('CSAPP'):
    for fn in files:
        if not fn.endswith('.md'): continue
        with open(os.path.join(root,fn), 'r', encoding='utf-8') as f:
            links = re.findall(r'\[\[([^\*)\]\]', f.read())
        # 按类型分类
"
```

---

> **最后更新**：2026-07-20
> **适用版本**：本手册适用于 CSAPP 课程笔记的知识图谱构建。
> **可复用性**：将 `CSAPP` 替换为目标课程名即可复用整套流程。
