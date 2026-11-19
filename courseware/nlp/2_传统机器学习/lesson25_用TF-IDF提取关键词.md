---
kind: lesson
outline: [2, 2]
time: 45 分钟
uses: [逐篇提取关键词, 嵌套循环, f-string, max 与 argmax]
record:
  - text: 第 24-27 课 · 机器学习流程
    link: /records/nlp/06_机器学习流程
  - text: 当时的代码 course_25.py
    link: https://github.com/syjlpineapple/ai-learning/blob/main/nlp/course_25.py
---

# 第 25 课：使用 TF-IDF 提取文本关键词

上一课你学会了从一篇文档里找出权重最高的词。今天是一个小阶段的总结课：把 TF、IDF、归一化、特征矩阵、`argmax()`、`enumerate()` 组合起来，**对每一篇文档都找出它的关键词**。

今天不要求你独立写完整项目，我们一步步来。

## 一、今天的学习目标

1. 输入多篇文本。
2. 用 `TfidfVectorizer` 生成特征矩阵。
3. 找出每篇文本里权重最高的词。
4. 看懂并解释结果。

## 二、第一步：准备文本数据

模拟三条商品评论：

```python
documents = [
    "phone camera good quality",
    "phone battery good",
    "camera quality excellent"
]
```

- 评论 A：手机摄像头质量很好
- 评论 B：手机电池很好
- 评论 C：摄像头质量优秀

每条评论就是一篇文档。

## 三、第二步：生成 TF-IDF 矩阵

```python
from sklearn.feature_extraction.text import TfidfVectorizer

documents = [
    "phone camera good quality",
    "phone battery good",
    "camera quality excellent"
]

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(documents)

words = vectorizer.get_feature_names_out()

print("词汇表：")
print(words)

print("矩阵形状：")
print(X.shape)

print("TF-IDF矩阵：")
print(X.toarray().round(3))
```

```text
词汇表：
['battery' 'camera' 'excellent' 'good' 'phone' 'quality']
矩阵形状：
(3, 6)
TF-IDF矩阵：
[[0.    0.5   0.    0.5   0.5   0.5  ]
 [0.681 0.    0.    0.518 0.518 0.   ]
 [0.    0.518 0.681 0.    0.    0.518]]
```

| 代码 | 作用 |
|---|---|
| `TfidfVectorizer()` | 创建 TF-IDF 工具 |
| `fit_transform()` | 学习词汇和 IDF，并生成特征矩阵 |
| `get_feature_names_out()` | 获取词汇表 |
| `X.shape` | 查看矩阵形状 |
| `X.toarray()` | 把稀疏矩阵转成普通数组 |

3 条评论，6 个不同的词，所以是 `(3, 6)`。

## 四、第三步：提取每条评论的关键词

这是今天最重要的部分。先看完整代码：

```python
import numpy as np

for doc_index in range(len(documents)):

    row = X.toarray()[doc_index]

    max_weight = row.max()

    print("第", doc_index + 1, "条评论的关键词：")

    for i, weight in enumerate(row):

        if np.isclose(weight, max_weight):
            print(words[i], weight)
```

```text
第 1 条评论的关键词：
camera 0.5
good 0.5
phone 0.5
quality 0.5
第 2 条评论的关键词：
battery 0.680918560398684
第 3 条评论的关键词：
excellent 0.680918560398684
```

别着急，一步步拆开。

**1. 遍历所有评论**

```python
for doc_index in range(len(documents)):
```

3 条评论，`doc_index` 依次是 0、1、2。

**2. 取出当前评论的 TF-IDF 向量**

```python
row = X.toarray()[doc_index]
```

`doc_index = 0` 时，就是第一条评论那一行。

**3. 找到这一行的最大权重**

```python
max_weight = row.max()
```

注意这一行写在外层循环**里面**，每条评论各算各的最大值。

**4. 遍历这一行的所有词和权重**

```python
for i, weight in enumerate(row):
```

`i` 是词的位置，`weight` 是对应的权重。

**5. 输出权重等于最大值的词**

```python
if np.isclose(weight, max_weight):
    print(words[i], weight)
```

用 `np.isclose()`，是为了避开浮点数的精度误差。

## 五、第四步：理解结果

为什么三条评论的结果这么不一样？对一下每个词出现在几条评论里：

| 词 | 出现在几条评论里 | 结果 |
|---|---:|---|
| `battery` | 1 | 第 2 条的关键词 |
| `excellent` | 1 | 第 3 条的关键词 |
| `phone`、`camera`、`good`、`quality` | 各 2 | 第 1 条四个词**全部并列** |

`battery` 和 `excellent` 只出现在一条评论里，IDF 高，就成了那一条的关键词。

第 1 条的四个词，每个都出现在两条评论里，TF 一样、IDF 也一样，归一化后各占 0.5。TF-IDF 分不出谁更重要，所以四个全部并列。这种时候如果用 `argmax`，会漏掉三个词。

记住：**TF-IDF 找出的是统计意义上权重高的词，不一定是人眼里真正的关键词。** 三条评论的语料太小，IDF 能区分的东西有限。

## 六、小测

```python
words = ["apple", "banana", "orange", "grape"]
row = np.array([0.2, 0.8, 0.5, 0.3])
```

我们想找到权重最高的词。

**1.** 下面哪行代码可以找到最大权重？

- A. `row.argmax()`
- B. `row.max()`
- C. `row.sum()`

**2.** 下面哪行代码可以找到最大权重对应的词语？

- A. `words[row.max()]`
- B. `words[np.argmax(row)]`
- C. `words[0]`

**3.** 为什么我们使用 `enumerate(row)`？

- A. 同时获取索引和权重
- B. 计算 IDF
- C. 删除重复词语

<details>
<summary>答案</summary>

1. B。`row.max()` 给的是数值 0.8；`row.argmax()` 给的是位置 1。
2. B。先 `argmax` 拿到位置 1，再去 `words` 里查。A 是拿 0.8 当下标，会直接报错，列表的下标必须是整数。
3. A。

</details>

完成今天的练习，你就走完了第一个 NLP 基础阶段：把文本变成数字，并且能读懂这些数字。下一课开始进入机器学习。

## 讲评（11-04）

你一共交了两版代码，还有一次小测。

**第一版**里你写的是：

```python
max_weight = np.max(X)
```

放在循环外面。`np.max(X)` 算的是**整个矩阵**的最大值，不是每条评论自己的最大值。跑出来是这样：

```text
battery 0.680918560398684
excellent 0.680918560398684
```

第 1 条评论一个关键词都没有。它的最大值只有 0.5，永远等不到 0.681。程序不报错，只是悄悄少了一条结果，这种错最难发现。

**第二版**你把 `max_weight = np.max(row)` 挪进了循环，换成了 `np.isclose`，最关键的问题改对了。剩下一个小地方：

```python
print("第{i}条评论中权重最高的词", i, words[index], weight)
```

字符串前面没有加 `f`，`{i}` 不会被替换，屏幕上会原样打出 `第{i}条评论中权重最高的词 0 camera 0.5`。最后提交的 `course_25.py` 已经改成了 `f"第{i+1}条..."`，编号也从 1 开始了。

**小测**你交的是 **A、A、A**，第 3 题对，前两题错。第 1 题混了 `max` 和 `argmax`；第 2 题选的 `words[row.max()]` 会用 0.8 当下标。有意思的是，你自己的代码里 `np.max(row)` 用得完全正确，说明不是不会用，是两个名字长得太像。你随后问「`row.max()` 和 `np.max(row)` 是不是一样的」，答案是一样，一个是数组自己的方法，一个是 NumPy 的函数。你把这四行写进了 `course_25.py` 的注释里：

```python
row.max()       # 最大值：0.9
np.max(row)     # 最大值
row.argmax()    # 最大值的索引：2
np.argmax(row)  # 最大值的索引：2
```

记一句就够：**`max` 找数值，`argmax` 找位置。**

