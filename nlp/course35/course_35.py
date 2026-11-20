
import jieba
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# 1. 中文分词
def chinese_tokenizer(text):
    return jieba.lcut(text)


# 2. 准备数据
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


# 3. 划分训练集和测试集
texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)


# 4. 定义两个模型
models = {
    "LogisticRegression": Pipeline([
        ("vectorizer", TfidfVectorizer(
            tokenizer=chinese_tokenizer,
            token_pattern=None
        )),
        ("model", LogisticRegression(
            C=1,
            max_iter=1000
        ))
    ]),

    "NaiveBayes": Pipeline([
        ("vectorizer", CountVectorizer(
            tokenizer=chinese_tokenizer,
            token_pattern=None
        )),
        ("model", MultinomialNB(alpha=1.0))
    ])
}


# 5. 分别训练和评估
for name, model in models.items():

    print("\n==========", name, "==========")

    model.fit(texts_train, y_train)

    train_pred = model.predict(texts_train)
    test_pred = model.predict(texts_test)

    print("训练准确率：",
          accuracy_score(y_train, train_pred))

    print("测试准确率：",
          accuracy_score(y_test, test_pred))

    print("Precision：",
          precision_score(y_test, test_pred,
                          pos_label=1, zero_division=0))

    print("Recall：",
          recall_score(y_test, test_pred,
                       pos_label=1, zero_division=0))

    print("F1：",
          f1_score(y_test, test_pred,
                   pos_label=1, zero_division=0))

    print("混淆矩阵：")
    print(confusion_matrix(y_test, test_pred))

    print("预测结果：", test_pred)





print("\n========== 两个模型预测对比 ==========")

lr_pred = models["LogisticRegression"].predict(texts_test)
nb_pred = models["NaiveBayes"].predict(texts_test)

for i in range(len(texts_test)):

    print("\n评论：", texts_test[i])
    print("真实标签：", y_test[i])
    print("逻辑回归预测：", lr_pred[i])
    print("朴素贝叶斯预测：", nb_pred[i])

    if lr_pred[i] != nb_pred[i]:
        print("模型判断不同！")
    else:
        print("模型判断相同")
