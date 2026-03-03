import db_config

conn = db_config.get_db_connection()
if conn:
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE student ADD COLUMN profile_pic VARCHAR(255) DEFAULT 'default_avatar.png'")
        print('Added profile_pic to student table')
    except Exception as e:
        print(f'Student alter error: {e}')
        
    try:
        cursor.execute("ALTER TABLE faculty ADD COLUMN profile_pic VARCHAR(255) DEFAULT 'default_avatar.png'")
        print('Added profile_pic to faculty table')
    except Exception as e:
        print(f'Faculty alter error: {e}')
        
    conn.commit()
    cursor.close()
    conn.close()
