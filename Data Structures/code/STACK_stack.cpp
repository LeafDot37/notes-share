#include <iostream>
#include <cstdlib>
#include <stdexcept>
using namespace std;

// 栈结构体
struct Stack 
{
    int* data;
    int capacity;
    int top;  // -1 表示空栈
};

// 初始化栈
void initStack(Stack* s, int initialCapacity = 10) 
{
    s->data = (int*)malloc(initialCapacity * sizeof(int));
    if (!s->data) 
    {
        cerr << "内存分配失败！\n";
        exit(1);
    }
    s->capacity = initialCapacity;
    s->top = -1;
}

// 销毁栈
void destroyStack(Stack* s) 
{
    free(s->data);
    s->data = nullptr;
    s->capacity = 0;
    s->top = -1;
}

// 判断是否为空
bool isEmpty(const Stack* s) 
{
    return s->top == -1;
}

// 获取当前大小
int size(const Stack* s) 
{
    return s->top + 1;
}

// 扩容
void resize(Stack* s) 
{
    int newCap = s->capacity * 2;
    int* newData = (int*)realloc(s->data, newCap * sizeof(int));
    if (!newData) {
        cerr << "扩容失败！\n";
        exit(1);
    }
    s->data = newData;
    s->capacity = newCap;
    cout << "[提示] 栈已扩容至 " << newCap << "\n";
}

// 入栈
void push(Stack* s, int value) 
{
    if (s->top + 1 >= s->capacity) 
    {
        resize(s);
    }
    s->data[++(s->top)] = value;
}

// 出栈
void pop(Stack* s) {
    if (isEmpty(s)) {
        throw out_of_range("pop(): 栈为空");
    }
    --(s->top);
}

// 查看栈顶
int top(const Stack* s) {
    if (isEmpty(s)) {
        throw out_of_range("top(): 栈为空");
    }
    return s->data[s->top];
}

int main() {
    Stack s;
    initStack(&s, 3);

    cout << "=== 简易栈演示程序 ===\n";
    cout << "支持操作：\n";
    cout << "  p <数字>  : 入栈\n";
    cout << "  o         : 出栈\n";
    cout << "  t         : 查看栈顶\n";
    cout << "  s         : 显示栈大小\n";
    cout << "  q         : 退出\n\n";

    char op;
    while (cin >> op && op != 'q') {
        try {
            if (op == 'p') {
                int x;
                cin >> x;
                push(&s, x);
                cout << "✅ 已入栈: " << x << "\n";
            }
            else if (op == 'o') {
                int val = top(&s);
                pop(&s);
                cout << "📤 弹出: " << val << "\n";
            }
            else if (op == 't') {
                cout << "🔍 栈顶: " << top(&s) << "\n";
            }
            else if (op == 's') {
                cout << "📊 当前大小: " << size(&s) << "\n";
            }
            else {
                cout << "❓ 无效命令，请重试。\n";
            }
        }
        catch (const exception& e) {
            cerr << "⚠️ 错误: " << e.what() << "\n";
        }
        cout << "\n";
    }

    destroyStack(&s);
    cout << "👋 程序结束，栈已释放。\n";
    return 0;
}