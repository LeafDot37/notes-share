#include <bits/stdc++.h>
using namespace std;
const int N = 102;

int n = 5;
double q[N] = {0.05, 0.1, 0.05, 0.05, 0.05, 0.1}; // q[0] ~ q[5]
double p[N] = {0, 0.15, 0.1, 0.05, 0.1, 0.2};     // p[1] ~ p[5]

double e[N][N];   // 期望代价（原 s）
int root[N][N];   // 最优根（原 r）
double w[N][N];   // 权重和

void print_tree(int i, int j) {
    if (i > j) return;
    if (i == j) {
        cout << "Node " << i << endl;
        return;
    }
    int r = root[i][j];
    cout << "Root: " << r << " (covers [" << i << "," << j << "])" << endl;
    print_tree(i, r - 1);
    print_tree(r + 1, j);
}

int main() {
    // 初始化 w 和 e 对角线（长度为 0 的子树）
    for (int i = 1; i <= n + 1; i++) {
        e[i][i - 1] = q[i - 1];
        w[i][i - 1] = q[i - 1];
    }

    // 枚举子树长度 len = 1 to n
    for (int len = 1; len <= n; len++) {
        for (int i = 1; i + len - 1 <= n; i++) {
            int j = i + len - 1;
            e[i][j] = 1e9; // 大数
            w[i][j] = w[i][j - 1] + p[j] + q[j]; // 累加：w[i][j] = w[i][j-1] + p[j] + q[j]

            for (int r = i; r <= j; r++) {
                double cost = e[i][r - 1] + e[r + 1][j] + w[i][j];
                if (cost < e[i][j]) {
                    e[i][j] = cost;
                    root[i][j] = r;
                }
            }
        }
    }

    cout << fixed << setprecision(2);
    cout << "Minimum expected search cost: " << e[1][n] << endl;
    cout << "\nTree structure:\n";
    print_tree(1, n);

    return 0;
}