import math

documents = [
    ["猫","喜欢","吃","鱼"],
    ["狗","喜欢","吃","肉"]
]

N = len(documents)
word = "猫"

# 计算包含该词的文档数量
df = sum(word in doc for doc in documents)

idf = math.log((N+1)/(df+1)) + 1
print(idf)

doc = documents[0]
tf = doc.count(word) / len(doc)
print(tf)

tf_idf = tf * idf

print("文档总数:", N)
print("文档频率:", df)
print("TF:", tf)
print("IDF:", round(idf, 3))
print("TF-IDF:", round(tf_idf, 3))