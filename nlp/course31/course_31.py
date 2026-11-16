"""
第31课：正则化--缓解过拟合
"""
import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score, \
    classification_report
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
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
vectorizer = TfidfVectorizer(tokenizer=vectorizer_chinese,token_pattern=None)

texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

x_train = vectorizer.fit_transform(texts_train)
x_test = vectorizer.transform(texts_test)

C_values = [10,1,0.1,0.01]

for c in C_values:
    model = LogisticRegression(C=c,max_iter=1000)
    model.fit(x_train, y_train)

    # 训练集预测
    train_pred = model.predict(x_train)
    # 测试机预测
    y_pred = model.predict(x_test)

    # 计算模型权重整体大小
    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, y_pred)

    weight_norm = np.linalg.norm(model.coef_)

    print("C参数：", c)
    print("训练集准确率：", train_acc)
    print("测试集准确率：", test_acc)
    print("权重整体大小：", weight_norm)
    print("--------------------------")
    # 获取好评概率， model.classes_ 表示模型训练时识别到的所有类别
    positive_index = list(model.classes_).index(1)

    # 预测每条测试数据属于各个类别的概率
    probabilities = model.predict_proba(x_test)[:, positive_index]

    print("预测标签：", y_pred)
    print("好评概率：", np.round(probabilities, 4))