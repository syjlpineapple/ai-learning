import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score

from nlp.course35.course_35 import models, texts_train, y_train

print("\n========== 交叉验证比较 ==========")

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
    print("每折准确率：", np.round(scores, 4))
    print("平均准确率：", round(scores.mean(), 4))
    print("标准差：", round(scores.std(), 4))
