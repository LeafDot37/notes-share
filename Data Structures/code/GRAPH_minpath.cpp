#include <iostream>
#include <vector>
#include <climits>
using namespace std;

const int MAXN = 100;
const int INF = 1e9; // 表示无穷大（足够大，但避免溢出）

// 打印距离矩阵（用于 Floyd）
void printDist(int dist[MAXN][MAXN], int n) {
    cout << "  ";
    for (int j = 0; j < n; j++) cout << j << " ";
    cout << "\n";
    for (int i = 0; i < n; i++) {
        cout << i << " ";
        for (int j = 0; j < n; j++) {
            if (dist[i][j] == INF)
                cout << "∞ ";
            else
                cout << dist[i][j] << " ";
        }
        cout << "\n";
    }
}

// ==================== Dijkstra 算法（单源最短路径）====================
void dijkstra(int graph[MAXN][MAXN], int n, int start) {
    vector<int> dist(n, INF);      // 距离数组
    vector<bool> visited(n, false); // 是否已确定最短路径
    vector<int> parent(n, -1);     // 路径回溯（可选）

    dist[start] = 0;

    for (int count = 0; count < n; count++) {
        // 找未访问中距离最小的顶点 u
        int u = -1;
        for (int i = 0; i < n; i++) {
            if (!visited[i] && (u == -1 || dist[i] < dist[u]))
                u = i;
        }

        if (dist[u] == INF) break; // 剩余点不可达
        visited[u] = true;

        // 松弛操作：更新 u 的所有邻接点
        for (int v = 0; v < n; v++) {
            if (graph[u][v] != 0 && !visited[v]) { // 存在边
                if (dist[u] + graph[u][v] < dist[v]) {
                    dist[v] = dist[u] + graph[u][v];
                    parent[v] = u;
                }
            }
        }
    }

    // 输出结果
    cout << "Dijkstra（源点 " << start << "）:\n";
    for (int i = 0; i < n; i++) {
        if (i == start) continue;
        cout << "  到顶点 " << i << ": ";
        if (dist[i] == INF)
            cout << "不可达\n";
        else
            cout << dist[i] << "\n";
    }
    cout << "\n";
}

// ==================== Floyd-Warshall 算法（全源最短路径）====================
void floydWarshall(int graph[MAXN][MAXN], int n) {
    // 初始化距离矩阵
    int dist[MAXN][MAXN];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j)
                dist[i][j] = 0;
            else if (graph[i][j] != 0)
                dist[i][j] = graph[i][j];
            else
                dist[i][j] = INF;
        }
    }

    // 动态规划：枚举中间点 k
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (dist[i][k] < INF && dist[k][j] < INF) // 避免溢出
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
            }
        }
    }

    // 输出结果
    cout << "Floyd-Warshall（所有点对最短路径）:\n";
    printDist(dist, n);
}

// ==================== 主函数 ====================
int main() {
    const int n = 5; // 5 个顶点：0 ~ 4

    // 构建邻接矩阵（0 表示无边）
    int graph[MAXN][MAXN] = {0};

    // 添加有向边：graph[u][v] = weight
    graph[0][1] = 10;
    graph[0][2] = 3;
    graph[1][3] = 1;
    graph[2][4] = 5;
    graph[3][2] = 7;
    graph[3][4] = 2;

    cout << "=== 最短路径算法示例 ===\n\n";

    // 运行 Dijkstra（以顶点 0 为源点）
    dijkstra(graph, n, 0);

    // 运行 Floyd-Warshall
    floydWarshall(graph, n);

    return 0;
}