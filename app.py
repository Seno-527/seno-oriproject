from flask import Flask, render_template, send_from_directory
import sqlite3
import os
from pathlib import Path

app = Flask(__name__)


# Vercel 适配：获取正确的数据库路径
def get_db_path():
    if 'VERCEL' in os.environ:  # 在Vercel环境使用临时目录
        return '/tmp/music.db'
    return 'music.db'


# 初始化数据库（适配Vercel）
def init_db():
    db_path = get_db_path()

    # Vercel环境下确保/tmp目录存在
    if 'VERCEL' in os.environ:
        Path('/tmp').mkdir(exist_ok=True)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 保持原表结构
    c.execute('''CREATE TABLE music
                 (
                     id         INTEGER PRIMARY KEY,
                     title      TEXT NOT NULL,
                     artist     TEXT NOT NULL,
                     album      TEXT,
                     duration   TEXT,
                     cover_path TEXT
                 )''')

    # 保持原歌曲数据
    songs = [
        (1, "Our Summer", "TOMORROW X TOGETHER", "The Dream Chapter: Magic", "3:30", "our_summer.jpg"),
        # ...（其他歌曲数据保持不变）
    ]

    c.executemany("INSERT INTO music VALUES (?, ?, ?, ?, ?, ?)", songs)
    conn.commit()
    conn.close()

    # 创建资源目录（适配Vercel）
    os.makedirs('static/audio', exist_ok=True)
    os.makedirs('static/covers', exist_ok=True)


# Vercel适配：静态文件路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


# 保持原有路由
@app.route('/covers/<filename>')
def serve_cover(filename):
    return send_from_directory('static/covers', filename)


@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)


@app.route('/')
def index():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT * FROM music ORDER BY id")
    songs = c.fetchall()
    conn.close()
    return render_template('index.html', songs=songs)


# Vercel适配：添加Serverless入口
def vercel_handler(request):
    with app.app_context():
        response = app.full_dispatch_request()()
    return response


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Vercel环境初始化
    init_db()