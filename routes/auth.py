from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

auth_bp = Blueprint('auth', __name__)

# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='resume_parser'
    )

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("Register endpoint hit")  # Log the request for debugging

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.register'))  # Redirect back to the registration page

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            return redirect(url_for('auth.register'))  # Redirect back to the registration page
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')  # Render the registration template for GET requests

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Login endpoint hit")  # Log the request for debugging

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.login'))

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user[0], password):
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('upload'))  # Redirect to the upload page
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            return redirect(url_for('auth.login'))
        finally:
            cursor.close()
            conn.close()
    return render_template('login.html')