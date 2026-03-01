import mysql.connector
from db_config import get_db_connection

def update_schema():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
        
    cursor = conn.cursor()
    
    columns_to_add = [
        ("prn", "VARCHAR(20) UNIQUE"),
        ("roll_no", "INT"),
        ("mother_name", "VARCHAR(100)"),
        ("address", "TEXT")
    ]
    
    for col_name, col_def in columns_to_add:
        try:
            print(f"Adding '{col_name}' column to student table...")
            cursor.execute(f"ALTER TABLE student ADD COLUMN {col_name} {col_def}")
            print(f"Successfully added {col_name}.")
        except mysql.connector.Error as err:
            if err.errno == 1060: # ER_DUP_FIELDNAME
                print(f"Column '{col_name}' already exists.")
            else:
                print(f"Error adding {col_name}: {err}")
                
    try:
        conn.commit()
        print("Schema update complete.")
    except Exception as e:
        print(f"Commit error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_schema()
