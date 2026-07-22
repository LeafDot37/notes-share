#include <iostream>
#include <algorithm>
using namespace std;

const int MAXN = 100;      // 最大顶点数
const int INF = 1e9;       // 表示无穷大

// ==================== Prim 算法（使用两个数组）====================
void prim(int graph[MAXN][MAXN], int n) {
    int minDist[MAXN];     // minDist[i]：顶点 i 到当前 MST 的最小边权
    int parent[MAXN];      // parent[i]：MST 中 i 的父节点
    bool inMST[MAXN];      // inMST[i]：顶点 i 是否已加入 MST

    // 初始化
    for (int i = 0; i < n; i++) {
        minDist[i] = INF;
        parent[i] = -1;
        inMST[i] = false;
    }

    minDist[0] = 0; // 从顶点 0 开始

    cout << "Prim 算法选择的边:\n";
    int totalWeight = 0;

    for (int count = 0; count < n; count++) {
        // 步骤1：从未加入 MST 的顶点中，选出 minDist 最小的顶点 u
        int u = -1;
        for (int i = 0; i < n; i++) {
            if (!inMST[i] && (u == -1 || minDist[i] < minDist[u]))
                u = i;
        }

        // 将 u 加入 MST
        inMST[u] = true;

        // 如果不是第一个顶点（parent[u] != -1），输出边
        if (parent[u] != -1) {
            cout << "  (" << parent[u] << ", " << u << ", " << graph[parent[u]][u] << ")\n";
            totalWeight += graph[parent[u]][u];
        }

        // 步骤2：更新 u 的所有邻接点 v 的 minDist
        for (int v = 0; v < n; v++) {
            if (graph[u][v] != 0 && !inMST[v]) { // 存在边且 v 不在 MST 中
                if (graph[u][v] < minDist[v]) {
                    minDist[v] = graph[u][v];
                    parent[v] = u;
                }
            }
        }
    }

    cout << "Prim 总权重: " << totalWeight << "\n\n";
}

// ==================== 并查集（用于 Kruskal）====================
int parent_uf[MAXN];

int find(int x) {
    if (parent_uf[x] != x)
        parent_uf[x] = find(parent_uf[x]); // 路径压缩
    return parent_uf[x];
}

bool unite(int x, int y) {
    x = find(x);
    y = find(y);
    if (x == y) return false;
    parent_uf[x] = y; // 简单合并（无按秩优化，但够用）
    return true;
}

// ==================== Kruskal 算法 ====================
struct Edge {
    int u, v, w;
};

bool edgeCmp(Edge a, Edge b) {
    return a.w < b.w; // 按权重升序排序
}

void kruskal(Edge edges[], int edgeCount, int n) {
    // 初始化并查集
    for (int i = 0; i < n; i++) {
        parent_uf[i] = i;
    }

    // 按权重排序所有边
    sort(edges, edges + edgeCount, edgeCmp);

    cout << "Kruskal 算法选择的边:\n";
    int totalWeight = 0;
    int added = 0;

    for (int i = 0; i < edgeCount; i++) {
        int u = edges[i].u;
        int v = edges[i].v;
        int w = edges[i].w;

        // 如果 u 和 v 不在同一集合，加入该边
        if (unite(u, v)) {
            cout << "  (" << u << ", " << v << ", " << w << ")\n";
            totalWeight += w;
            added++;
            if (added == n - 1) break; // MST 有 n-1 条边
        }
    }

    cout << "Kruskal 总权重: " << totalWeight << "\n\n";
}

// ==================== 主函数 ====================
int main() {
    const int n = 6; // 顶点数：0 ~ 5

    // 构建邻接矩阵（0 表示无边）
    int graph[MAXN][MAXN] = {0};
    auto addEdge = [&](int u, int v, int w) 
    {
        graph[u][v] = w;
        graph[v][u] = w; // 无向图
    };

    addEdge(0, 1, 4);
    addEdge(0, 2, 5);
    addEdge(0, 3, 3);
    addEdge(1, 2, 2);
    addEdge(1, 5, 3);
    addEdge(2, 5, 1);
    addEdge(2, 4, 1);
    addEdge(3, 5, 6);
    addEdge(4, 5, 7);

    // 构建边数组（用于 Kruskal）
    Edge edges[] = {
        {0, 1, 4},
        {0, 2, 5},
        {0, 3, 3},
        {1, 2, 2},
        {1, 5, 3},
        {2, 5, 1},
        {2, 4, 1},
        {3, 5, 6},
        {4, 5, 7}
    };
    int edgeCount = sizeof(edges) / sizeof(edges[0]);

    cout << "=== 最小生成树示例（6 个顶点）===\n\n";

    // 运行 Prim
    prim(graph, n);

    // 运行 Kruskal
    kruskal(edges, edgeCount, n);

    return 0;
}