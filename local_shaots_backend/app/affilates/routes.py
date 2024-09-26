from flask import Blueprint, request, json, jsonify, make_response
from app.utils.helpers import token_required, delete_item
from app.affilates.models import Affilate
from app.affilates.schemas import affilate_schema
from app.users.models import User
from app import db
from sqlalchemy import desc
from app.utils.helpers import query_items, handle_action
from app.affilates.utills import serialized_affilate
from datetime import  timezone

affilates = Blueprint('affilates', __name__)

@affilates.route('/add-affilates', methods=['POST'])
@token_required(1, 2)
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

    
@affilates.route("/affilates-list", methods = ['GET'])
@token_required(1, 2)
def get_affilates(user_details):
    try:        
        search = request.args.get('search')
        if search:
            affilates = Affilate.query.filter(Affilate.affilate_name.ilike(f'%{search}%')).order_by(desc(Affilate.id))
        else:
            affilates = Affilate.query.all()
        serialized_affilates = []
        for affilate in affilates:
            date = json.loads(affilate.date)
            serialized_affilate = {
                'id' : affilate.id,
                'affilate_name' : affilate.affilate_name,
                'email' : affilate.email,
                'mobile_number' : affilate.mobile_number,
                'address' : affilate.address,
                'sub_start' : date.get('sub_start', ""),
                'sub_end' : date.get('sub_end', ""),
                'created_at' : affilate.created_at,
                'updated_at' : affilate.updated_at                
            }
            serialized_affilates.append(serialized_affilate)
        return make_response(jsonify({'affilates' : serialized_affilates}))
    except Exception as e:
        return make_response(jsonify({'message' : e.args, 'status':'error'}))

    
@affilates.route('/view-affilate/<int:id>', methods = ['GET'])
@token_required(1, 2)
def view_affilate(user_details, id):
    try:
        affilate = Affilate.query.get(id)
        if affilate:
            date = json.loads(affilate.date)
            serialized_affilate = {
                'id' : affilate.id,
                'affilate_name' : affilate.affilate_name,
                'email' : affilate.email,
                'mobile_number' : affilate.mobile_number,
                'address' : affilate.address,
                'sub_start' : date.get('sub_start', ""),
                'sub_end' : date.get('sub_end', "")
            }
        return make_response(jsonify({'affilate': serialized_affilate}))
    except Exception as e:
        return make_response(jsonify({'message':e.args, 'status':'error'}))
        


@affilates.route("/update-affilate/<int:id>", methods=["PUT"])
@token_required(1,)
def update_affilate(user_details, id):
    try:
        affilate = Affilate.query.filter_by(id=id).first()
        user = User.query.filter_by(affilate_id=id).first()
        if affilate:
            data = request.get_json()
            schemaArray = {
                'affilate_name': data.get('affilate_name', '').title(),
                'email': data.get('email', ''),
                'mobile_number': str(data.get('mobile_number', '')),
                'address': data.get('address', ''),
                'date': json.dumps({
                    'sub_start': data.get('sub_start'),
                    'sub_end': data.get('sub_end')
                })
            }
            loaded_data = affilate_schema.load(schemaArray)
            affilate.affilate_name = loaded_data.get('affilate_name', affilate.affilate_name)
            affilate.email = loaded_data.get('email', affilate.email)
            affilate.date = loaded_data.get('date', affilate.date)
            affilate.mobile_number = str(loaded_data.get('mobile_number', affilate.mobile_number))
            affilate.address = loaded_data.get('address', affilate.address)
            
            if user:
                user.name = loaded_data.get('name', user.name)
                user.email = loaded_data.get('email', user.email)
                user.details = f"{loaded_data.get('phone_num', '')} {loaded_data.get('address', user.details)}"  
            
            db.session.commit()
            return make_response(jsonify({'message': 'Affilate updated successfully', "status": "Success"}), 200)
        return make_response(jsonify({'message': 'Affilate not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'args': str(e), "status": "error", "message": 'Error updating affilate'}), 500)

    
@affilates.route('/delete-affilate/<int:id>', methods=['DELETE'])
@token_required(1)
def delete_affiliate(user_details, id):
  return delete_item(Affilate, user_details, id, "Affilate")

