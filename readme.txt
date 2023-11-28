from flask import Flask, request, jsonify,make_response,send_file
import os
import jwt
import re
from datetime import date, datetime
import mysql.connector
import dotenv
dotenv.load_dotenv()
user can upload pdf directly with out user id 
user can use bearer token  for authentication

