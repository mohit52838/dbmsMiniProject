import mysql.connector

def reset_and_seed_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='M@ratha12',
        database='college_management'
    )
    cursor = conn.cursor()

    try:
        print("Disabling foreign key checks to safely clean data...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        print("Clearing old duplicated records...")
        # Clear out existing messy records. 
        # WARNING: This deletes the data in these tables so we can start fresh for the demo!
        # (It leaves 'student', 'attendance', 'marks', 'admin' untouched to preserve student data)
        cursor.execute("TRUNCATE TABLE subject;")
        cursor.execute("TRUNCATE TABLE faculty;")
        cursor.execute("TRUNCATE TABLE department;")

        # ---------------------------------------------------------------------------------
        # 1. ADD THE 5 DEPARTMENTS (BRANCHES)
        # ---------------------------------------------------------------------------------
        print("Inserting exact 5 branches...")
        departments = [
            (1, "Mechanical engineering (Mech)"),
            (2, "Civil engineering (CE)"),
            (3, "Computer Science & Engineering (CSE)"),
            (4, "Information Technology (IT)"),
            (5, "Electronics and Telecommunication (E&TC)")
        ]
        cursor.executemany("INSERT INTO department (dept_id, dept_name) VALUES (%s, %s)", departments)

        # ---------------------------------------------------------------------------------
        # 2. ADD FACULTY MEMBERS BY BRANCH
        # Format: (faculty_id, name, email, phone, dept_id)
        # ---------------------------------------------------------------------------------
        print("Inserting faculty...")
        
        mech_faculty = [
            (1, "Mr. M. L. Thorat", "mlthorat@gmail.com", "**********", 1),
            (2, "Mr. N. J. Runwal", "njrunwal@gmail.com", "**********", 1),
            (3, "Mr. R. A. Solunke", "rasolunke@gmail.com", "**********", 1),
            (4, "Dr. S. C. Kulkarni", "sckulkarni@gmail.com", "**********", 1),
            (5, "Mr. K. M. Patil", "kmpatil@gmail.com", "**********", 1),
        ]
        ce_faculty   = [
            (6, "Mr. Sudhir S. Nikam", "sudhirnikam@gmail.com", "**********", 2),
            (7, " Mrs. Surekha S. Patil", "surekha@gmail.com", "**********", 2),
            (8, "Ms. Sneha S. Bhende", "snehabhende@gmail.com", "**********", 2),
            (9, "Ms. Pooja Sonawane", "pooja@gmail.com", "**********", 2),
            (10, "Mr. Suraj W. Jagtap", "suraj@gmail.com", "**********", 2),
        ]
        cse_faculty  = [
            (11, "Ms. Priyanka Jadhav", "priyanka@gmail.com", "**********", 3),
            (12, "Mrs. Durga Sawant", "durgasawant@gmail.com", "**********", 3),
            (13, "Mrs. Swati Patange", "swati@gmail.com", "**********", 3),
            (14, "Prof. Nandini Lambole", "nandini@gmail.com", "**********", 3),
            (15, "Mrs. Priyanka Waghmare", "priyankawaghmare@gmail.com", "**********", 3),
        ]
        it_faculty   = [
            (16, "Ms. Jaitee Bankar", "jaiteebankar@gmail.com", "**********", 4),
            (17, "Mr. Vishal Abhong", "vishalabhong@gmail.com", "**********", 4),
            (18, "Mrs. Suvarna Potdukhe", "suvarnapotdukhe@gmail.com", "**********", 4),
            (19, "Mrs. Sweta Kale", "swetakale@gmail.com", "**********", 4),
            (20, "Mrs. Pooja Sonwane", "poojasonwane@gmail.com", "**********", 4),
        ]
        etc_faculty  = [
            (21, "Mr. Bhupesh Shukla", "bhupeshshukla@gmail.com", "**********", 5),
            (22, "Mrs. Shalini", "shalini@gmail.com", "**********", 5),
            (23, "Ms. Shrushti Kadam", "shrushtikadam@gmail.com", "**********", 5),
            (24, "Dr. Balram Goyal", "balramgoyal@gmail.com", "**********", 5),
            (25, "Mrs. Swati Kshirsagar", "swatikshirsagar@gmail.com", "**********", 5),
        ]
        
        all_faculty = mech_faculty + ce_faculty + cse_faculty + it_faculty + etc_faculty
        cursor.executemany("INSERT INTO faculty (faculty_id, name, email, phone, dept_id) VALUES (%s, %s, %s, %s, %s)", all_faculty)

        # ---------------------------------------------------------------------------------
        # 3. ADD SUBJECTS BY BRANCH
        # Format: (subject_id, subject_name, dept_id, faculty_id)
        # ---------------------------------------------------------------------------------
        print("Inserting subjects...")
        
        mech_subjects = [
            (1, "Manufacturing Processes-I", 1, 1),
            (2, "Fluid Mechanics", 1, 2),
            (3, "Applied Thermodynamics", 1, 3),
            (4, "Open Elective-II", 1, 4),
            (5, "Engineering Economics", 1, 5),
        ]
        
        ce_subjects = [
            (6, "Fluid Mechanics", 2, 6),
            (7, "Concrete Technology", 2, 7),
            (8, "Modern Indian Language", 2, 8),
            (9, "Project Management", 2, 9),
            (10, "Engineering Geology", 2, 10),
        ]
        
        cse_subjects = [
            (11, "Database Management Systems", 3, 11),
            (12, "Project Management", 3, 12),
            (13, "Modern Indian Language", 3, 13),
            (14, "Discrete Mathematics", 3, 14),
            (15, "Web Development", 3, 15),
        ]
        
        it_subjects = [
            (16, "Database Management Systems", 4, 16),
            (17, "Computer Graphics", 4, 17),
            (18, "E-Commerce", 4, 18),
            (19, "Modern Indian Language", 4, 19),
            (20, "Open Elective-II", 4, 20),
        ]
        
        etc_subjects = [
            (21, "Signals & Systems", 5, 21),
            (22, "Entrepreneurship Development", 5, 22),
            (23, "Modern Indian Language", 5, 23),
            (24, "Electronic Skill Development", 5, 24),
            (25, "Environmental Awareness", 5, 25),
        ]
        
        all_subjects = mech_subjects + ce_subjects + cse_subjects + it_subjects + etc_subjects
        cursor.executemany("INSERT INTO subject (subject_id, subject_name, dept_id, faculty_id) VALUES (%s, %s, %s, %s)", all_subjects)

        print("Re-enabling foreign key checks and committing...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Database successfully seeded for the demo! No duplicates remain.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_and_seed_data()
