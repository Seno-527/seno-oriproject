# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox


class DianCanSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("点餐系统")
        self.root.geometry("600x400")

        # 菜单数据
        self.menu = {
            "鱼香肉丝": 28,
            "宫保鸡丁": 32,
            "水煮鱼": 45,
            "米饭": 2,
            "可乐": 5
        }
        self.order = {}

        # 界面布局
        self.setup_ui()

    def setup_ui(self):
        # 左侧菜单列表
        frame_menu = ttk.LabelFrame(self.root, text="菜单", padding=10)
        frame_menu.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.tree_menu = ttk.Treeview(frame_menu, columns=("price"), show="headings", height=15)
        self.tree_menu.heading("#0", text="菜品")
        self.tree_menu.heading("price", text="价格（元）")
        self.tree_menu.column("#0", width=120)
        self.tree_menu.column("price", width=80, anchor=tk.CENTER)

        for dish, price in self.menu.items():
            self.tree_menu.insert("", tk.END, text=dish, values=(price,))
        self.tree_menu.pack()

        # 右侧订单区
        frame_order = ttk.LabelFrame(self.root, text="订单", padding=10)
        frame_order.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_order = ttk.Treeview(frame_order, columns=("price", "subtotal"), show="headings", height=10)
        self.tree_order.heading("#0", text="菜品")
        self.tree_order.heading("price", text="单价")
        self.tree_order.heading("subtotal", text="小计")
        self.tree_order.column("#0", width=120)
        self.tree_order.column("price", width=80, anchor=tk.CENTER)
        self.tree_order.column("subtotal", width=80, anchor=tk.CENTER)
        self.tree_order.pack(fill=tk.BOTH, expand=True)

        # 操作按钮
        frame_buttons = ttk.Frame(frame_order)
        frame_buttons.pack(fill=tk.X, pady=5)

        self.spin_num = tk.Spinbox(frame_buttons, from_=1, to=10, width=5)
        self.spin_num.pack(side=tk.LEFT, padx=5)

        btn_add = ttk.Button(frame_buttons, text="点餐", command=self.add_dish)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_remove = ttk.Button(frame_buttons, text="退菜", command=self.remove_dish)
        btn_remove.pack(side=tk.LEFT, padx=5)

        btn_checkout = ttk.Button(frame_order, text="结算", command=self.checkout)
        btn_checkout.pack(pady=10)

    def add_dish(self):
        selected = self.tree_menu.focus()
        if not selected:
            messagebox.showwarning("提示", "请先选择菜品！")
            return

        dish = self.tree_menu.item(selected, "text")
        price = self.menu[dish]
        num = int(self.spin_num.get())

        if dish in self.order:
            self.order[dish] += num
        else:
            self.order[dish] = num

        self.update_order_list()

    def remove_dish(self):
        selected = self.tree_order.focus()
        if not selected:
            messagebox.showwarning("提示", "请先选择订单中的菜品！")
            return

        dish = self.tree_order.item(selected, "text")
        num = int(self.spin_num.get())

        if self.order[dish] <= num:
            del self.order[dish]
        else:
            self.order[dish] -= num

        self.update_order_list()

    def update_order_list(self):
        self.tree_order.delete(*self.tree_order.get_children())
        for dish, num in self.order.items():
            price = self.menu[dish]
            subtotal = price * num
            self.tree_order.insert("", tk.END, text=dish, values=(price, subtotal))

    def checkout(self):
        if not self.order:
            messagebox.showwarning("提示", "订单为空！")
            return

        total = sum(self.menu[dish] * num for dish, num in self.order.items())
        discount = tk.simpledialog.askfloat("折扣", "请输入折扣率（0.1~1.0）：", minvalue=0.1, maxvalue=1.0)

        if discount is None:
            return

        final_price = total * discount
        messagebox.showinfo("结算结果",
                            f"总价: {total}元\n折扣率: {discount}\n实付: {final_price:.2f}元")


if __name__ == "__main__":
    root = tk.Tk()
    app = DianCanSystem(root)
    root.mainloop()