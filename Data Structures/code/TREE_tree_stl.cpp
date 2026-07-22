//本例中采用了数字作为节点的方式，在实际操作中，可以为复杂数据类型开一个数组，用数字代表下标进行中间转化，
//这样可以避免大数据的传输

#include <iostream>
#include <vector>
#include <queue>
#include <algorithm>
using namespace std;

const int N = 102; // 节点编号 1~100

vector<int> s[N]; // s[u]：u 的孩子列表（最多两个，按左、右顺序）
int f[N] = {0};   // f[u]：u 的父节点
bool visited[N];
int depth[N];

// 前序遍历：根 -> 左 -> 右
void preorder(int u) {
    if (u == 0) return;
    cout << u << " ";
    if (s[u].size() > 0) preorder(s[u][0]); // 左孩子
    if (s[u].size() > 1) preorder(s[u][1]); // 右孩子
}

// 中序遍历：左 -> 根 -> 右
void inorder(int u) {
    if (u == 0) return;
    if (s[u].size() > 0) inorder(s[u][0]); // 左
    cout << u << " ";
    if (s[u].size() > 1) inorder(s[u][1]); // 右
}

// 后序遍历：左 -> 右 -> 根
void postorder(int u) {
    if (u == 0) return;
    if (s[u].size() > 0) postorder(s[u][0]); // 左
    if (s[u].size() > 1) postorder(s[u][1]); // 右
    cout << u << " ";
}

// 层序遍历，并计算高度与最大宽度
void levelOrderWithStats(int root) {
    for (int i = 1; i < N; ++i) {
        visited[i] = false;
        depth[i] = 0;
    }

    queue<int> q;
    q.push(root);
    visited[root] = true;
    depth[root] = 1;

    int height = 0;
    int maxWidth = 0;

    while (!q.empty()) {
        int size = q.size();
        maxWidth = max(maxWidth, size);
        height++;

        for (int i = 0; i < size; ++i) {
            int u = q.front();
            q.pop();
            cout << u << " ";

            for (int v : s[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    depth[v] = depth[u] + 1;
                    q.push(v);
                }
            }
        }
    }
    cout << "\n";
    cout << "树的高度: " << height << "\n";
    cout << "树的最大宽度: " << maxWidth << "\n";
}

// LCA 函数：基于父指针上移
int lca(int u, int v) {
    // 提升较深的节点
    while (depth[u] > depth[v]) u = f[u];
    while (depth[v] > depth[u]) v = f[v];
    // 同时上移直到相同
    while (u != v) {
        u = f[u];
        v = f[v];
    }
    return u;
}

// 初始化目标树
void initTree() {
    // 清空原有数据
    for (int i = 0; i < N; ++i) {
        s[i].clear();
        f[i] = 0;
    }

    // 添加边：父 -> 子
    s[1].push_back(2); f[2] = 1;
    s[1].push_back(3); f[3] = 1;

    s[2].push_back(4); f[4] = 2;
    s[2].push_back(5); f[5] = 2;

    s[3].push_back(6); f[6] = 3;

    s[5].push_back(7); f[7] = 5;

    // 注意：s[u] 的顺序决定了“左”和“右”
    // 这里我们按输入顺序视为：先左后右
}

int main() {
    initTree(); // 自动构建树

    cout << "=== 二叉树遍历与LCA演示 ===\n\n";

    cout << "层序遍历: ";
    levelOrderWithStats(1);

    cout << "前序遍历: ";
    preorder(1);
    cout << "\n";

    cout << "中序遍历: ";
    inorder(1);
    cout << "\n";

    cout << "后序遍历: ";
    postorder(1);
    cout << "\n\n";

    // 演示两个 LCA 查询
    int x1 = 4, y1 = 7;
    int w1 = lca(x1, y1);
    cout << "LCA(" << x1 << ", " << y1 << ") = " << w1 << "\n";

    int x2 = 4, y2 = 6;
    int w2 = lca(x2, y2);
    cout << "LCA(" << x2 << ", " << y2 << ") = " << w2 << "\n";

    return 0;
}