# auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from db_connection import create_connection

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']  # Set role from DB, not from form

            if user['role'] == 'admin':
                return redirect(url_for('index'))  # Admin dashboard
            elif user['role'] == 'employee':
                return redirect(url_for('employee_bp.employee_home'))  # Employee dashboard
            else:
                flash('Unknown user role.', 'danger')
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# auth_routes.py
@auth_bp.route('/home')
def home_redirect():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('index'))
    elif role == 'employee':
        return redirect(url_for('employee_bp.employee_home'))
    else:
        # If not logged in or unknown role
        return redirect(url_for('auth_bp.login'))


