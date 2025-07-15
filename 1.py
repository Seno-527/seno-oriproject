import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget, QTableWidget,
                             QTableWidgetItem, QComboBox, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class RestaurantOrderSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("餐厅点菜系统")
        self.setGeometry(100, 100, 800, 600)

        # 初始化数据
        self.menu = {
            "红烧肉": 28,
            "清蒸鱼": 32,
            "宫保鸡丁": 45,
            "米饭": 2,
            "蔬菜沙拉": 5,
            "汤": 15,
            "海鲜拼盘": 88
        }
        self.order = {
            "customer_name": "",
            "dishes": {},
            "total": 0,
            "discount": 1.0
        }

        # 设置UI
        self.init_ui()

    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 左侧菜单区域
        left_panel = QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # 顾客姓名输入
        name_label = QLabel("顾客姓名:")
        name_label.setFont(QFont("Arial", 10))
        self.name_input = QLineEdit()
        left_layout.addWidget(name_label)
        left_layout.addWidget(self.name_input)

        # 菜单列表
        menu_label = QLabel("菜单:")
        menu_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(menu_label)

        self.menu_list = QListWidget()
        for dish, price in self.menu.items():
            self.menu_list.addItem(f"{dish} - {price}元")
        left_layout.addWidget(self.menu_list)

        # 数量选择
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel("数量:")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spin)
        left_layout.addLayout(quantity_layout)

        # 操作按钮
        add_button = QPushButton("添加菜品")
        add_button.clicked.connect(self.add_dish)
        remove_button = QPushButton("移除菜品")
        remove_button.clicked.connect(self.remove_dish)
        left_layout.addWidget(add_button)
        left_layout.addWidget(remove_button)

        # 右侧订单区域
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # 当前订单
        order_label = QLabel("当前订单:")
        order_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(order_label)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(3)
        self.order_table.setHorizontalHeaderLabels(["菜品", "单价", "数量"])
        self.order_table.setColumnWidth(0, 150)
        self.order_table.setColumnWidth(1, 80)
        self.order_table.setColumnWidth(2, 80)
        right_layout.addWidget(self.order_table)

        # 总价和折扣
        total_layout = QHBoxLayout()
        total_label = QLabel("总价:")
        self.total_display = QLabel("0元")
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        right_layout.addLayout(total_layout)

        discount_layout = QHBoxLayout()
        discount_label = QLabel("折扣率:")
        self.discount_input = QLineEdit("1.0")
        discount_layout.addWidget(discount_label)
        discount_layout.addWidget(self.discount_input)
        right_layout.addLayout(discount_layout)

        final_layout = QHBoxLayout()
        final_label = QLabel("实付金额:")
        self.final_display = QLabel("0元")
        final_layout.addWidget(final_label)
        final_layout.addWidget(self.final_display)
        right_layout.addLayout(final_layout)

        # 结账按钮
        checkout_button = QPushButton("结账")
        checkout_button.clicked.connect(self.checkout)
        right_layout.addWidget(checkout_button)

        # 添加左右面板
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

    def add_dish(self):
        selected = self.menu_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择菜品")
            return

        dish_name = selected.text().split(" - ")[0]
        quantity = self.quantity_spin.value()

        # 更新订单
        if dish_name in self.order["dishes"]:
            self.order["dishes"][dish_name] += quantity
        else:
            self.order["dishes"][dish_name] = quantity

        # 更新顾客姓名
        self.order["customer_name"] = self.name_input.text()

        self.update_order_display()

    def remove_dish(self):
        selected = self.menu_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择菜品")
            return

        dish_name = selected.text().split(" - ")[0]
        quantity = self.quantity_spin.value()

        if dish_name in self.order["dishes"]:
            if self.order["dishes"][dish_name] > quantity:
                self.order["dishes"][dish_name] -= quantity
            else:
                del self.order["dishes"][dish_name]

        self.update_order_display()

    def update_order_display(self):
        self.order_table.setRowCount(len(self.order["dishes"]))

        total = 0
        for row, (dish, quantity) in enumerate(self.order["dishes"].items()):
            price = self.menu[dish]
            self.order_table.setItem(row, 0, QTableWidgetItem(dish))
            self.order_table.setItem(row, 1, QTableWidgetItem(f"{price}元"))
            self.order_table.setItem(row, 2, QTableWidgetItem(str(quantity)))

            total += price * quantity

        self.order["total"] = total
        self.total_display.setText(f"{total}元")

        # 计算折扣后价格
        self.calculate_final_price()

    def calculate_final_price(self):
        try:
            discount = float(self.discount_input.text())
            if discount <= 0 or discount > 1:
                raise ValueError
            self.order["discount"] = discount
            final_price = self.order["total"] * discount
            self.final_display.setText(f"{final_price:.2f}元")
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的折扣率(0-1之间)")
            self.discount_input.setText("1.0")
            self.order["discount"] = 1.0
            self.final_display.setText(f"{self.order['total']}元")

    def checkout(self):
        if not self.order["dishes"]:
            QMessageBox.warning(self, "警告", "订单为空，请先添加菜品")
            return

        # 显示账单详情
        bill_details = f"顾客: {self.order['customer_name']}\n\n"
        bill_details += "订单明细:\n"

        for dish, quantity in self.order["dishes"].items():
            price = self.menu[dish]
            bill_details += f"{dish} - {price}元 × {quantity} = {price * quantity}元\n"

        bill_details += f"\n总价: {self.order['total']}元\n"
        bill_details += f"折扣率: {self.order['discount']}\n"
        bill_details += f"实付金额: {float(self.final_display.text()[:-1]):.2f}元"

        QMessageBox.information(self, "账单", bill_details)

        # 重置订单
        self.order = {
            "customer_name": self.name_input.text(),
            "dishes": {},
            "total": 0,
            "discount": 1.0
        }
        self.update_order_display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    system = RestaurantOrderSystem()
    system.show()
    sys.exit(app.exec_())