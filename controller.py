from flask import Flask, request, jsonify,make_response,send_file
import os
import jwt
import re
from datetime import date, datetime
import mysql.connector
import dotenv
dotenv.load_dotenv()
from model import *

app = Flask(__name__)


@app.route('/users/signup',methods=['POST'])
def createing_token():
    return(token_generation())
    

@app.route('/users/login',methods =['GET'])
def veladiting_token():
    return(token_validation())

@app.route('/api/items', methods=['GET'])
def getting_data_database():
    return(data_from_database())
    
    
    
@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return(get_one_item_from_database_using_id(item_id))




@app.route('/api/items', methods=['POST'])
def add_item():
    return(add_one_item_to_database())






@app.route('/api/items/<int:item_id>', methods=['PUT'])
def put_item(item_id):
    return(update_item(item_id))






@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    return(delete_item_from_database(item_id))



@app.route('/uploaded_files/<filename>',methods=['GET'])
def getting_pdf(filename):
    return send_file(f"uploaded_files/{filename}")



@app.route("/user/login", methods=["GET"])
def user_login():
    return(bearer_token_validation())


@app.route('/user/pdf',methods=['POST'])
def upload_pdf():
    # print(uid)
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return make_response("Authorization header is missing", 401)
    else:
        token_prefix = "Bearer "
        token = authorization_header.split()
        print(token[1])
        print(type(authorization_header))
        try:    
            decoded = jwt.decode(token[1],security_key,algorithms='HS256')
        except:
            return jsonify({"Message":"Invalid token"})
        email_db_checker = decoded['email']
        print(email_db_checker)
        try:
            my_cursor.execute(f"use {databasename}")
            my_cursor.execute(f"select email from {table_name} where email = '{email_db_checker}' ")
            email_db = my_cursor.fetchall()
            print(email_db[0][0])
            connection.commit()
            if email_db is None:
                return jsonify({"Message":"Invalid Bearer Token"}),401
            if email_db[0][0] != email_db_checker:
                # return jsonify({"Message":"Invalid user id"}),400
                print(email_db[0][0])
        except:
            return jsonify({"Message":""}),400
        try:
            
            file = request.files['pdf']
            # if file is None:
            #     return ("no file found")
            # return(type(file))
            file_path = f"uploaded_files/{file.filename}" 
            file.save(file_path)
            print(file.filename)
            print(file_path)
            my_cursor.execute(f"use {databasename}")
            my_cursor.execute(f"update  {table_name} set pdf = '{file_path}' where email = '{email_db_checker}'")
            connection.commit()
            
            return(file_path)
        except:
            return jsonify({"Message":"PDF not found"}),404


if __name__ == '__main__':
    app.run(debug=True)    
