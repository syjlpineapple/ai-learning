"""
print("随机数：",random_num)
print(f"随机数：{random_num}")

1. random 导入方式不对
你写的是：
from random import random
random_num = random.randint(1, 100)
这里的 random 实际上是一个函数，不是整个模块，所以不能直接调用 random.randint()。
有两种正确写法，选一种就行：
写法 A（推荐，比较直观）
import random
random_num = random.randint(1, 100)

写法 B
from random import randint
random_num = randint(1, 100)
"""

import random

random_num = random.randint(1, 100)
print("随机数：",random_num)
# 或者print(f"随机数：{random_num}")
while True:
    input_num = int(input("请输入数字:"))
    if input_num > random_num:
        print("猜大了")
    elif input_num < random_num:
        print("猜小了")
    else:
        print("猜对了")
        break
