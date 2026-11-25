import numpy as np

A = np.array([
    [10,20,30],
    [40,50,60],
    [70,80,90]
])

print(A.shape)

# 这里变一维了，不保留二维结构
print(A[0])
print(A[0].shape)
print(A[0].ndim)

# 保留二维结构
"""
B[N:M] 是 Python 的切片（Slice）语法。
- N：开始位置，包含 N。
- M：结束位置，不包含 M。
也就是说：从第 N 个索引开始，取到第 M 个索引之前。
"""
print("-------")
print(A[0:1])

