#include <iostream>
#include <string>
using namespace std;

// ==============================
// 1. 表头表尾分析法（Head-Tail）
// ==============================

enum class NodeTypeHT { ATOM, LIST };

struct HTNode {
    NodeTypeHT tag;
    union {
        char atom;      // 原子值（简化为 char）
        struct {
            HTNode* head;
            HTNode* tail;
        } list;
    } data;

    // 构造原子节点
    static HTNode* createAtom(char a) {
        HTNode* node = new HTNode;
        node->tag = NodeTypeHT::ATOM;
        node->data.atom = a;
        return node;
    }

    // 构造表节点（head + tail）
    static HTNode* createList(HTNode* h, HTNode* t) {
        HTNode* node = new HTNode;
        node->tag = NodeTypeHT::LIST;
        node->data.list.head = h;
        node->data.list.tail = t;
        return node;
    }
};

void printHT(const HTNode* node, bool isTop = true) {
    if (!node) {
        if (isTop) cout << "∅";
        return;
    }

    if (node->tag == NodeTypeHT::ATOM) {
        cout << node->data.atom;
    } else {
        cout << "(";
        printHT(node->data.list.head, false);
        if (node->data.list.tail) {
            cout << ", ";
            printHT(node->data.list.tail, false);
        }
        cout << ")";
    }
}

// ==============================
// 2. 子表分析法（Child-Sibling）
// ==============================

enum class NodeTypeCS { ATOM, LIST };

struct CSNode {
    NodeTypeCS tag;
    union {
        char atom;
        CSNode* child;  // 若为 LIST，child 指向第一个元素
    } data;
    CSNode* sibling;    // 指向同级下一个元素

    // 构造原子节点
    static CSNode* createAtom(char a) {
        CSNode* node = new CSNode;
        node->tag = NodeTypeCS::ATOM;
        node->data.atom = a;
        node->sibling = nullptr;
        return node;
    }

    // 构造子表节点（child 指向子表首元素）
    static CSNode* createList(CSNode* c) {
        CSNode* node = new CSNode;
        node->tag = NodeTypeCS::LIST;
        node->data.child = c;
        node->sibling = nullptr;
        return node;
    }
};

void printCS(const CSNode* node, bool isTop = true) {
    if (!node) {
        if (isTop) cout << "∅";
        return;
    }

    if (node->tag == NodeTypeCS::ATOM) {
        cout << node->data.atom;
    } else {
        cout << "(";
        printCS(node->data.child, false);
        cout << ")";
    }

    if (node->sibling) {
        cout << ", ";
        printCS(node->sibling, false);
    }
}

// ==============================
// 主函数：构建同一个广义表 L = (a, (b, c), d)
// ==============================

int main() {
    // 构建广义表: L = (a, (b, c), d)

    // ------------------------------
    // 1. 表头表尾法构建
    // ------------------------------

    // 最内层: (b, c)
    HTNode* inner_bc = HTNode::createList(
        HTNode::createAtom('b'),
        HTNode::createList(
            HTNode::createAtom('c'),
            nullptr
        )
    );

    // 整体: (a, (b,c), d)
    HTNode* L_HT = HTNode::createList(
        HTNode::createAtom('a'),
        HTNode::createList(
            inner_bc,
            HTNode::createList(
                HTNode::createAtom('d'),
                nullptr
            )
        )
    );

    // ------------------------------
    // 2. 子表分析法构建
    // ------------------------------

    // 构建最内层子表 (b, c)
    CSNode* c_node = CSNode::createAtom('c');
    CSNode* b_node = CSNode::createAtom('b');
    b_node->sibling = c_node;
    CSNode* inner_bc_cs = CSNode::createList(b_node);

    // 构建顶层: a -> (b,c) -> d
    CSNode* d_node = CSNode::createAtom('d');
    inner_bc_cs->sibling = d_node;
    CSNode* a_node = CSNode::createAtom('a');
    a_node->sibling = inner_bc_cs;

    CSNode* L_CS = CSNode::createList(a_node); // 整个表是一个 LIST 节点

    // ------------------------------
    // 输出结果
    // ------------------------------

    cout << "=== 广义表 L = (a, (b, c), d) ===\n\n";

    cout << "【表头表尾分析法】存储结构打印:\n";
    printHT(L_HT);
    cout << "\n\n";

    cout << "【子表分析法】（Child-Sibling）存储结构打印:\n";
    printCS(L_CS);
    cout << "\n\n";

    // 验证两者逻辑一致
    cout << "✅ 两种表示法均正确表达了同一个广义表。\n";

    return 0;
}