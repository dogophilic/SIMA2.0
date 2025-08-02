from flask import Blueprint, render_template
from datetime import datetime
from db_connection import create_connection

view_products_bp = Blueprint('view_products_bp', __name__)

@view_products_bp.route('/view_products')
def view_products():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    today = datetime.today().date()

    for product in products:
        expiry = product.get('expiry')
        if expiry:
            expiry_date = expiry if isinstance(expiry, datetime) else datetime.strptime(str(expiry), "%Y-%m-%d").date()
            days_remaining = (expiry_date - today).days
            if days_remaining < 0:
                product['expiry_warning'] = 'expired'
            elif days_remaining <= 30:
                product['expiry_warning'] = 'soon'
            else:
                product['expiry_warning'] = 'ok'
        else:
            product['expiry_warning'] = 'none'

    return render_template('view_products.html', products=products)
