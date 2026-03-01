import db_config
import reprlib

def export_table_data(cursor, table_name):
    # Retrieve all columns and rows from a table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if not rows:
        return []

    # Get column names
    columns = [desc[0] for desc in cursor.description]
    return {'columns': columns, 'rows': rows}

def generate_seed_script():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return

    cursor = conn.cursor(dictionary=False)

    tables = ['student', 'attendance', 'marks', 'fees']
    data = {}

    try:
        for table in tables:
            data[table] = export_table_data(cursor, table)
            print(f"Extracted {len(data[table].get('rows', []))} rows from {table}")
    finally:
        cursor.close()
        conn.close()

    # Generate the seed_static_demo.py script
    script_content = f"""import db_config
import datetime

def seed_static_data():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect to DB for static seeding.")
        return
        
    cursor = conn.cursor()
    
    # We will truncate those tables first to ensure a clean slate
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE fees;")
        cursor.execute("TRUNCATE TABLE attendance;")
        cursor.execute("TRUNCATE TABLE marks;")
        cursor.execute("TRUNCATE TABLE student;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Cleared existing student/attendance/marks/fees tables.")
    except Exception as e:
        print(f"Error clearing tables: {{e}}")
        conn.rollback()
        return

    try:
"""
    # Write insert statements for each table
    for table in tables:
        table_data = data.get(table, {})
        rows = table_data.get('rows', [])
        columns = table_data.get('columns', [])
        
        if not rows:
            continue
            
        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(["%s"] * len(columns))
        
        script_content += f"""
        print("Inserting static records into {table}...")
        {table}_query = "INSERT INTO {table} ({columns_str}) VALUES ({placeholders_str})"
        {table}_records = [
"""
        for row in rows:
            # Need to carefully format objects like dates/decimals for the python script literal
            formatted_row = []
            for item in row:
                if isinstance(item, str):
                    formatted_row.append(repr(item))
                elif item is None:
                    formatted_row.append("None")
                elif hasattr(item, 'strftime'): # datetime/date
                    formatted_row.append(f"datetime.date({item.year}, {item.month}, {item.day})")
                else: # Decimal, int, etc. For precise Decimal insertion we can just pass strings or floats as DB connector handles it mostly, but float is safer literal.
                    formatted_row.append(repr(item))
            script_content += f"            ({', '.join(formatted_row)}),\n"
            
        script_content += f"""        ]
        cursor.executemany({table}_query, {table}_records)
"""

    script_content += """
        conn.commit()
        print("Successfully seeded static demo data!")
    except Exception as e:
        print(f"Error executing static seed: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    seed_static_data()
"""

    with open("seed_static_demo.py", "w", encoding='utf-8') as f:
        f.write(script_content)

    print("Successfully generated seed_static_demo.py!")

if __name__ == "__main__":
    generate_seed_script()
