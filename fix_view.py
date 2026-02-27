import mysql.connector

def run_custom_view():
    cloud_conn = mysql.connector.connect(
        host='gondola.proxy.rlwy.net',
        port=36060,
        user='root',
        password='bLuIAYbwDxXdavqVxZpWAjYGFlGrpESx',
        database='railway'
    )
    cloud_cursor = cloud_conn.cursor()

    # The issue: If a student has 5 subjects (5 marks rows) and 10 attendance rows,
    # the LEFT JOIN matches all 5 with all 10, creating 50 rows before grouping!
    # The fix: Aggregate `marks` first, then JOIN!
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
    
    -- Subquery 1: Aggregate Marks per student exactly once
    LEFT JOIN (
        SELECT 
            student_id,
            SUM(total) as total_marks_obtained,
            COUNT(mark_id) * 100 as max_possible_marks
        FROM marks
        GROUP BY student_id
    ) m ON s.student_id = m.student_id
    
    -- Subquery 2: Aggregate Attendance per student exactly once
    LEFT JOIN (
        SELECT 
            student_id,
            (SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as attendance_percentage
        FROM attendance
        WHERE status IS NOT NULL
        GROUP BY student_id
    ) a ON s.student_id = a.student_id;
    """
    
    cloud_cursor.execute(view_query)
    cloud_conn.commit()
    print("Fixed student_reports View created on Cloud!")
    cloud_cursor.close()
    cloud_conn.close()

if __name__ == '__main__':
    run_custom_view()
