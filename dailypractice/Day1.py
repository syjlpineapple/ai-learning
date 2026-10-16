"""
    1. input() 表示输入
    2. exit() 和 break的区别： exit(0) 退出程序，break退出循环
    3. isdigit 判断是否是整形
"""

input_num = int(input("请输入数字"))

if input_num > 10:
    print("输入的数字太大了")
elif input_num < 10:
    print("输入的数字太小了")
else:
    print("猜对了")


while True:
    input_num = input("请输入数字")

    if input_num.isdigit():
        input_num = int(input_num)
        if input_num > 10:
            print("输入的数字太大了")
        elif input_num < 10:
            print("输入的数字太小了")
        else:
            break
    else:
        if input_num == 'q':
            break


