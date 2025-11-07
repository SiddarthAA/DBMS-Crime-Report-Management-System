from flask import Flask, render_template, request, redirect, session, url_for, flash
import pymysql
from datetime import datetime,date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'QwerTy07',
    'database': 'CRMS'
}

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='QwerTy07',
        database='CRMS',
        cursorclass=pymysql.cursors.DictCursor  # <-- use DictCursor
    )

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash("Unauthorized access!", "danger")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_by_id(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name, email, role, phone_number, address, created_at AS joined_on FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def update_user(user_id, name, email, phone_number, address):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users
            SET name = %s, email = %s, phone_number = %s, address = %s
            WHERE user_id = %s
        """, (name, email, phone_number, address, user_id))
        conn.commit()
    except pymysql.MySQLError as e:
        conn.rollback()
        flash("Error updating user: " + str(e), 'danger')
    finally:
        cursor.close()
        conn.close()

def calculate_age(dob):
    today = date.today()  # Use date.today() for today's date
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Plain text password
        phone_number = request.form['phone_number']
        address = request.form['address']
        role = request.form['role']

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(""" 
                INSERT INTO users (name, email, password_hash, role, phone_number, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, password, role, phone_number, address))
            conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except pymysql.MySQLError as e:
            flash('Error during signup: ' + str(e), 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT user_id, name, password_hash, role FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and user['password_hash'] == password:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))

        flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['name'], role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/citizen/report-crime', methods=['GET', 'POST'])
@role_required('citizen')
def report_crime():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        crime_type = request.form['crime_type']
        location = request.form['location']
        reported_by = session['user_id']

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO crimes (title, description, crime_type, location, reported_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, description, crime_type, location, reported_by))
            db.commit()
            flash("Crime reported successfully.", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.rollback()
            flash(f"Error reporting crime: {e}", "danger")
        finally:
            db.close()

    return render_template('citizen_report_crime.html')

@app.route('/citizen/view-status')
@role_required('citizen')
def view_status():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT crime_id, title, crime_type, location, date_reported
        FROM crimes
        WHERE reported_by = %s
    """, (user_id,))
    crimes = cursor.fetchall()
    db.close()
    return render_template('citizen_view_status.html', crimes=crimes)

@app.route('/officer/crimes')
@role_required('officer')
def view_assigned_crimes():
    officer_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT c.crime_id, c.title, c.crime_type, c.location, c.date_reported, u.name AS officer_name
        FROM crimes c
        LEFT JOIN case_assignments ca ON c.crime_id = ca.crime_id
        LEFT JOIN users u ON ca.officer_id = u.user_id
        WHERE ca.officer_id = %s
    """, (officer_id,))
    crimes = cursor.fetchall()

    for crime in crimes:
        cursor.execute("SELECT description FROM evidence WHERE crime_id = %s", (crime['crime_id'],))
        crime['evidence'] = cursor.fetchall()

    db.close()
    return render_template('officer_crimes.html', crimes=crimes)

@app.route('/admin/users')
@role_required('admin')
def manage_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id, name, email, role FROM users")
    users = cursor.fetchall()
    db.close()
    return render_template('admin_users.html', users=users)

@app.route('/admin_users')
def admin_users():
    if session.get('role') != 'admin':
        flash('Access denied.')
        return redirect(url_for('dashboard'))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/assignments', methods=['GET', 'POST'])
@role_required('admin')
def assign_officers():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        crime_id = request.form['crime_id']
        officer_id = request.form['officer_id']
        
        cursor.execute("SELECT * FROM case_assignments WHERE crime_id = %s", (crime_id,))
        exists = cursor.fetchone()

        try:
            if exists:
                cursor.execute("""
                    UPDATE case_assignments SET officer_id = %s WHERE crime_id = %s
                """, (officer_id, crime_id))
            else:
                cursor.execute("""
                    INSERT INTO case_assignments (crime_id, officer_id) VALUES (%s, %s)
                """, (crime_id, officer_id))
            db.commit()
            flash("Officer assignment saved.", "success")
        except Exception as e:
            db.rollback()
            flash(str(e), "danger")

    cursor.execute("""
        SELECT 
            c.crime_id, c.title, c.crime_type, c.location, 
            u.name AS officer_name
        FROM crimes c
        LEFT JOIN case_assignments ca ON c.crime_id = ca.crime_id
        LEFT JOIN users u ON ca.officer_id = u.user_id
    """)
    crimes = cursor.fetchall()

    cursor.execute("SELECT user_id, name FROM users WHERE role = 'officer'")
    officers = cursor.fetchall()

    db.close()
    return render_template('admin_assignments.html', crimes=crimes, officers=officers)

@app.route('/admin/reports')
@role_required('admin')
def view_reports():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT r.report_id, c.title, u.name, r.generated_at
        FROM reports r
        JOIN crimes c ON r.crime_id = c.crime_id
        JOIN users u ON r.generated_by = u.user_id
    """)
    reports = cursor.fetchall()
    db.close()
    return render_template('admin_reports.html', reports=reports)

@app.route('/officer/witnesses')
@role_required('officer')
def officer_witnesses():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT w.witness_id, w.name, w.contact_info, w.statement,
               c.title AS crime_title
        FROM witnesses w
        JOIN crimes c ON w.crime_id = c.crime_id
        JOIN case_assignments ca ON c.crime_id = ca.crime_id
        WHERE ca.officer_id = %s
    """, (session['user_id'],))
    witnesses = cursor.fetchall()

    db.close()
    return render_template('officer_witnesses.html', witnesses=witnesses)

@app.route('/officer/add_witness', methods=['GET', 'POST'])
@role_required('officer')
def add_witness():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        crime_id = request.form['crime_id']
        name = request.form['name']
        contact_info = request.form['contact_info']
        statement = request.form['statement']
        try:
            cursor.execute("""
                INSERT INTO witnesses (crime_id, name, contact_info, statement)
                VALUES (%s, %s, %s, %s)
            """, (crime_id, name, contact_info, statement))
            db.commit()
            flash('Witness added.', 'success')
            return redirect(url_for('officer_witnesses'))
        except Exception as e:
            db.rollback()
            flash(str(e), 'danger')

    cursor.execute("""
        SELECT c.crime_id, c.title 
        FROM crimes c
        JOIN case_assignments ca ON c.crime_id = ca.crime_id
        WHERE ca.officer_id = %s
    """, (session['user_id'],))
    crimes = cursor.fetchall()

    db.close()
    return render_template('add_witness.html', crimes=crimes)

@app.route('/officer/delete_witness/<int:witness_id>', methods=['POST'])
@role_required('officer')
def delete_witness(witness_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM witnesses WHERE witness_id = %s", (witness_id,))
        db.commit()
        flash('Witness deleted.', 'success')
    except Exception as e:
        db.rollback()
        flash(str(e), 'danger')
    finally:
        db.close()

    return redirect(url_for('officer_witnesses'))

@app.route('/officer_criminals')
@role_required('officer')
def officer_criminals():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("SELECT criminal_id, name, dob, crime_history, last_arrest_date FROM criminals")
        criminals = cursor.fetchall()

        criminals_with_age = []
        for criminal in criminals:
            dob = criminal['dob']
            age = calculate_age(dob) if dob else 'N/A'
            criminal_with_age = dict(criminal)
            criminal_with_age['age'] = age
            criminals_with_age.append(criminal_with_age)

    finally:
        db.close()

    return render_template('officer_criminals.html', criminals=criminals, calculate_age=calculate_age)

@app.route('/add_criminal', methods=['GET', 'POST'])
@role_required('officer')
def add_criminal():
    if request.method == 'POST':
        name = request.form['name']
        alias = request.form['alias']
        dob = request.form['dob']
        crime_history = request.form['crime_history']
        last_arrest_date = request.form['last_arrest_date']

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "INSERT INTO criminals (name, alias, dob, crime_history, last_arrest_date) VALUES (%s, %s, %s, %s, %s)",
                (name, alias, dob, crime_history, last_arrest_date)
            )
            db.commit()
            return redirect(url_for('officer_criminals'))

        finally:
            db.close()

    return render_template('add_criminal.html')

@app.route('/delete_criminal/<int:criminal_id>', methods=['GET', 'POST'])
@role_required('officer')
def delete_criminal(criminal_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM criminals WHERE criminal_id = %s", (criminal_id,))
        db.commit()

    finally:
        db.close()

    return redirect(url_for('officer_criminals'))

@app.route('/profile')
@login_required
def view_profile():
    user = get_user_by_id(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('login'))
    return render_template('view_profile.html', user=user)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone_number']
        address = request.form['address']

        cursor.execute("""
            UPDATE users 
            SET name = %s, email = %s, phone_number = %s, address = %s 
            WHERE id = %s
        """, (name, email, phone, address, user_id))
        conn.commit()
        conn.close()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users'))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return render_template('edit_user.html', user=user)
    else:
        flash('User not found.', 'error')
        return redirect(url_for('manage_users'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    app.run(debug=True)