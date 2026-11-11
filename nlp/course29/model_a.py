"""
本节课重点
模型评估——准确率、精确率、召回率和 F1-score。
评估模型
模型预测准不准
"""
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score, \
    classification_report

"""
假设我们有100条手机评论，50条好评，50条差评
实际50条好评     模型预测好评40        模型预测差评10
实际50条差评     模型预测好评5         模型预测差评45

TP（真正例）： 实际好评、模型也预测好评；40条
FP（假正例）： 实际差评、模型预测好评；5条
TN（真负例）： 实际差评、模型预测差评；45条
FN（假负例）： 实际好评、模型预测差评；10条

准确率Accuracy：整体预测正确的比例
Accuracy= （TP+TN)/(TP+FP+TN+FN)

精确率Precision：模型预测为好评的评论中，真正好评的比例：
Precision = TP/(TP+FP)

召回率Recall:所有实际好评中，被模型找出来的比例
Recall = TP/(TP+FN)

F1-Score:综合考虑精确率和召回率
F1 = 2*Precision*Recall/(Precision+Recall)
"""

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def chinese_tokenizer(text:str):
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
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)

texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

X_train = vectorizer.fit_transform(texts_train)
X_test = vectorizer.transform(texts_test)

model = LogisticRegression(max_iter=10)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("混淆矩阵:")
print(confusion_matrix(y_test, y_pred))
print("准确率:",accuracy_score(y_test, y_pred))
print("精确率",precision_score(y_test, y_pred))
print("召回率",recall_score(y_test, y_pred))
print("F1分数:",f1_score(y_test, y_pred))
print("分类报告：")
print(classification_report(y_test, y_pred,target_names=["差评","好评"]))


print("\n测试集预测详情：")

for text, true_label, pred_label in zip(
    texts_test, y_test, y_pred
):
    print("评论：", text)
    print("真实标签：", true_label)
    print("预测标签：", pred_label)
    print("是否正确：", true_label == pred_label)
    print("-" * 30)

print("\n训练集分词结果：")

for text in texts_train:
    print(text, "=>", chinese_tokenizer(text))


print("\n测试集未登录词检查：")
vocab = set(vectorizer.get_feature_names_out())

for text in texts_test:
    words = chinese_tokenizer(text)

    unknown_words = [
        word for word in words
        if word not in vocab
    ]

    print("原文：", text)
    print("分词：", words)
    print("未登录词：", unknown_words)
    print("-" * 30)