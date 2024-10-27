from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')
    conn.commit()
    conn.close()

# Create a new user
def create_user(username, password):
    try:
        conn = sqlite3.connect('user.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Username already exists. Please try a different one.")
    finally:
        conn.close()

# Login function to verify user credentials
def login_user(username, password):
    conn = sqlite3.connect('user.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Route to home page
@app.route('/')
def home():
    return render_template('home.html')

# Route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login_user(username, password)
        if user:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
    return render_template('login.html')

# Route to signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        create_user(username, password)
        flash("Account created successfully. You can now log in.")
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route to user dashboard after login
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# Route to list items
@app.route('/list_items')
def list_items():
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))
    return "Your old items: [Placeholder]"

# Route to create a new list
@app.route('/create_list')
def create_list():
    if 'username' not in session:
        flash("You need to log in first.")
        return redirect(url_for('login'))
    return "Create a new list: [Placeholder]"

# Route to logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('home'))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
