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

        print("Clearing old records of students, attendance, marks...")
        cursor.execute("TRUNCATE TABLE marks;")
        cursor.execute("TRUNCATE TABLE attendance;")
        cursor.execute("TRUNCATE TABLE student;")
        
        branches = [1, 2, 3, 4, 5]
        divisions = ['A', 'B', 'C', 'D']
        
        # Indian names lists
        first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Aarush", "Dhruv", "Kabir", "Rishi", "Samar", "Rohan", "Siddharth", "Vikram", "Neha", "Priya", "Anjali", "Riya", "Sneha", "Kriti", "Pooja", "Aarohi", "Tanvi", "Shruti", "Meera", "Kavya", "Isha", "Rashi", "Aditi", "Simran", "Nisha", "Swati", "Divya", "Ananya"]
        last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Singh", "Patil", "Deshmukh", "Joshi", "Kulkarni", "Deshpande", "Chavan", "Pawar", "Shinde", "Kale", "Gaikwad", "Jadhav", "Mane", "Wagh", "Kamble", "More", "Suryawanshi", "Mohite", "Kadam", "Bhosale", "Yadav", "Rajput", "Chaudhary", "Mahajan", "Khandekar", "Bapat"]
        
        students_to_insert = []
        student_id_counter = 1
        
        print("Generating 100 dummy students (5 per division per branch)...")
        for branch in branches:
            for div in divisions:
                for _ in range(5):
                    # Random name
                    name = f"{random.choice(first_names)} {random.choice(last_names)}"
                    email = f"{name.lower().replace(' ', '.')}.{student_id_counter}@example.com"
                    phone = f"98{random.randint(10000000, 99999999)}"
                    students_to_insert.append((student_id_counter, name, email, phone, branch, div))
                    student_id_counter += 1
                    
        query = "INSERT INTO student (student_id, name, email, phone, dept_id, division) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query, students_to_insert)
        
        print("Re-enabling foreign key checks and committing...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print(f"Successfully inserted {len(students_to_insert)} students!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_students()
