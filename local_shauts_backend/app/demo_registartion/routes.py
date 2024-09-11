from flask import Blueprint, request, current_app as app,jsonify, make_response, session
from app.utils.helpers import token_required
from app.demo_registartion.models import DemoRegistration
from app.demo_registartion.schemas import demo_schema
from app import db
from app.utils.helpers import query_items
from datetime import timezone

demo_registartions = Blueprint('demo_registartions', __name__)

@demo_registartions.route('/create_demo_registration', methods=['POST'])
def create_demo_registration():
    try:
        data = request.get_json()
        schemaArray = {
            'full_name': data['full_name'].title(),
            'email': data['email'],
            'phone': data['phone'],
            'state': data['state'],
            'demo_date': data['date']
        }
        validate_data = demo_schema.load(schemaArray)
        new_registration = DemoRegistration(**validate_data)
        db.session.add(new_registration)
        db.session.commit()
        return make_response(jsonify({'message': 'successfully registered', 'status': 'Success'}), 200)
    except Exception as e:
        return make_response(jsonify({'args': e.args, 'status': 'error', 'message': 'error creating registration'}), 500)
    
@demo_registartions.route('/get_demo_registration', methods=['GET'])
@token_required(1,)
def get_demo_registration(user_details):
    try:
        search = request.args.get('search')
        direction = request.args.get('direction')
        timestamp = request.args.get('timestamp')
        registrations = query_items(DemoRegistration.query, user_details, search, direction, timestamp,
            DemoRegistration.updated_at, [DemoRegistration.full_name])
        if registrations:
            serialized_demo = [
                {
                    'id': registration.id,
                    'full_name': registration.full_name,
                    'email': registration.email,
                    'phone': registration.phone,
                    'demo_date': registration.demo_date,
                    'state': registration.state,
                    'created_at': registration.created_at,
                    'timestamp': int(registration.updated_at.replace(tzinfo=timezone.utc).timestamp()),
                    'updated_at': registration.updated_at,
                    'deleted_at': registration.deleted_at
                }
                for registration in registrations
            ]
            return make_response(jsonify({'serialized_demo': serialized_demo}), 200)
        return make_response(jsonify({'message': 'No Registration found'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Unexpected Error: {e}', "status": "error"}), 500)