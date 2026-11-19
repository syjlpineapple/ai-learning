---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [TfidfVectorizer, fit_transform, 特征矩阵形状, L2 归一化, 稀疏矩阵]
record:
  - text: 第 16-23 课 · 文本向量化
    link: /records/nlp/05_文本向量化
  - text: 当时的代码 day_8.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/day_8.py
---

# 第 23 课：使用 scikit-learn 生成 TF-IDF 向量

前两课你已经能手算 TF-IDF 了。但手算一个词就要写好几行，如果有 1 万篇文档、几万个不同的词，就没法这么干了。今天把这件事交给工具，并学会读懂工具给出的矩阵。暂时不训练模型。

## 一、为什么需要工具？

手算要自己统计词频、文档频率，再算 IDF，一个词一个词地来。

`scikit-learn` 是 Python 里最常用的机器学习库，它的 `TfidfVectorizer` 能一次性把一批文本全部变成 TF-IDF 向量。

## 二、准备文本

先用两句英文，避开中文分词的麻烦：

```python
documents = [
    "cat likes fish",
    "dog likes meat"
]
```

可以理解成两篇文档：猫喜欢鱼、狗喜欢肉。和第 21 课那两篇是同一个意思。

## 三、运行代码

如果还没装，先在终端执行：

```bash
pip install scikit-learn
```

然后运行：

```python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat likes fish",
    "dog likes meat"
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)

print("词汇表：")
print(vectorizer.get_feature_names_out())

print("矩阵形状：")
print(X.shape)

print("TF-IDF 矩阵：")
print(X.toarray().round(3))
```

输出：

```text
词汇表：
['cat' 'dog' 'fish' 'likes' 'meat']
矩阵形状：
(2, 5)
TF-IDF 矩阵：
[[0.632 0.    0.632 0.449 0.   ]
 [0.    0.632 0.    0.449 0.632]]
```

## 四、理解每一行代码

**1. 创建工具**

```python
vectorizer = TfidfVectorizer()
```

创建一个 TF-IDF 向量化器，准备处理文本。

**2. 学习词汇表并转换文本**

```python
X = vectorizer.fit_transform(documents)
```

- `fit`：从输入文本里**学**两样东西：词汇表，和每个词的 IDF。
- `transform`：用学到的东西，把文本**转换**成向量。

`fit_transform` 就是把这两步合在一起做。这个「先学再转」的区分以后会反复出现，第 27 课还会因为它踩一个坑。

**3. 查看词汇表**

```python
vectorizer.get_feature_names_out()
```

返回矩阵每一列对应的词。

**4. 查看矩阵形状**

```python
X.shape
```

`(2, 5)`：第一个数是文档数量，第二个数是词（特征）的数量。

## 五、怎样理解输出矩阵？

默认的 `TfidfVectorizer` 会把英文转成小写，并且忽略只有一个字符的词。词汇表按字母顺序排列：`['cat', 'dog', 'fish', 'likes', 'meat']`，所以矩阵是 2 行 5 列。

把矩阵配上表头：

| 文档 | cat | dog | fish | likes | meat |
|---|---:|---:|---:|---:|---:|
| 文档 A | 0.632 | 0 | 0.632 | 0.449 | 0 |
| 文档 B | 0 | 0.632 | 0 | 0.449 | 0.632 |

三个重点：

1. **一行代表一篇文档。**
2. **一列代表一个词。**
3. **数字是这个词在这篇文档里的 TF-IDF 权重。**

文档 A 里没有 `dog`，对应位置就是 0。`likes` 两篇都有，权重比 `cat`、`fish` 低，这和第 21 课「到处都有的词 IDF 低」是一回事。

还有一点：`fit_transform` 返回的其实是**稀疏矩阵**，它只存非零的位置。真实文本的词汇表动辄几万列，每篇文档只用到几十个词，大部分都是 0，稀疏存储能省下大量内存。`toarray()` 把它展开成普通数组，只适合在小例子里看一看。

## 六、动手观察矩阵

再加一篇 `cat likes meat`，变成三篇文档，词汇表里的词还是那 5 个：

| 文本组 | 矩阵形状 | 说明 |
|---|---|---|
| cat likes fish / dog likes meat | `(2, 5)` | 2 篇文档，5 个不同的词 |
| cat likes fish / dog likes meat / cat likes meat | `(3, 5)` | 3 篇文档，仍然是 5 个词 |

**行数跟着文档数变，列数跟着词汇表变。**

## 七、为什么和手算的对不上？

第 22 课你手算过，「猫」在这种情况下的 TF-IDF 是 0.4685。可上面矩阵里 `cat` 是 0.632。哪里不一样？

先列出手算的原始结果。每篇文档 3 个词，每个词出现 1 次，TF 都是 $1/3$：

| 词语 | TF | IDF | TF-IDF |
|---|---:|---:|---:|
| cat | 0.333 | 1.405 | 0.4685 |
| fish | 0.333 | 1.405 | 0.4685 |
| likes | 0.333 | 1.000 | 0.3333 |

文档 A 的原始向量是 $[0.4685,\ 0,\ 0.4685,\ 0.3333,\ 0]$。

`TfidfVectorizer` 默认还会多做一步：**L2 归一化**。它把整行按比例缩放，让这一行的长度等于 1：

$$
x_i'=\frac{x_i}{\sqrt{\sum_j x_j^2}}
$$

- $x_i$：归一化前某个词的权重
- 分母：这一行所有权重先平方、再相加、再开方，也就是第 18 课算过的**向量长度**

用文档 A 算一遍。这一行的长度是：

$$
\sqrt{0.4685^2+0.4685^2+0.3333^2}\approx0.7417
$$

再用它去除每一项：

$$
\frac{0.4685}{0.7417}\approx0.632,\qquad \frac{0.3333}{0.7417}\approx0.449
$$

和矩阵第一行完全一样。

用 NumPy 验证：

```python
import numpy as np

x = np.array([0.4685, 0.4685, 0.3333])

# 计算向量长度
length = np.linalg.norm(x)

# L2 归一化
x_normalized = x / length

print("原始向量：", x)
print("向量长度：", length)
print("归一化后：", x_normalized)
print("归一化后长度：", np.linalg.norm(x_normalized))
```

```text
原始向量： [0.4685 0.4685 0.3333]
向量长度： 0.7416693265869906
归一化后： [0.63168313 0.63168313 0.44939165]
归一化后长度： 1.0
```

记住：**归一化改变了数值，但没有改变权重之间的比例。** 归一化前 $0.4685/0.3333\approx1.406$，归一化后 $0.632/0.449$ 还是 1.406。所以哪个词更重要，归一化前后的结论不变。

想关掉归一化，写 `TfidfVectorizer(norm=None)`。

> 注意：关掉归一化以后，结果正好是手算的 3 倍，不是 0.4685。所以两边其实有**两处**不同：sklearn 的 TF 直接用出现次数，不除以文档长度；再加上 L2 归一化。
<details>
<summary>实测细节</summary>

```text
[[1.405 0.    1.405 1.    0.   ]
 [0.    1.405 0.    1.    1.405]]
```

默认情况下能对上，是因为归一化把整行同时缩放，那个公共的「除以 3」被消掉了。结果对上了，不代表每一步都一样。这是整理时实测发现的，当时只查到了归一化这一处。

</details>

顺便确认一件事：Python 的 `math.log(x)` 就是数学里的 $\ln x$，以 $e\approx2.718$ 为底。以 10 为底要用 `math.log10(x)`，或者 `math.log(x, 10)`。所以第 21 课的 `math.log((N + 1) / (df + 1)) + 1` 写法是对的。

## 八、小测

**1.** `TfidfVectorizer` 的主要作用是什么？

- A. 自动把文本转换成 TF-IDF 特征
- B. 自动把中文翻译成英文
- C. 自动生成文本摘要

**2.** 如果有 3 篇文档和 5 个不同的词语特征，矩阵形状应该是什么？

- A. `(5, 3)`
- B. `(3, 5)`
- C. `(3, 3)`

**3.** 在 TF-IDF 矩阵中，一个词在某篇文档中没有出现，通常对应什么数值？

- A. 1
- B. -1
- C. 0

**4.** 把 `TfidfVectorizer` 改成 `norm=None`，会发生什么？

- A. 所有 TF-IDF 权重都会变成 0
- B. 保留原始 TF-IDF 权重，不再做 L2 归一化
- C. IDF 不再计算，所有词的权重都相同

<details>
<summary>答案</summary>

1. A。
2. B。行是文档，列是词。这个「行是样本、列是特征」的约定，以后所有模型都一样。
3. C。
4. B。不过「原始权重」用的是 sklearn 自己的 TF 定义，见第七部分的注意。

</details>

## 讲评（10-27）

前三题你交的是 **A、B、C**，全对。

这一课最有价值的不是小测，是你后面接连问的两个问题。

先是问：「cat 的 TF-IDF 是不是 `print(1/3 * (math.log(3/2)+1))`？」公式完全对，结果约 0.4685。接着你把 `day_8.py` 跑出来的矩阵贴了过来，问「那为什么 TfidfVectorizer 算的是 0.632」。于是有了第七部分的 L2 归一化。你还顺手确认了 `math.log` 就是 $\ln$。最后的归一化理解题你选了 **B**，答对了。

`day_8.py` 最后两行留下了当时的痕迹：

```python
# 自己算
print(1/3 * (math.log(3/2)+1))

# 扩展，对不上为什么？ 原因是：TfidfVectorizer 默认不仅计算 TF-IDF，还会对每篇文档的向量进行归一化（Normalization）。
```

这次发现的前提是**你先手算过**。如果直接调库，看到 0.632 只会觉得「哦，就是这样」，根本没有对照。把疑问和结论写进注释，也让以后回头看的时候知道自己当时在想什么。

