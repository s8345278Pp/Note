from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = 'database.db'

# 建立資料庫
def init_db():
    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

init_db()

# 首頁
@app.route('/')
def index():
    return render_template('index.html')

# 處理登入
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with sqlite3.connect(app.config['DATABASE']) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        session['username'] = username
        return jsonify({'success': True, 'message': '登入成功'})
    return jsonify({'success': False, 'message': '帳號或密碼錯誤'})

# 處理註冊
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    try:
        with sqlite3.connect(app.config['DATABASE']) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        return jsonify({'success': True, 'message': '註冊成功'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': '使用者名稱已存在'})

# 處理圖片上傳
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未選擇檔案'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '未選擇檔案'})

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        if 'user_id' in session:
            with sqlite3.connect(app.config['DATABASE']) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO uploads (filename, user_id) VALUES (?, ?)', (filename, session['user_id']))
                conn.commit()

        return jsonify({'success': True, 'message': '上傳成功', 'filename': filename})
    
    return jsonify({'success': False, 'message': '上傳失敗'})

# 登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
