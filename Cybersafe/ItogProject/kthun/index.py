from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from sqlite3 import Error
import hashlib


app = Flask(__name__)
app.secret_key = 'hJGHIUgehgjkSDgn7g&Th4gHG478g4gHG7g4hgdsHG&*@#YT&ytg7834ghEDUIg73DHGhgh4jhSDHJGhSDJKvkldshfgjkSDMGklsdGHeruigrhjgkBGiurhvjkrfh'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        username = request.form.get('username')
        hash = hashlib.sha256()
        password = request.form.get('password').encode()
        hash.update(password)
        password = hash.hexdigest()
        crs = conn.cursor()
        crs.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        password TEXT NOT NULL
        )''')
        crs.execute('SELECT id FROM Users WHERE username = ?', (username,))
        usr = crs.fetchall()
        if not usr:
            crs.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return f'Successfully registered!'
        else:
            return f'This username is taken, please, try another one.'
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        username = request.form.get('username')
        hash = hashlib.sha256()
        password = request.form.get('password').encode()
        hash.update(password)
        password = hash.hexdigest()
        crs = conn.cursor()
        crs.execute('SELECT password FROM Users WHERE username = ?', (username,))
        usr = crs.fetchone()
        if not usr:
            return f'Incorrect login'
        saved_password = usr[0]
        if password == saved_password:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return 'Incorrect password'
    return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    crs = conn.cursor()
    crs.execute('''
    CREATE TABLE IF NOT EXISTS Posts (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    if request.method == 'POST':
        content = request.form.get('content')
        username = session['username']
        crs.execute('INSERT INTO Posts (username, content) VALUES (?, ?)', (username, content))
        conn.commit()

    crs.execute('SELECT username, content, created_at FROM Posts ORDER BY created_at DESC')
    posts = crs.fetchall()
    conn.close()
    online_users = session['username'] 
    return render_template('index.html', posts=posts, username=session['username'], online_users=online_users)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run('0.0.0.0', port=80)
