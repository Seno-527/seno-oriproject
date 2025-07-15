# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class DianCanSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("点餐系统 - 优化版")
        self.root.geometry("700x500")
        self.root.configure(bg="#F5F5F5")

        # 菜单数据（菜品名称 -> 价格）
        self.menu = {
            "鱼香肉丝": 28,
            "宫保鸡丁": 32,
            "水煮鱼": 45,
            "米饭": 2,
            "可乐": 5,
            "蓝汁叉烧包": 15,
            "沙皇黑金链肚": 88
        }
        self.order = {}  # 订单存储（菜品 -> 数量）

        # 设置UI
        self.setup_ui()

    def setup_ui(self):
        # 顶部标题
        lbl_title = tk.Label(
            self.root, text="点餐系统",
            font=("微软雅黑", 16, "bold"), bg="#F5F5F5", fg="#333"
        )
        lbl_title.pack(pady=10)

        # 主框架（菜单 + 订单）
        frame_main = tk.Frame(self.root, bg="#F5F5F5")
        frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 左侧菜单列表
        frame_menu = ttk.LabelFrame(frame_main, text="菜单", padding=10)
        frame_menu.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.tree_menu = ttk.Treeview(
            frame_menu,
            columns=("price"),
            show="headings",
            height=15,
            selectmode="browse"
        )
        self.tree_menu.heading("#0", text="菜品名称", anchor=tk.W)
        self.tree_menu.heading("price", text="价格（元）", anchor=tk.CENTER)
        self.tree_menu.column("#0", width=150, anchor=tk.W)
        self.tree_menu.column("price", width=80, anchor=tk.CENTER)

        # 插入菜单数据
        for dish, price in self.menu.items():
            self.tree_menu.insert("", tk.END, text=dish, values=(price,))
        self.tree_menu.pack()

        # 右侧订单区
        frame_order = ttk.LabelFrame(frame_main, text="当前订单", padding=10)
        frame_order.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_order = ttk.Treeview(
            frame_order,
            columns=("price", "quantity", "subtotal"),
            show="headings",
            height=10
        )
        self.tree_order.heading("#0", text="菜品名称", anchor=tk.W)
        self.tree_order.heading("price", text="单价（元）", anchor=tk.CENTER)
        self.tree_order.heading("quantity", text="数量", anchor=tk.CENTER)
        self.tree_order.heading("subtotal", text="小计（元）", anchor=tk.CENTER)
        self.tree_order.column("#0", width=120, anchor=tk.W)
        self.tree_order.column("price", width=80, anchor=tk.CENTER)
        self.tree_order.column("quantity", width=60, anchor=tk.CENTER)
        self.tree_order.column("subtotal", width=80, anchor=tk.CENTER)
        self.tree_order.pack(fill=tk.BOTH, expand=True)

        # 操作按钮区
        frame_buttons = tk.Frame(frame_order, bg="#F5F5F5")
        frame_buttons.pack(fill=tk.X, pady=10)

        lbl_num = tk.Label(frame_buttons, text="数量:", bg="#F5F5F5")
        lbl_num.pack(side=tk.LEFT, padx=5)

        self.spin_num = tk.Spinbox(frame_buttons, from_=1, to=10, width=5)
        self.spin_num.pack(side=tk.LEFT, padx=5)

        btn_add = ttk.Button(frame_buttons, text="点餐", command=self.add_dish)
        btn_add.pack(side=tk.LEFT, padx=5)

        btn_remove = ttk.Button(frame_buttons, text="退菜", command=self.remove_dish)
        btn_remove.pack(side=tk.LEFT, padx=5)

        btn_checkout = ttk.Button(
            frame_order,
            text="结算订单",
            style="Accent.TButton",
            command=self.checkout
        )
        btn_checkout.pack(pady=10)

    def add_dish(self):
        selected = self.tree_menu.focus()
        if not selected:
            messagebox.showwarning("提示", "请先在菜单中选择菜品！")
            return

        dish = self.tree_menu.item(selected, "text")
        price = self.menu[dish]
        num = int(self.spin_num.get())

        # 更新订单
        if dish in self.order:
            self.order[dish] += num
        else:
            self.order[dish] = num

        self.update_order_list()
        messagebox.showinfo("成功", f"已添加 {dish} x{num}")

    def remove_dish(self):
        selected = self.tree_order.focus()
        if not selected:
            messagebox.showwarning("提示", "请先在订单中选择菜品！")
            return

        dish = self.tree_order.item(selected, "text")
        num = int(self.spin_num.get())

        if self.order[dish] <= num:
            del self.order[dish]
        else:
            self.order[dish] -= num

        self.update_order_list()
        messagebox.showinfo("成功", f"已退 {dish} x{num}")

    def update_order_list(self):
        """刷新订单列表显示"""
        self.tree_order.delete(*self.tree_order.get_children())
        for dish, quantity in self.order.items():
            price = self.menu[dish]
            subtotal = price * quantity
            self.tree_order.insert(
                "", tk.END,
                text=dish,
                values=(price, quantity, subtotal)
            )

    def checkout(self):
        if not self.order:
            messagebox.showwarning("提示", "当前没有订单！")
            return

        total = sum(self.menu[dish] * num for dish, num in self.order.items())
        discount = simpledialog.askfloat(
            "折扣",
            "请输入折扣率（0.1~1.0）：\n例如：0.8表示8折",
            minvalue=0.1,
            maxvalue=1.0,
            initialvalue=1.0
        )

        if discount is None:  # 用户取消输入
            return

        final_price = total * discount
        messagebox.showinfo(
            "结算详情",
            f"总价: {total}元\n折扣率: {discount}\n实付金额: {final_price:.2f}元"
        )


if __name__ == "__main__":
    root = tk.Tk()
    # 设置现代风格（Windows 11效果）
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Accent.TButton", foreground="white", background="#0078D7")

    app = DianCanSystem(root)
    root.mainloop()