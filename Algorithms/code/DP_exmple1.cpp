#include <bits/stdc++.h>
using namespace std;
const int N = 102;

int n = 4;
int h[N] = {0, 10, 20, 30, 40};
int t[N] = {0, 20, 30, 40, 30};
int s[N][N] = {0};
int r[N][N] = {0};

void ppout(int x,int y)
{
    if(x==y) return;
    int w = r[x][y];
    cout << w << endl;
    ppout(x,w);
    ppout(w+1,y);
}

int main()
{
    memset(s,127,sizeof(s));
    for (int i = 1; i <= n; i++)
    {
        s[i][i] = 0;
        r[i][i] = i;
    }
    for (int k = 1; k <= n-1; k++)
    {
        for (int i = 1; i <= n - 1; i++)
        {
            int j = i + k;
            if (j > n)
                break;

            for (int w = i; w <= j - 1; w++)
            {
                int ds = s[i][w] + s[w + 1][j] + h[i] * t[w] * t[j];
                if(s[i][j] > ds)
                {
                    r[i][j] = w;
                    s[i][j] = ds;
                }
            }
        }
    }
    cout << s[1][n] << endl;
    ppout(1,n);
}