"""
第30课：模型优化与过拟合
过拟合： 模型吧训练数据记得很熟，但是没有真正学会可以推广到新评论的规律
"""

"""
本节课重点
模型评估——准确率、精确率、召回率和 F1-score。
评估模型
模型预测准不准
"""
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score, \
    classification_report
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

# 逻辑分类
model = LogisticRegression(max_iter=10)
# 训练模型
model.fit(X_train, y_train)
# 预测模型
y_pred = model.predict(X_test)

# 预测训练集
train_pred = model.predict(X_train)

for text, pre_label ,label in zip(texts_train,train_pred,y_train):
    print("文本：",text, "预测：",pre_label,"实际：", label)


# 计算训练集准确率
train_acc = accuracy_score(y_train, train_pred)

# 计算测试集准确率
test_acc = accuracy_score(y_test, y_pred)

# 计算准确率差距
gap = train_acc - test_acc

print("训练集准确率：", train_acc)
print("测试集准确率：", test_acc)
print("准确率差距：", gap)


print("测试集预测详情：")

for text, pred, actual in zip(texts_test, y_pred, y_test):
    print(
        "评论：", text,
        "预测：", pred,
        "实际：", actual,
        "是否正确：", pred == actual
    )