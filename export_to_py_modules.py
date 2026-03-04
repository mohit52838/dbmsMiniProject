import db_config
import os
import decimal
import datetime

def format_value(val):
    if val is None:
        return "None"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, decimal.Decimal):
        return str(float(val))
    if isinstance(val, (datetime.date, datetime.datetime)):
        return repr(str(val))
    return repr(str(val))

def export_db_to_python_modules():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect.")
        return

    cursor = conn.cursor(dictionary=False)
    
    # We will export tables to individual python files
    tables = {
        'student': 'students_data.py',
        'faculty': 'faculty_data.py',
        'subject': 'subjects_data.py',
        'department': 'department_data.py',
        'fees': 'fees_data.py',
        'books': 'books_data.py',
        'book_issues': 'book_issues_data.py',
    }
    
    os.makedirs('demo_data_py', exist_ok=True)
    
    try:
        for table, filename in tables.items():
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            file_path = f"demo_data_py/{filename}"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Auto-generated data for {table}\n")
                f.write(f"{table}_records = [\n")
                
                for row in rows:
                    formatted_row = [format_value(item) for item in row]
                    f.write(f"    ({', '.join(formatted_row)}),\n")
                    
                f.write("]\n")
            print(f"Exported {len(rows)} records to {file_path}")
            
        # Due to size, marks and attendance get special handling to avoid massive single files
        # We will split attendance into 5 chunks (branches roughly)
        for big_table in ['marks', 'attendance']:
            cursor.execute(f"SELECT * FROM {big_table}")
            rows = cursor.fetchall()
            
            chunk_size = 15000  # Split chunks explicitly
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i+chunk_size]
                file_path = f"demo_data_py/{big_table}_data_part_{i//chunk_size + 1}.py"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Auto-generated data chunk for {big_table}\n")
                    f.write(f"{big_table}_records_part_{i//chunk_size + 1} = [\n")
                    for row in chunk:
                        formatted_row = [format_value(item) for item in row]
                        f.write(f"    ({', '.join(formatted_row)}),\n")
                    f.write("]\n")
                print(f"Exported chunk of {len(chunk)} {big_table} records to {file_path}")
                
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    export_db_to_python_modules()
