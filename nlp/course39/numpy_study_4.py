"""
转置.T
转置就是： 把矩阵的行和列交换
"""
import numpy as np

A = np.array([
    [1,2,3],
    [4,5,6],
])
print("原始矩阵：\n",A)
print("原始形状：\n",A.shape)

print("\n转置矩阵\n",A.T)
print("转置形状：",A.T.shape)

"""
一个非常重要的细节：一维数组转置不会改变形状
因为一维数组没有明确的行和列，.T 对它不起作用。
"""
B = np.array([1, 2, 3, 4, 5, 6])
print(B.shape)
print(B.T.shape)


