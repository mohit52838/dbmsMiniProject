import db_config
conn = db_config.get_db_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute("DESCRIBE student_reports")
print("=== student_reports VIEW SCHEMA ===")
for row in cursor.fetchall():
    print(row['Field'])

cursor.execute("SELECT name, gender FROM student LIMIT 3")
print("\n=== RAW STUDENT GENDERS ===")
for r in cursor.fetchall():
    print(r)

print("\n=== STUDENT REPORTS OUTPUT ===")
try:
    cursor.execute("SELECT name, gender FROM student_reports LIMIT 3")
    for r in cursor.fetchall():
        print(r)
except Exception as e:
    print(f"Error selecting gender from view: {e}")

cursor.close()
conn.close()
