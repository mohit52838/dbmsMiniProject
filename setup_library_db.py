import db_config

def setup_library_tables():
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Create books table
            query_books = """
            CREATE TABLE IF NOT EXISTS books (
                book_id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                isbn VARCHAR(50),
                total_copies INT NOT NULL DEFAULT 1,
                available_copies INT NOT NULL DEFAULT 1
            )
            """
            cursor.execute(query_books)
            print("Successfully created 'books' table.")

            # Create book_issues table
            query_book_issues = """
            CREATE TABLE IF NOT EXISTS book_issues (
                issue_id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                student_id INT NOT NULL,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                status ENUM('Issued', 'Returned') NOT NULL DEFAULT 'Issued',
                FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
            )
            """
            cursor.execute(query_book_issues)
            print("Successfully created 'book_issues' table.")
            
            conn.commit()
            print("Library Database Setup Complete!")
        except Exception as e:
            print(f"Error creating library tables: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    setup_library_tables()
