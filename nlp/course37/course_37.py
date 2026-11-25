"""
1. 什么是语义搜索，区分于关键词搜索
2. Embedding（文本嵌入）
  Embedding 的核心思想：把一段文本转换成一组数字，让意思相近的文本在向量空间中更加接近。
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

vector_a = np.array([[0.82,0.75,0.21]])
vector_b = np.array([[0.80,0.77,0.24]])
vector_c = np.array([[0.12,0.25,0.91]])

similarity_ab = cosine_similarity(vector_a, vector_b)
similarity_ac = cosine_similarity(vector_a, vector_c)

print(similarity_ab[0][0])
print(similarity_ac[0][0])