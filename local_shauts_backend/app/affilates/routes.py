from flask import Blueprint, request, json, jsonify, make_response
from app.utils.helpers import token_required
from sqlalchemy import desc
from app.affilates.models import Affilate
from app.affilates.schemas import affilate_schema
from app.users.models import User
from app import db
from app.utils.helpers import query_items
from datetime import  timezone

affilates = Blueprint('affilates', __name__)

@affilates.route('/add-affilates', methods=['POST'])
# @token_required(1)
def add_affilate():
    try:
        data = request.get_json()
        # company_dict = json.loads(data['formData'])
       
        sub_date = {
            'sub_start': data['sub_start'],
            'sub_end': data['sub_end'],
        }
        schemaArray = {
            'affilate_name': data['affilate_name'].title(),
            'email': data['email'],
            'mobile_number': data['mobile_number'],
            'address': data['address']
        }
        loaded_data = affilate_schema.load(schemaArray)
        loaded_data.update({'date': json.dumps(sub_date)})
        
        new_affilate = Affilate(**loaded_data)
        db.session.add(new_affilate)
        db.session.commit()
        print(new_affilate.affilate_id)
        address ={"address": data['address']}
       
        if isinstance(address, str):
            address = data['address']
       
        address['mobile_number'] = data['mobile_number']
        
        userArray = {
            'name': data['affilate_name'].title(),
            'email': data['email'],
            'password': "123456",
            'affilate_id': new_affilate.affilate_id,
            'role_id': "2",
            'details': json.dumps(address),
            'flag': "1"
        }
        new_user = User(**userArray)
        db.session.add(new_user)
        db.session.commit()
        return make_response(
            jsonify({'message': 'Affilate created successfully', "status": "Success"}),
            200)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'error create Affilate'}), 500)

    
@affilates.route('/get-company', methods=['GET'])
@token_required(1, 2, 3, 4)
def get_company_timestamp(user_details):
    try:
        search = request.args.get('search')
        direction = request.args.get('direction')
        timestamp = request.args.get('timestamp')
        companies = query_items(
            Affilate.query,
            user_details,
            search,
            direction,
            timestamp,
            Affilate.updated_at,
            [Affilate.company_name]
        )
        serialized_company = [{
            'id': company.id,
            'company_name': company.company_name,
            'email': company.email,
            'mobile_number': company.mobile_number,
            'address': company.address,
            'workshop_type_name': company.workshop_type.workshop_type_name,
            'created_at': company.created_at.strftime('%d-%m-%Y %I:%M%p'),
            'updated_at': company.updated_at.strftime('%d-%m-%Y %I:%M%p'),
            'timestamp': int(company.updated_at.replace(tzinfo=timezone.utc).timestamp()),
            'deleted_at': company.deleted_at.strftime('%d-%m-%Y %I:%M%p')
        } for company in companies if company.id not in (1,)]
        if serialized_company:
            return jsonify({'companies': serialized_company, "status": "Success"})
        return make_response(jsonify({'message': 'Companies not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@affilates.route("/get-company/<int:id>", methods=["GET"])
@token_required(1, 2)
def get_company(user_details, id):
    try:
        company = Affilate.query.filter_by(id=id).first()
        if not company:
            return make_response(jsonify({'message': 'Company not found', 'status': 'error'}), 404)
        bank_details = {}
        date = {}
        serialized_company = {
            'id': company.id,
            'company_name': company.company_name,
            'email': company.email,
            'mobile_number': company.mobile_number,
            'address': company.address,
            'bank_name': bank_details.get('bank_name'),
            'act_no': bank_details.get('act_no'),
            'ifsc': bank_details.get('ifsc'),
            'brach_name': bank_details.get('brach_name'),
            'vpa': bank_details.get('vpa'),
            'currency': bank_details.get('currency'),
            'sub_start': date.get('sub_start', ""),
            'sub_end': date.get('sub_end', ""),
            'created_at_date': company.created_at.strftime('%d-%m-%Y'),
            'created_at_time': company.created_at.strftime('%I:%M%p'),
            'updated_at': company.updated_at,
            'deleted_at': company.deleted_at
        }
        return make_response(jsonify({'company': serialized_company}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', 'status': 'error'}), 500)

@affilates.route("/update_company/<int:id>", methods=["PUT"])
@token_required(1, 2)
def update_company(user_details, id):
    try:
        company = Affilate.query.filter_by(id=id).first()
        user = User.query.filter_by(company_id=id).first()
        if company:
            data = request.get_json()
            data_dict = json.loads(data['formData'])
            schemaArray = {
                'company_name': data_dict['company_name'].title(),
                'email': data_dict['email'],
                'mobile_number': str(data_dict['mobile_number']),
                'address': data_dict['address'],
                'workshop_type_id': 1,
                'bank_details': json.dumps({
                    'bank_name': data_dict.get('bank_name').title(),
                    'act_no': data_dict.get('act_no'),
                    'ifsc': data_dict.get('ifsc'),
                    'brach_name': data_dict.get('brach_name').title(),
                    'vpa': data_dict.get('vpa'),
                    'currency': data_dict.get('currency')
                }),
                'date':json.dumps({
                'sub_start': data_dict.get('sub_start'),
                'sub_end': data_dict.get('sub_end')
                })
            }
            loaded_data = affilate_schema.load(schemaArray)
            company.company_name = loaded_data['company_name']
            company.email = loaded_data['email']
            company.bank_details = loaded_data['bank_details']
            company.date = loaded_data['date']
            company.mobile_number = str(loaded_data['mobile_number'])
            company.address = loaded_data['address']
            user.name = loaded_data['company_name']
            user.email = loaded_data['email']
            user.full_name = json.dumps({"first_name": loaded_data['company_name'], "last_name": loaded_data['company_name']})
            user.details = loaded_data['mobile_number'] + " " + loaded_data['address']  
            db.session.commit()
            return make_response(jsonify({'message': 'Workshop updated successfully', "status": "Success"}), 200)
        return make_response(jsonify({'message': 'Company not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'args': e.args, "status": "error", "message": 'Error updating company'}), 500)
    
@affilates.route('/delete_company/<int:id>', methods=['DELETE'])
@token_required(1)
def delete_company(user_details, id):
    try:
        company = Affilate.query.get(id)
        if company:
            User.query.filter_by(company_id=id).delete()
            db.session.delete(company)
            db.session.commit()
            return make_response(jsonify({'message': 'Company deleted successfully', "status": "success"}), 200)
        return make_response(jsonify({'message': 'company not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'error deleting company: {e}', "status": "error"}), 500)

