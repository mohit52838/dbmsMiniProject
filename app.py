from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
import db_config
import os
import csv
from io import StringIO

app = Flask(__name__)
# Use a static secret key so dev-server reloads don't log the user out
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_static_key_for_development')

# Initialize DB View on startup
db_config.create_student_reports_view()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role', 'Admin')
        username = request.form['username']
        password = request.form['password']
        
        # Admin Role
        if role == 'Admin':
            # Simple admin login
            if username == 'Mohit' and password == 'Mohit123':
                session['logged_in'] = True
                session['role'] = 'admin'
                session['user_id'] = 0
                flash('Welcome built-in Admin!', 'success')
                return redirect(url_for('dashboard'))
            elif username == 'Parth' and password == 'Parth123':
                session['logged_in'] = True
                session['role'] = 'admin'
                session['user_id'] = 0
                flash('Welcome built-in Admin!', 'success')
                return redirect(url_for('dashboard'))
            elif username == 'Kaustubh' and password == 'Kaustubh123':
                session['logged_in'] = True
                session['role'] = 'admin'
                session['user_id'] = 0
                flash('Welcome built-in Admin!', 'success')
                return redirect(url_for('dashboard'))
            else:
                conn = db_config.get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    try:
                        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
                        admin = cursor.fetchone()
                        if admin:
                            session['logged_in'] = True
                            session['role'] = 'admin'
                            session['user_id'] = admin['admin_id']
                            flash('Login successful!', 'success')
                            return redirect(url_for('dashboard'))
                    except Exception as e:
                        print(f"DB Auth Error: {e}")
                    finally:
                        cursor.close()
                        conn.close()
                flash('Invalid Admin credentials.', 'danger')
                
        # Faculty Role
        elif role == 'Faculty':
            conn = db_config.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    # Allow Faculty to login by Email OR exact Name for robust fallback
                    cursor.execute("SELECT * FROM faculty WHERE (email=%s OR name=%s) AND password=%s", (username, username, password))
                    faculty = cursor.fetchone()
                    if faculty:
                        session['logged_in'] = True
                        session['role'] = 'faculty'
                        session['user_id'] = faculty['faculty_id']
                        session['name'] = faculty['name']
                        faculty_raw_name = faculty['name']
                        cleaned_name = faculty_raw_name.replace('Mr. ', '').replace('Mrs. ', '').replace('Ms. ', '').replace('Dr. ', '').replace('Prof. ', '').strip()
                        last_name = cleaned_name.split()[-1] if len(cleaned_name.split()) > 0 else cleaned_name
                        flash(f"Welcome back, Prof. {last_name}!", 'success')
                        return redirect(url_for('dashboard'))
                except Exception as e:
                    print(f"Faculty Auth Error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            flash('Invalid Faculty credentials.', 'danger')

        # Student Role
        elif role == 'Student':
            conn = db_config.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute("SELECT * FROM student WHERE (email=%s OR name=%s) AND password=%s", (username, username, password))
                    student = cursor.fetchone()
                    if student:
                        session['logged_in'] = True
                        session['role'] = 'student'
                        session['user_id'] = student['student_id']
                        session['name'] = student['name']
                        flash(f"Welcome, {student['name'].split()[0]}!", 'success')
                        return redirect(url_for('dashboard'))
                except Exception as e:
                    print(f"Student Auth Error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            flash('Invalid Student credentials.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = db_config.get_db_connection()
    students_count = 0
    faculty_count = 0
    student_stats = {}
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if session.get('role') in ['admin', 'faculty']:
                cursor.execute("SELECT COUNT(*) as count FROM student")
                students_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM faculty")
                faculty_count = cursor.fetchone()['count']
                
            elif session.get('role') == 'student':
                student_id = session.get('user_id')
                
                # Get Attendance %
                cursor.execute("SELECT COUNT(*) as total_classes FROM attendance WHERE student_id = %s", (student_id,))
                total_classes = cursor.fetchone()['total_classes']
                
                cursor.execute("SELECT COUNT(*) as present_classes FROM attendance WHERE student_id = %s AND status = 'Present'", (student_id,))
                present_classes = cursor.fetchone()['present_classes']
                
                if total_classes > 0:
                    student_stats['attendance_pct'] = (present_classes / total_classes) * 100
                else:
                    student_stats['attendance_pct'] = 0.0
                    
                # Get Average Marks
                cursor.execute("SELECT AVG(total) as avg_marks FROM marks WHERE student_id = %s", (student_id,))
                res = cursor.fetchone()
                student_stats['avg_marks'] = res['avg_marks'] if res['avg_marks'] else 0.0
                
                # Get Detailed Attendance
                cursor.execute("""
                    SELECT sub.subject_name, 
                           SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present_count,
                           COUNT(a.attendance_id) as total_count
                    FROM attendance a
                    JOIN subject sub ON a.subject_id = sub.subject_id
                    WHERE a.student_id = %s
                    GROUP BY a.subject_id, sub.subject_name
                """, (student_id,))
                student_stats['detailed_attendance'] = cursor.fetchall()
                
                # Get Detailed Marks
                cursor.execute("""
                    SELECT sub.subject_name, m.internal_marks, m.external_marks, m.total, m.grade
                    FROM marks m
                    JOIN subject sub ON m.subject_id = sub.subject_id
                    WHERE m.student_id = %s
                """, (student_id,))
                student_stats['detailed_marks'] = cursor.fetchall()

                # Get Fee Status
                cursor.execute("SELECT status FROM fees WHERE student_id = %s ORDER BY payment_date DESC LIMIT 1", (student_id,))
                fee_record = cursor.fetchone()
                student_stats['fee_status'] = fee_record['status'] if fee_record else 'Unpaid'

        except Exception as e:
            print(f"Dashboard Query Error: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('dashboard.html', 
                           students_count=students_count, 
                           faculty_count=faculty_count,
                           student_stats=student_stats)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied. Admins and Faculty only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department_id = request.form.get('department_id', 1) # Default to 1
        division = request.form.get('division', 'A')
        
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Adapted to real columns without course_id
                query = "INSERT INTO student (name, email, phone, gender, dob, dept_id, division) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(query, (name, email, phone, 'Other', '2000-01-01', department_id, division))
                conn.commit()
                flash('Student added successfully!', 'success')
                return redirect(url_for('view_students'))
            except Exception as e:
                flash(f'Error adding student: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
                
    departments = []
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if session.get('role') == 'faculty':
                # Only show their own department
                cursor.execute("""
                    SELECT d.dept_id, d.dept_name 
                    FROM department d 
                    JOIN faculty f ON d.dept_id = f.dept_id 
                    WHERE f.faculty_id = %s
                """, (session.get('user_id'),))
            else:
                cursor.execute("SELECT dept_id, dept_name FROM department")
                
            departments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('add_student.html', departments=departments)

@app.route('/view_students')
def view_students():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if session.get('role') == 'faculty':
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id FROM faculty WHERE faculty_id = %s", (session.get('user_id'),))
            faculty_dept = cursor.fetchone()
            if faculty_dept:
                dept_id_filter = faculty_dept[0]
            else:
                dept_id_filter = request.args.get('dept_id')  # Fallback
            cursor.close()
            conn.close()
    else:
        dept_id_filter = request.args.get('dept_id')
    
    conn = db_config.get_db_connection()
    reports = {}
    departments = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch departments for the filter dropdown
            if session.get('role') == 'faculty':
                # Only show their own department in the dropdown
                cursor.execute("""
                    SELECT d.dept_id, d.dept_name 
                    FROM department d 
                    JOIN faculty f ON d.dept_id = f.dept_id 
                    WHERE f.faculty_id = %s
                """, (session.get('user_id'),))
            else:
                cursor.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
                
            departments = cursor.fetchall()
            
            # Using the VIEW created in phase 2/3
            query = """
                SELECT sr.*, d.dept_id
                FROM student_reports sr
                LEFT JOIN department d ON sr.branch = d.dept_name
            """
            params = []
            
            # Implement explicit Branch filtering if selected
            if dept_id_filter:
                query += " WHERE d.dept_id = %s "
                params.append(dept_id_filter)
                
            # Enforce strict alphabetical sorting for Divisions: A -> B -> C -> D
            query += " ORDER BY d.dept_id ASC, COALESCE(sr.division, 'A') ASC, sr.name ASC "
            
            cursor.execute(query, tuple(params))
            reports_raw = cursor.fetchall()
            
            # Application-level logic for calculating grades from total_marks
            for r in reports_raw:
                r['grade'] = db_config.calculate_grade(r.get('total_marks', 0))
                # Also format attendance percentage
                att_pct = r.get('attendance_percentage', 0)
                r['attendance_percentage'] = round(att_pct, 2) if att_pct else 0.0
                
                branch = r['branch'] or 'Unassigned Branch'
                division = r.get('division', 'A') or 'A'
                
                if branch not in reports:
                    reports[branch] = {}
                if division not in reports[branch]:
                    reports[branch][division] = []
                    
                reports[branch][division].append(r)
                
        except Exception as e:
            print(f"Error fetching from view: {e}")
            flash('Error fetching student reports view.', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('view_students.html', reports=reports, departments=departments, current_dept_id=dept_id_filter)

@app.route('/add_faculty', methods=['GET', 'POST'])
def add_faculty():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form['name']
        department = request.form['department']
        email = request.form['email']
        
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Adjust to real schema
                query = "INSERT INTO faculty (name, email, phone, dept_id) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (name, email, '0000000000', department))
                conn.commit()
                flash('Faculty added successfully!', 'success')
                return redirect(url_for('view_faculty'))
            except Exception as e:
                flash(f'Error adding faculty: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
                
    departments = []
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT dept_id, dept_name FROM department")
            departments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching departments: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('add_faculty.html', departments=departments)

@app.route('/view_faculty')
def view_faculty():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = db_config.get_db_connection()
    faculties = {}
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT f.faculty_id, f.name, f.email, f.phone, COALESCE(d.dept_name, 'Unassigned Branch') as department
                FROM faculty f
                LEFT JOIN department d ON f.dept_id = d.dept_id
                ORDER BY d.dept_id, f.faculty_id
            """)
            faculties_raw = cursor.fetchall()
            
            # Group dynamically in python to preserve SQL sorting order (Jinja groupby sorts alphabetically)
            for f in faculties_raw:
                dept = f['department']
                if dept not in faculties:
                    faculties[dept] = []
                faculties[dept].append(f)
                
        except Exception as e:
            flash(f'Error fetching faculty logic: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('view_faculty.html', faculties=faculties)

@app.route('/view_subjects')
def view_subjects():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = db_config.get_db_connection()
    subjects = {}
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT s.subject_id, s.subject_name, f.name as faculty_name, COALESCE(d.dept_name, 'Unassigned Branch') as department
                FROM subject s
                LEFT JOIN department d ON s.dept_id = d.dept_id
                LEFT JOIN faculty f ON s.faculty_id = f.faculty_id
                ORDER BY d.dept_id, s.subject_id
            """)
            subjects_raw = cursor.fetchall()
            
            # Group dynamically in python to preserve SQL sorting order
            for s in subjects_raw:
                dept = s['department']
                if dept not in subjects:
                    subjects[dept] = []
                subjects[dept].append(s)
                
        except Exception as e:
            flash(f'Error fetching subjects: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('view_subjects.html', subjects=subjects)

@app.route('/add_marks', methods=['GET', 'POST'])
def add_marks():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                query = "INSERT INTO marks (student_id, subject_id, internal_marks, external_marks, total, grade) VALUES (%s, %s, %s, %s, %s, %s)"
                
                # Check for dynamic keys generated by JS: 'marks_{subject_id}'
                for key, value in request.form.items():
                    if key.startswith('marks_') and value.strip():
                        subject_id = key.split('_')[1]
                        marks = float(value)
                        calculated_grade = db_config.calculate_grade(marks)
                        cursor.execute(query, (student_id, subject_id, marks/2, marks/2, marks, calculated_grade))
                
                conn.commit()
                flash('All subject marks recorded successfully!', 'success')
            except Exception as e:
                flash(f'Error adding bulk marks: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
                
    departments = []
    current_dept_id = None
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if session.get('role') == 'faculty':
                # Faculty can only see their department
                cursor.execute("SELECT d.dept_id, d.dept_name FROM department d JOIN faculty f ON d.dept_id = f.dept_id WHERE f.faculty_id = %s", (session.get('user_id'),))
                departments = cursor.fetchall()
                if departments:
                    current_dept_id = departments[0]['dept_id']
            else:
                cursor.execute("SELECT dept_id, dept_name FROM department")
                departments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching departments: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('add_marks.html', departments=departments)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        if not student_id:
            flash('Error: No student selected.', 'danger')
            return redirect(url_for('attendance'))

        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                import datetime
                today = datetime.date.today().strftime('%Y-%m-%d')
                
                query = "INSERT INTO attendance (student_id, subject_id, date, status) VALUES (%s, %s, %s, %s)"
                
                total_present_across_subjects = 0
                total_days_across_subjects = 0
                
                # Loop through all dynamic `present_X` and `total_X` inputs
                for key, value in request.form.items():
                    if key.startswith('present_'):
                        subject_id = key.split('_')[1]
                        present_days = int(value)
                        total_days = int(request.form.get(f'total_{subject_id}', 1))
                        
                        if total_days <= 0:
                            continue # Skip invalid ones
                            
                        total_present_across_subjects += present_days
                        total_days_across_subjects += total_days
                        
                        # Generate the daily rows to satisfy the database schema
                        for i in range(total_days):
                            status = 'Present' if i < present_days else 'Absent'
                            test_date = (datetime.date.today() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                            cursor.execute(query, (student_id, subject_id, test_date, status))
                
                conn.commit()
                
                if total_days_across_subjects > 0:
                    overall_percentage = (total_present_across_subjects / total_days_across_subjects) * 100
                    flash(f'Bulk Attendance recorded! Overall Percentage: {overall_percentage:.2f}%', 'success')
                else:
                    flash('No valid attendance data was submitted.', 'warning')
                    
            except Exception as e:
                flash(f'Error recording attendance: {e}', 'danger')
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
                
    departments = []
    current_dept_id = None
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if session.get('role') == 'faculty':
                # Faculty can only see their department
                cursor.execute("SELECT d.dept_id, d.dept_name FROM department d JOIN faculty f ON d.dept_id = f.dept_id WHERE f.faculty_id = %s", (session.get('user_id'),))
                departments = cursor.fetchall()
                if departments:
                    current_dept_id = departments[0]['dept_id']
            else:
                cursor.execute("SELECT dept_id, dept_name FROM department")
                departments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching departments: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('attendance.html', departments=departments)

@app.route('/update_student/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = db_config.get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department_id = request.form.get('department_id')
        division = request.form.get('division', 'A')
        
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE student SET name=%s, email=%s, phone=%s, dept_id=%s, division=%s WHERE student_id=%s", (name, email, phone, department_id, division, id))
                conn.commit()
                flash('Student updated successfully!', 'success')
                return redirect(url_for('view_students'))
            except Exception as e:
                flash(f'Error updating student: {e}', 'danger')
            finally:
                cursor.close()
                conn.close()
    else:
        # GET request to display form
        departments = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM student WHERE student_id=%s", (id,))
                student = cursor.fetchone()
                
                cursor.execute("SELECT dept_id, dept_name FROM department")
                departments = cursor.fetchall()
                
                return render_template('update_student.html', student=student, departments=departments)
            except Exception as e:
                flash(f'Error fetching student: {e}', 'danger')
                return redirect(url_for('view_students'))
            finally:
                cursor.close()
                conn.close()
                
    return redirect(url_for('view_students'))

@app.route('/delete_student/<int:id>', methods=['POST'])
def delete_student(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM student WHERE student_id=%s", (id,))
            conn.commit()
            flash('Student deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting student: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return redirect(url_for('view_students'))

@app.route('/student_marks/<int:id>')
def view_student_marks(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    conn = db_config.get_db_connection()
    marks_details = []
    student_info = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch student name
            cursor.execute("SELECT name FROM student WHERE student_id=%s", (id,))
            student_info = cursor.fetchone()
            
            # Fetch detailed subject-level marks, grouping them safely just in case there are duplicates
            cursor.execute("""
                SELECT 
                    s.subject_name, 
                    SUM(m.internal_marks) as internal_marks, 
                    SUM(m.external_marks) as external_marks, 
                    SUM(m.total) as total, 
                    MAX(m.grade) as grade
                FROM marks m
                JOIN subject s ON m.subject_id = s.subject_id
                WHERE m.student_id = %s
                GROUP BY s.subject_name
            """, (id,))
            marks_details = cursor.fetchall()

            # Recalculate the grade based on the newly summed actual total
            for row in marks_details:
                row['grade'] = db_config.calculate_grade(row['total'])
        except Exception as e:
            flash(f'Error fetching marks details: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    if not student_info:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_students'))
        
    return render_template('view_student_marks.html', student=student_info, marks=marks_details)

# ==========================================
# JSON API ENDPOINTS (For JS cascading dropdowns)
# ==========================================

@app.route('/api/divisions/<int:dept_id>')
def api_divisions(dept_id):
    # Returns a hardcoded list of supported divisions. 
    # (Could be expanded to query DISTINCT divisions from the DB if they were fully dynamic)
    return jsonify(['A', 'B', 'C', 'D'])

@app.route('/api/students/<int:dept_id>/<string:division>')
def api_students(dept_id, division):
    conn = db_config.get_db_connection()
    students = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT student_id, name FROM student WHERE dept_id=%s AND division=%s ORDER BY name", (dept_id, division))
            students = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    return jsonify(students)

@app.route('/api/subjects/<int:dept_id>')
def api_subjects(dept_id):
    conn = db_config.get_db_connection()
    subjects = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT subject_id, subject_name FROM subject WHERE dept_id=%s ORDER BY subject_id", (dept_id,))
            subjects = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    return jsonify(subjects)

# ==========================================
# FEES MANAGEMENT ENDPOINTS
# ==========================================

@app.route('/add_fees', methods=['GET', 'POST'])
def add_fees():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') != 'admin':
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        branch = request.form.get('branch_name') # we'll pass the text value directly from frontend or fetch it
        class_year = request.form.get('class_year', 'A') # Using division as class_year if mapping directly
        
        try:
            total_fees = float(request.form.get('total_fees', 0.0))
            amount_paid = float(request.form.get('amount_paid', 0.0))
        except ValueError:
            flash('Invalid fee amounts entered.', 'danger')
            return redirect(url_for('add_fees'))
            
        remaining_amount = total_fees - amount_paid
        if amount_paid >= total_fees:
            status = 'Paid'
        elif amount_paid == 0:
            status = 'Unpaid'
        else:
            status = 'Partial'
            
        import datetime
        payment_date = datetime.date.today().strftime('%Y-%m-%d')
        
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # If a fee record exists for this student, update it. Otherwise, insert.
                # Assuming 1 fee record per student per year (simplified to 1 per student here)
                cursor.execute("SELECT fee_id FROM fees WHERE student_id = %s", (student_id,))
                existing_fee = cursor.fetchone()
                
                if existing_fee:
                    query = """
                    UPDATE fees 
                    SET total_fees=%s, amount_paid=%s, remaining_amount=%s, status=%s, payment_date=%s
                    WHERE student_id=%s
                    """
                    cursor.execute(query, (total_fees, amount_paid, remaining_amount, status, payment_date, student_id))
                    flash('Fee record updated successfully!', 'success')
                else:
                    query = """
                    INSERT INTO fees 
                    (student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (student_id, branch, class_year, total_fees, amount_paid, remaining_amount, status, payment_date))
                    flash('Fee record added successfully!', 'success')
                
                conn.commit()
                return redirect(url_for('view_fees'))
            except Exception as e:
                flash(f'Error saving fee record: {e}', 'danger')
                conn.rollback()
            finally:
                cursor.close()
                conn.close()
                
    departments = []
    conn = db_config.get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT dept_id, dept_name FROM department")
            departments = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching departments: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('add_fees.html', departments=departments)

@app.route('/view_fees')
def view_fees():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session.get('role') not in ['admin', 'faculty']:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    
    branch_filter = request.args.get('branch')
    class_filter = request.args.get('class_year')
    
    conn = db_config.get_db_connection()
    fees_data = {}
    departments = []
    
    if session.get('role') == 'faculty':
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT d.dept_id, d.dept_name FROM department d JOIN faculty f ON d.dept_id = f.dept_id WHERE f.faculty_id = %s", (session.get('user_id'),))
            faculty_dept = cursor.fetchone()
            if faculty_dept:
                branch_filter = faculty_dept[1] # Override whatever was selected with their actual branch
            cursor.close()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if session.get('role') == 'faculty':
                # Faculty only see their department
                cursor.execute("""
                    SELECT department.dept_id, department.dept_name 
                    FROM department
                    JOIN faculty ON department.dept_id = faculty.dept_id 
                    WHERE faculty.faculty_id = %s
                """, (session.get('user_id'),))
            else:
                cursor.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
            
            departments = cursor.fetchall()
            
            query = """
                SELECT f.*, s.name as student_name, d.dept_id
                FROM fees f
                JOIN student s ON f.student_id = s.student_id
                LEFT JOIN department d ON f.branch = d.dept_name
            """
            params = []
            conditions = []
            
            if session.get('role') == 'faculty':
                # Absolute override: Force the query to ONLY look at their assigned branch
                cursor.execute("SELECT faculty.dept_id FROM faculty WHERE faculty.faculty_id = %s", (session.get('user_id'),))
                faculty_dept = cursor.fetchone()
                if faculty_dept:
                    conditions.append("d.dept_id = %s")
                    params.append(faculty_dept['dept_id'])
            elif branch_filter:
                conditions.append("f.branch = %s")
                params.append(branch_filter)
                
            if class_filter:
                conditions.append("f.class_year = %s")
                params.append(class_filter)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            query += " ORDER BY d.dept_id ASC, f.class_year ASC, s.name ASC"
            
            cursor.execute(query, tuple(params))
            records = cursor.fetchall()
            
            for r in records:
                b = r['branch']
                cy = r['class_year']
                if b not in fees_data:
                    fees_data[b] = {}
                if cy not in fees_data[b]:
                    fees_data[b][cy] = []
                fees_data[b][cy].append(r)
                
        except Exception as e:
            flash(f'Error fetching fees: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
    return render_template('view_fees.html', fees_data=fees_data, departments=departments, current_branch=branch_filter, current_class=class_filter)


@app.route('/api/fees_by_branch/<string:branch>')
def api_fees_by_branch(branch):
    # API alternative for filtering fees if needed dynamically
    conn = db_config.get_db_connection()
    fees = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT f.*, s.name as student_name 
                FROM fees f 
                JOIN student s ON f.student_id = s.student_id 
                WHERE f.branch = %s
            """, (branch,))
            fees = cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()
    return jsonify(fees)

@app.route('/export/students')
def export_students():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    if session.get('role') == 'faculty':
        conn = db_config.get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dept_id FROM faculty WHERE faculty_id = %s", (session.get('user_id'),))
            faculty_dept = cursor.fetchone()
            if faculty_dept:
                dept_id_filter = faculty_dept[0]
            else:
                dept_id_filter = request.args.get('dept_id')  # Fallback
            cursor.close()
            conn.close()
    else:
        dept_id_filter = request.args.get('dept_id')
        
    conn = db_config.get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('view_students'))
        
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT sr.*, d.dept_id
            FROM student_reports sr
            LEFT JOIN department d ON sr.branch = d.dept_name
        """
        params = []
        
        if dept_id_filter:
            query += " WHERE d.dept_id = %s "
            params.append(dept_id_filter)
            
        query += " ORDER BY d.dept_id ASC, COALESCE(sr.division, 'A') ASC, sr.name ASC "
        
        cursor.execute(query, tuple(params))
        students = cursor.fetchall()
        
        def generate():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(['Roll No', 'Name', 'PRN', 'Branch', 'Division', 'Email', 'Phone', 'Mother Name', 'Score', 'Attendance %'])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
            for s in students:
                score_str = f"{s['total_marks_obtained']} / {s['max_possible_marks']} ({s['percentage']:.2f}%)" if s.get('max_possible_marks') else "0 / 0"
                att_str = f"{s['attendance_percentage']:.2f}%" if s.get('attendance_percentage') else "0.00%"
                
                writer.writerow([
                    s.get('roll_no', ''), s.get('name', ''), s.get('prn', ''), s.get('branch', ''), s.get('division', ''), 
                    s.get('email', ''), s.get('phone', ''), s.get('mother_name', ''), score_str, att_str
                ])
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
                
        return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=students_report.csv'})
    finally:
        cursor.close()
        conn.close()

@app.route('/export/fees')
def export_fees():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    branch_filter = request.args.get('branch', '')
    class_filter = request.args.get('class_year', '')
    
    conn = db_config.get_db_connection()
    if not conn:
        flash('Database connection failed.', 'danger')
        return redirect(url_for('view_fees'))
        
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT f.*, s.name as student_name, s.prn, d.dept_id
            FROM fees f
            JOIN student s ON f.student_id = s.student_id
            LEFT JOIN department d ON f.branch = d.dept_name
        """
        params = []
        conditions = []
        
        if session.get('role') == 'faculty':
            cursor.execute("SELECT faculty.dept_id FROM faculty WHERE faculty.faculty_id = %s", (session.get('user_id'),))
            faculty_dept = cursor.fetchone()
            if faculty_dept:
                conditions.append("d.dept_id = %s")
                params.append(faculty_dept['dept_id'])
        elif branch_filter:
            conditions.append("f.branch = %s")
            params.append(branch_filter)
            
        if class_filter:
            conditions.append("f.class_year = %s")
            params.append(class_filter)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY d.dept_id ASC, f.class_year ASC, s.name ASC"
        
        cursor.execute(query, tuple(params))
        fees = cursor.fetchall()
        
        def generate():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(['Student Name', 'PRN', 'Branch', 'Class/Div', 'Total Fees', 'Amount Paid', 'Remaining Amount', 'Status', 'Last Payment Date'])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
            for row in fees:
                pay_date_str = row.get('payment_date').strftime('%Y-%m-%d') if row.get('payment_date') else ''
                
                writer.writerow([
                    row.get('student_name', ''), row.get('prn', ''), row.get('branch', ''), row.get('class_year', ''),
                    row.get('total_fees', ''), row.get('amount_paid', ''), row.get('remaining_amount', ''),
                    row.get('status', ''), pay_date_str
                ])
                yield data.getvalue()
                data.seek(0)
                data.truncate(0)
                
        return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=fees_report.csv'})
    finally:
        cursor.close()
        conn.close()

@app.errorhandler(500)
def internal_error(exception):
    import traceback
    import sys
    print("500 ERROR CAUGHT!", file=sys.stderr)
    traceback.print_exc()
    print("500 ERROR CAUGHT!", file=sys.stdout)
    traceback.print_exc(file=sys.stdout)
    return "500 Internal Server Error", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
