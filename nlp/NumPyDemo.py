
import numpy as np

X = np.array([
    [1,0,2],
    [0,1,1],
    [2,1,0]
])

print("平均值",X.mean(axis=1))

x = np.array([1, 2, 3])
w = np.array([0.2, 0.5, -0.1])

score = np.dot(x, w)
print("得分:", score)
print("矩阵形状:", X.shape)


