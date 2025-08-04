# generate_pdf.py
import pdfkit
from flask import Blueprint, render_template, send_file, abort
from db_connection import create_connection
from decimal import Decimal
import os
import datetime

generate_pdf_bp = Blueprint('generate_pdf', __name__)

# Detect Render or local environment and configure wkhtmltopdf accordingly
if os.getenv("RENDER"):
    # Render environment: use bundled binary
    WKHTMLTOPDF_PATH = os.path.join('bin', 'wkhtmltopdf')
else:
    # Local environment: use installed wkhtmltopdf path (Windows)
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

@generate_pdf_bp.route('/download_bill_pdf/<int:bill_id>')
def download_bill_pdf(bill_id):
    try:
        conn = create_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch the bill
        cursor.execute("SELECT * FROM bills WHERE bill_id = %s", (bill_id,))
        bill = cursor.fetchone()

        # Fetch bill items
        cursor.execute(
            "SELECT bi.*, p.name FROM bill_items bi JOIN products p ON bi.product_id = p.product_id WHERE bill_id = %s",
            (bill_id,)
        )
        items = cursor.fetchall()

        cursor.close()
        conn.close()

        if not bill:
            abort(404)

        # Format date
        if bill.get('created_at'):
            bill['created_at_str'] = bill['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            bill['created_at_str'] = 'N/A'

        # Calculate subtotal using Decimal
        subtotal = sum(Decimal(item['quantity']) * Decimal(item['price_at_sale']) for item in items)
        bill['subtotal'] = float(subtotal)

        # Ensure discount is float (default 0)
        bill['discount'] = float(bill.get('discount', 0))

        # Calculate total
        bill['total'] = float(bill.get('total_amount', 0))

        current_year = datetime.datetime.now().year

        rendered = render_template('bill_template.html', bill=bill, items=items, current_year=current_year)

        os.makedirs('temp', exist_ok=True)
        output_path = f'temp/bill_{bill_id}.pdf'

        pdfkit.from_string(rendered, output_path, configuration=PDFKIT_CONFIG)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"Error generating PDF: {e}", 500
