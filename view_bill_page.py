from flask import Blueprint, render_template, abort
from db_connection import create_connection

view_bill_page_bp = Blueprint('view_bill_page', __name__)

@view_bill_page_bp.route('/view_bill/<int:bill_id>')
def view_bill(bill_id):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch bill
    cursor.execute("SELECT * FROM bills WHERE bill_id = %s", (bill_id,))
    bill = cursor.fetchone()

    # Fetch bill items
    cursor.execute("""
        SELECT bi.*, p.name 
        FROM bill_items bi 
        JOIN products p ON bi.product_id = p.product_id 
        WHERE bill_id = %s
    """, (bill_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    if not bill:
        abort(404)

    return render_template("bill_preview.html", bill=bill, items=items)
