from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import db_config
import os

app = Flask(__name__)
# Use a static secret key so dev-server reloads don't log the user out
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_static_key_for_development')

# Initialize DB View on startup
db_config.create_student_reports_view()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple admin login (can be adapted to query the 'admin' table)
        if username == 'Mohit' and password == 'Mohit123':
            session['logged_in'] = True
            session['role'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif username == 'Parth' and password == 'Parth123':
            session['logged_in'] = True
            session['role'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif username == 'Kaustubh' and password == 'Kaustubh123':
            session['logged_in'] = True
            session['role'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            conn = db_config.get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                # Note: Adjust column names if different in the actual 'admin' table
                # Handling basic fallback if tables have different schema
                try:
                    cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
                    admin = cursor.fetchone()
                    if admin:
                        session['logged_in'] = True
                        session['role'] = 'admin'
                        flash('Login successful!', 'success')
                        return redirect(url_for('dashboard'))
                except Exception as e:
                    print(f"DB Auth Error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            
            flash('Invalid credentials. Please try again.', 'danger')
            
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
    
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM student")
            students_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM faculty")
            faculty_count = cursor.fetchone()[0]
        except Exception as e:
            print(f"Dashboard Query Error: {e}")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('dashboard.html', students_count=students_count, faculty_count=faculty_count)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
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
    
    dept_id_filter = request.args.get('dept_id')
    
    conn = db_config.get_db_connection()
    reports = {}
    departments = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch departments for the filter dropdown
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
            
    return render_template('add_marks.html', departments=departments)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
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
            
            # Fetch detailed subject-level marks
            cursor.execute("""
                SELECT s.subject_name, m.internal_marks, m.external_marks, m.total, m.grade
                FROM marks m
                JOIN subject s ON m.subject_id = s.subject_id
                WHERE m.student_id = %s
            """, (id,))
            marks_details = cursor.fetchall()
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
