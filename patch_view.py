import db_config

def patch_student_reports_view():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    try:
        # Drop the existing view
        cursor.execute("DROP VIEW IF EXISTS `student_reports`")
        
        # Recreate the view with the 'gender' column included
        query = """
        CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `student_reports` AS 
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
            COALESCE(`m`.`total_marks_obtained`, 0) AS `total_marks_obtained`,
            COALESCE(`m`.`max_possible_marks`, 0) AS `max_possible_marks`,
            (CASE 
                WHEN (`m`.`max_possible_marks` > 0) THEN ((`m`.`total_marks_obtained` / `m`.`max_possible_marks`) * 100) 
                ELSE 0 
            END) AS `percentage`,
            COALESCE(`a`.`attendance_percentage`, 0) AS `attendance_percentage` 
        FROM (((`student` `s` 
        LEFT JOIN `department` `d` ON((`s`.`dept_id` = `d`.`dept_id`))) 
        LEFT JOIN (
            SELECT 
                `marks`.`student_id` AS `student_id`,
                SUM(`marks`.`total`) AS `total_marks_obtained`,
                (COUNT(`marks`.`mark_id`) * 100) AS `max_possible_marks` 
            FROM `marks` 
            GROUP BY `marks`.`student_id`
        ) `m` ON((`s`.`student_id` = `m`.`student_id`))) 
        LEFT JOIN (
            SELECT 
                `attendance`.`student_id` AS `student_id`,
                ((SUM((CASE WHEN (`attendance`.`status` = 'Present') THEN 1 ELSE 0 END)) / COUNT(0)) * 100) AS `attendance_percentage` 
            FROM `attendance` 
            WHERE (`attendance`.`status` IS NOT NULL) 
            GROUP BY `attendance`.`student_id`
        ) `a` ON((`s`.`student_id` = `a`.`student_id`)))
        """
        cursor.execute(query)
        conn.commit()
        print("Successfully patched `student_reports` view to include gender!")
    except Exception as e:
        print(f"Error patching view: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    patch_student_reports_view()
