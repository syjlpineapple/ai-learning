import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
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

texts_train,texts_test,y_train,y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels,
)

vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)
X_train = vectorizer.fit_transform(texts_train)
X_test = vectorizer.transform(texts_test)

C_values = [0.001,0.01,0.1,1,10,100]

for c in C_values:
    model = LogisticRegression(C=c,max_iter=1000)
    model.fit(X_train,y_train)

    y_pred = model.predict(X_test)
    train_pred = model.predict(X_train)

    train_acc = accuracy_score(y_train, train_pred)
    text_acc = accuracy_score(y_test,y_pred)

    print("C参数:",c)
    print("训练准确率",train_acc)
    print("测试准确率",text_acc)
    print("准确率差距",train_acc-text_acc)

    print(model.classes_)
    positive_index = list(model.classes_).index(1)

    probabilities = model.predict_proba(X_test)[:,positive_index]
    print("好评概率：", np.round(probabilities, 4))
    print("---------------------------------------------------------")
