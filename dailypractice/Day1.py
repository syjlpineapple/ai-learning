input_num = int(input("请输入数字"))

if input_num > 10:
    print("输入的数字太大了")
elif input_num < 10:
    print("输入的数字太小了")
else:
    print("猜对了")


while 1:
    input_num = input("请输入数字")

    if input_num.isdigit():
        input_num = int(input_num)
        if input_num > 10:
            print("输入的数字太大了")
        elif input_num < 10:
            print("输入的数字太小了")
        else:
            exit(0)
    else:
        if input_num == 'q':
            exit(0)