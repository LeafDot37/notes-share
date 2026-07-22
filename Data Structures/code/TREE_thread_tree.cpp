#include <iostream>
using namespace std;

struct ThreadNode {
    int data;
    ThreadNode *left, *right;
    int ltag, rtag;

    ThreadNode(int val) : data(val), left(nullptr), right(nullptr), ltag(0), rtag(0) {}
};

ThreadNode* pre = nullptr;

// 普通递归中序遍历（用于验证树是否建对）
void normalInOrder(ThreadNode* root) {
    if (!root) return;
    normalInOrder(root->left);
    cout << root->data << " ";
    normalInOrder(root->right);
}

// 中序线索化
void inOrderThreading(ThreadNode* p) {
    if (!p) return;
    inOrderThreading(p->left);

    if (p->left == nullptr) {
        p->left = pre;
        p->ltag = 1;
    }
    if (pre && pre->right == nullptr) {
        pre->right = p;
        pre->rtag = 1;
    }
    pre = p;

    inOrderThreading(p->right);
}

// 构建正确的二叉树（重点！）
ThreadNode* buildCorrectTree() {
    /*
            1
           / \
          2   3
         / \   \
        4   5   6
           /
          7
    */
    ThreadNode* n1 = new ThreadNode(1);
    ThreadNode* n2 = new ThreadNode(2);
    ThreadNode* n3 = new ThreadNode(3);
    ThreadNode* n4 = new ThreadNode(4);
    ThreadNode* n5 = new ThreadNode(5);
    ThreadNode* n6 = new ThreadNode(6);
    ThreadNode* n7 = new ThreadNode(7);

    // 关键：left 和 right 必须指向孩子！
    n1->left = n2;   // 1 的左孩子是 2
    n1->right = n3;  // 1 的右孩子是 3

    n2->left = n4;   // 2 的左孩子是 4
    n2->right = n5;  // 2 的右孩子是 5

    n3->right = n6;  // 3 的右孩子是 6

    n5->left = n7;   // 5 的左孩子是 7

    return n1;
}

ThreadNode* createThreadedTreeWithHeader(ThreadNode* root) {
    if (!root) {
        ThreadNode* h = new ThreadNode(0);
        h->left = h->right = h;
        h->ltag = h->rtag = 1;
        return h;
    }

    ThreadNode* header = new ThreadNode(0);
    header->ltag = 0;
    header->rtag = 1;
    header->left = root;
    header->right = header; // 临时

    pre = header; // ⚠️ 必须设为 header！
    inOrderThreading(root);

    // 连接末节点到 header
    pre->right = header;
    pre->rtag = 1;
    header->right = pre;

    return header;
}

void traverseWithHeader(ThreadNode* header) {
    cout << "中序线索遍历结果: ";
    if (header->left == header) {
        cout << "(空)" << endl;
        return;
    }

    // 关键：找到中序第一个节点
    ThreadNode* p = header->left; // 根
    while (p->ltag == 0) {        // 只要还能往左孩子走，就走
        p = p->left;
    }

    while (p != header) {
        cout << p->data << " ";
        if (p->rtag == 1) {
            p = p->right; // 线索：直接后继
        } else {
            // 进入右子树，并找到其最左节点
            p = p->right;
            while (p->ltag == 0) {
                p = p->left;
            }
        }
    }
    cout << endl;
}

int main() {
    ThreadNode* root = buildCorrectTree();

    // 先验证原始树是否正确！
    cout << "普通中序遍历（验证树结构）: ";
    normalInOrder(root);
    cout << endl;

    // 再线索化并遍历
    ThreadNode* header = createThreadedTreeWithHeader(root);
    traverseWithHeader(header);

    return 0;
}