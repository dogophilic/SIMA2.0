# product_routes.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_connection import create_connection
from datetime import datetime

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            name = request.form['name'].strip().lower()
            category = request.form['category'].strip().lower()
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            expiry_str = request.form.get('expiry', '').strip()
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date() if expiry_str else None

            conn = create_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM products WHERE name = %s AND category = %s", (name, category))
            existing = cursor.fetchone()

            if existing:
                new_stock = existing['stock'] + stock
                cursor.execute(
                    "UPDATE products SET stock = %s, price = %s, expiry = %s WHERE product_id = %s",
                    (new_stock, price, expiry_date, existing['product_id'])
                )
            else:
                cursor.execute(
                    "INSERT INTO products (name, category, price, stock, expiry) VALUES (%s, %s, %s, %s, %s)",
                    (name, category, price, stock, expiry_date)
                )

            conn.commit()
            cursor.close()
            conn.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('product_bp.add_product'))
 

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('add_product.html')
