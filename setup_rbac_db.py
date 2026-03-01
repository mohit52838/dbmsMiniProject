import mysql.connector
from db_config import get_db_connection

def setup_rbac():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
        
    cursor = conn.cursor()
    
    try:
        print("Adding 'password' column to student table...")
        try:
            cursor.execute("ALTER TABLE student ADD COLUMN password VARCHAR(255) DEFAULT 'student123'")
            print("Successfully added password to student.")
        except mysql.connector.Error as err:
            if err.errno == 1060:
                print("Password column already exists in student table.")
            else:
                raise err
                
        print("Adding 'password' column to faculty table...")
        try:
            cursor.execute("ALTER TABLE faculty ADD COLUMN password VARCHAR(255) DEFAULT 'faculty123'")
            print("Successfully added password to faculty.")
        except mysql.connector.Error as err:
            if err.errno == 1060:
                print("Password column already exists in faculty table.")
            else:
                raise err
                
        print("Ensuring Admin setup is seeded...")
        # Check if the admins exist, if not, create them
        cursor.execute("SELECT COUNT(*) FROM admin")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            cursor.execute("INSERT INTO admin (username, password) VALUES ('Mohit', 'Mohit123')")
            cursor.execute("INSERT INTO admin (username, password) VALUES ('Parth', 'Parth123')")
            cursor.execute("INSERT INTO admin (username, password) VALUES ('Kaustubh', 'Kaustubh123')")
            print("Created default admin accounts.")
            
        conn.commit()
        print("RBAC Database Setup Complete!")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_rbac()
