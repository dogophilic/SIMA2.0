from flask import Blueprint, render_template, request, session, redirect, url_for
from db_connection import create_connection

bill_bp = Blueprint('bill_bp', __name__)

@bill_bp.route('/home')
def home_redirect():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_bp.index'))  # Replace with your admin home route endpoint
    elif role == 'employee':
        return redirect(url_for('employee_bp.employee_home'))  # Replace with your employee home route endpoint
    else:
        return redirect(url_for('auth_routes.login'))  # If not logged in

@bill_bp.route('/bill', methods=['GET', 'POST'])
def bill():
    if 'cart' not in session:
        session['cart'] = []

    error = None

    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        try:
            product_id = int(request.form['product_id'])
            customer_name = request.form['customer_name'].strip()
            customer_mobile = request.form['customer_mobile'].strip()

            try:
                quantity = int(request.form['quantity'])
                if quantity <= 0:
                    raise ValueError("Quantity must be a positive integer.")
            except ValueError:
                raise ValueError("Invalid quantity entered.")

            if not customer_name or not customer_mobile:
                raise ValueError("Customer name and mobile are required.")

            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            product = cursor.fetchone()
            cursor.close()
            conn.close()

            if not product:
                raise ValueError("Selected product does not exist.")

            if product['stock'] < quantity:
                raise ValueError(f"Only {product['stock']} units available in stock.")

            price = float(product['price'])
            total = round(price * quantity, 2)

            session['customer_name'] = customer_name
            session['customer_mobile'] = customer_mobile

            cart = session['cart']
            cart.append({
                'product_id': product_id,
                'name': product['name'],
                'price': price,
                'quantity': quantity,
                'total': total
            })
            session['cart'] = cart

        except ValueError as ve:
            error = str(ve)
        except Exception:
            error = "An unexpected error occurred. Please try again."

    cart = session.get('cart', [])
    grand_total = round(sum(float(item['total']) for item in cart), 2)

    return render_template('bill.html', products=products, cart=cart, grand_total=grand_total, error=error)
