import db_config

def execute_faculty_schema_update():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    try:
        print("Checking if columns already exist...")
        
        # We will wrap each alter in a try-except to ignore errors if it already exists
        columns_to_add = [
            ("gender", "VARCHAR(10)"),
            ("dob", "DATE"),
            ("address", "TEXT"),
            ("designation", "VARCHAR(100)"),
            ("join_date", "DATE")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE faculty ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except Exception as e:
                # 1060 is the Duplicate Column error code in MySQL
                if "Duplicate column name" in str(e):
                    print(f"Column '{col_name}' already exists.")
                else:
                    print(f"Error adding {col_name}: {e}")
                    
        # Update existing records with default dummy data so templates don't crash
        print("Providing fallback values to existing faculty members...")
        cursor.execute("""
            UPDATE faculty 
            SET 
                gender = 'Male',
                dob = '1985-01-01',
                address = 'University Staff Quarters, Pune',
                designation = 'Assistant Professor',
                join_date = '2020-06-15'
            WHERE gender IS NULL
        """)
        
        conn.commit()
        print("Faculty schemas updated successfully!")

    except Exception as e:
        print(f"Major Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    execute_faculty_schema_update()
