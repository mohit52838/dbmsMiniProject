import db_config
try:
    conn = db_config.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE OR REPLACE VIEW `student_reports` AS 
        SELECT 
            `s`.`student_id` AS `student_id`,
            `s`.`name` AS `name`,
            `s`.`prn` AS `prn`,
            `s`.`roll_no` AS `roll_no`,
            `s`.`email` AS `email`,
            `s`.`phone` AS `phone`,
            `s`.`gender` AS `gender`,
            `s`.`mother_name` AS `mother_name`,
            `s`.`address` AS `address`,
            `s`.`profile_pic` AS `profile_pic`,
            `d`.`dept_name` AS `branch`,
            `s`.`division` AS `division`,
            coalesce(`m`.`total_marks_obtained`,0) AS `total_marks_obtained`,
            coalesce(`m`.`max_possible_marks`,0) AS `max_possible_marks`,
            (case when (`m`.`max_possible_marks` > 0) then ((`m`.`total_marks_obtained` / `m`.`max_possible_marks`) * 100) else 0 end) AS `percentage`,
            coalesce(`a`.`attendance_percentage`,0) AS `attendance_percentage` 
        FROM (((`student` `s` 
        LEFT JOIN `department` `d` ON((`s`.`dept_id` = `d`.`dept_id`))) 
        LEFT JOIN (
            SELECT `marks`.`student_id` AS `student_id`,
                   sum(`marks`.`total`) AS `total_marks_obtained`,
                   (count(`marks`.`mark_id`) * 100) AS `max_possible_marks` 
            FROM `marks` 
            GROUP BY `marks`.`student_id`
        ) `m` ON((`s`.`student_id` = `m`.`student_id`))) 
        LEFT JOIN (
            SELECT `attendance`.`student_id` AS `student_id`,
                   ((sum((case when (`attendance`.`status` = 'Present') then 1 else 0 end)) / count(0)) * 100) AS `attendance_percentage` 
            FROM `attendance` 
            WHERE (`attendance`.`status` is not null) 
            GROUP BY `attendance`.`student_id`
        ) `a` ON((`s`.`student_id` = `a`.`student_id`)))
    """)
    conn.commit()
    print("SUCCESS: `student_reports` fully rebuilt and populated with `gender` flag!")
except Exception as e:
    print(f"Error recreating student_reports view: {e}")
finally:
    if cursor: cursor.close()
    if conn: conn.close()
