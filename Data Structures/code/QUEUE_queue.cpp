#include <iostream>
using namespace std;

const int MAX_SIZE = 100;  // 队列最大容量

struct Queue {
    int data[MAX_SIZE];
    int front;   // 队首下标
    int rear;    // 队尾下标
    int size;    // 当前元素个数

    // 初始化队列
    void init() {
        front = 0;
        rear = -1;
        size = 0;
    }

    // 入队
    void enqueue(int value) {
        if (isFull()) {
            cout << "队列已满，无法入队！\n";
            return;
        }
        rear = (rear + 1) % MAX_SIZE;
        data[rear] = value;
        size++;
        cout << "入队: " << value << endl;
    }

    // 出队
    void dequeue() {
        if (isEmpty()) {
            cout << "队列为空，无法出队！\n";
            return;
        }
        cout << "出队: " << data[front] << endl;
        front = (front + 1) % MAX_SIZE;
        size--;
    }

    // 查看队首元素
    int getFront() {
        if (isEmpty()) {
            cout << "队列为空！\n";
            return -1;
        }
        return data[front];
    }

    // 判断是否为空
    bool isEmpty() {
        return size == 0;
    }

    // 判断是否已满
    bool isFull() {
        return size == MAX_SIZE;
    }

    // 获取当前元素数量
    int getSize() {
        return size;
    }
};

// 示例：主函数演示
int main() {
    Queue q;
    q.init();  // 必须先初始化！

    q.enqueue(5);
    q.enqueue(15);
    q.enqueue(25);

    cout << "队首元素: " << q.getFront() << endl;
    cout << "当前大小: " << q.getSize() << endl;

    q.dequeue();
    q.dequeue();

    q.enqueue(35);
    q.enqueue(45);

    // 清空队列
    while (!q.isEmpty()) {
        q.dequeue();
    }

    return 0;
}