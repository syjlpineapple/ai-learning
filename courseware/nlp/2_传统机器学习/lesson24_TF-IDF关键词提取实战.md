---
kind: lesson
outline: [2, 2]
time: 40 分钟
uses: [np.argmax, max 与 argmax, enumerate, np.isclose, 读懂特征矩阵]
record:
  - text: 第 24-27 课 · 机器学习流程
    link: /records/nlp/06_机器学习流程
  - text: 当时的代码 course_24_1.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/course_24_1.py
  - text: 当时的代码 course_24_2.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/course_24_2.py
---

# 第 24 课：TF-IDF 关键词提取实战

上一课你学会了生成 TF-IDF 矩阵，还弄清了它为什么和手算的不一样。但会生成矩阵还不够，算法工程师得能**从矩阵里读出信息**，能解释模型的输入是什么。

今天就做一件事：**找出一篇文档里权重最高的词。**

## 一、准备数据

还是上一课那两篇：

```python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat likes fish",
    "dog likes meat"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

words = vectorizer.get_feature_names_out()

print(words)
print(X.toarray().round(3))
```

```text
['cat' 'dog' 'fish' 'likes' 'meat']
[[0.632 0.    0.632 0.449 0.   ]
 [0.    0.632 0.    0.449 0.632]]
```

`words` 的顺序就是矩阵列的顺序。**`words[i]` 和第 `i` 列是同一个词的「名字」和「权重」。** 今天所有的操作都靠这个对应关系。

## 二、取出第一篇文档的权重

```python
row = X.toarray()[0]

print(row)
```

```text
[0.6316672  0.         0.6316672  0.44943642 0.        ]
```

`[0]` 表示取第 1 篇文档，Python 的索引从 0 开始。这里没有 `round(3)`，所以小数位多一些。

## 三、找到权重最大的词

NumPy 的 `argmax()` 能找到最大值**所在的位置**：

```python
import numpy as np

index = np.argmax(row)

print(index)
print(words[index])
print(row[index])
```

```text
0
cat
0.6316672017376245
```

最大权重在第 0 列，第 0 列对应的词是 `cat`。

三个容易混的写法放在一起：

| 写法 | 作用 | `row = [0.2, 0.8, 0.5]` 时的结果 |
|---|---|---|
| `np.argmax(row)` | 最大值的**位置** | `1` |
| `np.max(row)` 或 `row.max()` | 最大值**本身** | `0.8` |
| `row[1]` | 取索引 1 的元素 | `0.8` |

查词的套路固定是两步：先用 `argmax` 拿位置，再用位置去 `words` 里查名字。

## 四、并列最高怎么办？

仔细看第一行：`cat` 和 `fish` 都是 0.632，它们**并列最高**。可 `argmax()` 只给了 `cat`。

这是因为 **`argmax()` 遇到多个相同的最大值，只返回第一个的位置。** `fish` 被漏掉了。

要找出所有并列最高的词，换个思路：先拿到最大值，再一个一个比。

```python
max_weight = row.max()

for i, weight in enumerate(row):
    if np.isclose(weight, max_weight):
        print(words[i], weight)
```

```text
cat 0.6316672017376245
fish 0.6316672017376245
```

这次两个都找到了。

## 五、`enumerate()` 是什么？

```python
for i, weight in enumerate(row):
```

`enumerate()` 是 Python 自带的函数，遍历列表时**同时拿到位置和值**：

```python
row = [0.2, 0.8, 0.5]

for i, weight in enumerate(row):
    print(i, weight)
```

```text
0 0.2
1 0.8
2 0.5
```

它每次给出一对数据 `(0, 0.2)`、`(1, 0.8)`、`(2, 0.5)`，Python 自动把这一对拆开，分别放进 `i` 和 `weight`。这叫**解包**。

为什么这里非用它不可？因为只拿到权重 0.632 不够，你还得知道它是**第几个**，才能去 `words[i]` 查出是哪个词。只遍历值的话，你能打印出两个 0.632，却说不出它们是谁。

再记三个遍历写法：

| 写法 | 含义 |
|---|---|
| `for x in row` | 只拿元素 |
| `for i in range(len(row))` | 通过索引遍历 |
| `for i, x in enumerate(row)` | 同时拿索引和元素 |

## 六、为什么用 `np.isclose`，不用 `==`？

计算机用二进制存小数，0.1、0.2 这类数存不精确：

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(np.isclose(0.1 + 0.2, 0.3))
```

```text
0.30000000000000004
False
True
```

`np.isclose(a, b)` 判断的是「差得足够小，可以当作相等」。TF-IDF 的权重经过了除法、对数、开平方，两个数学上相等的数，算出来可能在最后几位小数上不一样。用 `==` 比，程序不会报错，只会悄悄少输出一个词。

## 七、实战巩固：三篇文档

现在把几个知识点串起来，读懂一段完整代码。加一篇 `cat likes meat`：

```python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "cat likes fish",
    "dog likes meat",
    "cat likes meat"
]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)
words = vectorizer.get_feature_names_out()

print(words)
print(X.shape)
print(X.toarray().round(3))

# 提取第一篇文档的关键词
row = X.toarray()[0]
max_weight = row.max()

for i, weight in enumerate(row):
    if np.isclose(weight, max_weight):
        print(words[i], weight)
```

```text
['cat' 'dog' 'fish' 'likes' 'meat']
(3, 5)
[[0.548 0.    0.72  0.425 0.   ]
 [0.    0.72  0.    0.425 0.548]
 [0.62  0.    0.    0.481 0.62 ]]
fish 0.7203334490549893
```

这次第一篇只剩 `fish` 一个关键词了。为什么？因为 `cat` 现在出现在两篇文档里（第 1 篇和第 3 篇），IDF 变低了；`fish` 还是只在一篇里，IDF 高。**文档集合变了，同一篇文档里词的权重也会变。** 这正是 IDF「看整个集合」的意思。

整个流程就是：输入文本 → `TfidfVectorizer` → TF-IDF 矩阵 → 找最大权重 → 查出对应的词。

## 八、小测

**1.** `row = [0.2, 0.8, 0.5]`，`np.argmax(row)` 返回什么？

- A. `0`，因为第一个词的索引是 0
- B. `1`，因为最大值 0.8 位于索引 1
- C. `2`，因为向量有 3 个元素

**2.** `words = ["cat", "dog", "fish", "meat"]`，`row = [0.6, 0.2, 0.6, 0.3]`，`print(words[np.argmax(row)])` 输出什么？

- A. cat
- B. fish
- C. cat 和 fish

**3.** `row = [0.3, 0.7, 0.9]`，用 `for i, weight in enumerate(row)` 遍历，第三次循环时 `i` 和 `weight` 分别是什么？

- A. `i = 2`，`weight = 0.9`
- B. `i = 3`，`weight = 0.9`
- C. `i = 2`，`weight = 0.7`

**4.** `row = np.array([0.2, 0.8, 0.5, 0.3])`，`row.max()` 是多少？

- A. 0.2
- B. 0.5
- C. 0.8
- D. 0.3

**5.** `words = ["apple", "banana", "orange", "grape"]`，上一题的 `row` 不变，`print(words[np.argmax(row)])` 输出哪个词？

- A. apple
- B. banana
- C. orange
- D. grape

<details>
<summary>答案</summary>

1. B。`argmax` 给的是位置。
2. A。并列最高时 `argmax` 只返回第一个。想要两个都拿到，用第四部分的写法。
3. A。索引从 0 开始，第三次是 2。
4. C。
5. B。最大值 0.8 在索引 1，`words[1]` 是 `banana`。

</details>

## 讲评（11-03）

这一课跨了两次。10-27 学到 `argmax` 就停了，11-03 回来交了第 1 题：**B**，对。

接着你问了一句「`for i, weight in enumerate(row):` 这个是啥意思」，第五部分就是那次的解释。enumerate 理解题（第 3 题）你选 **A**，对。实战巩固的两题（第 4、5 题）你交的是 **C、B**，都对。第 2 题当时没有交答案。

两份代码都在仓库里。`course_24_1.py` 用 `enumerate` 加 `np.isclose` 找出了 `cat` 和 `fish`；最后你还试了一段只遍历值的循环，它只能打印出两个 `0.6316672`，说不出是哪两个词，正好反过来说明了为什么要 `enumerate`。

`course_24_2.py` 里你把比较写成了 `weight == max_weight`。这次没出错，输出 `fish 0.7203334490549893`，因为三篇文档时第一行的最高值只有一个。但换一组有并列、而且并列的两个数来自不同计算路径的数据，`==` 就可能漏词。没有理由冒这个险，还是用 `np.isclose`。

