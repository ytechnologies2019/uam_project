from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

# Database Configuration
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123abc!@#',
    'database': 'UAM_Project'
}

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Ensure session security

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check user credentials
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                session['username'] = user['username']
                session['role'] = user['role']
                
                # Redirect users based on their role
                if user['role'] == 'datauser':
                    return redirect(url_for('data_submit'))
                elif user['role'] == 'approver':
                    return redirect(url_for('approval_dashboard'))
                elif user['role'] == 'auditor':
                    return "Auditor functionality is under development."
            else:
                return render_template('login.html', error="Invalid credentials!")
        except Exception as e:
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html')

# Data Submission Page
@app.route('/data_submit', methods=['GET', 'POST'])
def data_submit():
    if 'username' in session and session['role'] == 'datauser':
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            phone_number = request.form['phone_number']
            department = request.form['department']

            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                # Insert submitted data into the database
                query = """
                    INSERT INTO submissions (name, username, email, phonenumber, department, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, session['username'], email, phone_number, department, 'Pending'))
                conn.commit()

                return render_template('data_submit.html', username=session['username'], message="Data submitted successfully!")
            except Exception as e:
                return str(e)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        return render_template('data_submit.html', username=session['username'])
    else:
        return redirect(url_for('login'))

# View Submitted Data (Status) by Data Users
@app.route('/submitted_data')
def submitted_data():
    if 'username' in session and session['role'] == 'datauser':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Retrieve data submitted by the logged-in user
            query = "SELECT * FROM submissions WHERE username = %s"
            cursor.execute(query, (session['username'],))
            submissions = cursor.fetchall()

            return render_template('submitted_data.html', submissions=submissions, username=session['username'])
        except Exception as e:
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return redirect(url_for('login'))

# View All Existing Users for Data Users
@app.route('/all_existing_users')
def all_existing_users():
    if 'username' in session and session['role'] == 'datauser':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Retrieve all approved users
            query = "SELECT * FROM all_users"
            cursor.execute(query)
            users = cursor.fetchall()

            return render_template('all_existing_users.html', users=users, username=session['username'])
        except Exception as e:
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return redirect(url_for('login'))

# Approval Dashboard for Approvers
# Approval Dashboard for Approvers
@app.route('/approval_dashboard', methods=['GET', 'POST'])
def approval_dashboard():
    if 'username' in session and session['role'] == 'approver':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Handle form submission for approval/rejection
            if request.method == 'POST':
                submission_id = request.form['submission_id']
                action = request.form['action']
                
                if action == 'approve':
                    # Insert approved submission into 'all_users' table
                    approve_query = """
                        INSERT INTO all_users (name, username, email, phonenumber, department)
                        SELECT name, username, email, phonenumber, department
                        FROM submissions
                        WHERE id = %s
                    """
                    cursor.execute(approve_query, (submission_id,))
                    conn.commit()

                    # Update status in 'submissions' table to 'Approved'
                    update_query = """
                        UPDATE submissions
                        SET status = 'Approved'
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (submission_id,))
                    conn.commit()

                elif action == 'reject':
                    # Update status in 'submissions' table to 'Rejected'
                    update_query = """
                        UPDATE submissions
                        SET status = 'Rejected'
                        WHERE id = %s
                    """
                    cursor.execute(update_query, (submission_id,))
                    conn.commit()

            # Handle department filtering
            selected_department = request.args.get('department', 'All')  # Default to 'All'
            
            # Filter submissions based on department selection
            if selected_department == 'All':
                query = "SELECT * FROM submissions WHERE status = 'Pending'"
                cursor.execute(query)
            else:
                query = "SELECT * FROM submissions WHERE status = 'Pending' AND department = %s"
                cursor.execute(query, (selected_department,))
            submissions = cursor.fetchall()

            # Retrieve approved users with filtering if needed
            if selected_department == 'All':
                query = "SELECT * FROM all_users"
                cursor.execute(query)
            else:
                query = "SELECT * FROM all_users WHERE department = %s"
                cursor.execute(query, (selected_department,))
            approved_users = cursor.fetchall()

            return render_template('approval_dashboard.html', 
                                   submissions=submissions, 
                                   approved_users=approved_users,
                                   selected_department=selected_department,
                                   username=session['username'])

        except Exception as e:
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return redirect(url_for('login'))



# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
