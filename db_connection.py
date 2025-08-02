import mysql.connector

def create_connection():
    return mysql.connector.connect(
        host='maglev.proxy.rlwy.net',
        port=31751,
        user='root',
        password='WrzJHWpSkFDKhqSJNHpgMJCPHGUXysmW',
        database='railway'
    )

