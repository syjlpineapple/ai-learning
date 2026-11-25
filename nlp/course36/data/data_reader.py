from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
# CSV 与当前 Python 文件在同一个目录
csv_path = BASE_DIR / "waimai_10k.csv"
csv = pd.read_csv(csv_path)

texts = csv["review"].tolist()
labels = csv["label"].tolist()


df = pd.read_csv(csv_path, encoding="utf-8")

print("========== 数据基本信息 ==========")
print("数据总量：", len(df))
print("字段：", df.columns.tolist())

print("\n========== 标签分布 ==========")
print(df["label"].value_counts(dropna=False))

print("\n========== 缺失值 ==========")
print(df.isnull().sum())

print("\n========== 重复评论 ==========")
print("重复评论数量：", df["review"].duplicated().sum())

print("\n========== 空评论 ==========")
print("空评论数量：", df["review"].fillna("").str.strip().eq("").sum())

print("\n========== 评论长度 ==========")
print(df["review"].fillna("").str.len().describe())

print("\n========== 随机抽取10条 ==========")
print(df.sample(min(10, len(df)), random_state=42))



from sklearn.model_selection import train_test_split

X = df["review"]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\n========== 数据集划分 ==========")
print("训练集数量：", len(X_train))
print("测试集数量：", len(X_test))

print("\n训练集标签分布：")
print(y_train.value_counts())

print("\n测试集标签分布：")
print(y_test.value_counts())