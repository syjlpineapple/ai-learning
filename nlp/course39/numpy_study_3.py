"""
这节课主要学习改变数组形状
reshape()
"""
import numpy as np

A = np.array([1,2,3,4,5,6])
print(A.shape)

# 使用reshape()
B = A.reshape(2,3)
print(B)
print(B.shape)

"""
A = np.array([1, 2, 3, 4, 5, 6])
A.reshape(2, 3)  # 正确
A.reshape(3, 2)  # 正确
A.reshape(6, 1)  # 正确
A.reshape(2, 4)  # 错误
"""

"""
还有一个常用写法：-1
-1 的意思是：让 NumPy 自动计算这一维应该有多长。
"""
A.reshape(2, -1)

