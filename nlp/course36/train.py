import joblib
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from nlp.course36.data.data_reader import texts, labels
from nlp.course36.tokenizer import chinese_tokenizer

texts_train,texts_test,y_train,y_test = train_test_split(
    texts,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels,
)

models = {
    "LogisticRegression": Pipeline([
        ("tfidf", TfidfVectorizer(tokenizer=chinese_tokenizer,token_pattern=None)),
        ("model",LogisticRegression(
            C=1,
            max_iter=1000
        ))
    ]),
    "NaiveBayes": Pipeline([
        ("count", CountVectorizer(
            tokenizer=chinese_tokenizer,
            token_pattern=None
        )),
        ("model",MultinomialNB(alpha=1.0))
    ])
}

# 交叉验证
cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


for name, model in models.items():
    scores = cross_val_score(
        model,
        texts_train,
        y_train,
        cv=cv,
        scoring="accuracy"
    )
    print("\n模型：", name)
    print("交叉验证平均准确率：", scores.mean())
    print("交叉验证标准差：", scores.std())

# 训练最终模型并测试
for name, model in models.items():
    model.fit(texts_train, y_train)
    predictions = model.predict(texts_test)
    print("\n==========", name, "==========")
    print("测试集准确率：", accuracy_score(y_test, predictions))
    print("混淆矩阵：")
    print(confusion_matrix(y_test, predictions))
    print("分类报告：")
    print(classification_report(y_test, predictions, zero_division=0))

    # 保存训练好的模型
    joblib.dump(model, f"models/{name}.pkl")


    # 找出预测错误的评论
    errors = []

    for text, true_label, pred_label in zip(
        texts_test,
        y_test,
        predictions
    ):
        if true_label != pred_label:
            errors.append({
                "评论": text,
                "真实标签": true_label,
                "预测标签": pred_label
            })

    print("\n错误评论数量：", len(errors))
    print("\n错误案例：")

    for item in errors[:20]:
        print(item)