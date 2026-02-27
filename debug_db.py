import mysql.connector
import pprint

def debug_data():
    cloud_conn = mysql.connector.connect(
        host='gondola.proxy.rlwy.net',
        port=36060,
        user='root',
        password='bLuIAYbwDxXdavqVxZpWAjYGFlGrpESx',
        database='railway'
    )
    cloud_cursor = cloud_conn.cursor(dictionary=True)

    print("--- RAW ATTENDANCE FOR AARAV WAGH (ID 23) ---")
    cloud_cursor.execute("SELECT * FROM attendance WHERE student_id = 23")
    pprint.pprint(cloud_cursor.fetchall())

    print("\n--- RAW MARKS FOR AARAV WAGH (ID 23) ---")
    cloud_cursor.execute("SELECT * FROM marks WHERE student_id = 23")
    pprint.pprint(cloud_cursor.fetchall())
    
    print("\n--- STUDENT_REPORTS VIEW RETURN FOR AARAV WAGH (ID 23) ---")
    cloud_cursor.execute("SELECT * FROM student_reports WHERE student_id = 23")
    pprint.pprint(cloud_cursor.fetchall())
    
    cloud_cursor.close()
    cloud_conn.close()

if __name__ == '__main__':
    debug_data()
