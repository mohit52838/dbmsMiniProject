import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='M@ratha12',
        database='college_management'
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables:", tables)

    for table in tables:
        print(f"\n--- {table} ---")
        cursor.execute(f"DESCRIBE {table}")
        for row in cursor.fetchall():
            print(row)
    
    conn.close()
except Exception as e:
    print("Error:", e)
