import db_config

def setup_fees_table():
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Create fees table
            query = """
            CREATE TABLE IF NOT EXISTS fees (
                fee_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                branch VARCHAR(100) NOT NULL,
                class_year VARCHAR(20) NOT NULL,
                total_fees DECIMAL(10, 2) NOT NULL,
                amount_paid DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                remaining_amount DECIMAL(10, 2) NOT NULL,
                status ENUM('Paid', 'Partial', 'Unpaid') NOT NULL,
                payment_date DATE,
                FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
            )
            """
            cursor.execute(query)
            conn.commit()
            print("Successfully created 'fees' table with ON DELETE CASCADE.")
        except Exception as e:
            print(f"Error creating fees table: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_fees_table()
