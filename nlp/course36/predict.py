
import joblib

# 加载训练好的模型
lr_model = joblib.load("models/LogisticRegression.pkl")
nb_model = joblib.load("models/NaiveBayes.pkl")

while True:

    text = input("\n请输入一条商品评论（输入 exit 退出）：")

    if text.lower() == "exit":
        break

    # 逻辑回归预测
    lr_pred = lr_model.predict([text])[0]
    lr_prob = lr_model.predict_proba([text])[0]

    # 朴素贝叶斯预测
    nb_pred = nb_model.predict([text])[0]
    nb_prob = nb_model.predict_proba([text])[0]

    lr_result = "好评" if lr_pred == 1 else "差评"
    nb_result = "好评" if nb_pred == 1 else "差评"

    print("\n========== 预测结果 ==========")

    print("逻辑回归：", lr_result)
    print("逻辑回归好评概率：", round(lr_prob[1], 4))

    print("朴素贝叶斯：", nb_result)
    print("朴素贝叶斯好评概率：", round(nb_prob[1], 4))
