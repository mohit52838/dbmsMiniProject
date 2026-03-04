import db_config
import random
import datetime

def seed_library():
    conn = db_config.get_db_connection()
    if not conn:
        print("Failed to connect to database.")
        return
    cursor = conn.cursor()

    try:
        print("Disabling foreign key checks to safely clean library data...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE book_issues;")
        cursor.execute("TRUNCATE TABLE books;")

        book_titles = [
            "Introduction to Algorithms", "Clean Code", "Design Patterns", "The Pragmatic Programmer", 
            "Structure and Interpretation of Computer Programs", "Refactoring", "Code Complete",
            "The Mythical Man-Month", "Head First Design Patterns", "Domain-Driven Design",
            "Engineering Mechanics", "Fluid Mechanics Fundamentals", "Thermodynamics: An Engineering Approach",
            "Materials Science and Engineering", "Fundamentals of Electric Circuits", "Digital Design",
            "Microelectronic Circuits", "Signals and Systems", "Control Systems Engineering",
            "Modern Control Engineering", "Structural Analysis", "Reinforced Concrete Design",
            "Geotechnical Engineering", "Transportation Engineering", "Environmental Engineering",
            "Water Resources Engineering", "Cryptography and Network Security", "Computer Networking: A Top-Down Approach",
            "Operating System Concepts", "Database System Concepts", "Artificial Intelligence: A Modern Approach",
            "Pattern Recognition and Machine Learning", "Deep Learning", "Speech and Language Processing",
            "Computer Vision: Algorithms and Applications", "Computer Graphics: Principles and Practice",
            "Fundamentals of Software Engineering", "Software Engineering: A Practitioner's Approach",
            "Agile Software Development", "The DevOps Handbook", "Site Reliability Engineering",
            "Designing Data-Intensive Applications", "Building Microservices", "Release It!",
            "Continuous Delivery", "The Phoenix Project", "Accelerate", "Zero to One",
            "The Lean Startup", "Good to Great", "Thinking, Fast and Slow", "Atomic Habits",
            "Discrete Mathematics", "Linear Algebra and Its Applications", "Calculus: Early Transcendentals",
            "Probability and Statistics for Engineers", "Numerical Methods for Engineers",
            "Engineering Mathematics", "Data Structures and Algorithms in Java", "Data Structures and Algorithms in C++",
            "Data Structures and Algorithms in Python", "Effective Java", "Effective C++"
        ]
        
        authors = [
            "Thomas H. Cormen", "Robert C. Martin", "Erich Gamma", "Andrew Hunt",
            "Harold Abelson", "Martin Fowler", "Steve McConnell", "Frederick P. Brooks Jr.",
            "Eric Freeman", "Eric Evans", "R. C. Hibbeler", "Yunus A. Cengel",
            "William D. Callister", "Charles K. Alexander", "M. Morris Mano",
            "Adel S. Sedra", "Alan V. Oppenheim", "Norman S. Nise", "Katsuhiko Ogata",
            "R. C. Hibbeler", "Jack C. McCormac", "Braja M. Das", "James H. Banks",
            "Mackenzie L. Davis", "David Chin", "William Stallings", "James F. Kurose",
            "Abraham Silberschatz", "Stuart Russell", "Christopher M. Bishop",
            "Ian Goodfellow", "Daniel Jurafsky", "Richard Szeliski", "John F. Hughes",
            "Roger S. Pressman", "Robert C. Martin", "Gene Kim", "Niall Richard Murphy",
            "Martin Kleppmann", "Sam Newman", "Michael T. Nygard", "Jez Humble",
            "Peter Thiel", "Eric Ries", "Jim Collins", "Daniel Kahneman", "James Clear",
            "Kenneth H. Rosen", "David C. Lay", "James Stewart", "Ronald E. Walpole",
            "Steven C. Chapra", "K. A. Stroud", "Michael T. Goodrich", "Mark Allen Weiss",
            "Michael T. Goodrich", "Joshua Bloch", "Scott Meyers"
        ]

        print(f"Generating 60 Library Books...")
        books_to_insert = []
        author_map = {}
        for i, title in enumerate(book_titles):
            author = authors[i % len(authors)]
            isbn = f"978-{random.randint(100000000, 999999999)}"
            total_copies = random.randint(3, 15)
            # available copies might be slightly less if books are issued, we will calculate after issues
            available_copies = total_copies
            books_to_insert.append((i+1, title, author, isbn, total_copies, available_copies))

        query_books = "INSERT INTO books (book_id, title, author, isbn, total_copies, available_copies) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.executemany(query_books, books_to_insert)

        print("Generating 150 Book Issues for Students...")
        
        # Get all students
        cursor.execute("SELECT student_id FROM student")
        students = [row[0] for row in cursor.fetchall()]
        
        if not students:
            print("No students found. Skipping book issues.")
        else:
            issues_to_insert = []
            today_date = datetime.date.today()
            
            # Keep track of available copies
            book_availability = {b[0]: b[4] for b in books_to_insert}
            
            for i in range(150):
                book_id = random.randint(1, len(book_titles))
                if book_availability[book_id] <= 0:
                    continue
                    
                student_id = random.choice(students)
                
                # Issue date from 60 days ago to today
                days_ago = random.randint(1, 60)
                issue_date = today_date - datetime.timedelta(days=days_ago)
                due_date = issue_date + datetime.timedelta(days=15)
                
                # 70% chance returned, 30% chance still issued
                if random.random() < 0.7:
                    status = 'Returned'
                    return_days_after = random.randint(5, 25)
                    return_date = issue_date + datetime.timedelta(days=return_days_after)
                    
                    fine_amount = 0.00
                    if return_date > due_date:
                        days_late = (return_date - due_date).days
                        fine_amount = days_late * 5.00 # $5 per day
                        
                    issues_to_insert.append((book_id, student_id, issue_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), return_date.strftime('%Y-%m-%d'), fine_amount, status))
                else:
                    status = 'Issued'
                    return_date = None
                    book_availability[book_id] -= 1
                    
                    fine_amount = 0.00
                    if today_date > due_date:
                        days_late = (today_date - due_date).days
                        fine_amount = days_late * 5.00
                        
                    issues_to_insert.append((book_id, student_id, issue_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), None, fine_amount, status))

            if issues_to_insert:
                query_issues = """
                    INSERT INTO book_issues (book_id, student_id, issue_date, due_date, return_date, fine_amount, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(query_issues, issues_to_insert)
                
                # Update available copies in books table
                for bid, avail in book_availability.items():
                    cursor.execute("UPDATE books SET available_copies = %s WHERE book_id = %s", (avail, bid))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("Successfully seeded Library Data!")

    except Exception as e:
        print(f"Error seeding library data: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_library()
