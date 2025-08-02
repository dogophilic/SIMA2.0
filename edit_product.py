from flask import Blueprint, render_template, request, redirect, url_for
from db_connection import create_connection

# Blueprint for editing products
edit_product_bp = Blueprint('edit_product', __name__)

@edit_product_bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        expiry = request.form.get('expiry') or None

        # Update the product record
        cursor.execute(
            """
            UPDATE products
               SET name=%s,
                   category=%s,
                   price=%s,
                   stock=%s,
                   expiry=%s
             WHERE product_id=%s
            """,
            (name, category, price, stock, expiry, product_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_products_bp.view_products'))

    # GET: fetch existing product data
    cursor.execute(
        "SELECT * FROM products WHERE product_id = %s", (product_id,)
    )
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_product.html', product=product)
