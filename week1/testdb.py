import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="ecommerce_db",
        user="postgres",
        password="12345"
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")