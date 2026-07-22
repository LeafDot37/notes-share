#include <bits/stdc++.h>
using namespace std;
const int N = 102;
int n,m;
char u[N];
char v[N];
int s[N][N] = {0};
int b[N][N] = {0};
void ppout(int x,int y)
{
    if(x==0||y==0) return;
    if(b[x][y]==1)
    {
        ppout(x-1,y-1);
        cout << u[x] << " ";
    }
    else
    {
        if(b[x][y] == 2) ppout(x-1,y);
        else ppout(x,y-1);
    }
}
int main()
{
    // 🔹 静态赋值两个字符串（修改这里即可更换测试用例）
    string str1 = "ABCDGH";
    string str2 = "AEDFHR";

    n = str1.length();
    m = str2.length();

    // 复制到 1-indexed 数组
    for (int i = 1; i <= n; ++i) u[i] = str1[i - 1];
    for (int i = 1; i <= m; ++i) v[i] = str2[i - 1];
    for(int i=0;i<=n;i++)
    {
        s[i][0] = 0;
    }
    for(int i=0;i<=m;i++)
    {
        s[0][i] = 0;
    }
    for(int i=1;i<=n;i++)
    {
        for(int j=1;j<=m;j++)
        {
            if(u[i]==v[j])
            {
                s[i][j] = s[i-1][j-1] + 1;
                b[i][j] = 1;
            }
            else
            {
                if(s[i-1][j] > s[i][j-1])
                {
                    s[i][j] = s[i-1][j];
                    b[i][j] = 2;
                }
                else
                {
                    s[i][j] = s[i][j-1];
                    b[i][j] = 3;
                }
            }
        }
    }
    cout << s[n][m] << endl;
    ppout(n,m);
}