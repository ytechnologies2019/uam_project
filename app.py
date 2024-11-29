from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pymysql

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
app.secret_key = 'supersecretkey'  # Ensure that you have a secret key for session management

# Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Check credentials
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                # Store user role in session
                session['username'] = user['username']
                session['role'] = user['role']
                
                # Debugging output
                print(f"User {username} logged in with role: {user['role']}")
                
                # Redirect based on role
                if user['role'] == 'datauser':
                    return redirect(url_for('data_submit'))
                elif user['role'] == 'approver':
                    return redirect(url_for('approval_dashboard'))
                elif user['role'] == 'auditor':
                    return "Redirect to auditor page (to be implemented)"
            else:
                print("Invalid credentials")
                return render_template('login.html', error="Invalid credentials!")
        except Exception as e:
            print(f"Error: {str(e)}")
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html')

# Data Submit Page
@app.route('/data_submit', methods=['GET', 'POST'])
def data_submit():
    if 'username' in session and session['role'] == 'datauser':
        if request.method == 'POST':
            # Add data to the database with status "Pending"
            data = request.form['data']
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                
                query = "INSERT INTO submissions (name, username, email, phonenumber, status) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (data, session['username'], "example@example.com", "1234567890", "Pending"))
                conn.commit()
                return render_template('data_submit.html', username=session['username'], message="Data submitted successfully!")
            except Exception as e:
                print(f"Error: {str(e)}")
                return str(e)
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
        return render_template('data_submit.html', username=session['username'])
    else:
        print("User is not logged in or has an invalid role")
        return redirect(url_for('login'))

# Approval Dashboard for Approvers
@app.route('/approval_dashboard', methods=['GET', 'POST'])
def approval_dashboard():
    if 'username' in session and session['role'] == 'approver':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            if request.method == 'POST':
                submission_id = request.form['submission_id']
                action = request.form['action']

                # Update the status based on approver action
                if action == 'approve':
                    status = 'Approved'
                elif action == 'reject':
                    status = 'Rejected'
                else:
                    return redirect(url_for('approval_dashboard'))

                query = "UPDATE submissions SET status = %s WHERE id = %s"
                cursor.execute(query, (status, submission_id))
                conn.commit()

            # Fetch all pending submissions
            query = "SELECT * FROM submissions WHERE status = 'Pending'"
            cursor.execute(query)
            submissions = cursor.fetchall()

            return render_template('approval_dashboard.html', submissions=submissions, username=session['username'])
        except Exception as e:
            print(f"Error: {str(e)}")
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        print("User is not logged in or has an invalid role")
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
