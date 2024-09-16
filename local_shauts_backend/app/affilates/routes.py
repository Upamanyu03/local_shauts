from flask import Blueprint, request, json, jsonify, make_response
from app.utils.helpers import token_required, delete_item
from app.affilates.models import Affilate
from app.affilates.schemas import affilate_schema
from app.users.models import User
from app import db
from app.utils.helpers import query_items, handle_action
from app.affilates.utills import serialized_affilate
from datetime import  timezone

affilates = Blueprint('affilates', __name__)

@affilates.route('/add-affilates', methods=['POST'])
@token_required(1)
def add_affilate(user_details):
    try:
        data = request.get_json()
        # affilate_dict = json.loads(data['formData'])
               
        schemaArray = {
            'affilate_name': data['affilate_name'].title(),
            'email': data['email'],
            'mobile_number': data['mobile_number'],
            'address': data['address'],
            'date' : json.dumps ({
            'sub_start': data['sub_start'],
            'sub_end': data['sub_end'],
         })
        }
        loaded_data = affilate_schema.load(schemaArray)
        new_affilate = Affilate(**loaded_data)
        db.session.add(new_affilate)
        db.session.commit()
        print(new_affilate.id)
        address ={"address": data['address']}
       
        if isinstance(address, str):
            address = data['address']
       
        address['mobile_number'] = data['mobile_number']
        
        userArray = {
            'name': data['affilate_name'].title(),
            'email': data['email'],
            'password': "123456",
            'affilate_id': new_affilate.id,
            'role_id': "2",
            'details': json.dumps(address),
            'flag': "1"
        }
        new_user = User(**userArray)
        return handle_action(new_user, 'create') 
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'error create Affilate'}), 500)

    
@affilates.route('/get-affilates', methods=['GET'])
@token_required(1, 2, 3, 4)
def get_affilates_timestamp(user_details):
    try:
        search = request.args.get('search')
        direction = request.args.get('direction')
        timestamp = request.args.get('timestamp')
        affilates = query_items(
            Affilate.query,
            user_details,
            search,
            direction,
            timestamp,
            Affilate.updated_at,
            [Affilate.affilate_name]
        )
        date = {}
        serialized_affilates = [serialized_affilate(affilate, date) for affilate in affilates if affilate.id not in (1,)]
        if serialized_affilates:
            return jsonify({'affilates': serialized_affilates, "date" : date })
        return make_response(jsonify({'message': 'Affilates not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@affilates.route("/get-affilate/<int:id>", methods=["GET"])
@token_required(1, 2)
def get_affilate(user_details, id):
    try:
        affilate = Affilate.query.filter_by(id=id).first()
        if not affilate:
            return make_response(jsonify({'message': 'Affilate not found', 'status': 'error'}), 404)
        date = {}
        serialized_affilates = serialized_affilate(affilate, date)
        return make_response(jsonify({'affilate': serialized_affilates, "date" : date}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', 'status': 'error'}), 500)

@affilates.route("/update-affilate/<int:id>", methods=["PUT"])
@token_required(1, 2)
def update_affilate(user_details, id):
    try:
        affilate = Affilate.query.filter_by(id=id).first()
        user = User.query.filter_by(affilate_id=id).first()
        if affilate:
            data = request.get_json()
            # data_dict = json.loads(data['formData'])
            schemaArray = {
                'affilate_name': data['affilate_name'].title(),
                'email': data['email'],
                'mobile_number': str(data['mobile_number']),
                'address': data['address'],
                'date':json.dumps({
                'sub_start': data.get('sub_start'),
                'sub_end': data.get('sub_end')
                })
            }
            loaded_data = affilate_schema.load(schemaArray)
            affilate.affilate_name = loaded_data['affilate_name']
            affilate.email = loaded_data['email']
            affilate.date = loaded_data['date']
            affilate.mobile_number = str(loaded_data['mobile_number'])
            affilate.address = loaded_data['address']
            if user:
                user.name = loaded_data['name']
                user.email = loaded_data['email']
                user.details = loaded_data['phone_num'] + " " + loaded_data['address']  
            db.session.commit()
            return make_response(jsonify({'message': 'Affilate updated successfully', "status": "Success"}), 200)
        return make_response(jsonify({'message': 'Affilate not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'Error updating affilate'}), 500)
    
@affilates.route('/delete_affilate/<int:id>', methods=['DELETE'])
@token_required(1)
def delete_affiliate(user_details, id):
  return delete_item(Affilate, user_details, id, "Affilate")

