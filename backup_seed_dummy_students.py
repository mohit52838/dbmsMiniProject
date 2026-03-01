import mysql.connector
import random
from db_config import get_db_connection

def seed_students():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
    cursor = conn.cursor()

    try:
        print("Disabling foreign key checks to safely clean data...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        print("Clearing old records of students, attendance, marks, fees...")
        cursor.execute("TRUNCATE TABLE fees;")
        cursor.execute("TRUNCATE TABLE marks;")
        cursor.execute("TRUNCATE TABLE attendance;")
        cursor.execute("TRUNCATE TABLE student;")
        
        branches = [1, 2, 3, 4, 5]
        divisions = ['A', 'B', 'C', 'D']
        
        # Indian names lists
        first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Aarush", "Dhruv", "Kabir", "Rishi", "Samar", "Rohan", "Siddharth", "Vikram", "Neha", "Priya", "Anjali", "Riya", "Sneha", "Kriti", "Pooja", "Aarohi", "Tanvi", "Shruti", "Meera", "Kavya", "Isha", "Rashi", "Aditi", "Simran", "Nisha", "Swati", "Divya", "Ananya"]
        last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Patil", "Deshmukh", "Joshi", "Kulkarni", "Deshpande", "Chavan", "Pawar", "Shinde", "Kale", "Gaikwad", "Jadhav", "Mane", "Wagh", "Kamble", "More", "Suryawanshi", "Mohite", "Kadam", "Bhosale", "Yadav", "Rajput", "Chaudhary", "Mahajan", "Khandekar", "Bapat"]
        
        cursor.execute("SELECT dept_id, dept_name FROM department")
        dept_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT subject_id, dept_id FROM subject")
        subjects_by_dept = {}
        for (sid, did) in cursor.fetchall():
            if did not in subjects_by_dept:
                subjects_by_dept[did] = []
            subjects_by_dept[did].append(sid)
        
        students_to_insert = []
        marks_to_insert = []
        fees_to_insert = []
        attendance_to_insert = []
        student_id_counter = 1
        
        import datetime
        from db_config import calculate_grade
        today_date = datetime.date.today()
        
        print("Generating 100 dummy students with marks, attendance, and fees...")
        for branch in branches:
            branch_name = dept_map.get(branch, f"Dept {branch}")
            for div in divisions:
                roll_no_counter = 1
                for _ in range(5):
                    # Random student
                    name = f"{random.choice(first_names)} {random.choice(last_names)}"
                    email = f"{name.lower().replace(' ', '.')}.{student_id_counter}@example.com"
                    phone = f"98{random.randint(10000000, 99999999)}"
                    password = "student123"
                    prn = f"PRN2026{str(student_id_counter).zfill(4)}"
                    roll_no = roll_no_counter
                    mother_name = random.choice(first_names)
                    address = f"{random.randint(10, 999)}, {random.choice(['MG Road', 'FC Road', 'JM Road', 'SB Road', 'DP Road'])}, Pune"
                    students_to_insert.append((student_id_counter, name, email, phone, random.choice(['Male', 'Female']), '2000-01-01', branch, div, password, prn, roll_no, mother_name, address))
                    
                    roll_no_counter += 1
                    
                    # Random fees
                    total_fees = 100000.0
                    fee_scenarios = [
                        (100000.0, 0.0, 'Paid'),   # fully paid
                        (100000.0, 0.0, 'Paid'),   # bias towards fully paid
                        (50000.0, 50000.0, 'Partial'), # half paid
                        (25000.0, 75000.0, 'Partial'), 
                        (0.0, 100000.0, 'Unpaid')      # unpaid
                    ]
                    paid, remain, status = random.choice(fee_scenarios)
                    
                    random_days_ago = random.randint(0, 90)
                    payment_date_str = (today_date - datetime.timedelta(days=random_days_ago)).strftime('%Y-%m-%d')
                    fees_to_insert.append((student_id_counter, branch_name, div, total_fees, paid, remain, status, payment_date_str))
                    
                    # Random marks and attendance per subject
                    subjects_for_this_dept = subjects_by_dept.get(branch, [])
                    for sub_id in subjects_for_this_dept:
                        # Marks out of 100
                        sub_marks = random.randint(35, 95)
                        internal = sub_marks // 2
                        external = sub_marks - internal
                        grade = calculate_grade(sub_marks)
                        marks_to_insert.append((student_id_counter, sub_id, internal, external, sub_marks, grade))
                        
                        # Attendance out of ~5 days for dummy purposes
                        total_days = 5
                        days_present = random.randint(2, 5)
                        for d_offset in range(total_days):
                            status_att = 'Present' if d_offset < days_present else 'Absent'
                            att_date = (today_date - datetime.timedelta(days=d_offset)).strftime('%Y-%m-%d')
                            attendance_to_insert.append((student_id_counter, sub_id, att_date, status_att))
                            
                    student_id_counter += 1
                    
        print("Inserting 100 students...")
        query_student = """
            INSERT INTO student (student_id, name, email, phone, gender, dob, dept_id, division, password, prn, roll_no, mother_name, address) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # (id, name, email, phone, gender, dob, dept, div, password, prn, roll, mother, address)
        cursor.executemany(query_student, students_to_insert)
        
        print(f"Inserting {len(fees_to_insert)} fee records...")
        query_fees = "INSERT INTO fees (student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.executemany(query_fees, fees_to_insert)
        
        print(f"Inserting {len(marks_to_insert)} marks records...")
        query_marks = "INSERT INTO marks (student_id, subject_id, internal_marks, external_marks, total, grade) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query_marks, marks_to_insert)
        
        print(f"Inserting {len(attendance_to_insert)} attendance records...")
        query_att = "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (%s, %s, %s, %s)"
        cursor.executemany(query_att, attendance_to_insert)
        
        print("Re-enabling foreign key checks and committing...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("All dummy data loaded successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_students()
