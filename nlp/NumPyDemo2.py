import numpy as np

X = np.array([[3, 0],
              [0, 2],
              [2, 1]
              ])

w = np.array([2, -1])
scores = X @ w
print(scores.shape)
print(X.shape)


