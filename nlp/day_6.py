import numpy as np

A = np.array([1,0])
B = np.array([0.9,0.1])

# 计算点积
dot_product = np.dot(A,B)

# 计算两个向量的长度
length_a = np.linalg.norm(A)
length_b = np.linalg.norm(B)

similarity = dot_product / (length_a * length_b)

print(f"余弦相似度：{similarity:.4f}")

vocab = ["我","喜欢","狗","猫"]

text = ["我","喜欢","猫"]

vector = []

for v in vocab:
    count = text.count(v)
    vector.append(count)

print(vector)

worlds = ["猫","喜欢","吃","鱼"]

word = "猫"

tf = worlds.count(word)/len(worlds)

print("词频TF:",tf)