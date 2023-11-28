from flask import Flask, request, jsonify,make_response
import jwt
import re
from datetime import date, datetime
import mysql.connector
import dotenv
import os
dotenv.load_dotenv()
host = os.environ.get("host")
password = os.environ.get("password")
user_name = os.environ.get("user_name")
databasename = os.environ.get("database_name")
table_name = os.environ.get("table_name")
security_key = os.environ.get("security_key")

connection = mysql.connector.connect(host=host, username=user_name, password=password, database=databasename)
my_cursor = connection.cursor()

my_cursor.execute(f"USE {databasename}")

def deleting_table_users():
    my_cursor.execute(f"drop table {table_name}")
    connection.commit()
    
def creating_tabel_users():
    my_cursor.execute(f"create table {table_name} (email varchar(50),password varchar(50))")

def get_items_from_database():
    my_cursor.execute(f"SELECT id , description, status , priority, delivery_date,start_date FROM {table_name}")
    columns = [col[0] for col in my_cursor.description]
    return columns, my_cursor.fetchall()
def add_item_to_database(item_data):
    insert_statement = f"INSERT INTO {table_name} (description, status, delivery_date, priority) VALUES (%s, %s, %s, %s)"

    item_tuple = (item_data["description"], item_data["status"], item_data["delivery_date"], item_data["priority"])

    my_cursor.execute(insert_statement, item_tuple)

    connection.commit()

def token_generation():
    user_data= request.get_json()
    email_condition ="^[a-z _]+[\._]?[a-z A-z 0-9]+[@]\w+[.]\w{2,3}$"
    my_cursor.execute(f"use {databasename}")
    if 'email' not in user_data:
        return jsonify({"Message":"Email is required for signup"}),400
    if not re.search(email_condition,user_data['email']):
        return jsonify({"Message":"Enter a valid email"}),400
    else:
        pass
    
    if 'password' not in user_data:
        return jsonify({"Message":"We need password for signup"}),400

    my_cursor.execute(f"SELECT email from {table_name} where email ='{user_data['email']}'")
    email_database = my_cursor.fetchall()
    connection.commit()

    if (email_database == []) :
        my_cursor.execute(f"insert into {table_name} (email,password) values ('{user_data["email"]}','{user_data["password"]}')")
        connection.commit()
        print(email_database)
    else:
        return jsonify({"Message":"User already exists"})

    payload = {
    'email': user_data['email'],
    # Assuming 'id' is a unique identifier for the user
}

    output = jwt.encode(payload,security_key,algorithm="HS256")
    return jsonify({"token":output}),200



def token_validation():
    token_checker = request.get_json()
    if ('token' not in token_checker):
        return jsonify({"Message":"token not found"})
    try:    
        decoded = jwt.decode(token_checker['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"})
    email_db_checker = decoded['email']
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')
    # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}' and password = '{token_checker['password']}' ")
    result = my_cursor.fetchone()
    connection.commit()
    if (result is  None):
        return jsonify({"Message":"Invalid token or password"}),404
    
    password = result[0]
    if (password != token_checker['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:
        return jsonify({"Message":"User login successfully"}),200
    

def data_from_database():
    columns, items = get_items_from_database()
    token_checker = request.get_json()
    if ('token' not in token_checker):
        return jsonify({"Message":"token not found"})
    
    # if (token_checker['token'] or token_checker['password'])is None:
    if 'token' not in token_checker or 'password' not in token_checker:
        return jsonify({"Message":"We need token and password"}),400
    else:
        pass
    try:
        decoded = jwt.decode(token_checker['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"}),400
    email_db_checker = decoded['email']
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')
    # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}'")
    result = my_cursor.fetchall()
    connection.commit()
    if (result is  None):
        return jsonify({"Message":"User not found"}),404
    
    password_token = result[0]
    print(password_token[0])
    if (password_token[0] != token_checker['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:
        
        
    

    # return jsonify(columns,items)
# def get_items():
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=10)
        status = request.args.get('status', type=str)
        priority = request.args.get('priority', type=str)
        get_by_delivery_date = request.args.get('delivery_date', type=str)
        get_by_date = request.args.get('start_date',type=str)

        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages

        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        
        # Convert get_by_delivery_date and get_by_date to date objects
        get_by_delivery_date = datetime.strptime(get_by_delivery_date, "%d-%m-%y").date() if get_by_delivery_date else None
        get_by_date = datetime.strptime(get_by_date, "%d-%m-%y").date() if get_by_date else None
        filtered_items = [dict(zip(columns, item)) for item in items if
            (status is None or item[2] == status) and
            (priority is None or item[3] == priority) and
            # (get_by_delivery_date is None or datetime.strptime(item[0], "%d-%m-%y").date() == get_by_delivery_date) and
            (get_by_delivery_date is None or datetime.strptime(item[4], "%d-%m-%y").date() == get_by_delivery_date) and
            # (get_by_date is None or get_by_date == datetime.strptime(item[5], "%d-%m-%y").date())
            (get_by_date is None or datetime.strptime(item[5], "%d-%m-%y").date() == get_by_date)
            
            # (get_by_date is None or datetime.strptime(item[5], "%d-%m-%y").date() == get_by_date)
        ]
        
        if any(item for item in filtered_items) is True:
            print(type(items[0][5]))
                # total_items = len(items)
            total_items = len(filtered_items)
            total_pages = (total_items + per_page - 1) // per_page  # Calculate total pages
            if page < 1:
                page = 1
            if page > total_pages:
                page = total_pages

            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_items)
            # if any(item for item in filtered_items) is not True:
            #     return jsonify({"Message":"Invalid input"}),400
            
            paginated_items = filtered_items[start_idx:end_idx]

            prev_page = page - 1 if page > 1 else None
            next_page = page + 1 if page < total_pages else None
            nav_bar = {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page,
                'prev_page': prev_page,
                'next_page': next_page
            }

            response_data = [
                {
                    'Items': paginated_items,
                    "Details": nav_bar
                }
            ]

            return jsonify(response_data), 200    
        else:
            nav_bar = {
                'total_items': 0,
                'total_pages': 0,
                'current_page': page,
                'per_page': per_page,
                'prev_page': None,
                'next_page': None
            }
            response_data=[
                {
                    "Items":[],
                    "Details":nav_bar
                }
            ]
            return jsonify(response_data)
    return('ok')        
def get_one_item_from_database_using_id(item_id):
    
    columns, items = get_items_from_database()
    token_checker = request.get_json()
    if ('token' not in token_checker):
        return jsonify({"Message":"token not found"}),400
    try:
        decoded = jwt.decode(token_checker['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"}),400
    email_db_checker = decoded['email']
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')
    # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}' and id = '{item_id}' ")
    result = my_cursor.fetchone()
    connection.commit()
    if (result is  None):
        return jsonify({"Message":"User not accessed to this item"}),404
    
    password = result[0]
    if (password != token_checker['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:
        item_to_get = next((dict(zip(columns, item)) for item in items if item[0] == item_id), None)

        if item_to_get is None:
            return jsonify({"message": "Item not found"}), 404

        return jsonify(item_to_get), 200



def add_one_item_to_database():
    data = request.get_json()
    item_data = request.get_json()
    # token_checker = request.get_json()
    if ('token' not in data):
        return jsonify({"Message":"token not found"}),400
    try:
        decoded = jwt.decode(data['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"}),400
    email_db_checker = decoded['email']
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')
    # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}' and password = '{data['password']}' ")
    result = my_cursor.fetchone()
    connection.commit()
    if (result is  None):
        return jsonify({"Message":"User not found"}),404
    
    password = result[0]
    if (password != data['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:
        if not all(key in data for key in ["description", "status", "delivery_date"]):
            return jsonify({"message": "Required fields:  description, status, delivery_date"}), 400

        status_condition = r"^(completed|inprogress|pending)$"
        if not re.search(status_condition, data["status"]):
            return jsonify({"Message": "Enter status only completed, inprogress and pending"}), 400

    #     # Use a regular expression to validate the delivery_date format
        date_format_condition = r"^(0[1-9]|[12][0-9]|3[01])\-(0[1-9]|1[0-2])\-\d{2}$"
        if not re.search(date_format_condition, data["delivery_date"]):
            return jsonify({"Message": "Enter delivery_date in this format (dd-mm-yy)"})
        

        priority_condition = r"^(normal|low|high)$"
        if "priority" not in data:
            data['priority'] = "normal"
        elif not re.search(priority_condition, data["priority"]):
            return jsonify({"Message": "The priority can only be high, low, or normal"}), 400
        if "start_date" not in data:
            pass
        else:
            my_cursor.execute(f"insert into {table_name}  (start_date,delivery_date,priority,status,description,email,password) values ('{data['start_date']}','{data['delivery_date']}','{data['priority']}','{data['status']}','{data['description']}','{email_db_checker}','{data['password']}')")
        # add_item_to_database(item_data)
        # my_cursor.execute(f"update  users set email = '{email_db_checker}'where password = '{data['password']}'")
        my_cursor.fetchall()
        connection.commit()
        
        # return jsonify(add_item_to_database(data))
        return jsonify({"Message":"Data posted successfully"})




def update_item(item_id):
    # item__id = request.json('item_id')
    
    
    # Database query to fetch items
    item_data = request.get_json()
    
    columns, items = get_items_from_database()
    token_checker = request.get_json()
    if ('token' not in token_checker):
        return jsonify({"Message":"token not found"})
    try:
        decoded = jwt.decode(token_checker['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"}),400
    email_db_checker = decoded['email']
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')
    # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}' and password = '{token_checker['password']}' ")
    result = my_cursor.fetchone()
    connection.commit()
    if (result is  None):
        return jsonify({"Message":"Invalid token or password"}),404
    
    password = result[0]
    if (password != token_checker['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:

    # updated_item = request.get_json()
        item_to_update = next((dict(zip(columns, item)) for item in items if item[0] == item_id), None)
        
        if item_to_update is None:
            return jsonify({"Message": "item not found."}), 404

        priority_condition = r"^(normal|low|high)$"
        if "priority" not in item_data:
            item_data['priority'] = "normal"
        elif not re.search(priority_condition, item_data["priority"]):
            return jsonify({"Message": "The priority can only be high, low, or normal"}), 400
        status_condition = r"^(completed|inprogress|pending)$"
        if "status" not in item_data:
            item_data["status"] = "pending"
        elif not re.search(status_condition, item_data["status"]):
            return jsonify({"Message": "Enter status only completed, inprogress and pending"}), 400

    #     # Use a regular expression to validate the delivery_date format
        date_format_condition = r"^(0[1-9]|[12][0-9]|3[01])\-(0[1-9]|1[0-2])\-\d{2}$"
        if not re.search(date_format_condition,item_data['delivery_date']):
            return jsonify({"Message":"delivery_date shoulde be in this formate (dd-mm-yy)"}),400
        else:
            pass
        if "delivery_date" in item_data:
            # my_cursor.execute('UPDATE users  SET delivery_date=%s WHERE id = %s',(item_data['delivery_date'],item_id))
            my_cursor.execute(f"update {table_name} set delivery_date ='{item_data['delivery_date']}' where id = '{item_id}'")
        elif "delivery_date" not in item_data:
            pass
        if "description" in item_data:
            my_cursor.execute(f'UPDATE {table_name} set description=%s WHERE id = %s',(item_data['description'],item_id))
        elif "description" not in item_data:
            pass
            

        

        my_cursor.execute(f'UPDATE {table_name} set priority = %s, status = %s,start_date =%s WHERE id = %s', (item_data['priority'], item_data['status'],item_data['start_date'],item_id))
        # my_cursor.execute(update_statement, (item_data["description"], item_data["priority"], item_data["status"], item_data["id"]))
        connection.commit()
        # result = my_cursor.execute(f"select id ,start_date,delivery_date,priority,description,status from users where id = '{item_to_update['id']}'") 
        query = f"SELECT id, start_date, delivery_date, priority, description, status FROM {table_name} WHERE id = '{item_to_update['id']}'"
        my_cursor.execute(query)
        result = my_cursor.fetchone()

        if result:
            # Convert the result to a dictionary with column names as keys
            column_names = [desc[0] for desc in my_cursor.description]
            output = {column_names[i]: result[i] for i in range(len(column_names))}
            connection.commit()
            return jsonify(output), 200



def delete_item_from_database(item_id):
    token_checker = request.get_json()
    if ('token' not in token_checker):
        return jsonify({"Message":"token not found"}),400

    try:
        decoded = jwt.decode(token_checker['token'],security_key,algorithms='HS256')
    except:
        return jsonify({"Message":"Invalid token"}),400
    my_cursor.execute(f"use {databasename}")
    my_cursor.execute(f"select id from {table_name} where id ='{item_id}'")
    ids = my_cursor.fetchone()
    connection.commit()
    # print(ids)
    if (ids)  is None:
        return jsonify({"Message":"Item not found"}),400
    if (ids ==[]):
        print(ids)
        return jsonify({"Message":"Invalid id"}),400
    exact_id = ids[0]
    # print(exact_id)
    # print(ids)
    if (exact_id != item_id):
        return jsonify({"Message":"Invalid Id"}),400
    
    
    # if (token_checker['token']) is None:

    email_db_checker = decoded['email']
    # print(email_db_checker)
    # print(email_db_checker)
    my_cursor.execute(f'use {databasename}')

    # # connection.commit()
    my_cursor.execute(f"select password from {table_name} where email = '{email_db_checker}' and id ='{item_id}'")
    result = my_cursor.fetchone()
    connection.commit()
    # print(result)
    # return('ok')
    if (result is  None):
        return jsonify({"Message":"Invalid token or password"}),404
    
    password = result[0]
    print(password)
    if (password != token_checker['password'] ):
        return jsonify({"Message":"Invalid token or password"}),400
    else:
    # Database query to fetch items
        columns, items = get_items_from_database()

        item_to_delete = next((dict(zip(columns, item)) for item in items if item[0] == item_id), None)
        if item_to_delete is None:
            return jsonify({"message": "Item not found"}), 404

        # Database query to delete item
        delete_statement = f"DELETE FROM {table_name} WHERE id=%s"
        my_cursor.execute(delete_statement, (item_id,))
        connection.commit()

        return jsonify({"message": "Item deleted successfully"}), 200




def bearer_token_validation():
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
        return(email_db_checker)
