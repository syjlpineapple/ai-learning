# 第24课 找出TF-IDF权重最高的词
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat likes fish",
    "dog likes meat"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

words = vectorizer.get_feature_names_out()

print(words)
print(X.toarray().round(3))

row = X.toarray()[0]

print(row)

index = np.argmax(row)
print(index)
print(words[index])
print(row[index])

max_weight = row.max()

"""
enumerate() 是 Python 自带的函数。
它可以在遍历列表时，同时获取元素的索引和元素本身。
"""
for i, weight in enumerate(row):
    if np.isclose(weight, max_weight):
        print(words[i], weight)
print("----------------------------")

for i in row:
    if np.isclose(i, max_weight):
        print(i)

#############################################################################################

