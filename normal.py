import numpy as np
import math


def max_minNorm(arr):
    arr=np.array(arr)
    x_max = arr.max() #数组元素中的最大值
    x_min = arr.min() #数组元素中的最小值
    x_mean = arr.mean()
    base= x_mean / len(arr)
    arr = np.around(((arr - x_min + base) / (x_max - x_min)), decimals=4)
    return arr



if __name__ == '__main__':
    arr = [179,175,176,173,178,172,156]
    print(max_minNorm(arr))