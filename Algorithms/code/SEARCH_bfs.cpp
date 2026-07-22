//在bfs中，无法通过和dfs一样的函数递归调用方式等价实现，只能借助于队列
//bfs在本例中意味着先遍历当前节点的所有子节点，在继续遍历。

#include <iostream>
#include <vector>
#include <queue>
using namespace std;

// 图的表示：邻接表
vector<vector<int>> graph;
vector<bool> visited;

/**
 * 使用STL队列实现的广度优先搜索(BFS)
 * @param start 起始节点
 */
void bfs(int start) {
    queue<int> q;
    // 将起始节点标记为已访问并入队
    visited[start] = true;
    q.push(start);

    while (!q.empty()) {
        int node = q.front(); // 获取队首元素
        q.pop();
        cout << "访问节点: " << node << endl;

        // 遍历该节点的所有邻接点
        for (int neighbor : graph[node]) {
            if (!visited[neighbor]) { // 如果未访问过
                visited[neighbor] = true; // 标记为已访问
                q.push(neighbor); // 入队
            }
        }
    }
}

int main() {
    // 假设我们有一个简单的无向图，包含5个节点
    int n = 5;
    graph.resize(n);
    visited.resize(n, false);

    // 添加边到图中（这里创建一个简单的环形图）
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

    cout << "从节点 0 开始的 BFS 遍历顺序：" << endl;
    bfs(0);

    return 0;
}