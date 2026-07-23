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
        folderClickBehavior: "link",
        // Use filename (with X.Y prefix) instead of H1 title for display
        mapFn: (node) => {
          if (node.file) {
            node.displayName = node.name
          }
        },
        // Natural number sort: 01, 02, ... and 1.1, 1.2, ...
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
        folderClickBehavior: "link",
        mapFn: (node) => {
          if (node.file) {
            node.displayName = node.name
          }
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
