#app.py
import csv
import io
import re
from flask import make_response, Response, Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from db_connection import create_connection
from pytz import timezone, utc

app = Flask(__name__)
app.secret_key = '123456'  # Replace with a secure key in production

# Blueprints
from auth_routes import auth_bp
app.register_blueprint(auth_bp)

@app.route('/')
def root():
    return redirect(url_for('auth_bp.login'))

from employee_routes import employee_bp
app.register_blueprint(employee_bp)

@app.route('/index')
def index():
    # Optional: protect with login
    if 'user_id' not in session:
        return redirect(url_for('auth_bp.login'))
    return render_template('index.html')

from product_routes import product_bp
app.register_blueprint(product_bp)

from view_products import view_products_bp
app.register_blueprint(view_products_bp)

from bill import bill_bp
app.register_blueprint(bill_bp)

@app.route('/search_bills')
def search_bills():
    query = request.args.get('query', '').strip()
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        if query:
            is_date = re.match(r'^\d{4}-\d{2}-\d{2}$', query)
            if is_date:
                cursor.execute("""
                    SELECT * FROM bills
                    WHERE customer_name LIKE %s OR DATE(created_at) = %s
                    ORDER BY created_at DESC
                """, (f"%{query}%", query))
            else:
                cursor.execute("""
                    SELECT * FROM bills
                    WHERE customer_name LIKE %s
                    ORDER BY created_at DESC
                """, (f"%{query}%",))
        else:
            cursor.execute("SELECT * FROM bills ORDER BY created_at DESC")

        bills = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('view_bills.html', bills=bills)

    except Exception as e:
        return f"Error during search: {str(e)}"

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Error deleting product: {str(e)}"
    
    return redirect(url_for('view_products_bp.view_products'))

@app.route('/view_bills')
def view_bills():
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bills ORDER BY created_at DESC")
        bills = cursor.fetchall()

        ist = timezone('Asia/Kolkata')

        for bill in bills:
            if isinstance(bill['created_at'], datetime):
                utc_time = bill['created_at'].replace(tzinfo=utc)
                local_time = utc_time.astimezone(ist)
                bill['created_at'] = local_time.strftime('%Y-%m-%d %I:%M %p')

        cursor.close()
        conn.close()
        return render_template('view_bills.html', bills=bills)
    
    except Exception as e:
        return f"Error fetching bills: {str(e)}"


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    session.pop('customer_name', None)
    session.pop('customer_mobile', None)
    return redirect(url_for('bill_bp.bill'))

from edit_product import edit_product_bp
app.register_blueprint(edit_product_bp)

from finalize_bill import finalize_bill_bp
app.register_blueprint(finalize_bill_bp)

from stock_alerts import stock_alerts
app.register_blueprint(stock_alerts)

from view_bill_page import view_bill_page_bp
app.register_blueprint(view_bill_page_bp)

from generate_pdf import generate_pdf_bp
app.register_blueprint(generate_pdf_bp)

if __name__ == '__main__':
    app.run(debug=True)
