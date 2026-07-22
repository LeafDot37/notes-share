#include <iostream>
#include <vector>
using namespace std;

struct Triple {
    int row, col, val;
    Triple(int r = 0, int c = 0, int v = 0) : row(r), col(c), val(v) {}
};

struct SparseMatrix {
    int rows, cols, num;           // 行数、列数、非零元个数
    vector<Triple> data;           // 三元组数组（按行优先顺序存储）

    SparseMatrix(int r = 0, int c = 0) : rows(r), cols(c), num(0) {}
};

// 快速转置算法
SparseMatrix fastTranspose(const SparseMatrix& A) {
    SparseMatrix B(A.cols, A.rows);  // 转置后行列互换
    B.num = A.num;

    if (A.num == 0) return B;

    int m = A.cols;  // 原矩阵列数 = 转置后行数
    vector<int> count(m, 0);   // count[j]：原矩阵第 j 列的非零元个数
    vector<int> start(m, 0);   // start[j]：转置后第 j 行的起始位置

    // Step 1: 统计每列非零元个数
    for (int i = 0; i < A.num; ++i) {
        count[A.data[i].col]++;
    }

    // Step 2: 计算 start 数组（前缀和）
    start[0] = 0;
    for (int j = 1; j < m; ++j) {
        start[j] = start[j - 1] + count[j - 1];
    }

    // Step 3: 构建转置矩阵 B
    B.data.resize(A.num);
    for (int i = 0; i < A.num; ++i) {
        int c = A.data[i].col;          // 原列号 → 转置后的行号
        int r = A.data[i].row;          // 原行号 → 转置后的列号
        int pos = start[c];             // 该元素在 B 中的位置
        B.data[pos] = Triple(c, r, A.data[i].val);
        start[c]++;                     // 下一个同列元素位置+1
    }

    return B;
}

// 辅助函数：打印稀疏矩阵
void printMatrix(const SparseMatrix& M) {
    cout << "rows=" << M.rows << ", cols=" << M.cols << ", num=" << M.num << "\n";
    for (int i = 0; i < M.num; ++i) {
        cout << "(" << M.data[i].row << ", " << M.data[i].col << ", " << M.data[i].val << ")\n";
    }
    cout << "-------------------\n";
}

// 示例
int main() {
    SparseMatrix A(4, 5);
    A.data = {
        Triple(0, 2, 3),
        Triple(1, 4, 5),
        Triple(2, 0, 2),
        Triple(3, 1, 6)
    };
    A.num = A.data.size();

    cout << "原矩阵 A:\n";
    printMatrix(A);

    SparseMatrix B = fastTranspose(A);

    cout << "转置矩阵 B:\n";
    printMatrix(B);

    return 0;
}