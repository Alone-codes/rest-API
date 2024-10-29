from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

DATABASE = 'user.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user(username, password)
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_id = login_user(username, password)
        if user_id:
            session['user_id'] = user_id
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    items = list_items(user_id)
    return render_template('dashboard.html', items=items)

@app.route('/create_list', methods=['POST'])
def create_list():
    if 'user_id' in session:
        user_id = session['user_id']
        data_value = request.form['data_value']
        add_item(user_id, data_value)
        flash('Item created successfully.')
    return redirect(url_for('dashboard'))

def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user['id'] if user else None

def list_items(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data_value FROM user_data WHERE user_id = ?", (user_id,))
    items = cursor.fetchall()
    conn.close()
    return [item['data_value'] for item in items]

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove the user_id from the session
    flash('You have been logged out.')
    return redirect(url_for('index'))


def add_item(user_id, data_value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                        data_id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        data_value TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )''')
    cursor.execute("INSERT INTO user_data (user_id, data_value) VALUES (?, ?)", (user_id, data_value))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
