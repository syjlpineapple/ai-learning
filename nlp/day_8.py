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
print(X.toarray().round(3))


print(1/3 * (math.log(3/2)+1))