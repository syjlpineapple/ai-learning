
# 目标值
y = 6
# 学习率
lr = 0.1
# 参数
x = 2

# 权重
w = 1.0

for i in range(10):
    y_pred = w * x
    loss = (y_pred - y) ** 2
    gradient = 2 * x * (w * x -y)
    w = w - lr * gradient
    print(f"------------------第{i+1}次------------------------")
    print("预测值:",y_pred)
    print("损失:",loss)
    print("梯度:",gradient)
    print("更新后的w:",w)


