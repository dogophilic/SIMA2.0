from flask import Blueprint, render_template
from db_connection import create_connection  # ✅ Import your shared DB connection

stock_alerts = Blueprint('stock_alerts', __name__)

def get_stock_alerts_data():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            p.name AS product_name,
            p.stock AS current_stock,

            -- Calculate 7-day average or fallback to overall average
            COALESCE((
                SELECT AVG(s2.quantity_sold)
                FROM sales s2
                WHERE s2.product_id = p.product_id
                AND s2.sale_date >= CURDATE() - INTERVAL 7 DAY
            ),
            (
                SELECT AVG(s3.quantity_sold)
                FROM sales s3
                WHERE s3.product_id = p.product_id
            ),
            0) AS avg_7_day_sales,

            -- Projected 15-day sales
            COALESCE((
                SELECT AVG(s2.quantity_sold)
                FROM sales s2
                WHERE s2.product_id = p.product_id
                AND s2.sale_date >= CURDATE() - INTERVAL 7 DAY
            ),
            (
                SELECT AVG(s3.quantity_sold)
                FROM sales s3
                WHERE s3.product_id = p.product_id
            ),
            0) * 15 AS projected_15_day_sales,

            -- Stock status
            CASE
                WHEN p.stock = 0 THEN 'Stock Out'
                ELSE ''
            END AS stock_status,

            -- Stock Category (Red/Orange/Green)
            CASE
                WHEN p.stock = 0 THEN 'Red'
                WHEN p.stock < (
                    COALESCE((
                        SELECT AVG(s2.quantity_sold)
                        FROM sales s2
                        WHERE s2.product_id = p.product_id
                        AND s2.sale_date >= CURDATE() - INTERVAL 7 DAY
                    ),
                    (
                        SELECT AVG(s3.quantity_sold)
                        FROM sales s3
                        WHERE s3.product_id = p.product_id
                    ),
                    0) * 15
                ) THEN 'Orange'
                ELSE 'Green'
            END AS stock_category,

            -- Expiry status
            CASE
                WHEN p.expiry IS NULL THEN ''
                WHEN p.expiry < CURDATE() THEN 'Expired'
                WHEN p.expiry <= CURDATE() + INTERVAL 30 DAY THEN 'Expiring Soon'
                ELSE ''
            END AS expiry_status

        FROM products p;
    """

    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

@stock_alerts.route('/show_stock_alerts')
def show_stock_alerts():
    stock_data = get_stock_alerts_data()
    return render_template('stock_alerts.html', stock_data=stock_data)
