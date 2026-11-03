import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat likes fish",
    "dog likes meat",
    "cat likes meat"
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)
words = vectorizer.get_feature_names_out()

print(words)
print(X.toarray().round(3))

# 提取第一篇文档
row = X.toarray()[0]
max_weight = np.max(row)

for i,weight in enumerate(row):
    if weight == max_weight:
        print(words[i],weight)
