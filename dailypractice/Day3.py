import random

count = 0
random_num = random.randint(1, 100)
print("随机数",random_num)
while True:
    input_num = input("请输入数字")

    if input_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break

    try:
        input_num = int(input_num)
        count += 1
        if int(input_num) < random_num:
            print("猜小了")
        elif int(input_num) > random_num:
            print("猜大了")
        else:
            print(f"猜对了，共猜了{count}次")
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")


