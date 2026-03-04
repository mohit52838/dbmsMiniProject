import db_config

def update_student_genders():
    # Known female names from our bulk generator:
    female_names = [
        "Neha", "Priya", "Anjali", "Riya", "Sneha", "Kriti", "Pooja", 
        "Aarohi", "Tanvi", "Shruti", "Meera", "Kavya", "Isha", "Rashi", 
        "Aditi", "Simran", "Nisha", "Swati", "Divya", "Ananya"
    ]
    
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    try:
        # We will loop through all students and update their gender
        cursor.execute("SELECT student_id, name FROM student")
        students = cursor.fetchall()
        
        updates = []
        for s_id, full_name in students:
            first_name = full_name.split()[0]
            if first_name in female_names:
                gender = 'Female'
            else:
                gender = 'Male'
            updates.append((gender, s_id))
            
        # Update everyone correctly
        query = "UPDATE student SET gender = %s WHERE student_id = %s"
        cursor.executemany(query, updates)
        conn.commit()
        print(f"Successfully fixed genders for {len(updates)} students!")

    except Exception as e:
        print(f"Error fixing genders: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_student_genders()
