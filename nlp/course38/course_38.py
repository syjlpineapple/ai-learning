import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 加载中文embedding模型
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
texts = [
    "手机续航很差",
    "手机电池不耐用",
    "手机屏幕显示效果很好",
    "这款手机特别费电"
]

# 将文本转换成Embedding向量
embeddings = model.encode(
    texts,
    normalize_embeddings=True
)

print("向量矩阵形状：",embeddings.shape)

similarity_matrix = cosine_similarity(embeddings)

print("\n文本相似度矩阵：")
print(np.round(similarity_matrix, 3))
