from flask import Blueprint, render_template, session, redirect, url_for

employee_bp = Blueprint('employee_bp', __name__)

@employee_bp.route('/employee')
def employee_home():
    # Ensure only employees can access
    if 'role' not in session or session['role'] != 'employee':
        return redirect(url_for('auth_bp.login'))

    return render_template('employee_home.html')  # This is the employee dashboard
