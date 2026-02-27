import mysql.connector

import os

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
# UPDATE THESE VALUES IF YOUR MYSQL SETUP IS DIFFERENT
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "M@ratha12") # Fallback to local password
DB_NAME = os.environ.get("DB_NAME", "college_management")

def get_db_connection():
    """Establish and return a database connection."""
    try:
        # Build connection arguments
        config = {
            'host': DB_HOST,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_NAME,
            'port': int(os.environ.get("DB_PORT", 3306)),
            'connection_timeout': int(os.environ.get("DB_TIMEOUT", 10))
        }

        # Check if production environment requires SSL (like Aiven or PlanetScale)
        if os.environ.get("DB_REQUIRE_SSL", "False").lower() == "true":
            config['ssl_disabled'] = False
            config['ssl_verify_identity'] = False # For general cloud hosts

        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        # Graceful handling without throwing full raw stack traces locally or in prod
        print(f"Database Connection Error: {err.msg}")
        return None

def calculate_grade(marks):
    """Automatic grade calculation logic."""
    if marks is None:
        return ""
    if marks >= 90:
        return "A"
    elif marks >= 75:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 40:
        return "D"
    else:
        return "F"

def create_student_reports_view():
    """Create the required view for student reports if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    # Assuming tables: students(student_id, name, ...), attendance(student_id, present_days, total_days, ...), marks(student_id, subject_id, total_marks, ...)
    # Create a simplified view based on typical schema for this system
    view_query = """
    CREATE OR REPLACE VIEW student_reports AS
    SELECT 
        s.student_id, 
        s.name, 
        d.dept_name as branch,
        s.division,
        COALESCE(m.total_marks_obtained, 0) AS total_marks_obtained,
        COALESCE(m.max_possible_marks, 0) AS max_possible_marks,
        CASE WHEN m.max_possible_marks > 0 THEN (m.total_marks_obtained / m.max_possible_marks) * 100 ELSE 0 END as percentage,
        COALESCE(a.attendance_percentage, 0) AS attendance_percentage
    FROM student s
    LEFT JOIN department d ON s.dept_id = d.dept_id
    LEFT JOIN (
        SELECT student_id, SUM(total) as total_marks_obtained, COUNT(mark_id) * 100 as max_possible_marks
        FROM marks GROUP BY student_id
    ) m ON s.student_id = m.student_id
    LEFT JOIN (
        SELECT student_id, (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as attendance_percentage
        FROM attendance WHERE status IS NOT NULL GROUP BY student_id
    ) a ON s.student_id = a.student_id;
    """
    
    try:
        cursor.execute(view_query)
        conn.commit()
        print("VIEW `student_reports` created or updated successfully.")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating view: {err}")
        # Note: If there is an error, it might be due to column names.
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_student_reports_view()
