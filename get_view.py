import mysql.connector

def get_view_sql():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='M@ratha12',
            database='college_management'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SHOW CREATE VIEW student_reports;")
        row = cursor.fetchone()
        with open('view_def.sql', 'w') as f:
            f.write(row['Create View'])
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    get_view_sql()
