
# 参数值
x = 2.0

# 预期值
y = 4.0

# 权重
w = 1.0

# 学习率
learning_rate = 0.1

# 预测值
prediction = x * w

# 损失
loss = (prediction - y) ** 2

# 损失对权重的导数
gradient = 2 * x * (prediction - y)

w = w - learning_rate * gradient

print("更新后的权重:", w)
