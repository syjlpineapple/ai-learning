import random

def check_guess(input_num:int ,random_num:int) -> str:
    if input_num < random_num:
        return "小了"
    elif input_num > random_num:
        return "大了"
    else:
        return "正确"

r_num = random.randint(1, 100)
print("随机数",r_num)
count = 0

while True:
    i_num = input("请输入数字")

    if i_num == 'q':
        print(f"游戏退出：共输入{count}次")
        break
    try:
        i_num = int(i_num)
        count += 1
        result = check_guess(i_num,r_num)
        print(result)
        if result == "正确":
            break
    except ValueError:
        print("输入无效，请输入正整数，退出请输入‘q’")






