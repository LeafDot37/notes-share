#include <iostream>
#include <stack>
using namespace std;
int main() {
   stack<int> s; // 定义一个int类型的栈
   int sum = 0;
   // 入栈操作
   for (int i = 1; i <= 10; i++) {
       s.push(i);
   }
   // 输出栈的大小
   cout << s.size() << endl;
   // 当栈不为空时，进行出栈操作，并计算总和
   while (!s.empty()) {
       sum += s.top();
       s.pop();
   }
   // 输出总和
   cout << sum << endl;
   return 0;
}