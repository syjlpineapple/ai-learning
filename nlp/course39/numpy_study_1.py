import numpy as np
"""
这节课补充numpy知识
很重要，学习后面的地基
"""

# 1. 一维数组
A = np.array([1,2,3,4,5,6])
print(A)
print(A.shape)
print(A.ndim)

# 2. 二维数组
B = np.array([
[1,2,3,4,5,6]
])
print(B)
print(B.shape)
print(B.ndim)

C = np.array([
    [1,2,3],
    [4,5,6],
])
print(C.shape)
print(C.ndim)