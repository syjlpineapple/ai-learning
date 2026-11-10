"""
用逻辑回归真实跑训练+预测
"""
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# 中文分词
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

#token_pattern=None是为啥？
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)

# 训练、测试切分
texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

print(len(texts_train), len(texts_test), len(y_train), len(y_test))

# 为什么texts_test不用fit_transform?
X_train = vectorizer.fit_transform(texts_train)
X_test = vectorizer.transform(texts_test)

# 逻辑回归
# max_iter的作用
model = LogisticRegression(max_iter=10)

# 训练
model.fit(X_train, y_train)

# 预测
y_pred = model.predict(X_test)


print(vectorizer.get_feature_names_out())

print(y_test)
print(y_pred)

# 计算模型准确率
print("准确率：", accuracy_score(y_test, y_pred))


print("混淆矩阵：")
print(confusion_matrix(y_test, y_pred))

print("分类报告：")
print(classification_report(y_test, y_pred, target_names=["差评", "好评"]))


new_text = ["这个手机拍照清晰，电池也很耐用"]
new_X = vectorizer.transform(new_text)
prediction = model.predict(new_X)

print("预测结果：", prediction)
probability = model.predict_proba(new_X)

print("差评概率：", probability[0][0])
print("好评概率：", probability[0][1])