import db_config

def clear_faculty_placeholder_addresses():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor()
    try:
        # Clear out the temporary "University Staff Quarters" address so it's blank until manually filled
        cursor.execute("UPDATE faculty SET address = NULL WHERE address = 'University Staff Quarters, Pune'")
        
        # We'll leave the generic Designations ("Assistant Professor") as they are somewhat standard until updated
        conn.commit()
        print("Placeholder Faculty Addresses cleared successfully!")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    clear_faculty_placeholder_addresses()
