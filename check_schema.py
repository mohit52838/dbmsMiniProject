import mysql.connector

def check_schema():
    local_conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='M@ratha12',
        database='college_management'
    )
    cloud_conn = mysql.connector.connect(
        host='gondola.proxy.rlwy.net',
        port=36060,
        user='root',
        password='bLuIAYbwDxXdavqVxZpWAjYGFlGrpESx',
        database='railway'
    )
    
    local_cursor = local_conn.cursor()
    cloud_cursor = cloud_conn.cursor()
    
    tables = ['department', 'faculty', 'subject', 'student', 'attendance', 'marks', 'admin']
    
    with open('schema_comparison.txt', 'w') as f:
        for table in tables:
            local_cursor.execute(f"DESCRIBE {table}")
            local_cols = [row[0] for row in local_cursor.fetchall()]
            
            cloud_cursor.execute(f"DESCRIBE {table}")
            cloud_cols = [row[0] for row in cloud_cursor.fetchall()]
            
            f.write(f"Table {table}:\n")
            f.write(f"  Local: {local_cols}\n")
            f.write(f"  Cloud: {cloud_cols}\n")
            if local_cols != cloud_cols:
                f.write("  *** MISMATCH ***\n")

if __name__ == '__main__':
    check_schema()
