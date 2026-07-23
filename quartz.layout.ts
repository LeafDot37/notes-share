import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/LeafDot37/notes-share",
    },
  }),
}

// components for content pages
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.DesktopOnly(
      Component.Explorer({
        title: "📂 笔记目录",
        folderDefaultState: "collapsed",
        folderClickBehavior: "collapse",
        mapFn: (node) => {
          if (node.file) {
            // Hide root-level files (index, README, methodology) from Explorer
            if (!node.file.slug.includes("/")) {
              node.displayName = "__HIDDEN__"
              return
            }
            // Atomic notes: show X.Y prefix
            if (/^\d+\.\d+ /.test(node.name)) {
              node.displayName = node.name
            }
            // Index files: derive name from parent directory
            if (node.name === "index" && node.file.slug) {
              const parts = node.file.slug.split("/")
              if (parts.length >= 2) {
                node.displayName = parts[parts.length - 2].replace(/^\d{1,2}-/, "")
              }
            }
          }
        },
        // Filter out hidden items and Others folder
        filterFn: (node) => {
          if (node.displayName === "__HIDDEN__") return false
          if (node.name === "Others") return false
          return true
        },
        sortFn: (a, b) => {
          if ((!a.isFolder && !b.isFolder) || (a.isFolder && b.isFolder)) {
            return a.displayName.localeCompare(b.displayName, "zh-CN", {
              numeric: true,
              sensitivity: "base",
            })
          }
          if (!a.isFolder && b.isFolder) return 1
          return -1
        },
      }),
    ),
  ],
  right: [
    Component.Graph({
      localGraph: {
        enableRadial: true,
        showTags: false,
      },
      globalGraph: {
        showTags: false,
      },
    }),
    Component.DesktopOnly(Component.TableOfContents()),
  ],
}

// components for listing pages
export const defaultListPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.ContentMeta(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Darkmode(),
    Component.DesktopOnly(
      Component.Explorer({
        title: "📂 笔记目录",
        folderDefaultState: "collapsed",
        folderClickBehavior: "collapse",
        mapFn: (node) => {
          if (node.file) {
            if (!node.file.slug.includes("/")) {
              node.displayName = "__HIDDEN__"
              return
            }
            if (/^\d+\.\d+ /.test(node.name)) {
              node.displayName = node.name
            }
            if (node.name === "index" && node.file.slug) {
              const parts = node.file.slug.split("/")
              if (parts.length >= 2) {
                node.displayName = parts[parts.length - 2].replace(/^\d{1,2}-/, "")
              }
            }
          }
        },
        filterFn: (node) => {
          if (node.displayName === "__HIDDEN__") return false
          if (node.name === "Others") return false
          return true
        },
        sortFn: (a, b) => {
          if ((!a.isFolder && !b.isFolder) || (a.isFolder && b.isFolder)) {
            return a.displayName.localeCompare(b.displayName, "zh-CN", {
              numeric: true,
              sensitivity: "base",
            })
          }
          if (!a.isFolder && b.isFolder) return 1
          return -1
        },
      }),
    ),
  ],
  right: [],
}
