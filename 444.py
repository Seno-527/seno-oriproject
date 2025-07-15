class RestaurantOrderSystem:
    def __init__(self):
        # 菜品数据 - 名称和价格
        self.menu_items = [
            {"name": "红烧肉", "price": 28},
            {"name": "清蒸鱼", "price": 32},
            {"name": "宫保鸡丁", "price": 45},
            {"name": "米饭", "price": 2},
            {"name": "蔬菜沙拉", "price": 5},
            {"name": "汤", "price": 15},
            {"name": "海鲜拼盘", "price": 88}
        ]
        self.current_order = []

    def display_menu(self):
        print("\n===== 菜单 =====")
        for idx, item in enumerate(self.menu_items, 1):
            print(f"{idx}. {item['name']} - {item['price']}元")

    def take_order(self):
        while True:
            self.display_menu()
            print("\n当前订单:")
            self.display_current_order()

            try:
                choice = input("\n请输入菜品编号添加到订单 (q退出, c清空订单): ")

                if choice.lower() == 'q':
                    break
                elif choice.lower() == 'c':
                    self.current_order = []
                    print("订单已清空")
                    continue

                item_idx = int(choice) - 1
                if 0 <= item_idx < len(self.menu_items):
                    selected_item = self.menu_items[item_idx]
                    quantity = int(input(f"请输入 {selected_item['name']} 的数量: "))

                    # 检查是否已点过此菜品
                    found = False
                    for item in self.current_order:
                        if item['name'] == selected_item['name']:
                            item['quantity'] += quantity
                            found = True
                            break

                    if not found:
                        self.current_order.append({
                            'name': selected_item['name'],
                            'price': selected_item['price'],
                            'quantity': quantity
                        })

                    print(f"已添加 {quantity}份 {selected_item['name']}")
                else:
                    print("无效的编号，请重新输入")
            except ValueError:
                print("请输入有效的数字")

    def display_current_order(self):
        if not self.current_order:
            print("  当前没有订单")
            return

        total = 0
        for item in self.current_order:
            item_total = item['price'] * item['quantity']
            print(f"  {item['name']} - {item['price']}元 × {item['quantity']} = {item_total}元")
            total += item_total

        print(f"  总计: {total}元")

    def run(self):
        print("=== 餐厅点餐系统 ===")
        self.take_order()
        print("\n最终订单:")
        self.display_current_order()
        print("\n感谢使用点餐系统！")


if __name__ == "__main__":
    system = RestaurantOrderSystem()
    system.run()