from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


BASE_PATH = Path(__file__).parent.parent
data_path = BASE_PATH / "data" / "waimai_10K.csv"

df = pd.read_csv(data_path)
# 从文件提取评论
reviews = df["review"].astype(str).tolist()
print("评论数：",len(reviews))

# 2.加载中文Embedding模型
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 3. 把所有评论转换为向量
# normalize_embeddings=True 把每条评论对应的向量归一化为长度1
print("\n正在生成评论向量，请稍等...")
reviews_embedding = model.encode(
    reviews,
    batch_size=64,
    normalize_embeddings=True,
    show_progress_bar=True,
)
print("评论向量形状：", reviews_embedding.shape)

query = "送餐速度太慢了"

query_text = "为这个句子生成表示以用于检索相关文章："+query

query_embedding = model.encode([query_text],normalize_embeddings=True)

# query_embedding[0] 二维变一维, 如果要保留二维：query_embedding[0:1]
similarity_scores = np.dot(
    reviews_embedding,
    query_embedding[0],
)

# 注意这里排序原始index不会变
top_indices = np.argsort(similarity_scores)[::-1][:5]

print("\n查询内容：", query)
print("\n最相似的5条评论：")

for rank, index in enumerate(top_indices, start=1):
    print("-" * 50)
    print("排名：", rank)
    print("评论：", reviews[index])
    print("相似度：", round(float(similarity_scores[index]), 4))
    print("真实标签：", df.iloc[index]["label"])




