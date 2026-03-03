import db_config
import os
import sys

# Add our new demo_data_py directory into python's search path
sys.path.insert(0, os.path.abspath('demo_data_py'))

def seed_from_modules():
    if not os.path.exists('demo_data_py'):
        print("No demo_data_py folder found. Skipping modular static seed.")
        return

    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    
    # We truncate tables manually in order of clearing
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE fees;")
        cursor.execute("TRUNCATE TABLE marks;")
        cursor.execute("TRUNCATE TABLE attendance;")
        cursor.execute("TRUNCATE TABLE student;")
        cursor.execute("TRUNCATE TABLE subject;")
        cursor.execute("TRUNCATE TABLE faculty;")
        cursor.execute("TRUNCATE TABLE department;")
        print("Cleared existing tables. Starting import from modular Python files...")

        # 1. Department 
        import department_data
        print("Inserting department...")
        q_dept = "INSERT INTO department (dept_id, dept_name) VALUES (%s, %s)"
        cursor.executemany(q_dept, department_data.department_records)
        
        # 2. Faculty
        import faculty_data
        print("Inserting faculty...")
        q_fac = "INSERT INTO faculty (faculty_id, name, email, phone, dept_id, password, profile_pic) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q_fac, faculty_data.faculty_records)

        # 3. Subject
        import subjects_data
        print("Inserting subjects...")
        q_sub = "INSERT INTO subject (subject_id, subject_name, dept_id, faculty_id) VALUES (%s, %s, %s, %s)"
        cursor.executemany(q_sub, subjects_data.subject_records)

        # 4. Student
        import students_data
        print("Inserting students...")
        q_stu = "INSERT INTO student (student_id, name, email, phone, gender, dob, dept_id, division, password, prn, roll_no, mother_name, address, profile_pic) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q_stu, students_data.student_records)
        
        # 5. Fees
        import fees_data
        print("Inserting fees...")
        q_fees = "INSERT INTO fees (fee_id, student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q_fees, fees_data.fees_records)

        # 6. Marks (Part 1)
        import marks_data_part_1
        print("Inserting marks...")
        q_marks = "INSERT INTO marks (mark_id, student_id, subject_id, internal_marks, external_marks, total, grade) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(q_marks, marks_data_part_1.marks_records_part_1)

        # 7. Attendance (Chunks 1 - 4)
        print("Inserting attendance chunks...")
        q_att = "INSERT INTO attendance (attendance_id, student_id, subject_id, date, status) VALUES (%s, %s, %s, %s, %s)"
        
        import attendance_data_part_1
        cursor.executemany(q_att, attendance_data_part_1.attendance_records_part_1)
        import attendance_data_part_2
        cursor.executemany(q_att, attendance_data_part_2.attendance_records_part_2)
        import attendance_data_part_3
        cursor.executemany(q_att, attendance_data_part_3.attendance_records_part_3)
        import attendance_data_part_4
        cursor.executemany(q_att, attendance_data_part_4.attendance_records_part_4)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Successfully loaded all data natively via Python modules! No external files needed.")

    except Exception as e:
        print(f"Error seeding native py chunks: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_from_modules()
