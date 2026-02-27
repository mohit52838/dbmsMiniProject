import mysql.connector

def fix_duplicates():
    cloud_conn = mysql.connector.connect(
        host='gondola.proxy.rlwy.net',
        port=36060,
        user='root',
        password='bLuIAYbwDxXdavqVxZpWAjYGFlGrpESx',
        database='railway'
    )
    cloud_cursor = cloud_conn.cursor()

    try:
        # Create a temporary table to keep the maximum mark_id for each student/subject pair
        cloud_cursor.execute("CREATE TEMPORARY TABLE temp_unique_marks AS SELECT MAX(mark_id) as keep_id FROM marks GROUP BY student_id, subject_id;")
        cloud_cursor.execute("DELETE FROM marks WHERE mark_id NOT IN (SELECT keep_id FROM temp_unique_marks);")
        cloud_conn.commit()
        print("Duplicates removed from marks table!")

        # Also let's check what the view actually looks like
        cloud_cursor.execute("SELECT * FROM student_reports WHERE student_id = 23")
        rows = cloud_cursor.fetchall()
        print("Aarav Wagh Reports:", rows)

    except Exception as e:
        print("Error:", e)
    finally:
        cloud_cursor.close()
        cloud_conn.close()

if __name__ == '__main__':
    fix_duplicates()
