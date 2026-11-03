import math

from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat like fish",
    "dog like meat"
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)

print("词汇表")
print(vectorizer.get_feature_names_out())

print("矩阵形状：")
print(X.shape)

print("TF-IDF矩阵：")
# .round 保留三位小数
print(X.toarray().round(3))



# 自己算
print(1/3 * (math.log(3/2)+1))

# 扩展，对不上为什么？ 原因是：TfidfVectorizer 默认不仅计算 TF-IDF，还会对每篇文档的向量进行归一化（Normalization）。
