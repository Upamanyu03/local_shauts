from app.customers.models import Customer
from app.customers.schemas import customer_schema
from app import db
from app.utils.helpers import delete_item
from flask import Blueprint, request, make_response, json, jsonify
from app.utils.helpers import token_required

customers = Blueprint('customers', __name__)

@customers.route('/add-customer', methods = ['POST'])
@token_required(1, 2)
def add_customer(user_details):
    try:
        data = request.get_json()
        customer_data = {
            'name' : data['name'],
            'email' : data['email'],
            'address' : data['address'],
            'contact_no' : data['contact_no'],
            'gender' : data['gender'],
            'age' : data['age']
        }
        loaded_customer_data = customer_schema.load(customer_data)
        new_customer = Customer(**loaded_customer_data)
        db.session.add(new_customer)
        db.session.commit()
        return make_response(jsonify({'message': 'customer added successfully', 'status':'Success'}), 200)
    except Exception as e:
        return make_response(jsonify({'message': str(e), 'status':'error'}), 500)
    
@customers.route('/get-customers', methods = ['GET'])
@token_required(1, 2)
def get_customers(user_details):
    try:
        search = request.args.get('search')
        if search:
            customers = Customer.query.filter(Customer.name.ilike(f'{search}'))
        else:
            customers = Customer.query.all()
            serialized_customers = []
            for customer in customers:
                serialized_customer = {
                    'name' : customer.name,
                    'id': customer.id,
                    'email': customer.email,
                    'address' : customer.address,
                    'contact_no' : customer.contact_no,
                    'gender' : customer.gender,
                    'age' : customer.age,
                    'created_at' : customer.created_at,
                    'updated_at' : customer.updated_at
                }
                serialized_customers.append(serialized_customer)
            return make_response(jsonify({'customers': serialized_customers}))
    except Exception as e:
        return make_response(jsonify({'message':e.args, 'status':'error'}))
    
@customers.route('/get-customer/<int:id>', methods = ['GET'])
@token_required(1, 2)
def get_customer(user_details, id):
    try:
        customer = Customer.query.filter_by(id=id).first()
        if customer:
            serialized_customer = {
                'id':customer.id,
                'name' : customer.name,
                'email' : customer.email,
                'address' : customer.address,
                'contact_no' : customer.contact_no,
                'gender' : customer.gender,
                'age' : customer.age,
                'created_at' : customer.created_at,
                'updated_at' : customer.updated_at
            }
            return make_response(jsonify({'customer': serialized_customer}))
    except Exception as e:
        return make_response(jsonify({'message':e.args, 'status':'error'}))
    
@customers.route('/edit-customer/<int:id>', methods = ['PUT'])
@token_required(1, 2)
def edit_customer(user_details, id):
    try:
        customer = Customer.query.get(id)
        data = request.get_json()
        customer.name = data.get('name',"")
        customer.email = data.get('email')
        customer.address = data.get('address')
        customer.contact_no = data.get('contact_no')
        customer.gender = data.get('gender')
        customer.age = data.get('age')
        db.session.commit()
        return make_response(jsonify({'message':'customer updated successfully', 'status':'Success'}), 200)
    except Exception as e:
        return make_response(jsonify({'message':e.args, 'status':'error'}), 500)
    
@customers.route('/delete-customer/<int:id>', methods = ['DELETE'])
@token_required(1, 2)
def delete_customer(user_details, id):
    return delete_item(Customer, user_details, id, "Customer")

