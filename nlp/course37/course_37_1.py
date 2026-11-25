import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

texts = [
    "手机电池不耐用",
    "手机续航能力很差",
    "手机屏幕显示效果很好",
    "这款手机特别费电"
]

def chinese_tokenizer(text):
    return jieba.cut(text)

vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)

tfidf_matrix = vectorizer.fit_transform(texts)

print(tfidf_matrix.shape)
print(vectorizer.get_feature_names_out())

similarity_matrix = cosine_similarity(tfidf_matrix)
print(np.round(similarity_matrix,3))


query = "手机续航很差"
query_vector = vectorizer.transform([query])
score = cosine_similarity(query_vector,tfidf_matrix)
print("score:\n",score)

scores = score[0]
# 排序
rank_indices = np.argsort(scores)[::-1]
print("\n搜索内容：", query)
print("\n搜索结果：")

for index in rank_indices:
    print(
        "评论：", texts[index],
        "相似度：", round(scores[index], 3)
    )

