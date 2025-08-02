from db_connection import create_connection

try:
    conn = create_connection()
    if conn.is_connected():
        print("✅ Successfully connected to Railway MySQL database!")
        conn.close()
    else:
        print("❌ Failed to connect.")
except Exception as e:
    print("❌ Error during connection:", e)
