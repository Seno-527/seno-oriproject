# -*- coding: utf-8 -*-
# 点餐系统（Python实现）

# 1. 定义菜单（菜品名称 -> 单价）
menu = {
    "金莎红米肠·": 43,
    "招牌虾饺皇": 37,
    "香芒夹心椰汁糕": 37,
    "干炒牛河": 43,
    "杨枝甘露": 43,
    "": 43,
}

# 2. 订单存储（菜品名称 -> 数量）
order_list = {}


# 3. 点菜函数
def order_dishes():
    print("\n=== 菜单 ===")
    for dish, price in menu.items():
        print(f"{dish}: {price}元")

    while True:
        dish = input("\n请输入菜品名称（输入q退出点餐）：").strip()
        if dish == "q":
            break
        if dish not in menu:
            print("菜品不存在，请重新输入！")
            continue

        try:
            num = int(input("请输入数量："))
            if num <= 0:
                print("数量必须大于0！")
                continue
        except ValueError:
            print("请输入有效数字！")
            continue

        if dish in order_list:
            order_list[dish] += num
        else:
            order_list[dish] = num
        print(f"已添加 {dish} x{num}")


# 4. 退菜函数
def back_dishes():
    print("\n=== 当前订单 ===")
    if not order_list:
        print("订单为空！")
        return

    for dish, num in order_list.items():
        print(f"{dish}: {num}份")

    while True:
        dish = input("\n请输入要退的菜品名称（输入q退出）：").strip()
        if dish == "q":
            break
        if dish not in order_list:
            print("订单中没有该菜品！")
            continue

        try:
            num = int(input("请输入退菜数量："))
            if num <= 0:
                print("数量必须大于0！")
                continue
            if num > order_list[dish]:
                print("退菜数量超过订单数量！")
                continue
        except ValueError:
            print("请输入有效数字！")
            continue

        order_list[dish] -= num
        if order_list[dish] == 0:
            del order_list[dish]
        print(f"已退 {dish} x{num}")


# 5. 计算总价函数
def sum_dishes():
    print("\n=== 订单结算 ===")
    if not order_list:
        print("订单为空！")
        return

    total = 0
    print("\n菜品详情：")
    for dish, num in order_list.items():
        price = menu[dish]
        subtotal = price * num
        print(f"{dish} x{num}: {price}元/份 → 小计 {subtotal}元")
        total += subtotal

    print(f"\n总价: {total}元")

    try:
        discount = float(input("请输入折扣率（0.1~1.0，例如0.8表示8折）："))
        if not 0.1 <= discount <= 1.0:
            print("折扣率无效，按原价计算！")
            discount = 1.0
    except ValueError:
        print("输入无效，按原价计算！")
        discount = 1.0

    final_price = total * discount
    print(f"实付金额: {final_price:.2f}元")


# 6. 主程序
def main():
    print("=== 欢迎使用点餐系统 ===")
    while True:
        print("\n1. 点餐\n2. 退菜\n3. 结算\n4. 退出")
        choice = input("请选择操作（1-4）：").strip()

        if choice == "1":
            order_dishes()
        elif choice == "2":
            back_dishes()
        elif choice == "3":
            sum_dishes()
        elif choice == "4":
            print("感谢使用，再见！")
            break
        else:
            print("输入无效，请重新选择！")


if __name__ == "__main__":
    main()