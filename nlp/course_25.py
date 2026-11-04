import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# 找出每条评论中权重最高的词

documents = [
    "phone camera good quality",
    "phone battery good",
    "camera quality excellent",
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)

words = vectorizer.get_feature_names_out()

"""

row.max()       # 最大值：0.9
np.max(row)     # 最大值
row.argmax()    # 最大值的索引：2
np.argmax(row)  # 最大值的索引：2
"""

for i in range(len(documents)):
    row = X.toarray()[i]
    print("----",row.max())
    max_weight = np.max(row)
    for index, weight in enumerate(row):
        if np.isclose(weight, max_weight):
            print(f"第{i+1}条评论中权重最高的词",words[index],weight)

