//这是基于栈的深度优先搜索实现
//正常深度搜索还可以通过函数递归调用的方式实现,但是其本质也是基于栈结构
//dfs在本例中意味着，先去遍历当前节点的子节点，并继续遍历子节点的子节点，再进行回溯
#include <iostream>
#include <vector>
#include <stack>
using namespace std;

// 图的表示：邻接表
vector<vector<int>> graph;
vector<bool> visited;

/**
 * 使用 STL 栈实现的深度优先搜索（DFS）
 * @param start 起始节点
 */
void dfs(int start) {
    stack<int> s;
    s.push(start);
    
    while (!s.empty()) {
        int node = s.top();
        s.pop();
        
        // 如果已经访问过，跳过（避免重复处理）
        if (visited[node]) continue;
        
        // 标记为已访问并输出
        visited[node] = true;
        cout << "访问节点: " << node << endl;
        
        // 将所有未访问的邻接点压入栈（按自然顺序）
        // 注意：由于栈是后进先出，实际会先访问最后一个邻接点
        // 如果希望先访问编号小的节点，可逆序压入；此处保持简洁
        for (int neighbor : graph[node]) {
            if (!visited[neighbor]) {
                s.push(neighbor);
            }
        }
    }
}

int main() {
    // 与 BFS 示例完全相同的图结构：5 个节点的环形无向图
    int n = 5;
    graph.resize(n);
    visited.resize(n, false);

    // 构建无向图（与 BFS 示例一模一样）
    graph[0].push_back(1);
    graph[1].push_back(0);
    
    graph[1].push_back(2);
    graph[2].push_back(1);
    
    graph[2].push_back(3);
    graph[3].push_back(2);
    
    graph[3].push_back(4);
    graph[4].push_back(3);
    
    graph[4].push_back(0);
    graph[0].push_back(4);

    cout << "从节点 0 开始的 DFS 遍历顺序：" << endl;
    dfs(0);

    return 0;
}