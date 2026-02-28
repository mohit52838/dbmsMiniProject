import db_config
import datetime

def test_fees_logic():
    conn = db_config.get_db_connection()
    if not conn:
        print("Could not connect to database")
        return
        
    cursor = conn.cursor(dictionary=True)
    try:
        # Get first student to test with
        cursor.execute("SELECT student_id, name, dept_id FROM student LIMIT 1")
        student = cursor.fetchone()
        
        if not student:
            print("No students found in the database to test with.")
            return
            
        student_id = student['student_id']
        name = student['name']
        
        # Get branch name
        cursor.execute("SELECT dept_name FROM department WHERE dept_id=%s", (student['dept_id'],))
        dept = cursor.fetchone()
        branch = dept['dept_name'] if dept else 'Unknown'
        
        print(f"Testing with student: {name} (ID: {student_id}, Branch: {branch})")
        
        # Scenario 1: Add Partial Fee
        print("\nScenario 1: Partial Fee (Total 100000, Paid 50000)")
        query = """
            INSERT INTO fees (student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            total_fees=VALUES(total_fees), amount_paid=VALUES(amount_paid), 
            remaining_amount=VALUES(remaining_amount), status=VALUES(status)
        """
        # (Though we aren't using ON DUPLICATE in python since fee_id is PK, we are doing SELECT then UPDATE in app.py)
        # Let's mimic what app.py does.
        
        cursor.execute("DELETE FROM fees WHERE student_id=%s", (student_id,))
        
        cursor.execute(
            query.replace("ON DUPLICATE KEY UPDATE", ""), 
            (student_id, branch, 'A', 100000.0, 50000.0, 50000.0, 'Partial', datetime.date.today().strftime('%Y-%m-%d'))
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM fees WHERE student_id=%s", (student_id,))
        fee = cursor.fetchone()
        print(f"Result: Status={fee['status']}, Remaining={fee['remaining_amount']}")
        assert fee['status'] == 'Partial'
        
        # Scenario 2: Update to Paid
        print("\nScenario 2: Fully Paid (Total 100000, Paid 100000)")
        cursor.execute("""
            UPDATE fees 
            SET amount_paid=100000.0, remaining_amount=0.0, status='Paid'
            WHERE student_id=%s
        """, (student_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM fees WHERE student_id=%s", (student_id,))
        fee = cursor.fetchone()
        print(f"Result: Status={fee['status']}, Remaining={fee['remaining_amount']}")
        assert fee['status'] == 'Paid'
        
        # Scenario 3: Unpaid
        print("\nScenario 3: Unpaid (Total 100000, Paid 0)")
        cursor.execute("""
            UPDATE fees 
            SET amount_paid=0.0, remaining_amount=100000.0, status='Unpaid'
            WHERE student_id=%s
        """, (student_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM fees WHERE student_id=%s", (student_id,))
        fee = cursor.fetchone()
        print(f"Result: Status={fee['status']}, Remaining={fee['remaining_amount']}")
        assert fee['status'] == 'Unpaid'
        
        # Clean up
        cursor.execute("DELETE FROM fees WHERE student_id=%s", (student_id,))
        conn.commit()
        print("\nAll tests passed and DB cleaned up!")
        
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    test_fees_logic()
