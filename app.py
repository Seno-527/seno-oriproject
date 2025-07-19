from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for, session
import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# 配置文件
app.config.update({
    'UPLOAD_FOLDER': 'static/uploads',
    'ALLOWED_EXTENSIONS': {'png', 'jpg', 'jpeg', 'mp3', 'wav'},
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
    'DATABASE': 'music.db',
    'DEFAULT_ADMIN': {'username': 'admin', 'password': 'admin123', 'email': 'admin@example.com'}
})

# 数据库辅助函数
class DB:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def execute(query, params=(), commit=False):
        conn = DB.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if commit:
                conn.commit()
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            elif query.strip().upper().startswith('INSERT'):
                return cursor.lastrowid
            return True
        except sqlite3.Error as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

# 装饰器
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return json_response('请先登录', 401)
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return json_response('请先登录', 401)
        if session.get('role') != 'admin':
            return json_response('需要管理员权限', 403)
        return f(*args, **kwargs)
    return decorated

# 响应辅助函数
def json_response(message=None, status=200, data=None):
    response = {'success': status == 200}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status

# 初始化数据库
def init_db():
    with app.app_context():
        # 创建表结构
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS music (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT,
                duration TEXT,
                cover_path TEXT,
                audio_path TEXT,
                genre TEXT,
                release_date TEXT,
                lyrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (song_id) REFERENCES music (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, song_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (song_id) REFERENCES music (id)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                type TEXT DEFAULT 'category',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS song_categories (
                song_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                PRIMARY KEY (song_id, category_id),
                FOREIGN KEY (song_id) REFERENCES music (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            '''
        ]

        for table in tables:
            DB.execute(table, commit=True)

        # 添加默认管理员
        admin = DB.execute("SELECT id FROM users WHERE username = ?", (app.config['DEFAULT_ADMIN']['username'],))
        if not admin:
            hashed_pw = generate_password_hash(app.config['DEFAULT_ADMIN']['password'])
            DB.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                (app.config['DEFAULT_ADMIN']['username'], hashed_pw,
                 app.config['DEFAULT_ADMIN']['email'], 'admin'),
                commit=True
            )

        # 创建必要目录
        os.makedirs('static/audio', exist_ok=True)
        os.makedirs('static/covers', exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 用户认证路由
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return json_response('用户名和密码不能为空', 400)

    user = DB.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
    if not user or not check_password_hash(user[0]['password'], password):
        return json_response('用户名或密码错误', 401)

    user = user[0]
    session.update({
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role']
    })

    return json_response('登录成功', data={
        'id': user['id'],
        'username': user['username'],
        'role': user['role']
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    email = data.get('email', '')

    if not all([username, password, confirm_password]):
        return json_response('请填写所有必填字段', 400)

    if password != confirm_password:
        return json_response('两次输入的密码不一致', 400)

    try:
        hashed_pw = generate_password_hash(password)
        user_id = DB.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_pw, email),
            commit=True
        )

        session.update({
            'user_id': user_id,
            'username': username,
            'role': 'user'
        })

        return json_response('注册成功', 201, {
            'id': user_id,
            'username': username,
            'role': 'user'
        })
    except sqlite3.IntegrityError:
        return json_response('用户名已存在', 400)
    except Exception as e:
        return json_response(str(e), 500)

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return json_response('已退出登录')

@app.route('/api/auth/me', methods=['GET'])
def current_user_info():
    if 'user_id' not in session:
        return json_response('未登录', 401)

    return json_response(data={
        'id': session['user_id'],
        'username': session['username'],
        'role': session['role']
    })

# 音乐相关路由
@app.route('/api/songs', methods=['GET'])
def get_songs():
    songs = DB.execute('''
        SELECT m.*, GROUP_CONCAT(c.name) as categories,
        GROUP_CONCAT(CASE WHEN c.type = 'tag' THEN c.name ELSE NULL END) as tags
        FROM music m
        LEFT JOIN song_categories sc ON m.id = sc.song_id
        LEFT JOIN categories c ON sc.category_id = c.id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    ''')

    songs_data = []
    for song in songs:
        song_data = dict(song)
        song_data['categories'] = song['categories'].split(',') if song['categories'] else []
        song_data['tags'] = song['tags'].split(',') if song['tags'] else []
        songs_data.append(song_data)

    return json_response(data=songs_data)

@app.route('/api/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    song = DB.execute('''
        SELECT m.*, GROUP_CONCAT(c.name) as categories,
        GROUP_CONCAT(CASE WHEN c.type = 'tag' THEN c.name ELSE NULL END) as tags
        FROM music m
        LEFT JOIN song_categories sc ON m.id = sc.song_id
        LEFT JOIN categories c ON sc.category_id = c.id
        WHERE m.id = ?
        GROUP BY m.id
    ''', (song_id,))

    if not song:
        return json_response('歌曲不存在', 404)

    song = song[0]
    song_data = dict(song)
    song_data['categories'] = song['categories'].split(',') if song['categories'] else []
    song_data['tags'] = song['tags'].split(',') if song['tags'] else []

    related = DB.execute('''
        SELECT id, title, artist, album, cover_path
        FROM music
        WHERE genre = ? AND id != ?
        ORDER BY RANDOM()
        LIMIT 3
    ''', (song_data['genre'], song_id))

    comments = DB.execute('''
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.song_id = ?
        ORDER BY c.created_at DESC
    ''', (song_id,))

    return json_response(data={
        'song': song_data,
        'related_songs': [dict(s) for s in related],
        'comments': [dict(c) for c in comments]
    })

# 收藏相关路由
@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    favorites = DB.execute('''
        SELECT m.*
        FROM favorites f
        JOIN music m ON f.song_id = m.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (session['user_id'],))

    return json_response(data=[dict(song) for song in favorites])

@app.route('/api/favorites/<int:song_id>', methods=['POST', 'DELETE'])
@login_required
def toggle_favorite(song_id):
    song = DB.execute("SELECT id FROM music WHERE id = ?", (song_id,))
    if not song:
        return json_response('歌曲不存在', 404)

    if request.method == 'POST':
        try:
            DB.execute(
                "INSERT INTO favorites (user_id, song_id) VALUES (?, ?)",
                (session['user_id'], song_id),
                commit=True
            )
            return json_response(data={'isFavorite': True})
        except sqlite3.IntegrityError:
            return json_response(data={'isFavorite': True})

    elif request.method == 'DELETE':
        DB.execute(
            "DELETE FROM favorites WHERE user_id = ? AND song_id = ?",
            (session['user_id'], song_id),
            commit=True
        )
        return json_response(data={'isFavorite': False})

# 评论相关路由
@app.route('/api/comments', methods=['POST'])
@login_required
def add_comment():
    data = request.get_json()
    song_id = data.get('song_id')
    content = data.get('content')

    if not song_id or not content:
        return json_response('缺少必要参数', 400)

    try:
        comment_id = DB.execute(
            "INSERT INTO comments (song_id, user_id, content) VALUES (?, ?, ?)",
            (song_id, session['user_id'], content),
            commit=True
        )

        new_comment = DB.execute('''
            SELECT c.*, u.username
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.id = ?
        ''', (comment_id,))[0]

        return json_response('评论发表成功', 201, dict(new_comment))
    except Exception as e:
        return json_response(str(e), 500)

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = DB.execute("SELECT * FROM comments WHERE id = ?", (comment_id,))
    if not comment:
        return json_response('评论不存在', 404)

    comment = comment[0]
    if session['role'] != 'admin' and comment['user_id'] != session['user_id']:
        return json_response('无权删除此评论', 403)

    DB.execute("DELETE FROM comments WHERE id = ?", (comment_id,), commit=True)
    return json_response('评论已删除')

# 管理员路由
@app.route('/api/admin/songs', methods=['GET', 'POST'])
@admin_required
def manage_songs():
    if request.method == 'GET':
        songs = DB.execute("SELECT * FROM music ORDER BY created_at DESC")
        return json_response(data=[dict(song) for song in songs])

    elif request.method == 'POST':
        data = request.get_json()
        required = ['title', 'artist', 'album', 'duration', 'cover_path',
                   'audio_path', 'genre', 'release_date', 'lyrics']

        if not all(field in data for field in required):
            return json_response('缺少必要字段', 400)

        try:
            song_id = DB.execute(
                '''
                INSERT INTO music (
                    title, artist, album, duration, cover_path,
                    audio_path, genre, release_date, lyrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    data['title'], data['artist'], data['album'], data['duration'],
                    data['cover_path'], data['audio_path'], data['genre'],
                    data['release_date'], data['lyrics']
                ),
                commit=True
            )
            return json_response('歌曲添加成功', 201, {'id': song_id})
        except Exception as e:
            return json_response(str(e), 500)

@app.route('/api/admin/songs/<int:song_id>', methods=['PUT', 'DELETE'])
@admin_required
def manage_song(song_id):
    song = DB.execute("SELECT id FROM music WHERE id = ?", (song_id,))
    if not song:
        return json_response('歌曲不存在', 404)

    if request.method == 'PUT':
        data = request.get_json()
        required = ['title', 'artist', 'album', 'duration', 'cover_path',
                   'audio_path', 'genre', 'release_date', 'lyrics']

        if not all(field in data for field in required):
            return json_response('缺少必要字段', 400)

        try:
            DB.execute(
                '''
                UPDATE music SET
                    title = ?, artist = ?, album = ?, duration = ?,
                    cover_path = ?, audio_path = ?, genre = ?,
                    release_date = ?, lyrics = ?
                WHERE id = ?
                ''',
                (
                    data['title'], data['artist'], data['album'], data['duration'],
                    data['cover_path'], data['audio_path'], data['genre'],
                    data['release_date'], data['lyrics'], song_id
                ),
                commit=True
            )
            return json_response('歌曲更新成功')
        except Exception as e:
            return json_response(str(e), 500)

    elif request.method == 'DELETE':
        try:
            DB.execute("DELETE FROM favorites WHERE song_id = ?", (song_id,), commit=True)
            DB.execute("DELETE FROM comments WHERE song_id = ?", (song_id,), commit=True)
            DB.execute("DELETE FROM song_categories WHERE song_id = ?", (song_id,), commit=True)
            DB.execute("DELETE FROM music WHERE id = ?", (song_id,), commit=True)
            return json_response('歌曲删除成功')
        except Exception as e:
            return json_response(str(e), 500)

# 静态文件路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# 初始化应用
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)