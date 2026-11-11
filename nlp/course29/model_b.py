import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, \
    classification_report
from sklearn.model_selection import train_test_split



def vectorizer_chinese(text:str):
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
    "手机运行速度快",
    "这个手机像素不错",
    "手机质感不错",
    "这个手机的拍照效果不错",

    "这个手机运行速度非常慢",
    "这个手机屏幕非常清晰",
    "这个手机使用起来发烫",
    "这个手机的屏幕太小了",
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

labels = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
]

#	特征数据 X
#标签数据 y
#测试集比例
# 随机种子保证每次划分结果一致
#分层抽样 保证训练集和测试集的类别比例尽量一致
texts_train,texts_test,y_train,y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

# token_pattern=None 的作用是：关闭 TfidfVectorizer 默认的正则表达式分词规则，让它使用你自己提供的 tokenizer 进行分词。
vectorizer = TfidfVectorizer(tokenizer=vectorizer_chinese,token_pattern=None)

x_train = vectorizer.fit_transform(texts_train)
x_test = vectorizer.transform(texts_test)

model = LogisticRegression(max_iter=1000)
model.fit(x_train, y_train)

y_pred = model.predict(x_test)

print("测试集原始文本：")
for text, real, pred in zip(texts_test, y_test, y_pred):
    print(f"文本：{text}")
    print(f"真实标签：{real}")
    print(f"预测标签：{pred}")
    print("-" * 30)

print("模型类别：", model.classes_)
print("训练集标签：", set(y_train))
print("测试集标签：", set(y_test))


print("混淆矩阵:")
print(confusion_matrix(y_test, y_pred))
print("准确率:",accuracy_score(y_test, y_pred))
print("精确率",precision_score(y_test, y_pred))
print("召回率",recall_score(y_test, y_pred))
print("F1分数:",f1_score(y_test, y_pred))
print("分类报告：")
print(classification_report(y_test, y_pred,target_names=["差评","好评"]))



print("\n训练集分词结果：")

for text in texts_train:
    print(text, "=>", vectorizer_chinese(text))


print("\n测试集未登录词检查：")
vocab = set(vectorizer.get_feature_names_out())

for text in texts_test:
    words = vectorizer_chinese(text)

    unknown_words = [
        word for word in words
        if word not in vocab
    ]

    print("原文：", text)
    print("分词：", words)
    print("未登录词：", unknown_words)
    print("-" * 30)


# 找到好评对应的类别列
positive_index = list(model.classes_).index(1)

print(model.classes_)

# 获取好评概率
probabilities = model.predict_proba(x_test)[:, positive_index]

print(probabilities)


threshold = 0.42

pred_threshold = np.where(
    probabilities >= threshold,
    1,
    0
)

print(pred_threshold)

print("Precision:", precision_score(y_test, pred_threshold))
print("Recall:", recall_score(y_test, pred_threshold))
print("F1:", f1_score(y_test, pred_threshold))