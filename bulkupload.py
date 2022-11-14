import os
from flask import Flask, request, render_template, redirect, url_for,flash, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from script import process_csv
from flask_mysqldb import MySQL 
import app


app.secret_key='secret123'
app.config['UPLOAD_FOLDER'] = "static/files"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Admin101-'
app.config['MYSQL_DB']='db_sample'
app.config['MYSQL_DATABASE_PORT'] = '5000'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
  print("ccccd")
  if request.method == 'POST':
    print("fgggggg")
    file = request.files['file']
    if file and allowed_file(file.filename):   
      filename = secure_filename(file.filename)
      new_filename = f'{filename.split(".")[0]}_{str(datetime.now())}.csv'
      save_location = os.path.join('input', new_filename)
      file.save(save_location)
      con= mysql.connection.cursor()
      con.execute("Insert into db_sample.users(UNAME,EMAIL,UPASS,CONTACT,DEPARTMENT,EMERGENCY,PICTURE,FILEPATH) values(?,?,?,?,?,?,?,?)", ())
      con.commit()
      flash("Excel Sheet UploadSuccessfully","success")
      output_file = process_csv(save_location)
      cur=con.cursor()
      con.execute("SELECT * from db_sample.users")
      data = cur.fetchall()
      con.close()
      return render_template("hr.html", data=data)       #return send_from_directory('output', output_file)
  return render_template('hr.html', data=data)



@app.route('/download')
def download():
  return render_template('download.html', files=os.listdir('output'))



@app.route('/download/<filename>')
def download_file(filename):
  return send_from_directory('output', filename)

