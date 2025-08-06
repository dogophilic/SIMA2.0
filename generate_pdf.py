import os
import datetime
from decimal import Decimal
import pytz
import pdfkit
from flask import Blueprint, render_template, send_file, abort
from db_connection import create_connection

generate_pdf_bp = Blueprint('generate_pdf', __name__)

# Determine the wkhtmltopdf path based on environment
if os.getenv("RENDER"):
    WKHTMLTOPDF_PATH = "/usr/bin/wkhtmltopdf"  # Render's apt-installed path
else:
    WKHTMLTOPDF_PATH = os.path.join(os.getcwd(), 'bin', 'wkhtmltopdf')  # Local binary

PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# Define IST timezone
IST = pytz.timezone("Asia/Kolkata")

@generate_pdf_bp.route('/download_bill_pdf/<int:bill_id>')
def download_bill_pdf(bill_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch bill data
        cursor.execute("SELECT * FROM bills WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            abort(404)

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

        # Format bill creation date in IST
        if bill.get('created_at'):
            raw_time = bill['created_at']
            if raw_time.tzinfo is None:
                raw_time = IST.localize(raw_time)  # Assume naive timestamp is already in IST
            ist_time = raw_time.astimezone(IST)
            bill['created_at_str'] = ist_time.strftime('%d-%m-%Y %I:%M %p IST')
        else:
            bill['created_at_str'] = 'N/A'

        # Calculate subtotal using Decimal
        subtotal = sum(Decimal(item['quantity']) * Decimal(item['price_at_sale']) for item in items)
        bill['subtotal'] = float(subtotal)
        bill['discount'] = float(bill.get('discount', 0))
        bill['total'] = float(bill.get('total_amount', 0))

        # Current year in IST
        current_year = datetime.datetime.now(IST).year

        # Render to HTML and generate PDF
        rendered = render_template('bill_template.html', bill=bill, items=items, current_year=current_year)
        os.makedirs('temp', exist_ok=True)
        output_path = f'temp/bill_{bill_id}.pdf'
        pdfkit.from_string(rendered, output_path, configuration=PDFKIT_CONFIG)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating PDF: {e}", 500
