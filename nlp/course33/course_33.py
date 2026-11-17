"""
33课
交叉验证
"""
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline

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

def chinese_tokenizer(text):
    return jieba.lcut(text)

# 创建模型流水线
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(tokenizer=chinese_tokenizer, token_pattern=None)),
    ("model",LogisticRegression(C=1,max_iter=1000))
])

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

scores = cross_val_score(
    pipeline,
    texts_train,
    y_train,
    cv=cv,
    scoring="accuracy"
)


print("每一折的准确率：", scores)
print("平均准确率：", scores.mean())
print("准确率标准差：", scores.std())