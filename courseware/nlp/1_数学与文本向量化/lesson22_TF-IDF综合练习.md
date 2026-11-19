---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [TF 与 df 的区别, 手算 TF-IDF, word in doc]
record:
  - text: 第 16-23 课 · 文本向量化
    link: /records/nlp/05_文本向量化
  - text: 当时的代码 day_7.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/day_7.py
---

# 第 22 课：TF-IDF 综合练习

上一课你看懂了 TF-IDF 的计算代码，小测 3 题全对。今天的目标是从「看得懂」进步到「自己写得出来」。

这次换一组数据，专门练一个最容易混的地方：**一个词在同一篇里出现两次，TF 和 df 各怎么算？**

## 一、先复习三个关键概念

| 概念 | 含义 | 记忆方法 |
|---|---|---|
| TF | 词在当前文档中的出现频率 | 看一篇文档 |
| df | 包含这个词的文档数量 | 看有几篇文档 |
| IDF | 词在整个集合里有多普遍，反过来算 | 越少见，通常越高 |

公式不变：

$$
IDF=\ln\left(\frac{N+1}{df+1}\right)+1,\qquad TF\text{-}IDF=TF\times IDF
$$

今天不用背公式，重点是每个变量是什么意思，在 Python 里怎么用对。

## 二、今天的练习数据

```python
documents = [
    ["猫", "喜欢", "猫"],
    ["狗", "喜欢", "鱼"]
]
```

- 文档 A：猫 / 喜欢 / 猫，共 3 个词
- 文档 B：狗 / 喜欢 / 鱼，共 3 个词

逐个分析：

- 「猫」在文档 A 里出现了**两次**，但只出现在一篇文档里，所以 `df = 1`。
- 「喜欢」两篇都有，所以 `df = 2`。
- 文档总数 `N = 2`。

记住：「猫」出现了两次，不等于 `df = 2`。同一篇里重复出现，只算一篇。

## 三、用 Python 统计 df

```python
documents = [
    ["猫", "喜欢", "猫"],
    ["狗", "喜欢", "鱼"]
]

word = "猫"

df = sum(word in doc for doc in documents)

print(df)
```

输出：

```text
1
```

- `word = "猫"`：指定要统计的词。
- `word in doc`：检查当前这篇文档里有没有这个词，有就是 `True`。
- `sum(...)`：把 `True` 当 1 加起来，得到包含这个词的文档篇数。

把 `word` 改成 `"喜欢"`，输出就变成 `2`。

## 四、计算一个词的 TF-IDF

现在算「猫」在文档 A 中的 TF-IDF：

```python
import math

documents = [
    ["猫", "喜欢", "猫"],
    ["狗", "喜欢", "鱼"]
]

doc = documents[0]
word = "猫"

# 计算 TF
tf = doc.count(word) / len(doc)

# 计算 df
N = len(documents)
df = sum(word in d for d in documents)

# 计算 IDF
idf = math.log((N + 1) / (df + 1)) + 1

# 计算 TF-IDF
tf_idf = tf * idf

print("TF:", round(tf, 3))
print("df:", df)
print("IDF:", round(idf, 3))
print("TF-IDF:", round(tf_idf, 3))
```

输出：

```text
TF: 0.667
df: 1
IDF: 1.405
TF-IDF: 0.937
```

一个一个对：

**TF 为什么是 0.667？** 「猫」在文档 A 里出现两次，文档 A 一共三个词：

$$
TF=\frac{2}{3}\approx0.667
$$

**IDF 为什么约等于 1.405？** 一共两篇文档，「猫」只在其中一篇：

$$
IDF=\ln\frac{2+1}{1+1}+1=\ln 1.5+1\approx1.405
$$

**最后相乘：**

$$
TF\text{-}IDF\approx0.667\times1.405\approx0.937
$$

和上一课的「鱼」比一下：两个词 IDF 一样，都是 1.405，但「猫」在自己那篇里占了三分之二，TF 高，所以 TF-IDF 也高得多。

## 五、你的动手练习

先别运行代码，自己分析。

**1.** 「猫」在文档 A 中出现两次，文档 A 总共有三个词。TF 是多少？

- A. 2
- B. 2/3，约等于 0.667
- C. 1/2，等于 0.5

**2.** 「喜欢」在两篇文档中都出现。它的 df 是多少？

- A. 1
- B. 2
- C. 3

**3.** 如果一个词在当前文档中出现得更频繁，而 IDF 不变，那么按照本课的公式，它的 TF-IDF 会怎样？

- A. 通常会增大
- B. 一定变成 0
- C. 一定不变

<details>
<summary>答案</summary>

1. B。次数除以当前文档的总词数。A 是只数了次数，没有除。
2. B。两篇都有，就是 2。同一篇里出现多少次都不影响 df。
3. A。TF-IDF 是两者相乘，IDF 不变时，TF 越大乘积越大。

</details>

今天达到三个目标就很好：能区分 `TF` 和 `df`；能说出 `word in doc` 为什么能判断一篇文档包不包含某个词；能看懂 TF、IDF、TF-IDF 的计算顺序。

## 讲评（10-27）

你交的是 **B、B、A**，三题全对。

这一天你还自己写了 `day_7.py`：用第 21 课的两篇文档（猫喜欢吃鱼 / 狗喜欢吃肉），算「猫」在文档 A 里的 TF-IDF。运行结果：

```text
1.4054651081081644
0.25
文档总数: 2
文档频率: 1
TF: 0.25
IDF: 1.405
TF-IDF: 0.351
```

前两行是你在中间加的 `print(idf)` 和 `print(tf)`，先把中间结果打出来看对不对，再算最终结果，这个习惯很好。「猫」在那组数据里和「鱼」的处境一模一样（各出现 1 次、各只在 1 篇里），所以结果也是 0.351，和第 21 课的表对得上。

手算你已经会了。下一课换成 scikit-learn 自动算，你会发现它给的数字和你手算的不一样。

