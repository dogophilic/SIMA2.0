from flask import Blueprint, render_template, abort
from db_connection import create_connection
import pytz

view_bill_page_bp = Blueprint('view_bill_page', __name__)
IST = pytz.timezone("Asia/Kolkata")

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

    # Convert created_at to IST
    if bill.get('created_at'):
        raw_time = bill['created_at']
        if raw_time.tzinfo is None:
            raw_time = pytz.utc.localize(raw_time)
        ist_time = raw_time.astimezone(IST)
        bill['created_at_str'] = ist_time.strftime('%d-%m-%Y %I:%M %p IST')
    else:
        bill['created_at_str'] = 'N/A'

    return render_template("bill_preview.html", bill=bill, items=items)
