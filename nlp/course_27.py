"""
监督学习 - 有正确答案
无监督学习 - 没有正确答案
"""
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split


# jieba中文分词
def chinese_tokenizer(text):
    return jieba.lcut(text)


texts = [
    "这个手机非常好用",
    "电池续航特别好",
    "拍照效果好",
    "手机质量很好",
    "这个手机太差了",
    "电池续航很差",
    "拍照效果不好",
    "手机质量太差"
]
labels = [1,1,1,1,0,0,0,0]
print(len(texts))
print(len(labels))

# TfidfVectorizer默认不对中文分词
vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)
X = vectorizer.fit_transform(texts)

words = vectorizer.get_feature_names_out()
print("特征矩阵形状:",X.shape)
print("词汇表：", words)
print("词汇数量：", len(words))
print("矩阵形状：", X.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

print("全部数据：", X.shape)
print("训练集：", X_train.shape)
print("测试集：", X_test.shape)
print("训练标签：", y_train)
print("测试标签：", y_test)










