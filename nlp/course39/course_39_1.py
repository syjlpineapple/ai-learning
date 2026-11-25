import pandas as pd
from sentence_transformers import SentenceTransformer

# 1. 加载真实外卖评论数据
DATA_PATH = r"D:\Lee\AICODE\ai-learning\nlp\data\waimai_10k.csv"

df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

reviews = df["review"].astype(str).tolist()

print("评论总数：", len(reviews))

# 2. 加载中文 Embedding 模型
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

# 3. 将所有评论转换成向量
print("\n正在生成评论向量，请稍等...")

review_embeddings = model.encode(
    reviews,
    batch_size=64,
    normalize_embeddings=True,
    show_progress_bar=True
)

# 4. 查看向量形状
print("\n向量矩阵形状：", review_embeddings.shape)

# 5. 查看第一条评论及其向量
print("\n第一条评论：", reviews[0])
print("第一条评论向量形状：", review_embeddings[0].shape)
print("第一条评论向量前6个值：", review_embeddings[0][:6])
