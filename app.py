from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret in production

# Database configuration – replace with your AlwaysData details
db_config = {
    'host': 'mysql-webproject.alwaysdata.net',
    'user': '400931',
    'password': 'adkadhf12',
    'db': 'webproject_0',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    connection = pymysql.connect(**db_config)
    return connection

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        userid = request.form['userid']
        password = request.form['password']
        email = request.form['email']

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Check if userid already exists
                sql = "SELECT * FROM users WHERE userid = %s"
                cursor.execute(sql, (userid,))
                if cursor.fetchone():
                    flash('User ID already exists!', 'error')
                    return redirect(url_for('register'))

                # Insert the new user
                sql = "INSERT INTO users (name, userid, password, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, userid, password, email))
                connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        finally:
            connection.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users WHERE userid = %s AND password = %s"
                cursor.execute(sql, (userid, password))
                user = cursor.fetchone()
                if user:
                    session['userid'] = user['userid']
                    session['name'] = user['name']
                    flash('Login successful!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid credentials. Please try again.', 'error')
                    return redirect(url_for('login'))
        finally:
            connection.close()
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'userid' in session:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT email FROM users WHERE userid = %s"
                cursor.execute(sql, (session['userid'],))
                user = cursor.fetchone()
                return render_template('dashboard.html', name=session.get('name'), email=user['email'])
        finally:
            connection.close()
    else:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
