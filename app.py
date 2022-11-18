import csv
import os
from functools import wraps

import pandas as pd
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
UPLOAD_FOLD = 'static/files/'

app.secret_key = 'secret123'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLD'] = UPLOAD_FOLD
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rationale-'
app.config['MYSQL_DB'] = 'db_sample'
app.config['MYSQL_DATABASE_PORT'] = '5000'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

ALLOWED_EXTENSIONS = set(
    ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', ''])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Registration


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    # if 'logged_in' in session:
    #     return redirect('home')
    if request.method == 'POST':
        f = request.files['file']
        f1 = (secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f1))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f1)
        name = request.form["uname"]
        email = request.form["email"]
        pwd = request.form["upass"]
        dep = request.form["department"]
        con = request.form["contact"]
        emergency = request.form["emergency"]
        cur = mysql.connection.cursor()
        cur.execute("Insert into users(UNAME,UPASS,EMAIL,PICTURE,DEPARTMENT,FILEPATH,CONTACT,EMERGENCY) values(%s,%s,%s,%s,%s,%s,%s,%s)",
                    (name, pwd, email, f1, dep, file_path, con, emergency))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successful. You can now login here.', 'success')
        return redirect('login')
    return render_template("reg.html")

# Administrative Page


@app.route('/admin')
def admin():
    if session['department'] == 'Administrator':
        print("abkjewjk")
        users = getallusers()
        print(users)
        return render_template("admin.html", data=users)


def getallusers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM db_sample.users")
    rows = cur.fetchall()
    cur.close()
    return rows

# HR Login Page


@app.route('/hr')
def hr():
    if session['department'] == 'HR':
        users = getemployees()
        return render_template("hr.html", data=users)


def getemployees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM db_sample.users WHERE DEPARTMENT='Employee' ")
    rows = cur.fetchall()
    cur.close()
    return rows


@app.route('/product/<uid>')
def product(uid):
    con = mysql.connection.cursor()
    con.execute("SELECT * FROM db_sample.users WHERE UID=%s", (uid,))
    details = con.fetchall()
    con.close()
    return render_template("product.html", abcd=details[0])


@app.route('/update_employee_details', methods=['POST'])
def update_employee_details():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        dep = request.form["department"]
        con = request.form["contact"]
        emergency = request.form["emergency"]
        uid = request.form["uid"]
        cur = mysql.connection.cursor()
        sql = "UPDATE users SET EMAIL = %s, UPASS = %s, CONTACT = %s, DEPARTMENT = %s, EMERGENCY = %s WHERE UID = %s"
        val = (email, pwd, con, dep, emergency, uid)
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.close()
    return redirect('hr')

# delete employee records


@app.route("/deleteemployee/<uid>")
def deleteemployee(uid):
    # if request.method=='GET':
    con = mysql.connection.cursor()
    sql = "DELETE from users WHERE UID = %s"
    val = (uid,)
    con.execute(sql, val)
    mysql.connection.commit()
    return redirect(url_for('hr'))


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    conn = mysql.connection.cursor()
    csv_data = csv.reader(open('DBO.csv'))
    for row in csv_data:
        conn.execute(
            "INSERT INTO db_sample.users (UNAME, EMAIL, CONTACT, DEPARTMENT, EMERGENCY) VALUES (%s,%s,%s,%s,%s)", row)
        print(row)
        mysql.connection.commit()
        print("done!")
    conn.close()
    return redirect(url_for('home'))


@app.route("/home", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        f = request.files['file']
        f1 = (secure_filename(f.filename))
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f1))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f1)
        cur = mysql.connection.cursor()
        sql = "UPDATE users SET FILEPATH = %s WHERE UNAME = %s"
        val = (file_path, session['username'])
        cur.execute(sql, val)
        mysql.connection.commit()
        cur.close()
        session['file_path'] = file_path
    return render_template('home.html')

# Login Page


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'logged_in' in session:
        return redirect('home')

    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["upass"]
        cur = mysql.connection.cursor()
        cur.execute(
            "select * from users where EMAIL=%s and UPASS=%s", (email, pwd))
        data = cur.fetchone()
        if data:
            session['logged_in'] = True
            session['uid'] = data["UID"]
            session['username'] = data["UNAME"]
            session['email'] = data["EMAIL"]
            session['department'] = data["DEPARTMENT"]
            session['contact'] = data["CONTACT"]
            session['emergency'] = data["EMERGENCY"]
            session['file_path'] = data["FILEPATH"]
            flash('Login Successful', 'success')
            return redirect('home')
        else:
            flash('Invalid Credentials. Try Again', 'danger')
    return render_template("login.html")

# Holding an active user session


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized Access, Please Login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout


@app.route("/logout")
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
