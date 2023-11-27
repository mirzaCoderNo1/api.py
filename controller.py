from flask import Flask, request, jsonify,make_response
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







if __name__ == '__main__':
    app.run(debug=True)    
