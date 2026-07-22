#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>   // 引入 printf 所需的头文件
#include <stdlib.h>  // 引入 exit 所需的头文件

int main() {
    pid_t pid;
    int x = 1;
    
    pid = fork();
    
    if (pid == 0) {  /* Child 子进程 */
        printf("child : x=%d\n", ++x);
        exit(0);
    }
    
    /* Parent 父进程 */
    printf("parent: x=%d\n", --x);
    exit(0);
}