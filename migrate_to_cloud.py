import mysql.connector

def migrate():
    try:
        local_conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='M@ratha12',
            database='college_management'
        )
        local_cursor = local_conn.cursor(dictionary=True)

        cloud_conn = mysql.connector.connect(
            host='gondola.proxy.rlwy.net',
            port=36060,
            user='root',
            password='bLuIAYbwDxXdavqVxZpWAjYGFlGrpESx',
            database='railway'
        )
        cloud_cursor = cloud_conn.cursor()

        tables = ['department', 'faculty', 'subject', 'student', 'attendance', 'marks', 'admin']

        print("Disabling foreign key checks on cloud...")
        cloud_cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        for table in tables:
            print(f"Migrating table {table}...")
            cloud_cursor.execute(f"TRUNCATE TABLE {table};")
            
            local_cursor.execute(f"SELECT * FROM {table}")
            rows = local_cursor.fetchall()
            
            if not rows:
                print(f"  No data in {table}")
                continue

            columns = list(rows[0].keys())
            
            # Handle the admin email mismatch between local and cloud
            if table == 'admin' and 'email' not in columns:
                columns.append('email')
                for row in rows:
                    row['email'] = f"{row['username']}@admin.com"

            cols_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            
            insert_query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
            
            insert_data = [tuple(row[col] for col in columns) for row in rows]
            
            cloud_cursor.executemany(insert_query, insert_data)
            cloud_conn.commit()
            print(f"  Inserted {len(rows)} rows into {table}")

        print("Re-enabling foreign key checks on cloud...")
        cloud_cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cloud_conn.commit()

        local_cursor.close()
        local_conn.close()
        cloud_cursor.close()
        cloud_conn.close()
        print("Migration complete!")
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == '__main__':
    migrate()
