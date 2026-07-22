# 🚀 GitHub Actions + Quartz：笔记自动构建为静态网站

## 一、概述

本仓库实现了一套完整的**自动化发布流水线**：将 Obsidian 笔记（Markdown 格式）通过 Quartz 自动构建为带关系图谱的静态网站，并部署到 GitHub Pages 免费托管。

### 核心组件

| 组件 | 作用 |
|------|------|
| **Obsidian Vault** | 笔记源文件（Markdown + Wiki-link + Front Matter） |
| **Git** | 版本控制，推送触发自动化流程 |
| **GitHub Actions** | CI/CD 引擎，在云端执行构建脚本 |
| **Quartz v4** | 静态网站生成器，将 Markdown 转换为 HTML |
| **GitHub Pages** | 静态文件托管服务，提供网页访问 |

---

## 二、工作流程全景图

```
你本地操作：                   GitHub 云端：                  用户访问：
┌─────────────┐    git push    ┌──────────────────┐           ┌──────────┐
│ 编辑笔记.md  │ ──────────→   │ 1. Actions 触发   │           │ 浏览器   │
│ 保存到 Notes │               │ 2. 克隆 Quartz    │           │          │
│ git commit   │               │ 3. 复制笔记内容    │           │          │
│ git push     │               │ 4. npm ci 安装依赖 │           │          │
└─────────────┘               │ 5. npm run build   │           │          │
                              │ 6. 输出 public/    │           │          │
                              │ 7. 上传构建产物     │           │          │
                              │ 8. Pages 部署      │ ───────→ │ 网页渲染 │
                              └──────────────────┘           └──────────┘
```

### 流程分解（5 个阶段）

---

## 三、阶段一：触发（Trigger）

### 触发条件

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches:
      - main
```

当你执行 `git push origin main` 时，GitHub 检测到 `main` 分支有新的提交，自动触发 Actions。

### 权限配置

```yaml
permissions:
  contents: read      # 读取仓库代码
  pages: write        # 写入 GitHub Pages
  id-token: write     # OIDC 身份认证
```

这是 GitHub 的安全机制——明确告诉平台：这个工作流需要"读取代码"和"写入 Pages"的权限。

---

## 四、阶段二：构建环境准备（Setup）

### 步骤 1：Checkout（检出代码）

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

GitHub Actions 启动一个 **Ubuntu 虚拟服务器**（每次全新启动），将你的仓库代码下载到这个服务器上。

- `actions/checkout@v4` 是 GitHub 官方 Action，负责拉取代码
- `fetch-depth: 0` 拉取完整 Git 历史（Quartz 需要基于文件修改时间排序）

### 步骤 2：安装 Node.js

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
```

`actions/setup-node@v4` 安装指定版本的 Node.js 运行环境。Quartz 是 Node.js 项目，需要 Node 来运行。

### 步骤 3：克隆 Quartz

```bash
git clone --depth 1 --branch v4 https://github.com/jackyzha0/quartz.git /tmp/quartz
```

在服务器上克隆 **Quartz v4 稳定版** 的完整项目代码（到 `/tmp/quartz` 临时目录）。

- `--depth 1`：只克隆最新版本，节省时间
- `--branch v4`：指定 v4 稳定分支

### 步骤 4：复制笔记内容

```bash
mkdir -p /tmp/quartz/content
for item in "${{ github.workspace }}"/*; do
  f=$(basename "$item")
  case "$f" in .github|quartz.config.ts|quartz.layout.ts) continue ;; esac
  cp -r "$item" /tmp/quartz/content/
done
cp quartz.config.ts /tmp/quartz/
cp quartz.layout.ts /tmp/quartz/
```

这是**关键步骤**——Quartz 的构建逻辑是：

```
Quartz 项目根目录
  ├── quartz/           ← Quartz 源码（框架本身）
  ├── content/          ← ← ← ← 你的笔记放这里！
  ├── quartz.config.ts  ← 网站配置
  ├── quartz.layout.ts  ← 页面布局
  ├── package.json      ← 依赖声明
  └── ...
```

你的笔记（Algorithms/、CSAPP/、index.md 等）被复制到 `content/` 目录，同时你的 `quartz.config.ts` 和 `quartz.layout.ts` 覆盖 Quartz 的默认配置。

---

## 五、阶段三：构建（Build）——核心环节

### 步骤 5：安装依赖

```bash
cd /tmp/quartz
npm ci
```

`npm ci`（而不是 `npm install`）根据 `package-lock.json` 精确安装所有依赖包，包括：
- Markdown 解析器（remark / rehype 生态）
- Katex（数学公式渲染）
- 语法高亮（Prism.js / Shiki）
- 构建工具（esbuild）

### 步骤 6：执行构建

```bash
npx quartz build
```

这是**最核心的步骤**。让我们深入理解 Quartz 内部做了什么：

#### Quartz 构建管线（Pipeline）

```
                         Quartz 构建管线
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │  content/*.md                                           │
  │      │                                                  │
  │      ▼                                                  │
  │  ┌─────────────┐                                        │
  │  │  读取文件     │  ← 扫描 content/ 所有 .md 文件        │
  │  └──────┬──────┘                                        │
  │         ▼                                               │
  │  ┌─────────────┐                                        │
  │  │  解析 Front  │  ← 提取 YAML 元数据（created、tags）   │
  │  │  Matter     │                                        │
  │  └──────┬──────┘                                        │
  │         ▼                                               │
  │  ┌─────────────┐                                        │
  │  │  Transformers │  ← 依次转换 Markdown 内容             │
  │  │  ▼           │                                        │
  │  │  FrontMatter │  → 解析元数据                          │
  │  │  ObsidianMD  │  → 转换 Wiki-link [[file]] 为 HTML    │
  │  │  Latex       │  → 将 $$公式$$ 渲染为 Katex HTML      │
  │  │  SyntaxHL    │  → 代码块语法高亮                      │
  │  │  CrawlLinks  │  → 解析链接关系（用于图谱）             │
  │  │  Description │  → 生成页面描述                        │
  │  │  Toc         │  → 生成目录                            │
  │  └──────┬──────┘                                        │
  │         ▼                                               │
  │  ┌─────────────┐                                        │
  │  │   Filters    │  ← 过滤不需要发布的页面                 │
  │  │  RemoveDrafts│  → 删除 draft: true 的笔记             │
  │  └──────┬──────┘                                        │
  │         ▼                                               │
  │  ┌─────────────┐                                        │
  │  │   Emitters   │  ← 输出 HTML/JSON/Assets               │
  │  │  ▼          │                                        │
  │  │  ContentPage│  → 每个 .md 生成一个 .html              │
  │  │  FolderPage │  → 文件夹生成索引页                     │
  │  │  TagPage    │  → 标签生成聚合页                       │
  │  │  ContentIdx │  → 生成搜索索引（JSON）                 │
  │  │  Assets     │  → 复制图片等静态资源                    │
  │  │  Static     │  → 复制 static/ 目录                   │
  │  │  NotFound   │  → 生成 404 页                         │
  │  │  AliasRedir │  → 处理别名重定向                       │
  │  │  Component  │  → 注入 React 组件（图谱、目录等）      │
  │  └──────┬──────┘                                        │
  │         ▼                                               │
  │  ┌─────────────┐                                        │
  │  │   public/    │  ← 输出目录，完整的静态网站             │
  │  │  ├── index.html                                       │
  │  │  ├── CSAPP/CSAPP.html                                 │
  │  │  ├── Algorithms/1.1 复杂度分析.html                   │
  │  │  ├── static/ (CSS/JS)                                 │
  │  │  └── index.xml (关闭后不生成)                         │
  │  └─────────────┘                                        │
  │                                                         │
  └─────────────────────────────────────────────────────────┘
```

#### 关键转换示例

**Obsidian 笔记原文（.md）**：
```markdown
---
created: 2026-07-20
tags: [csapp, chapter1]
---

# 计算机系统漫游

信息就是 [[01-计算机系统漫游/1.1 位+上下文|位+上下文]]

$$ E = mc^2 $$
```

**Quartz 处理后（HTML）**：
```html
<!DOCTYPE html>
<html>
<head>
  <title>计算机系统漫游</title>
  <meta name="tags" content="csapp, chapter1">
  <script src="/static/graph.js"></script>
</head>
<body>
  <h1>计算机系统漫游</h1>
  <p>信息就是 <a href="/notes/1.1-位+上下文">位+上下文</a></p>
  <span class="katex">E = mc²</span>
  <!-- ← 关系图谱数据嵌入在 data-graph 属性中 -->
</body>
</html>
```

#### 关系图谱是如何工作的

```
笔记 A ──── Wiki-link ────→ 笔记 B
  │                            │
  │                            │
  ▼                            ▼
CrawlLinks 插件解析所有链接关系
  │
  ▼
生成全局链接数据 JSON（嵌入页面）
  │
  ▼
Graph 组件（D3.js 可视化）在页面右侧渲染力导向图
```

当你浏览 "CSAPP.md" 时：
1. 页面加载时，Graph 组件读取嵌入的链接关系数据
2. D3.js 计算出节点位置（力导向布局）
3. 渲染出可交互的关系图谱，节点可点击跳转

---

## 六、阶段四：上传产物（Upload Artifact）

```yaml
- uses: actions/upload-pages-artifact@v3
  with:
    path: /tmp/quartz/public
```

构建完成后，`public/` 目录包含完整的静态网站（HTML + CSS + JS + 图片）。`upload-pages-artifact` 将这个目录**压缩上传**到 GitHub 内部的存储系统，等待部署。

上传的内容结构：
```
public/
├── index.html                    ← 首页
├── 404.html                      ← 404 页面
├── static/
│   ├── styles.css                ← 全局样式
│   ├── quartz.js                 ← SPA 路由/搜索/图谱
│   ├── clz.js                    ← 代码高亮
│   └── popover.js                ← 悬停预览
├── index.xml                     ← RSS（已关闭）
├── sitemap.xml                   ← SEO 站点地图
├── CSAPP/
│   ├── CSAPP.html                ← CSAPP 根节点页
│   ├── index.html                ← 文件夹索引
│   └── 01-计算机系统漫游/
│       ├── 计算机系统漫游.html     ← 章节 Hub 页
│       └── 1.1-位+上下文.html     ← 原子笔记页
├── Algorithms/
│   └── ...
├── tags/
│   └── csapp/index.html          ← 按标签聚合的页面
└── contentIndex.json             ← 全文搜索索引数据
```

---

## 七、阶段五：部署（Deploy）

```yaml
deploy:
  needs: build                                    # 等待 build 完成
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  runs-on: ubuntu-latest
  steps:
    - uses: actions/deploy-pages@v4                # 官方 Pages 部署 Action
```

`actions/deploy-pages@v4` 的作用：

1. 从 Artifact 存储中下载之前上传的压缩包
2. 解压到 GitHub Pages 的内容分发网络（CDN）
3. 将 `https://LeafDot37.github.io/notes-share/` 指向这些文件
4. 全世界的用户通过 CDN 边缘节点快速访问

### GitHub Pages 的工作原理

```
用户浏览器                              GitHub CDN
┌─────────┐    DNS 解析                  ┌──────────────┐
│ 请求     │ ───→ leafdot37.github.io    │ 全球 CDN     │
│ notes-  │                              │ 边缘节点     │
│ share/  │ ←─── 返回 index.html         │              │
└─────────┘                              │ 存储静态文件  │
                                         └──────────────┘
                                               ▲
                                               │ 上传产物
                                         ┌────┴─────┐
                                         │ Actions   │
                                         │ 构建产物   │
                                         └──────────┘
```

**关键特性**：
- **CDN 加速**：GitHub Pages 使用 Fastly CDN，全球访问速度快
- **自动 HTTPS**：自动签发 Let's Encrypt SSL 证书
- **SPA 支持**：Quartz 生成的是单页应用（SPA），页面切换无需重新加载
- **无服务器逻辑**：只托管静态文件，不支持后端代码

---

## 八、为什么选择这个方案？

### 方案对比

| 维度 | Quartz + Actions | 直接上传 HTML | 自建服务器 |
|------|-----------------|---------------|-----------|
| **成本** | 免费 | 免费 | 需要服务器 |
| **自动化** | 全自动 | 手动操作 | 需配置 CI |
| **关系图谱** | ✅ 原生支持 | ❌ | ❌ |
| **双向链接** | ✅ | ❌ | ❌ |
| **搜索** | ✅ 全文搜索 | ❌ | ❌ |
| **Wiki-link** | ✅ 自动转换 | ❌ | ❌ |
| **维护** | 零维护 | 每次手动上传 | 需运维 |
| **更新频率** | push 即更新 | 手动操作 | 需配置 |

### 核心优势

1. **push 即发布**：修改笔记 → `git push` → 网站自动更新
2. **零成本**：GitHub Actions 每月 2000 分钟免费额度，完全够用
3. **功能完整**：图谱、搜索、标签、目录、暗色模式一应俱全
4. **Obsidian 原生**：直接使用 Wiki-link `[[链接]]`，无需修改笔记格式
5. **静态网站速度快**：CDN 加速，首屏秒开

---

## 九、扩展阅读

- [Quartz 官方文档](https://quartz.jzhao.xyz/)
- [GitHub Actions 文档](https://docs.github.com/actions)
- [GitHub Pages 文档](https://docs.github.com/pages)
- [Obsidian 官方文档](https://help.obsidian.md/)
- [本仓库的 GitHub Actions 配置](https://github.com/LeafDot37/notes-share/blob/main/.github/workflows/deploy.yml)

---

> 📝 本文档由 Claude Code 编写，记录了本仓库的完整构建流程。
