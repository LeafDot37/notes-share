#include <iostream>
#include <chrono>
#include <cmath>
#include <cstring> // for memcpy

using namespace std;
using namespace chrono;

// 全局计数器（每个排序函数内部重置）
long long compareCount, moveCount, passCount;

// 辅助函数：打印数组（前 n 个元素）
void printArray(int arr[], int n) {
    for (int i = 0; i < n; ++i) {
        cout << arr[i] << " ";
    }
    cout << endl;
}

// =============== 1. 直接插入排序 ===============
void InsertSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    for (int i = 1; i < n; ++i) {
        passCount++;
        int key = arr[i];
        moveCount++; // 取出视为一次移动
        int j = i - 1;
        while (j >= 0) {
            compareCount++;
            if (arr[j] > key) {
                arr[j + 1] = arr[j];
                moveCount++;
                j--;
            } else {
                break;
            }
        }
        arr[j + 1] = key;
        moveCount++; // 放回
        // cout << "第 " << passCount << " 趟: "; printArray(arr, n);
    }
}

// =============== 2. 折半插入排序 ===============
void BinaryInsertSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    for (int i = 1; i < n; ++i) {
        passCount++;
        int key = arr[i];
        moveCount++;

        // 折半查找插入位置
        int low = 0, high = i - 1;
        while (low <= high) {
            int mid = (low + high) / 2;
            compareCount++;
            if (key < arr[mid]) {
                high = mid - 1;
            } else {
                low = mid + 1;
            }
        }
        // 将 [low, i-1] 后移一位
        for (int j = i - 1; j >= low; --j) {
            arr[j + 1] = arr[j];
            moveCount++;
        }
        arr[low] = key;
        moveCount++;
        // cout << "第 " << passCount << " 趟: "; printArray(arr, n);
    }
}

// =============== 3. 希尔排序（增量从 n/5 开始） ===============
void ShellSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    int gap = n / 2;
    if (gap == 0) gap = 1;

    while (gap > 0) {
        passCount++;
        for (int i = gap; i < n; ++i) {
            int key = arr[i];
            moveCount++;
            int j = i - gap;
            while (j >= 0) {
                compareCount++;
                if (arr[j] > key) {
                    arr[j + gap] = arr[j];
                    moveCount++;
                    j -= gap;
                } else {
                    break;
                }
            }
            arr[j + gap] = key;
            moveCount++;
        }
        // cout << "增量 " << gap << " 趟: "; printArray(arr, n);
        if (gap == 1) break;
        gap = gap / 2;
        if (gap == 0) gap = 1;
    }
}

// =============== 4. 冒泡排序 ===============
void BubbleSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    bool swapped;
    for (int i = 0; i < n - 1; ++i) {
        passCount++;
        swapped = false;
        for (int j = 0; j < n - 1 - i; ++j) {
            compareCount++;
            if (arr[j] > arr[j + 1]) {
                // 交换
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
                moveCount += 3; // 三次赋值
                swapped = true;
            }
        }
        // cout << "第 " << passCount << " 趟: "; printArray(arr, n);
        if (!swapped) break;
    }
}

// =============== 5. 快速排序（pivot 为最左元素，严格按“先右后左、交替交换”） ===============
void QuickSortImpl(int arr[], int low, int high, long long& comp, long long& mov) {
    if (low < high) {
        int pivot = arr[low];   // 轴值（pivot）
        int lp = low;           // 左指针
        int rp = high;          // 右指针

        while (lp < rp) {
            // 1. 从右往左找第一个 < pivot 的元素
            while (lp < rp) {
                comp++;  // 每次比较都计数
                if (arr[rp] < pivot) {
                    break;
                }
                rp--;
            }
            // 找到后，与左指针位置交换
            arr[lp] = arr[rp];
            mov++;  // 一次赋值（可视为“半次交换”）

            // 2. 从左往右找第一个 > pivot 的元素
            while (lp < rp) {
                comp++;  // 每次比较都计数
                if (arr[lp] > pivot) {
                    break;
                }
                lp++;
            }
            // 找到后，与右指针位置交换
            arr[rp] = arr[lp];
            mov++;  // 一次赋值
        }

        // 循环结束时 lp == rp，此处即 pivot 的最终位置
        arr[lp] = pivot;
        mov++;  // 最后一次赋值

        int pi = lp;

        // 递归处理左右子数组
        QuickSortImpl(arr, low, pi - 1, comp, mov);
        QuickSortImpl(arr, pi + 1, high, comp, mov);
    }
}

void QuickSort(int arr[], int n) {
    compareCount = moveCount = 0;
    passCount = 0;
    QuickSortImpl(arr, 0, n - 1, compareCount, moveCount);
}

// =============== 6. 简单选择排序 ===============
void SelectSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    for (int i = 0; i < n - 1; ++i) {
        passCount++;
        int minIdx = i;
        for (int j = i + 1; j < n; ++j) {
            compareCount++;
            if (arr[j] < arr[minIdx]) {
                minIdx = j;
            }
        }
        if (minIdx != i) {
            int temp = arr[i];
            arr[i] = arr[minIdx];
            arr[minIdx] = temp;
            moveCount += 3;
        }
        // cout << "第 " << passCount << " 趟: "; printArray(arr, n);
    }
}

// =============== 7. 树形选择排序（锦标赛排序） ===============
void TreeSelectSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    if (n <= 1) return;

    // 构建完全二叉树的叶子层大小：2^k >= n
    int treeSize = 1;
    while (treeSize < n) treeSize *= 2;
    int* tree = new int[2 * treeSize]; // tree[treeSize ... treeSize+n-1] 存原数组
    int* index = new int[2 * treeSize]; // 记录叶子来源索引

    // 初始化叶子
    for (int i = 0; i < n; ++i) {
        tree[treeSize + i] = arr[i];
        index[treeSize + i] = i;
    }
    for (int i = n; i < treeSize; ++i) {
        tree[treeSize + i] = INT_MAX; // 哨兵
        index[treeSize + i] = -1;
    }

    // 构建锦标赛树（最小值）
    for (int i = treeSize - 1; i >= 1; --i) {
        int left = tree[2 * i];
        int right = tree[2 * i + 1];
        compareCount++;
        if (left <= right) {
            tree[i] = left;
            index[i] = index[2 * i];
        } else {
            tree[i] = right;
            index[i] = index[2 * i + 1];
        }
    }

    // 逐个选出最小值
    int* result = new int[n];
    bool* used = new bool[n](); // 是否已输出

    for (int round = 0; round < n; ++round) {
        passCount++;
        int minVal = tree[1];
        int pos = index[1];
        result[round] = minVal;
        used[pos] = true;

        // 更新叶子
        tree[treeSize + pos] = INT_MAX;
        index[treeSize + pos] = -1;

        // 向上更新路径
        int p = (treeSize + pos) / 2;
        while (p >= 1) {
            int leftChild = 2 * p;
            int rightChild = 2 * p + 1;
            int leftVal = tree[leftChild];
            int rightVal = tree[rightChild];
            compareCount++;
            if (leftVal <= rightVal) {
                tree[p] = leftVal;
                index[p] = index[leftChild];
            } else {
                tree[p] = rightVal;
                index[p] = index[rightChild];
            }
            p /= 2;
        }
    }

    // 复制回 arr
    for (int i = 0; i < n; ++i) {
        arr[i] = result[i];
        moveCount++;
    }

    delete[] tree;
    delete[] index;
    delete[] result;
    delete[] used;
}

// =============== 8. 堆排序（手写大根堆） ===============
void heapify(int arr[], int n, int i, long long& comp, long long& mov) {
    int largest = i;
    int l = 2 * i + 1;
    int r = 2 * i + 2;

    if (l < n) {
        comp++;
        if (arr[l] > arr[largest]) largest = l;
    }
    if (r < n) {
        comp++;
        if (arr[r] > arr[largest]) largest = r;
    }

    if (largest != i) {
        int temp = arr[i];
        arr[i] = arr[largest];
        arr[largest] = temp;
        mov += 3;
        heapify(arr, n, largest, comp, mov);
    }
}

void HeapSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;

    // 建大根堆（从最后一个非叶节点开始）
    for (int i = n / 2 - 1; i >= 0; --i) {
        heapify(arr, n, i, compareCount, moveCount);
    }

    // 逐个提取堆顶
    for (int i = n - 1; i > 0; --i) {
        passCount++; // 每次提取算一趟
        // 交换堆顶与末尾
        int temp = arr[0];
        arr[0] = arr[i];
        arr[i] = temp;
        moveCount += 3;
        // 调整堆
        heapify(arr, i, 0, compareCount, moveCount);
    }
}

// =============== 9. 归并排序 ===============
void merge(int arr[], int temp[], int left, int mid, int right, long long& comp, long long& mov) {
    int i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right) {
        comp++;
        if (arr[i] <= arr[j]) {
            temp[k++] = arr[i++];
        } else {
            temp[k++] = arr[j++];
        }
        mov++;
    }
    while (i <= mid) {
        temp[k++] = arr[i++];
        mov++;
    }
    while (j <= right) {
        temp[k++] = arr[j++];
        mov++;
    }
    for (i = left; i <= right; ++i) {
        arr[i] = temp[i];
    }
}

void mergeSortImpl(int arr[], int temp[], int left, int right, long long& comp, long long& mov, int& passes) {
    if (left < right) {
        passes++;
        int mid = left + (right - left) / 2;
        mergeSortImpl(arr, temp, left, mid, comp, mov, passes);
        mergeSortImpl(arr, temp, mid + 1, right, comp, mov, passes);
        merge(arr, temp, left, mid, right, comp, mov);
    }
}

void MergeSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    int* temp = new int[n];
    int passes = 0;
    mergeSortImpl(arr, temp, 0, n - 1, compareCount, moveCount, passes);
    passCount = passes;
    delete[] temp;
}

// =============== 10. 基数排序（LSD，假设非负整数） ===============
void RadixSort(int arr[], int n) {
    compareCount = moveCount = passCount = 0;
    if (n <= 1) return;

    // 找最大值
    int maxVal = arr[0];
    for (int i = 1; i < n; ++i) {
        if (arr[i] > maxVal) maxVal = arr[i];
    }

    int* output = new int[n];
    int exp = 1;
    passCount = 0;

    while (maxVal / exp > 0) {
        passCount++; // 每位一趟
        int count[10] = {0};

        // 计数
        for (int i = 0; i < n; ++i) {
            count[(arr[i] / exp) % 10]++;
        }

        // 累加
        for (int i = 1; i < 10; ++i) {
            count[i] += count[i - 1];
        }

        // 构建输出（从后往前稳定）
        for (int i = n - 1; i >= 0; --i) {
            output[count[(arr[i] / exp) % 10] - 1] = arr[i];
            count[(arr[i] / exp) % 10]--;
            moveCount++;
        }

        // 复制回 arr
        for (int i = 0; i < n; ++i) {
            arr[i] = output[i];
        }

        exp *= 10;
    }

    delete[] output;
}

// =============== 主函数 ===============
int main() {
    const int N = 100;
    int original[N] = {
    642, 385, 917, 124, 673, 299, 845, 501, 736, 158,
    427, 963, 210, 555, 802, 334, 689, 123, 777, 444,
    901, 256, 618, 372, 825, 149, 593, 704, 286, 657,
    410, 933, 168, 522, 784, 341, 695, 207, 859, 476,
    132, 588, 943, 305, 661, 219, 774, 437, 890, 153,
    606, 278, 731, 394, 847, 512, 175, 629, 292, 745,
    408, 961, 125, 580, 834, 367, 720, 483, 936, 199,
    652, 315, 768, 431, 884, 247, 600, 363, 816, 479,
    142, 595, 948, 311, 674, 227, 780, 443, 896, 159,
    612, 275, 728, 391, 844, 507, 170, 623, 286, 739
    };
    int arr[N];

    struct SortMethod {
        const char* name;
        void (*func)(int[], int);
    };

    SortMethod methods[] = {
        {"直接插入排序", InsertSort},
        {"折半插入排序", BinaryInsertSort},
        {"希尔排序", ShellSort},
        {"冒泡排序", BubbleSort},
        {"快速排序", QuickSort},
        {"简单选择排序", SelectSort},
        {"树形选择排序", TreeSelectSort},
        {"堆排序", HeapSort},
        {"归并排序", MergeSort},
        {"基数排序", RadixSort}
    };

    int numMethods = sizeof(methods) / sizeof(methods[0]);

    for (int i = 0; i < numMethods; ++i) {
        cout << "\n========== " << methods[i].name << " ==========\n";
        memcpy(arr, original, sizeof(original)); // 恢复原数组

        auto start = high_resolution_clock::now();
        methods[i].func(arr, N);
        auto stop = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(stop - start);

        cout << "排序结果: ";
        printArray(arr, N);
        cout << "比较次数: " << compareCount << endl;
        cout << "移动次数: " << moveCount << endl;
        if (passCount > 0) {
            cout << "趟数: " << passCount << endl;
        }
        cout << "耗时: " << duration.count() << " 微秒" << endl;
    }

    return 0;
}