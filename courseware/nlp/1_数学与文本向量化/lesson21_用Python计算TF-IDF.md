---
kind: lesson
outline: [2, 2]
time: 30 分钟
uses: [TF-IDF 计算, math.log, df 统计, sum 统计布尔值]
record:
  - text: 第 16-23 课 · 文本向量化
    link: /records/nlp/05_文本向量化
---

# 第 21 课：用 Python 计算 TF-IDF

第 18、19、20 课的小测你都是满分。上一课分别认识了 TF 和 IDF，今天把它们串起来，让 Python 算出一个词完整的 TF-IDF。

## 一、先复习：TF-IDF 是什么？

- **TF（词频）**：一个词在当前文档中出现得有多频繁。
- **IDF（逆文档频率）**：一个词在整个文档集合中有多普遍，越普遍越低。

$$
TF\text{-}IDF=TF\times IDF
$$

## 二、准备两篇文档

两篇已经分好词的文本：

- 文档 A：猫 喜欢 吃 鱼
- 文档 B：狗 喜欢 吃 肉

一共两篇，所以文档总数 $N=2$。

- 「喜欢」出现在两篇中，它的文档频率 $df=2$。
- 「鱼」只出现在文档 A 中，它的 $df=1$。

注意：$df$ 数的是**包含这个词的文档有几篇**，不是这个词一共出现了几次。

## 三、第一步：计算 TF

文档 A 是 `["猫", "喜欢", "吃", "鱼"]`，4 个词，每个都出现 1 次：

$$
TF(\text{鱼})=\frac{1}{4}=0.25,\qquad TF(\text{喜欢})=\frac{1}{4}=0.25
$$

两个词的 TF 一样。但它们的 IDF 不一样，所以最后的 TF-IDF 也会不一样。

## 四、第二步：计算 IDF

继续用上一课的平滑 IDF 公式：

$$
IDF=\ln\left(\frac{N+1}{df+1}\right)+1
$$

| 符号 | 含义 |
|---|---|
| $N$ | 文档总数 |
| $df$ | 包含这个词的文档数量 |
| $\ln$ | 自然对数，交给 Python 算 |

「喜欢」：

$$
IDF(\text{喜欢})=\ln\left(\frac{3}{3}\right)+1=1
$$

「鱼」：

$$
IDF(\text{鱼})=\ln\left(\frac{3}{2}\right)+1\approx1.405
$$

「鱼」只出现在一篇文档里，所以它的 IDF 比「喜欢」高。

## 五、第三步：计算 TF-IDF

| 词语 | TF | IDF（约） | TF-IDF（约） |
|---|---:|---:|---:|
| 喜欢 | 0.25 | 1.000 | 0.250 |
| 鱼 | 0.25 | 1.405 | 0.351 |

**关键理解：TF 一样的时候，出现在更少文档里的词，IDF 更高，TF-IDF 也更高。**

但 TF-IDF 高不等于这个词一定最重要，更不代表计算机理解了它的意思。它只是一个统计出来的权重。

## 六、第四步：用 Python 完成计算

```python
import math

documents = [
    ["猫", "喜欢", "吃", "鱼"],
    ["狗", "喜欢", "吃", "肉"]
]

N = len(documents)

word = "鱼"

# 计算包含该词的文档数量
df = sum(word in doc for doc in documents)

# 计算平滑 IDF
idf = math.log((N + 1) / (df + 1)) + 1

# 计算文档 A 中该词的 TF
doc = documents[0]
tf = doc.count(word) / len(doc)

# 计算 TF-IDF
tf_idf = tf * idf

print("文档总数:", N)
print("文档频率:", df)
print("TF:", tf)
print("IDF:", round(idf, 3))
print("TF-IDF:", round(tf_idf, 3))
```

输出：

```text
文档总数: 2
文档频率: 1
TF: 0.25
IDF: 1.405
TF-IDF: 0.351
```

把 `word` 改成 `"喜欢"` 再跑一次，会得到 `文档频率: 2`、`IDF: 1.0`、`TF-IDF: 0.25`，和上面的表一致。

### 重点理解这三行

```python
N = len(documents)
```

数的是**文档有几篇**，不是文档里有几个词。`documents` 是一个装着两篇文档的列表，所以 `N` 是 2。

```python
df = sum(word in doc for doc in documents)
```

逐篇检查文档里有没有这个词。`word in doc` 的结果是 `True` 或 `False`，而在 Python 里 `True` 就等于 1、`False` 等于 0，所以直接 `sum` 就能数出有几篇包含它。比如 `sum([True, False, True])` 的结果是 `2`。一个词在同一篇里出现再多次，`word in doc` 也只给一个 `True`，所以每篇最多算一次。

```python
tf_idf = tf * idf
```

当前文档的词频，乘以这个词的逆文档频率。

这段代码是为了让你看清计算过程。实际项目里我们会用成熟的工具，第 23 课就会学到。

## 七、小测

今天重点检查你是否理解了代码和变量的含义。

**1.** 一个词在同一篇文档中出现 3 次，但只出现在这一篇文档中，那么 df 应该是多少？

- A. 1
- B. 3
- C. 取决于文档总词数

**2.** 在今天的例子中，「鱼」和「喜欢」的 TF 都是 0.25，为什么「鱼」的 TF-IDF 更高？

- A. 因为「鱼」的 TF 更高
- B. 因为「鱼」的 IDF 更高
- C. 因为「鱼」的 Token ID 更大

**3.** 下面这行代码的作用是什么？

```python
df = sum(word in doc for doc in documents)
```

- A. 统计所有文档的总词数
- B. 统计目标词在所有文档中总共出现了多少次
- C. 统计包含目标词的文档数量

<details>
<summary>答案</summary>

1. A。df 数的是「几篇文档包含它」，出现 3 次也只在 1 篇里。
2. B。TF 一样，差别全在 IDF。
3. C。B 是最容易选错的：要数总次数得用 `sum(doc.count(word) for doc in documents)`，那是另一回事。

</details>

今天你把三件事连起来了：算当前文档的 TF，算整个集合的 df 再得到 IDF，两者相乘得到 TF-IDF。能说清每个变量是什么意思，比背下整段代码更重要。

## 讲评（10-26）

你交的是 **A、B、C**，三题全对。

第 1 题和第 3 题考的是同一件事：**TF 看次数，df 看篇数。** 这两个都和「出现」有关，最容易混。你两题都选对了，说明这个区分已经建立起来了。

你的概念题一直很稳，下一课要换个练法：不只看懂代码，而是自己动手把它写出来。

