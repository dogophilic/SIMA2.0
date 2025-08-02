#finalize_bill.py
from flask import Blueprint, session, render_template, redirect, url_for
from datetime import datetime
from db_connection import create_connection

# Create Blueprint instance
finalize_bill_bp = Blueprint('finalize_bill', __name__)

@finalize_bill_bp.route('/finalize_bill', methods=['POST'])
def finalize_bill():
    customer_name = session.get('customer_name', '')
    customer_mobile = session.get('customer_mobile', '')
    cart = session.get('cart', [])

    grand_total = round(sum(float(item['total']) for item in cart), 2)

    if not customer_name or not customer_mobile or not cart:
        return redirect(url_for('bill'))

    try:
        conn = create_connection()
        cursor = conn.cursor()
        now = datetime.now()

        # Insert bill
        cursor.execute("""
            INSERT INTO bills (customer_name, customer_mobile, total_amount, created_at)
            VALUES (%s, %s, %s, %s)
        """, (customer_name, customer_mobile, grand_total, now))

        cursor.execute("SELECT LAST_INSERT_ID()")
        bill_id = cursor.fetchone()[0]

        for item in cart:
            cursor.execute("""
                INSERT INTO bill_items (bill_id, product_id, quantity, price_at_sale)
                VALUES (%s, %s, %s, %s)
            """, (
                bill_id,
                item['product_id'],
                item['quantity'],
                item['price']
            ))

            cursor.execute("""
                UPDATE products SET stock = stock - %s WHERE product_id = %s
            """, (
                item['quantity'],
                item['product_id']
            ))

            # Insert into sales table
            cursor.execute("""
                INSERT INTO sales (product_id, sale_date, quantity_sold)
                VALUES (%s, %s, %s)
            """, (
                item['product_id'],
                now.date(),
                item['quantity']
            ))

        conn.commit()
        cursor.close()
        conn.close()

        session.pop('cart', None)
        session.pop('customer_name', None)
        session.pop('customer_mobile', None)

        return render_template('bill_summary.html',
                               customer_name=customer_name,
                               customer_mobile=customer_mobile,
                               cart=cart,
                               grand_total=grand_total)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error finalizing bill: {str(e)}"
