import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from PIL import Image, ImageTk
import os


class MusicApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.init_db()
        self.load_music()

    def setup_ui(self):
        """设置Apple Music风格的UI界面"""
        self.root.title("音乐管理系统 ♪")
        self.root.geometry("1000x600")

        # Apple Music配色方案
        self.bg_color = "#000000"  # 黑色背景
        self.sidebar_color = "#121212"  # 侧边栏深灰
        self.card_color = "#181818"  # 卡片颜色
        self.accent_color = "#FF2D55"  # Apple Music红
        self.text_color = "#FFFFFF"  # 白色文字
        self.secondary_text = "#B3B3B3"  # 次要文字

        # 主窗口背景
        self.root.configure(bg=self.bg_color)

        # 创建侧边栏
        self.create_sidebar()

        # 创建主内容区
        self.create_main_content()

    def init_db(self):
        """初始化数据库和表结构"""
        self.conn = sqlite3.connect('music.db')
        self.c = self.conn.cursor()

        # 删除旧表（开发时使用，正式环境应移除）
        self.c.execute("DROP TABLE IF EXISTS music")
        self.c.execute("DROP TABLE IF EXISTS playlists")
        self.c.execute("DROP TABLE IF EXISTS playlist_music")

        # 创建新表（file_path不再有UNIQUE约束）
        self.c.execute('''CREATE TABLE music
                          (
                              id         INTEGER PRIMARY KEY AUTOINCREMENT,
                              title      TEXT NOT NULL,
                              artist     TEXT NOT NULL,
                              album      TEXT,
                              duration   TEXT,
                              file_path  TEXT,
                              cover_path TEXT
                          )''')

        self.c.execute('''CREATE TABLE playlists
                          (
                              id   INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT NOT NULL UNIQUE
                          )''')

        self.c.execute('''CREATE TABLE playlist_music
                          (
                              playlist_id INTEGER,
                              music_id    INTEGER,
                              FOREIGN KEY (playlist_id) REFERENCES playlists (id),
                              FOREIGN KEY (music_id) REFERENCES music (id),
                              PRIMARY KEY (playlist_id, music_id)
                          )''')

        # 插入示例数据（确保file_path唯一）
        sample_data = [
            ("Blinding Lights", "The Weeknd", "After Hours", "3:20", "/music/weeknd1.mp3", ""),
            ("Save Your Tears", "The Weeknd", "After Hours", "3:35", "/music/weeknd2.mp3", ""),
            ("Levitating", "Dua Lipa", "Future Nostalgia", "3:23", "/music/dua1.mp3", ""),
            ("Don't Start Now", "Dua Lipa", "Future Nostalgia", "3:03", "/music/dua2.mp3", ""),
            ("Watermelon Sugar", "Harry Styles", "Fine Line", "2:54", "/music/harry1.mp3", "")
        ]

        self.c.executemany(
            "INSERT INTO music (title, artist, album, duration, file_path, cover_path) VALUES (?, ?, ?, ?, ?, ?)",
            sample_data
        )
        self.conn.commit()

    def load_music(self):
        """从数据库加载音乐并显示"""
        try:
            # 清空现有显示
            for widget in self.music_frame.winfo_children():
                widget.destroy()

            # 查询数据
            self.c.execute("SELECT id, title, artist, album, duration FROM music")
            songs = self.c.fetchall()

            # 显示音乐卡片
            for i, (song_id, title, artist, album, duration) in enumerate(songs):
                card = tk.Frame(
                    self.music_frame,
                    bg=self.card_color,
                    padx=15,
                    pady=15,
                    relief=tk.RAISED,
                    bd=1
                )
                card.grid(row=i // 4, column=i % 4, padx=10, pady=10)

                # 封面占位图
                cover = tk.Label(card, bg="#333333", width=10, height=5)
                cover.pack()

                # 歌曲信息
                tk.Label(
                    card,
                    text=title,
                    bg=self.card_color,
                    fg=self.text_color,
                    font=("Helvetica", 10, "bold")
                ).pack(anchor="w")

                tk.Label(
                    card,
                    text=f"{artist} • {album}",
                    bg=self.card_color,
                    fg=self.secondary_text
                ).pack(anchor="w")

                # 播放按钮
                tk.Button(
                    card,
                    text="▶ 播放",
                    bg=self.accent_color,
                    fg="white",
                    command=lambda id=song_id: self.play_music(id)
                ).pack(fill=tk.X, pady=5)

        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"加载音乐失败: {str(e)}")

    def play_music(self, song_id):
        """播放音乐（模拟功能）"""
        self.c.execute("SELECT title, artist FROM music WHERE id=?", (song_id,))
        song = self.c.fetchone()
        if song:
            messagebox.showinfo(
                "播放音乐",
                f"正在播放: {song[0]} - {song[1]}\n(此为模拟功能)"
            )

    def create_sidebar(self):
        """创建侧边导航栏"""
        sidebar = tk.Frame(self.root, bg=self.sidebar_color, width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # 应用标题
        tk.Label(
            sidebar,
            text="♪ Music",
            bg=self.sidebar_color,
            fg=self.text_color,
            font=("Helvetica", 20, "bold")
        ).pack(pady=30)

        # 导航按钮
        nav_buttons = [
            ("浏览音乐", self.load_music),
            ("创建播放列表", self.create_playlist),
            ("导入音乐", self.import_music),
            ("设置", self.show_settings)
        ]

        for text, cmd in nav_buttons:
            tk.Button(
                sidebar,
                text=text,
                bg=self.sidebar_color,
                fg=self.text_color,
                activebackground="#282828",
                activeforeground=self.text_color,
                bd=0,
                font=("Helvetica", 12),
                padx=20,
                pady=10,
                anchor="w",
                command=cmd
            ).pack(fill=tk.X)

    def create_main_content(self):
        """创建主内容区域"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 标题
        tk.Label(
            main_frame,
            text="音乐库",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Helvetica", 24, "bold")
        ).pack(pady=20, padx=20, anchor="w")

        # 音乐显示区域
        self.music_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.music_frame.pack(fill=tk.BOTH, expand=True, padx=20)

    # 其他功能方法
    def create_playlist(self):
        """创建播放列表"""
        messagebox.showinfo("提示", "播放列表功能将在后续版本中实现")

    def import_music(self):
        """导入音乐文件"""
        messagebox.showinfo("提示", "音乐导入功能将在后续版本中实现")

    def show_settings(self):
        """显示设置界面"""
        messagebox.showinfo("提示", "设置功能将在后续版本中实现")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicApp(root)
    root.mainloop()