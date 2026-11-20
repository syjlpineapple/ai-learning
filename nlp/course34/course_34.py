"""
朴素贝叶斯
"""
import jieba
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

def chinese_tokenizer(text):
    return jieba.lcut(text)

texts = [
    "这个手机非常好用",
    "手机质量非常好",
    "电池续航特别棒",
    "拍照效果非常清晰",
    "这个手机值得购买",
    "使用体验特别满意",
    "手机运行速度很快",
    "屏幕显示效果很好",
    "电池非常耐用",
    "手机外观很漂亮",
    "拍照质量特别优秀",
    "这个产品真的不错",

    "这个手机太差了",
    "手机质量非常糟糕",
    "电池续航特别差",
    "拍照效果非常模糊",
    "这个手机不值得购买",
    "使用体验非常失望",
    "手机运行速度很慢",
    "屏幕显示效果很差",
    "电池一点都不耐用",
    "手机外观很难看",
    "拍照质量特别糟糕",
    "这个产品真的不好"
]

labels = [1] * 12 + [0] * 12

texts_train,texts_test,y_train,y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

pipeline = Pipeline([
    ("vectorizer",CountVectorizer(
        tokenizer=chinese_tokenizer,
        token_pattern=None
    )),
    ("model",MultinomialNB(alpha=1.0))
])

pipeline.fit(texts_train,y_train)

y_pred = pipeline.predict(texts_test)
train_pred = pipeline.predict(texts_train)

print("训练准确率",accuracy_score(y_train,train_pred))
print("测试准确率",accuracy_score(y_test,y_pred))

print("混淆矩阵：")
print(confusion_matrix(y_test,y_pred))

print("分类报告：")
print(classification_report(
    y_test,
    y_pred,
    zero_division=0
))

model = pipeline.named_steps["model"]

positive_index = list(model.classes_).index(1)

probabilities = pipeline.predict_proba(texts_test)[:, positive_index]

print("真实标签：", y_test)
print("预测标签：", y_pred)
print("好评概率：", np.round(probabilities, 4))


print("\n========== alpha 参数实验 ==========")

for alpha in [0.01, 0.1, 1.0, 10.0, 100.0]:

    model = MultinomialNB(alpha=alpha)

    test_pipeline = Pipeline([
        ("vectorizer", CountVectorizer(
            tokenizer=chinese_tokenizer,
            token_pattern=None
        )),
        ("model", model)
    ])

    test_pipeline.fit(texts_train, y_train)

    train_pred = test_pipeline.predict(texts_train)
    test_pred = test_pipeline.predict(texts_test)

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)

    print(
        f"alpha={alpha:<6} "
        f"训练准确率={train_acc:.4f} "
        f"测试准确率={test_acc:.4f}"
    )