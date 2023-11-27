from flask import Flask, request, jsonify,make_response,send_file
import os
import jwt
import re
from datetime import date, datetime
import mysql.connector
import dotenv
dotenv.load_dotenv()
host = os.environ.get("host")

connection = mysql.connector.connect(host=host, username="root", password="muazzam*786", database="files")
my_cursor = connection.cursor()
# from model import *

app = Flask(__name__)


@app.route('/users/pdf/<uid>',methods=['POST'])
def upload_pdf(uid):
    print(request.files)
    print(request.files["pdf"])
    file = request.files["pdf"]
    print(file)
    file.save(f"uploaded_files/{file.filename}")
    finalFilePath = f"uploaded_files/{file.filename}"
    
    my_cursor.execute("use files")
    my_cursor.execute(f"insert into file (file_name) values ('{finalFilePath}')")
    my_cursor.execute(f"select file_name from file where id ='{uid}'")
    fileName = my_cursor.fetchone()
    connection.commit()
    return fileName[0]
    # return(token_generation())
@app.route('/uploaded_files/<filename>',methods=['GET'])
def getting_pdf(filename):
    return send_file(f"uploaded_files/{filename}")
    # return filename
if __name__ == '__main__':
    app.run(debug=True)    
