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

            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                # Insert submitted data into the database
                query = """
                    INSERT INTO submissions (name, username, email, phonenumber, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (name, session['username'], email, phone_number, 'Pending'))
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

# Approval Dashboard for Approvers
@app.route('/approval_dashboard', methods=['GET', 'POST'])
def approval_dashboard():
    if 'username' in session and session['role'] == 'approver':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Approve or reject submissions
            if request.method == 'POST':
                submission_id = request.form['submission_id']
                action = request.form['action']

                if action == 'approve':
                    # Retrieve the submission details
                    query = "SELECT * FROM submissions WHERE id = %s"
                    cursor.execute(query, (submission_id,))
                    submission = cursor.fetchone()

                    if submission:
                        # Move the submission to the all_users table
                        insert_query = """
                            INSERT INTO all_users (name, username, email, phonenumber)
                            VALUES (%s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            submission['name'], 
                            submission['username'], 
                            submission['email'], 
                            submission['phonenumber']
                        ))
                        
                        # Delete the entry from the submissions table
                        delete_query = "DELETE FROM submissions WHERE id = %s"
                        cursor.execute(delete_query, (submission_id,))
                        
                        conn.commit()

                elif action == 'reject':
                    # Update the status to 'Rejected' in the submissions table
                    update_query = "UPDATE submissions SET status = %s WHERE id = %s"
                    cursor.execute(update_query, ('Rejected', submission_id))
                    conn.commit()

            # Retrieve all pending submissions
            query = "SELECT * FROM submissions WHERE status = 'Pending'"
            cursor.execute(query)
            submissions = cursor.fetchall()

            return render_template('approval_dashboard.html', submissions=submissions, username=session['username'])
        except Exception as e:
            return str(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return redirect(url_for('login'))

#Check the Submission Status
# Route to View Submitted Data for Data User
@app.route('/my_submissions', methods=['GET'])
def my_submissions():
    if 'username' in session and session['role'] == 'datauser':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Retrieve submissions of the current datauser
            query = "SELECT * FROM submissions WHERE username = %s"
            cursor.execute(query, (session['username'],))
            submissions = cursor.fetchall()
            
            return render_template('my_submissions.html', submissions=submissions)
        
        except Exception as e:
            return str(e)
        
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    else:
        return redirect(url_for('login'))

#Check all users from Approver
# Route for Approver Dashboard (View all approved users)
@app.route('/approver_dashboard', methods=['GET'])
def approver_dashboard():
    if 'username' in session and session['role'] == 'approver':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)

            # Retrieve all approved users from the 'all_users' table
            query = "SELECT * FROM all_users"
            cursor.execute(query)
            all_users = cursor.fetchall()

            return render_template('approver_dashboard.html', all_users=all_users, username=session['username'])
        
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
