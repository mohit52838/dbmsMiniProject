import mysql.connector
import random
import datetime
from db_config import get_db_connection

def sync_fees_to_existing_students():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
    cursor = conn.cursor(dictionary=True)

    try:
        print("Clearing old unsynced fee records...")
        cursor.execute("TRUNCATE TABLE fees;")

        print("Fetching all REAL existing students from the database...")
        cursor.execute("""
            SELECT s.student_id, s.division, d.dept_name 
            FROM student s
            LEFT JOIN department d ON s.dept_id = d.dept_id
        """)
        students = cursor.fetchall()
        
        if not students:
            print("No students found in the database. Please add students first.")
            return

        fees_to_insert = []
        today_date = datetime.date.today()
        
        print(f"Generating realistic fee scenarios for {len(students)} students...")
        for student in students:
            student_id = student['student_id']
            # Fallback for branch name if somehow missing
            branch_name = student['dept_name'] if student['dept_name'] else "Unassigned Branch"
            div = student['division'] if student['division'] else "A"
            
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
            
            fees_to_insert.append((student_id, branch_name, div, total_fees, paid, remain, status, payment_date_str))
            
        print("Saving synced fee records into the database...")
        query_fees = """
            INSERT INTO fees (student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query_fees, fees_to_insert)
        conn.commit()
        
        print(f"Successfully synced exactly {len(fees_to_insert)} fee records to match existing students!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    sync_fees_to_existing_students()
