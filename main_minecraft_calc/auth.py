import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = 'database.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            nickname TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            avatar TEXT DEFAULT 'default.png'
        )
    ''')
    conn.commit()
    conn.close()


def register_user(username, nickname, password, avatar):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, nickname,\
                        password_hash, avatar) VALUES (?, ?, ?, ?)',
                       (username, nickname, password_hash, avatar))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users\
                   WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return user[0]
    return None


def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, avatar FROM users\
                    WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user
