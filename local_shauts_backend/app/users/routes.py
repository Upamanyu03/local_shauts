from flask import Blueprint, request, json, jsonify, make_response,session
from app.users.models import User
import json
from app.roles.models import Roles
from app.users.schemas import user_schema, login_schema, user_update_schema, password_schema
from app.users.utills import generate_token, asia_kokata_time
from app.users.utills import serialized_user
from app import db
from bcrypt import checkpw
# from app.utils.helpers import token_required, delete_item
from sqlalchemy import desc, or_, and_
from app.utils.helpers import query_items, single_query, token_required, delete_item, handle_action
import bcrypt
from datetime import datetime, timezone


users = Blueprint('users', __name__)

@users.route('/add-user', methods=['POST'])
# @token_required(1, 2, 3)
def add_user():
    try:
        data= request.get_json()
        
        # data_dict = json.loads(data['formData'])
        details_json = {
            'phone_num': data['phone_num'],
            'address': data['address'],
        }
        schemaArray = {
            'name' : data['name'],
            'role_id': str(1),
            'affilate_id': data['affilate_id'],
            'email': data['email'],
            'password': data['password'],
            'confirm_password': data['confirm_password']

        }
        loaded_data = user_schema.load(schemaArray)
        loaded_data.pop('confirm_password')
        loaded_data.update({'details': json.dumps(details_json)})
        loaded_data.update({"flag": '0'})
        new_user = User(**loaded_data)
        return handle_action(new_user, 'create')
    except Exception as e:
        return make_response(jsonify({'args':e.args,"status":"error","message":'error Staff user'}), 500)


@users.route('/add-or-update', methods=['POST', 'PUT'])
def add_or_update_user(user_details):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.affilate_id == User.affilate_id, user_details.role_id == 1)).first()
        data= request.get_json()
        id = request.args.get('id')

        if id:
            user_to_update = User.query.get(id)
            if not user_to_update:
                return make_response(jsonify({'message' :'user not found', 'status':'error'}))
            schemaArray=dict()
            schemaArray['name']=data['name']
            schemaArray['phone_num'] = data['phone_num']
            schemaArray['address'] = data['address']
            schemaArray['role_id'] = data['role_id']
            schemaArray['email'] = data['email']
            schemaArray['password'] = data['password']
            schemaArray['confirmPassword'] = data['confirmPassword']
            loaded_data = user_update_schema.load(schemaArray)
            user.name = loaded_data['name']
            user.details = json.dumps({"phone_num": loaded_data['phone_num'], "address": loaded_data['address']})
            user.role_id = loaded_data['role_id']
            user.email = loaded_data['email']
            user.password =bcrypt.hashpw(loaded_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.commit()
            return make_response(jsonify({'message':'user updated successfully', 'status':'success'}), 200)
        else:
            details_json = {
               'phone_num': data['phone_num'],
               'address': data['address'],
            }
            schemaArray = {
                'name' : data['name'],
                'role_id': str(1),
                'affilate_id': data['affilate_id'],
                'email': data['email'],
                'password': data['password'],
                'confirm_password': data['confirm_password']
            }
            loaded_data = user_schema.load(schemaArray)
            loaded_data.pop('confirm_password')
            loaded_data.update({'details': json.dumps(details_json)})
            loaded_data.update({"flag": '0'})
            new_user = User(**loaded_data)
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify({'message':'user added successfully', 'status':'success'}), 200)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "message": 'Failed to process request', "status": "error"}), 500)

            


@users.route('/get-user', methods=['GET'])
@token_required(1, 2, 3, 4)
def get_users_timestamp(user_details):
    try:
        search = request.args.get('search')
        direction = request.args.get('direction')
        timestamp = request.args.get('timestamp')
        users = query_items(
            User.query,
            user_details,
            search,
            direction,
            timestamp,
            User.updated_at,
            [User.name]
        )
        serialized_users = [serialized_user(user) for user in users if user and user.role_id is not None and user.role_id not in (1, )]

        if serialized_users:
            return jsonify({'users': serialized_users, "status": "Success"})
        return make_response(jsonify({'message': 'users not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@users.route("/get-user/<int:id>", methods=["GET"])
@token_required(1, 2, 3, 4)
def get_user(user_details,id):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.affilate_id == User.affilate_id, user_details.role_id == 1)).first()
        if user.affilate_id == user_details.affilate_id or user_details.role_id == 1:
            if user:
                serialized_users = serialized_user(user)
                return make_response(jsonify({'users': serialized_users}), 200)
        return make_response(jsonify({'message':'User not found', "status": "error"}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', "status": "error"}), 500)
    
@users.route("/update-user/<int:id>", methods=["PUT"])
@token_required(1, 2, 3, 4)
def update_user(user_details, id):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.affilate_id == User.affilate_id, user_details.role_id == 1)).first()
        if user.affilate_id == user_details.affilate_id or user_details.role_id == 1:
            if user:
                data = request.get_json()
                # data_dict = json.loads(data['formData'])
                schemaArray=dict()
                schemaArray['name']=data['name']
                schemaArray['phone_num'] = data['phone_num']
                schemaArray['address'] = data['address']
                schemaArray['role_id'] = data['role_id']
                schemaArray['email'] = data['email']
                schemaArray['password'] = data['password']
                schemaArray['confirmPassword'] = data['confirmPassword']
                loaded_data = user_update_schema.load(schemaArray)
                user.name = loaded_data['name']
                user.details = json.dumps({"phone_num": loaded_data['phone_num'], "address": loaded_data['address']})
                user.role_id = loaded_data['role_id']
                # user.name = data['first_name'].title()+" "+data['middle_name'].title()+" "+data['last_name'].title()
                user.email = loaded_data['email']
                user.password =bcrypt.hashpw(loaded_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                return handle_action(data, 'update')
            return make_response(jsonify({'message': 'Staff not found', "status": "error"}), 404)
        return make_response(jsonify({'message': "Unauthorized access", "status": "error"}), 500)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'error Staff user'}), 500)
    
@users.route('/delete-user/<int:id>', methods=['DELETE'])
@token_required(1, 2, 3)
def delete_user(user_details, id):
    try:
        return delete_item(User, user_details, id, "User")
    except Exception as e:
        return make_response(jsonify({'message': f'error deleting user: {e}',"status": "error"}), 500)

@users.route('/login', methods=['POST'])
def Login():
    try:
        data = request.get_json()
        schemaArray = dict()
        # data_dict = json.loads(data['formData'])
        schemaArray['email'] = data['email']
        schemaArray['password'] = data['password']
        loaded_data = login_schema.load(schemaArray)
        user = User.query.filter_by(email=loaded_data['email']).first()
        if user and checkpw(loaded_data['password'].encode('utf-8'), user.password.encode('utf-8')):
            if user.role_id != 1:
                    affilate = user.affilate
                    if affilate:
                        date_info = json.loads(affilate.date)
                        sub_end_str = date_info.get('sub_end', "")
                        if sub_end_str:
                            sub_end = datetime.strptime(sub_end_str, '%Y-%m-%d').date()
                            today = datetime.today().date()
                            if sub_end < today:
                                return make_response(jsonify({"login_subcription": "Expired"}), 403)
            token = generate_token(user.id)
            return make_response(jsonify({"message": "Login successfully", 'token': token, "status": "Success"}), 200)
        else:
            return make_response(jsonify({'invalid': 'Invalid credentials', "status": "error"}), 403)
    except Exception as e:
        return make_response(jsonify({'message': f'error Login user', 'args': e.args, "status": "error"}), 500)
    
@users.route('/dashboard', methods=['GET'])
@token_required(1, 2, 3, 4)
def dashboard(user_details):
    try:
        if user_details.role_id == 1:
            query = {
                "user_count": User.query.filter(User.role_id != 2).count() - 1,
            }
        else:
            affilate_id = user_details.affilate_id
            query = {
                "user_count": User.query.filter_by(affilate_id=affilate_id).count() - 1,
            }
        return jsonify(query)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', "status": "error"}), 500)

@users.route('/profile-information', methods=['GET'])
@token_required(1, 2, 3, 4)  
def profile_information(current_user):
    try:
        user = User.query.filter_by(id=current_user.id).first()
        print(user.affilate)
        if user:
            affilate = user.affilate
            print(affilate)
            date = {}
            if affilate and affilate.date:
                try:
                    print(f"Raw date: {affilate.date}")
                    date = json.loads(affilate.date)
                except json.JSONDecodeError:
                    return make_response(jsonify({'message': 'Invalid date JSON', 'status': 'error'}), 400)
            sub_end = date.get('sub_end', "")
            serialized_user = {
                'id': user.id,
                'role_id': user.role_id,
                'affilate_id': user.affilate_id,
                'name': user.name,
                'email': user.email,
                'profile_pic': user.profile_pic if user.profile_pic else "",
                'details': user.details,
                'flag': user.flag,
                'sub_start': date.get('sub_start', ""),
                'sub_end': sub_end,
                'created_at_date': user.created_at.strftime('%d-%m-%Y'),
                'created_at_time': user.created_at.strftime('%I:%M%p'),
                'updated_at': user.updated_at
            }
            return make_response(jsonify({'user': serialized_user}), 200)

        return make_response(jsonify({'message': 'User not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)

@users.route('/logout', methods=['GET'])
def logout():
    try:
        device_identifier = request.remote_addr
        if device_identifier:
            session.pop(f'token_{device_identifier}', None)
        response = make_response(jsonify({"message": "Logout successful"}), 200)
        response.delete_cookie('session_token')
        return response
    except Exception as e:
        print(f"An error occurred during logout: {str(e)}")
        return make_response(jsonify({"message": "An error occurred while logging out"}), 500 )

@users.route("/update-password/<int:id>", methods=["PUT"])
@token_required(1, 2)
def update_password(user_details, id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            # data_dict = json.loads(data['formData'])
            schemaArray=dict()
            schemaArray['password'] = data['password']
            schemaArray['confirmPassword'] = data['confirmPassword']
            loaded_data = password_schema.load(schemaArray)
            password =bcrypt.hashpw(loaded_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            db.session.query(User).filter(User.id == id).update({
                User.password: password,
                User.flag: "0"
            })
            db.session.commit()
            return make_response(jsonify({'message': 'Profile password updated successfully', "status": "Success"}), 200)
        return make_response(jsonify({'message': 'Staff not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'error Staff user'}), 500)