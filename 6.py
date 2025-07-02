# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.font import Font
from PIL import Image, ImageTk

# ==================== 数据层 ====================
menu = {
    "鱼子酱片皮鸭": 688,
    "香槟汁煎银鳕鱼": 318,
    "鱼子酱鹅肝脆皮鸭卷": 438,
    "松茸鲍鱼酥": 48,
    "炭烧蜜汁叉烧": 188,
    "澳龙花椒鸡汤": 198,
    "鹅肝虾多士": 128,
    "香椰冰淇淋蛋糕": 118,
    "柚子抹茶冰淇淋": 103,
    "热巧克力": 108,
    "精选马卡龙": 98,
    "白桃焦糖布丁": 80,
    "荔枝莫吉托": 100,
    "龙舌兰日出": 162
}

order_list = []

# ==================== 业务逻辑 ====================
class OrderSystem:
    @staticmethod
    def calculate_total():
        return sum(menu[dish] * qty for dish, qty in order_list)
    
    @staticmethod
    def apply_discount(total, discount):
        return total * (1 - discount)

# ==================== UI层 ====================
class AppUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        self.apply_styles()
    
    def setup_window(self):
        self.root.title("🌟 Se No-ori Order")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)
        self.root.configure(bg="#e6f0f5")
    
    def apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#e6f0f5"
        card_color = "#f5f9fc"
        accent_color = "#4a6b8a"
        text_color = "#333333"
        
        # 配置Didot字体
        try:
            didot_font = ("Didot", 10)
            title_font = ("Didot", 18, "bold")
            total_font = ("Didot", 14, "bold")
        except:
            didot_font = ("Times New Roman", 10)
            title_font = ("Times New Roman", 18, "bold")
            total_font = ("Times New Roman", 14, "bold")
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color, font=didot_font)
        style.configure('TButton', font=didot_font, padding=8, 
                       background=card_color, foreground=text_color, borderwidth=1)
        style.map('TButton', 
                 background=[('active', '#d8e4f0'), ('pressed', '#c8d4e0')])
        
        style.configure('Title.TLabel', font=title_font, foreground=accent_color)
        style.configure('Subtitle.TLabel', font=didot_font, foreground=text_color)
        style.configure('Total.TLabel', font=total_font, foreground=accent_color)
        
        style.configure('TLabelframe', background=bg_color, foreground=accent_color, 
                       font=(didot_font[0], 12, "bold"), bordercolor="#c0d0e0")
        style.configure('TLabelframe.Label', background=bg_color, foreground=accent_color)
        
        style.configure('Menu.Treeview', background=card_color, fieldbackground=card_color, 
                       foreground=text_color, rowheight=35, font=didot_font)
        style.map('Menu.Treeview', background=[('selected', '#e0e8f0')])
        
        style.configure('Order.Treeview', background=card_color, fieldbackground=card_color, 
                       foreground=text_color, rowheight=30, font=didot_font)
        style.map('Order.Treeview', background=[('selected', '#e0e8f0')])
        
        style.configure('Treeview.Heading', background="#d0dce8", foreground=text_color, 
                       font=(didot_font[0], 10, "bold"), relief='flat')
    
    def on_entry_change(self, event):
        value = self.dish_entry.get()
        
        if value == '':
            self.listbox.place_forget()
            return
        
        # 获取匹配的菜品
        matches = [dish for dish in menu.keys() if value.lower() in dish.lower()]
        
        # 更新列表框
        self.listbox.delete(0, tk.END)
        for dish in matches:
            self.listbox.insert(tk.END, f"{dish} - ¥{menu[dish]}")
        
        # 显示列表框在输入框下方，并确保它在最上层
        if matches:
            # 提升列表框到最上层
            self.listbox.lift()
            # 计算合适的高度（每项20像素，最多显示5项）
            height = min(100, len(matches)*20)
            self.listbox.place(
                x=self.dish_entry.winfo_x(),
                y=self.dish_entry.winfo_y() + self.dish_entry.winfo_height(),
                width=self.dish_entry.winfo_width(),
                height=height
            )
        else:
            self.listbox.place_forget()
    
    def on_listbox_select(self, event):
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            dish_name = selected.split(" - ")[0]
            self.dish_entry.delete(0, tk.END)
            self.dish_entry.insert(0, dish_name)
            self.listbox.place_forget()
    
    def add_to_order(self):
        selected = self.dish_entry.get()
        if not selected:
            messagebox.showwarning("SORRY", "Please enter the NAME of the dish")
            return
        
        if selected not in menu:
            messagebox.showwarning("SORRY", "The dish is not found")
            return
        
        qty = simpledialog.askinteger("Quantities", f"Please enter the quantity of the '{selected}':", 
                                     parent=self.root, minvalue=1, maxvalue=20)
        if qty:
            order_list.append((selected, qty))
            self.update_order_list()
            self.dish_entry.delete(0, tk.END)
    
    def update_order_list(self):
        self.order_tree.delete(*self.order_tree.get_children())
        for dish, qty in order_list:
            price = menu[dish]
            subtotal = price * qty
            self.order_tree.insert('', tk.END, text=dish, 
                                 values=(f"¥{price}", qty, f"¥{subtotal}"))
        
        total = OrderSystem.calculate_total()
        self.total_label.config(text=f"¥{total}")
    
    def checkout(self):
        if not order_list:
            messagebox.showwarning("SORRY", "Order is empty")
            return
        
        # 创建结算窗口
        checkout_window = tk.Toplevel(self.root)
        checkout_window.title("Check")
        checkout_window.geometry("400x300")
        checkout_window.resizable(False, False)
        checkout_window.configure(bg="#e6f0f5")
        
        # 结算信息
        total = OrderSystem.calculate_total()
        
        tk.Label(checkout_window, text="Check detail", font=("Didot", 16, "bold"), 
                bg="#e6f0f5", fg="#4a6b8a").pack(pady=10)
        
        info_frame = tk.Frame(checkout_window, bg="#e6f0f5")
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text="original price:", font=("Didot", 12), 
                bg="#e6f0f5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Label(info_frame, text=f"¥{total}", font=("Didot", 12), 
                bg="#e6f0f5").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        tk.Label(info_frame, text="rebates:", font=("Didot", 12), 
                bg="#e6f0f5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.discount_entry = tk.Entry(info_frame, font=("Didot", 12), width=10)
        self.discount_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.discount_entry.insert(0, "0")
        
        tk.Label(info_frame, text="amount due:", font=("Didot", 12, "bold"), 
                bg="#e6f0f5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.final_price_label = tk.Label(info_frame, text=f"¥{total}", font=("Didot", 12, "bold"), 
                                        bg="#e6f0f5")
        self.final_price_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # 折扣计算按钮
        tk.Button(checkout_window, text="calculate discount", font=("Didot", 10), 
                 bg="#f5f9fc", command=lambda: self.calculate_discount(total)).pack(pady=10)
        
        # 确认支付按钮
        tk.Button(checkout_window, text="confirmation of payment", font=("Didot", 12), 
                 bg="#4a6b8a", fg="white", command=lambda: self.confirm_payment(checkout_window)).pack(pady=20)
    
    def calculate_discount(self, total):
        try:
            discount = float(self.discount_entry.get())
            if discount < 0 or discount > 1:
                messagebox.showerror("SORRY", "Discount must be between 0-9")
                return
            
            final_price = total * (1 - discount)
            self.final_price_label.config(text=f"¥{final_price:.2f}")
        except ValueError:
            messagebox.showerror("SORRY", "Please enter a valid discount")
    
    def confirm_payment(self, window):
        messagebox.showinfo("Pay successfully", "THANKS FOR COMING！")
        order_list.clear()
        self.update_order_list()
        window.destroy()
    
    def clear_order(self):
        order_list.clear()
        self.update_order_list()
    
    def remove_selected(self):
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("SORRY", "Please select the dishes to be deteled first")
            return
        
        for item in selected:
            dish = self.order_tree.item(item, 'text')
            for i, (order_dish, qty) in enumerate(order_list):
                if order_dish == dish:
                    order_list.pop(i)
                    break
        
        self.update_order_list()
    
    def create_widgets(self):
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 顶部标题栏
        header = ttk.Frame(main_frame, style='TFrame')
        header.pack(fill=tk.X, pady=(0,20))
        
        # 标题区域
        title_frame = ttk.Frame(header, style='TFrame')
        title_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(title_frame, text="Se No-ori", style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(title_frame, text="Carpe · diem", style='Subtitle.TLabel').pack(anchor=tk.W)
        
        # 主内容区
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧菜单区
        menu_frame = ttk.LabelFrame(content_frame, text=" Menu ", style='TLabelframe', padding=15)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,15))
        
        # 菜品输入区
        input_frame = ttk.Frame(menu_frame, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0,15))
        
        ttk.Label(input_frame, text="Choose to enjoy:", style='TLabel').pack(side=tk.LEFT)
        self.dish_entry = ttk.Entry(input_frame, font=("Didot", 10))
        self.dish_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.dish_entry.bind('<KeyRelease>', self.on_entry_change)
        
        ttk.Button(input_frame, text="Add", style='TButton', command=self.add_to_order).pack(side=tk.LEFT)
        
        # 自动补全列表框（放在菜单框架内但会浮在最上层）
        self.listbox = tk.Listbox(menu_frame, bg="#f5f9fc", fg="#333333", font=("Didot", 10), 
                                selectbackground="#d0dce8", selectforeground="#333333",
                                borderwidth=1, relief="solid", highlightthickness=0)
        self.listbox.bind('<ButtonRelease-1>', self.on_listbox_select)
        
        # 菜单树状图
        self.menu_tree = ttk.Treeview(menu_frame, columns=('price'), style='Menu.Treeview', height=12)
        self.menu_tree.heading('#0', text='Delicacies', anchor=tk.W)
        self.menu_tree.heading('price', text='Price (¥)', anchor=tk.CENTER)
        self.menu_tree.column('#0', width=250, anchor=tk.W)
        self.menu_tree.column('price', width=100, anchor=tk.CENTER)
        
        for dish, price in menu.items():
            self.menu_tree.insert('', tk.END, text=dish, values=(f"¥{price}",))
        
        self.menu_tree.pack(fill=tk.BOTH, expand=True)
        
        # 右侧订单区
        order_frame = ttk.LabelFrame(content_frame, text=" My order ", style='TLabelframe', padding=15)
        order_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 订单树状图
        self.order_tree = ttk.Treeview(order_frame, columns=('price', 'qty', 'subtotal'), 
                                     style='Order.Treeview', height=10)
        self.order_tree.heading('#0', text='Delicacies', anchor=tk.W)
        self.order_tree.heading('price', text='Unit price', anchor=tk.CENTER)
        self.order_tree.heading('qty', text='Amount', anchor=tk.CENTER)
        self.order_tree.heading('subtotal', text='Subtotal', anchor=tk.CENTER)
        
        self.order_tree.column('#0', width=180, anchor=tk.W)
        self.order_tree.column('price', width=80, anchor=tk.CENTER)
        self.order_tree.column('qty', width=60, anchor=tk.CENTER)
        self.order_tree.column('subtotal', width=80, anchor=tk.CENTER)
        
        self.order_tree.pack(fill=tk.BOTH, expand=True)
        
        # 订单操作区
        order_btn_frame = ttk.Frame(order_frame, style='TFrame')
        order_btn_frame.pack(fill=tk.X, pady=(10,0))
        
        ttk.Button(order_btn_frame, text="Delete selected", style='TButton', command=self.remove_selected).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(order_btn_frame, text="Empty all", style='TButton', command=self.clear_order).pack(side=tk.LEFT)
        
        # 底部总计区
        footer = ttk.Frame(main_frame, style='TFrame')
        footer.pack(fill=tk.X, pady=(20,0))
        
        total_frame = ttk.Frame(footer, style='TFrame')
        total_frame.pack(side=tk.RIGHT)
        
        ttk.Label(total_frame, text="Total: ", style='Total.TLabel').pack(side=tk.LEFT)
        self.total_label = ttk.Label(total_frame, text="¥0", style='Total.TLabel')
        self.total_label.pack(side=tk.LEFT, padx=(5,20))
        
        ttk.Button(footer, text="Account", style='TButton', command=self.checkout).pack(side=tk.RIGHT, padx=(0,10))
        
        # 状态栏
        status_bar = ttk.Frame(self.root, style='TFrame', height=30)
        status_bar.pack(fill=tk.X, padx=20, pady=(0,20))
        
        self.status_label = ttk.Label(status_bar, text="Welcome", style='TLabel')
        self.status_label.pack(side=tk.LEFT)
        
        ttk.Label(status_bar, text="Tel: 400-888-8888", style='TLabel').pack(side=tk.RIGHT)

# 运行应用
if __name__ == "__main__":
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()
