#include <iostream>
#include <queue>
#include <vector>
using namespace std;

// 1. 使用 struct 定义经典的二叉链表结构
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

// 2. 先序遍历（根 -> 左 -> 右）
void preorder(TreeNode* root) {
    if (!root) return;
    cout << root->val << " ";
    preorder(root->left);
    preorder(root->right);
}

// 3. 中序遍历（左 -> 根 -> 右）
void inorder(TreeNode* root) {
    if (!root) return;
    inorder(root->left);
    cout << root->val << " ";
    inorder(root->right);
}

// 4. 后序遍历（左 -> 右 -> 根）
void postorder(TreeNode* root) {
    if (!root) return;
    postorder(root->left);
    postorder(root->right);
    cout << root->val << " ";
}

// 5. 层序遍历 + 计算深度和最大宽度
void levelOrderWithStats(TreeNode* root, int& depth, int& maxWidth) {
    if (!root) {
        depth = 0;
        maxWidth = 0;
        return;
    }

    queue<TreeNode*> q;
    q.push(root);
    depth = 0;
    maxWidth = 0;

    while (!q.empty()) {
        int levelSize = q.size();
        maxWidth = max(maxWidth, levelSize); // 更新最大宽度
        depth++; // 每一层深度+1

        for (int i = 0; i < levelSize; ++i) {
            TreeNode* node = q.front();
            q.pop();
            cout << node->val << " ";

            if (node->left) q.push(node->left);
            if (node->right) q.push(node->right);
        }
    }
}

// 6. 辅助函数：查找节点是否在子树中（用于 LCA）
bool findNode(TreeNode* root, TreeNode* target) {
    if (!root) return false;
    if (root == target) return true;
    return findNode(root->left, target) || findNode(root->right, target);
}

// 7. 最近公共祖先（LCA）函数（假设所有节点值唯一，且 p 和 q 一定存在于树中）
TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
    if (!root || root == p || root == q) {
        return root;
    }

    TreeNode* left = lowestCommonAncestor(root->left, p, q);
    TreeNode* right = lowestCommonAncestor(root->right, p, q);

    if (left && right) {
        return root; // p 和 q 分别在左右子树，当前 root 是 LCA
    }
    return left ? left : right; // 否则 LCA 在非空一侧
}

// 主函数：构建树、遍历、计算深度宽度、求 LCA
int main() {
    /*
     * 构建如下二叉树：
     *         1
     *        / \
     *       2   3
     *      / \   \
     *     4   5   6
     *        /
     *       7
     *
     * 节点地址用于 LCA 查找（使用指针比较）
     */

    TreeNode* root = new TreeNode(1);
    TreeNode* n2 = new TreeNode(2);
    TreeNode* n3 = new TreeNode(3);
    TreeNode* n4 = new TreeNode(4);
    TreeNode* n5 = new TreeNode(5);
    TreeNode* n6 = new TreeNode(6);
    TreeNode* n7 = new TreeNode(7);

    root->left = n2;
    root->right = n3;
    n2->left = n4;
    n2->right = n5;
    n3->right = n6;
    n5->left = n7;

    // 先序、中序、后序遍历
    cout << "先序遍历: ";
    preorder(root);
    cout << "\n";

    cout << "中序遍历: ";
    inorder(root);
    cout << "\n";

    cout << "后序遍历: ";
    postorder(root);
    cout << "\n\n";

    // 层序遍历 + 深度与宽度
    int depth = 0, maxWidth = 0;
    cout << "层序遍历: ";
    levelOrderWithStats(root, depth, maxWidth);
    cout << "\n";
    cout << "树的深度: " << depth << "\n";
    cout << "树的最大宽度: " << maxWidth << "\n\n";

    // 最近公共祖先（LCA）示例
    TreeNode* p = n4; // 节点 4
    TreeNode* q = n7; // 节点 7
    TreeNode* lca = lowestCommonAncestor(root, p, q);
    cout << "节点 " << p->val << " 和节点 " << q->val << " 的最近公共祖先: " << lca->val << "\n";

    p = n4;
    q = n6;
    lca = lowestCommonAncestor(root, p, q);
    cout << "节点 " << p->val << " 和节点 " << q->val << " 的最近公共祖先: " << lca->val << "\n";

    return 0;
}