---
kind: lesson
outline: [2, 2]
time: 60 分钟
uses: [逻辑回归, fit 与 transform, predict, predict_proba, 准确率, max_iter]
record:
  - text: 第 28-29 课 · 模型评估
    link: /records/nlp/07_模型评估
  - text: 当时的代码 course_28.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/course_28.py
---

# 第 28 课：训练你的第一个 NLP 文本分类模型

上一课你已经会了：`X` 是特征，`y` 是标签，`train_test_split()` 划分数据，`random_state` 保证可复现，`stratify` 保持类别比例。还看到了先 `fit` 全量会泄漏。

今天不再只学概念，要让计算机真正学会判断一条评论是好评还是差评。完整走一遍：

**中文文本 → 分词 → TF-IDF → 划分数据 → 训练模型 → 预测 → 评估**

## 一、今天的分类算法：逻辑回归

今天用**逻辑回归（Logistic Regression）**。名字里有「回归」，但它主要用来做分类。

它会根据输入特征，算出一条评论属于某一类的**概率**。比如（示意）：

| 评论 | 模型算出的好评概率 | 预测结果 |
|---|---:|---|
| 这个手机非常好用 | 0.95 | 好评 |
| 电池续航很差 | 0.08 | 差评 |
| 拍照效果很棒 | 0.89 | 好评 |

先简单记住：

- 概率大于等于 0.5，预测为好评（1）
- 概率小于 0.5，预测为差评（0）

这个 0.5 叫**决策阈值**，是二分类的默认值，下一课会学怎么调它。

## 二、准备训练数据

这次数据多一些，24 条，好评、差评各 12 条：

```python
texts = [
    # 好评 12 条
    "这个手机非常好用", "手机质量非常好", "电池续航特别棒", "拍照效果非常清晰",
    "这个手机值得购买", "使用体验特别满意", "手机运行速度很快", "屏幕显示效果很好",
    "电池非常耐用", "手机外观很漂亮", "拍照质量特别优秀", "这个产品真的不错",
    # 差评 12 条
    "这个手机太差了", "手机质量非常糟糕", "电池续航特别差", "拍照效果非常模糊",
    "这个手机不值得购买", "使用体验非常失望", "手机运行速度很慢", "屏幕显示效果很差",
    "电池一点都不耐用", "手机外观很难看", "拍照质量特别糟糕", "这个产品真的不好"
]

labels = [1] * 12 + [0] * 12
```

`[1] * 12 + [0] * 12` 就是 12 个 1 后面接 12 个 0，和上面评论的顺序对得上。这仍然是教学数据，远比不上真实用户评论复杂。

## 三、先划分，再提取特征

上一课说过，规范的顺序是：**先划分原始文本，再只用训练集学习 TF-IDF。**

```python
from sklearn.model_selection import train_test_split

texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)
```

注意，这次划分的是 `texts`（原始文本），不是已经算好的 `X`。24 条按 25% 划分，训练 18 条，测试 6 条。

## 四、中文分词与 TF-IDF

```python
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer

# 定义中文分词函数
def chinese_tokenizer(text):
    return jieba.lcut(text)

# 创建 TF-IDF 向量化器
vectorizer = TfidfVectorizer(
    tokenizer=chinese_tokenizer,
    token_pattern=None
)

# 只用训练集学习词汇和权重
X_train = vectorizer.fit_transform(texts_train)

# 测试集只进行转换，不重新学习词汇
X_test = vectorizer.transform(texts_test)
```

| 方法 | 作用 |
|---|---|
| `fit_transform()` | 学习词汇表和 IDF，再转换文本 |
| `transform()` | 用已经学到的词汇表和 IDF 转换新文本 |

为什么测试集不能用 `fit_transform()`？因为测试集要模拟「模型从没见过的新数据」。新数据来了，模型只能用训练时学到的词表去看它，不能为它重新建词表。

## 五、正式训练第一个模型

```python
from sklearn.linear_model import LogisticRegression

# 创建模型
model = LogisticRegression(max_iter=1000)

# 训练模型
model.fit(X_train, y_train)
```

重点理解这一行：

```python
model.fit(X_train, y_train)
```

它在告诉模型：这是输入特征，这是每条评论的正确答案，请从中学出分类规律。`fit` 里面跑的，就是你第 15 课手写过的那种训练循环：算预测、算损失、算梯度、更新权重，只是梯度不用手推。

`max_iter` 是训练时最多迭代多少轮，是一个**上限**，不是越大越准。

## 六、让模型预测并评估

```python
from sklearn.metrics import accuracy_score

y_pred = model.predict(X_test)

print("真实标签：", y_test)
print("预测标签：", y_pred)
print("模型准确率：", accuracy_score(y_test, y_pred))
```

- `y_test`：真实答案
- `y_pred`：模型的预测
- 准确率：预测对的条数占总条数的比例

$$
Accuracy=\frac{\text{预测正确的数量}}{\text{总预测数量}}
$$

比如 6 条里对 5 条，准确率就是 $5/6\approx83.33\%$。

## 七、完整代码：亲自运行

```python
import jieba

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 1. 准备文本数据
texts = [
    "这个手机非常好用", "手机质量非常好", "电池续航特别棒", "拍照效果非常清晰",
    "这个手机值得购买", "使用体验特别满意", "手机运行速度很快", "屏幕显示效果很好",
    "电池非常耐用", "手机外观很漂亮", "拍照质量特别优秀", "这个产品真的不错",

    "这个手机太差了", "手机质量非常糟糕", "电池续航特别差", "拍照效果非常模糊",
    "这个手机不值得购买", "使用体验非常失望", "手机运行速度很慢", "屏幕显示效果很差",
    "电池一点都不耐用", "手机外观很难看", "拍照质量特别糟糕", "这个产品真的不好"
]

# 2. 准备标签
labels = [1] * 12 + [0] * 12

# 3. 划分训练集和测试集
texts_train, texts_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.25,
    random_state=42,
    stratify=labels
)

# 4. 中文分词
def chinese_tokenizer(text):
    return jieba.lcut(text)

# 5. TF-IDF 特征提取
vectorizer = TfidfVectorizer(
    tokenizer=chinese_tokenizer,
    token_pattern=None
)

X_train = vectorizer.fit_transform(texts_train)
X_test = vectorizer.transform(texts_test)

# 6. 创建逻辑回归模型
model = LogisticRegression(max_iter=1000)

# 7. 训练模型
model.fit(X_train, y_train)

# 8. 预测
y_pred = model.predict(X_test)

# 9. 评估
accuracy = accuracy_score(y_test, y_pred)

print("训练集形状：", X_train.shape)
print("测试集形状：", X_test.shape)
print("真实标签：", y_test)
print("预测标签：", y_pred)
print("模型准确率：", accuracy)
```

运行结果：

```text
训练集形状： (18, 37)
测试集形状： (6, 37)
真实标签： [0, 1, 1, 1, 0, 0]
预测标签： [1 0 1 0 1 1]
模型准确率： 0.16666666666666666
```

训练集 18 条、测试集 6 条，jieba 分完一共 37 个词，测试集也只能用这 37 列。

流程跑通了，可准确率只有 **16.7%**，6 条里只对了 1 条。先别急着改，下一课专门查它为什么这么差。

> 注意：效果差不是因为 `max_iter` 不够。实测设成 10、1000、10000，`model.n_iter_` 都是 `[5]`，第 5 轮就收敛了，三种设置的结果一模一样。
<details>
<summary>怎么判断</summary>

想知道够不够，就打印 `model.n_iter_`：它等于 `max_iter` 才说明撞上了上限。sklearn 没收敛时也会主动发 `ConvergenceWarning`，没有警告，就不是这个原因。

</details>

## 八、小测

**1.** `model.fit(X_train, y_train)` 的作用是什么？

- A. 训练模型
- B. 测试模型
- C. 删除文本

**2.** 为什么 `X_test` 使用 `transform()`，而不是 `fit_transform()`？

- A. 因为测试集不能有文本
- B. 避免测试集信息泄漏，使用训练集学到的词汇和 IDF
- C. 因为 transform 会自动训练模型

**3.** `y_pred` 代表什么？

- A. 真实标签
- B. 训练集特征
- C. 模型预测出来的标签

**4.** `accuracy_score(y_test, y_pred)` 计算什么？

- A. 训练集数量
- B. 预测正确的比例
- C. TF-IDF 特征数量

<details>
<summary>答案</summary>

1. A。
2. B。
3. C。
4. B。

</details>

## 九、今天的编程作业

给训练好的模型输入一条从没出现在训练集里的新评论：

```python
new_text = ["这个手机拍照清晰，电池也很耐用"]

new_X = vectorizer.transform(new_text)

prediction = model.predict(new_X)
print("预测结果：", prediction)

probability = model.predict_proba(new_X)
print("差评概率：", probability[0][0])
print("好评概率：", probability[0][1])
```

`predict_proba()` 返回每个类别的概率，列的顺序看 `model.classes_`，这里是 `[0 1]`，所以第 0 列是差评、第 1 列是好评。

## 讲评（11-09）

你交的代码流程完全正确，而且做对了今天最要紧的一点：**先划分，只用训练集 `fit_transform`，测试集只 `transform`**。上一课自己发现的泄漏问题，这次没有再犯。

你当时写的是 `LogisticRegression(max_iter=10000)`，GPT 说没必要这么大。后来存进仓库的 `course_28.py` 里你又改成了 `max_iter=10`，旁边写了一个问题。这份文件里一共三个问号注释：

```python
#token_pattern=None是为啥？
# 为什么texts_test不用fit_transform?
# max_iter的作用
```

前两个今天都有答案：`token_pattern=None` 是关掉默认的切词规则，让 jieba 接手；测试集只 `transform` 是为了不泄漏。第三个看上面的注意，10 也够用。把疑问直接写在代码旁边，是很好的学习习惯。

作业那条新评论，按上面的代码跑出来是：

```text
预测结果： [1]
差评概率： 0.4842186033050574
好评概率： 0.5157813966949426
```

判成了好评，但好评概率只有 0.516，几乎是五五开。模型其实没什么把握。这和那个 16.7% 是同一个信号，下一课一起查。

