from flask import Blueprint, request, json, jsonify, make_response,session
from app.users.models import User
from app.roles.models import Roles
from app.users.schemas import user_schema, login_schema, user_update_schema, password_schema
from app.users.utills import generate_token, asia_kokata_time
from app import db
from bcrypt import checkpw
from app.utils.helpers import token_required
from sqlalchemy import desc, or_, and_
from app.utils.helpers import query_items, single_query
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
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message':'A ffilate added successfully',"status":"Success"}), 200)
    except Exception as e:
        return make_response(jsonify({'args':e.args,"status":"error","message":'error Staff user'}), 500)


@users.route('/get-users', methods=['GET'])
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
        serialized_users = [{
            'id': user.id,
            'role_id': user.role_id,
            'company_id': user.company_id,
            'name': user.name,
            'full_name': user.full_name,
            'email': user.email,
            'profile_pic': user.profile_pic,
            'details': user.details,
            'created_at': user.created_at.strftime('%d-%m-%Y %I:%M%p'),
            'updated_at': user.updated_at.strftime('%d-%m-%Y %I:%M%p'),
            'timestamp': int(user.updated_at.replace(tzinfo=timezone.utc).timestamp()),
            'deleted_at': user.deleted_at.strftime('%d-%m-%Y %I:%M%p')
        } for user in users if user.role_id not in (1, 2)]
        if serialized_users:
            return jsonify({'users': serialized_users, "status": "Success"})
        return make_response(jsonify({'message': 'users not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@users.route("/get_user/<int:id>", methods=["GET"])
@token_required(1, 2, 3, 4)
def get_user(user_details,id):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.company_id == User.company_id, user_details.role_id == 1)).first()
        if user.company_id == user_details.company_id or user_details.role_id == 1:
            full_name = json.loads(user.full_name.replace("'", '"'))
            first_name = full_name.get('first_name')
            last_name = full_name.get('last_name')
            middle_name = full_name.get('middle_name')
            if user:
                serialized_users = {
                    'id': user.id,
                    'role_id': user.role_id,
                    'company_id': user.company_id,
                    'name': user.name,
                    'full_name': user.full_name,
                    'middle_name':middle_name,
                    'last_name': last_name,
                    'first_name': first_name,
                    'email': user.email,
                    'profile_pic': user.profile_pic,
                    'details': user.details,
                    'password': "",
                    'confirmPassword': "",
                    'created_at_date': user.created_at.strftime('%d-%m-%Y'),
                    'created_at_time': user.created_at.strftime('%I:%M%p'),
                    'updated_at': user.updated_at,
                    'deleted_at': user.deleted_at
                }
                return make_response(jsonify({'users': serialized_users}), 200)
        return make_response(jsonify({'message':'User not found', "status": "error"}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', "status": "error"}), 500)
    
@users.route("/update_user/<int:id>", methods=["PUT"])
@token_required(1, 2, 3, 4)
def update_user(user_details, id):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.company_id == User.company_id, user_details.role_id == 1)).first()
        if user.company_id == user_details.company_id or user_details.role_id == 1:
            if user:
                data = request.get_json()
                data_dict = json.loads(data['formData'])
                schemaArray=dict()
                schemaArray['first_name']=data_dict['first_name']
                schemaArray['last_name'] = data_dict['last_name']
                schemaArray['role_id'] = data_dict['role_id']
                schemaArray['email'] = data_dict['email']
                schemaArray['password'] = data_dict['password']
                schemaArray['confirmPassword'] = data_dict['confirmPassword']
                loaded_data = user_update_schema.load(schemaArray)
                user.full_name = json.dumps({"first_name": loaded_data['first_name'].title(), "middle_name": data_dict['middle_name'].title(),
                                        "last_name": loaded_data['last_name'].title()})
                user.role_id = loaded_data['role_id']
                user.name = data_dict['first_name'].title()+" "+data_dict['middle_name'].title()+" "+data_dict['last_name'].title()
                user.email = loaded_data['email']
                user.password =bcrypt.hashpw(loaded_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db.session.commit()
                return make_response(jsonify({'message': 'Staff updated successfully',"status":"Success"}), 200)
            return make_response(jsonify({'message': 'Staff not found', "status": "error"}), 404)
        return make_response(jsonify({'message': "Unauthorized access", "status": "error"}), 500)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'error Staff user'}), 500)
    
@users.route('/delete_user/<int:id>', methods=['DELETE'])
@token_required(1, 2, 3)
def delete_user(user_details, id):
    try:
        user = User.query.filter(and_(User.id == id), or_(user_details.company_id == User.company_id,  user_details.role_id == 1)).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted', "status": "success"}), 200)
        return make_response(jsonify({'message': 'user not found', "status": "error"}), 404)
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
            # if user.role_id != 1:
            #         company = user.companies
            #         if company:
            #             date_info = json.loads(company.date)
            #             sub_end_str = date_info.get('sub_end', "")
            #             if sub_end_str:
            #                 sub_end = datetime.strptime(sub_end_str, '%Y-%m-%d').date()
            #                 today = datetime.today().date()
            #                 if sub_end < today:
            #                     return make_response(jsonify({"login_subcription": "Expired"}), 403)
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
            company_id = user_details.company_id
            query = {
                "user_count": User.query.filter_by(company_id=company_id).count() - 1,
            }
        return jsonify(query)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', "status": "error"}), 500)

@users.route('/profile_information', methods=['GET'])
@token_required(1, 2, 3, 4)  
def profile_information(current_user):
    try:
        user = User.query.filter_by(id=current_user.id).first()

        if user:
            company = user.companies
            date = {}
            if company and company.date:
                try:
                    date = json.loads(company.date)
                except json.JSONDecodeError:
                    return make_response(jsonify({'message': 'Invalid date JSON', 'status': 'error'}), 400)
            sub_end = date.get('sub_end', "")
            serialized_user = {
                'id': user.id,
                'role_id': user.role_id,
                'company_id': user.company_id,
                'name': user.name,
                'full_name': user.full_name,
                'first_name': user.name,
                'email': user.email,
                'profile_pic': user.profile_pic if user.profile_pic else "",
                'details': user.details,
                'flag': user.flag,
                'sub_start': date.get('sub_start', ""),
                'sub_end': sub_end,
                'created_at_date': user.created_at.strftime('%d-%m-%Y'),
                'created_at_time': user.created_at.strftime('%I:%M%p'),
                'updated_at': user.updated_at,
                'deleted_at': user.deleted_at
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

@users.route("/update_password/<int:id>", methods=["PUT"])
@token_required(1, 2)
def update_password(user_details, id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            data_dict = json.loads(data['formData'])
            schemaArray=dict()
            schemaArray['password'] = data_dict['password']
            schemaArray['confirmPassword'] = data_dict['confirmPassword']
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