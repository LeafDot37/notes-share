#include <bits/stdc++.h>
using namespace std;
const int N = 102;
const int X = 102;
int n = 4;               // 物品数量
int x = 8;               // 背包容量

// 物品价值 v[1..n] 和重量 w[1..n]（1-indexed）
int v[N] = {0, 10, 40, 30, 50};   // v[0] unused
int w[N] = {0, 5,  4,  6,  3};    // w[0] unused
int e[N][X] = {0};


int main()
{
    for(int i=0;i<=n;i++)
    {
        e[i][0] = 0;
    }
    for(int i=0;i<=x;i++)
    {
        e[0][i] = 0;
    }
    for(int i=1;i<=n;i++)
    {
        for(int j=1;j<=x;j++)
        {
            if(j<w[i])
            {
                e[i][j] = e[i-1][j];
                continue;
            }
            e[i][j] = max(e[i-1][j],e[i-1][j-w[i]]+v[i]);
        }
    }
    cout << e[n][x];
}