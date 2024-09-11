from flask import Blueprint, request, json, jsonify, make_response, send_file
from app.utils.helpers import token_required
from sqlalchemy import or_,and_
from sqlalchemy import desc
from app.job_sheet.models import Customer, JobSheet, CustomerVehicle
from app.estimate.models import Estimate
from app.invoices.models import Invoice
from math import ceil
# import io
# import pandas as pd
# import os
# import csv
from app import db
from app.customers.schemas import customer_schema
from app.customers.utills import update_table
from app.job_sheet.models import Vehicle
from datetime import datetime, timezone
from app.job_sheet.schemas import vehicle_schema
from app.labour.utills import query_items,delete_item

customer = Blueprint('customer', __name__)

@customer.route('/create-customers', methods=['POST'])
@token_required(1, 2, 3, 4)
def add_customers(user_details):
    try:
        data = request.get_json()
        data_dict = json.loads(data['formData'])
        schema_array = {
            'full_name': data_dict['full_name'],
            'address': data_dict['address'],
            'company_id':str(user_details.company_id),
            'email': data_dict['email'],
            'mobile_number': data_dict['mobile_number'],
            'alternet_number': data_dict['alternet_number']
        }
        customer_schema.load(schema_array)
        new_customer = Customer(**schema_array)
        db.session.add(new_customer)
        db.session.commit()
        return make_response(jsonify({'message': 'customer added successfully', 'status': 'Success'}), 200)
    except Exception as e:
        return make_response(jsonify({'args': e.args, 'status': 'error', 'message': 'error creating customer'}), 500)


@customer.route('/get_customers', methods=['GET'])
@token_required(1, 2, 3, 4)
def get_customers(user_details):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        search = request.args.get('search')
        customer_query = Customer.query
        if search:
            if user_details.role_id == 1:
                customer_query = customer_query.filter(Customer.full_name.ilike(f'%{search}%'))
            else:
                customer_query = customer_query.filter(Customer.full_name.ilike(f'%{search}%')) \
                    .filter_by(company_id=user_details.company_id)
        else:
            if user_details.role_id == 1:
                customer_query = customer_query.order_by(desc(Customer.id))
            else:
                customer_query = customer_query.filter_by(company_id=user_details.company_id).order_by(desc(Customer.id))

        customer_paginate = customer_query.paginate(page=page, per_page=per_page, error_out=False)

        total_count = customer_paginate.total
        total_pages = ceil(total_count / per_page)
        start_index = (page - 1) * per_page + 1
        end_index = min(page * per_page, total_count)

        if customer_paginate.items:
            serialized_customers = []
            for customer in customer_paginate.items:
                serialized_customer = {
                    'id': customer.id,
                    'full_name': customer.full_name,
                    'address': customer.address,
                    'email': customer.email,
                    'mobile_number': customer.mobile_number,
                    'created_at': customer.created_at,
                    'updated_at': customer.updated_at,
                    'deleted_at': customer.deleted_at
                }
                serialized_customers.append(serialized_customer)
            data = {
                'total_count': total_count,
                'total_pages': total_pages,
                'start_index': start_index,
                'end_index': end_index,
                'page': page,
            }
            return make_response(jsonify({'data': data,'customers': serialized_customers}), 200)
        return make_response(jsonify({'message': 'No customers found', 'data': {'total_count': total_count,'total_pages': total_pages, 'start_index': start_index, 'end_index':end_index}}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', "status": "error"}), 500)
    
@customer.route('/get-customers', methods=['GET'])
@token_required(1, 2, 3, 4)
def get_cutomers_timestamp(user_details):
    try:
        search = request.args.get('search')
        direction = request.args.get('direction')
        timestamp = request.args.get('timestamp')
        customers = query_items(
            Customer.query,
            user_details,
            search,
            direction,
            timestamp,
            Customer.updated_at,
            [Customer.full_name]
        )
        serialized_customer = [{
            'id': customer.id,
            'full_name': customer.full_name,
            'address': customer.address,
            'email': customer.email,
            'mobile_number': customer.mobile_number,
            'created_at': customer.created_at.strftime('%d-%m-%Y %I:%M%p'),
            'updated_at': customer.updated_at.strftime('%d-%m-%Y %I:%M%p'),
            'timestamp': int(customer.updated_at.replace(tzinfo=timezone.utc).timestamp()),
            'deleted_at': customer.deleted_at.strftime('%d-%m-%Y %I:%M%p')
        } for customer in customers]
        if serialized_customer:
            return jsonify({'customers': serialized_customer, "status": "Success"})
        return make_response(jsonify({'message': 'Mechanics not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@customer.route("/update_customer/<int:id>", methods=["PUT"])
@token_required(1, 2, 3, 4)
def update_customer(user_details, id):
    try:
        customer = Customer.query.filter(
            and_(
                Customer.id == id,
                or_(
                    user_details.company_id == Customer.company_id,
                    user_details.role_id == 1
                )
            )
        ).first()
        if customer:
            getData = request.get_json()
            data_dict = json.loads(getData.get('formData', '{}'))
            table_name = data_dict.get('filter','')
            vehicle_number = {
                'vehicle_number': "1234",
                'mobile_number':str(data_dict['mobile_number']),
                "full_name": data_dict['full_name'],
            }
            vehicle_schema.load(vehicle_number)
            data = {
                'full_name': data_dict.get('full_name').title(),
                'address': data_dict.get('address').capitalize(),
                'email': data_dict.get('email'),
                'mobile_number': str(data_dict['mobile_number']),
            }
            for key, value in data.items():
                setattr(customer, key, value)
            if table_name:
                update_table(data_dict.get('filter'), data_dict.get('id_flag'))
            db.session.commit()

            return make_response(jsonify({'message': 'Customer updated successfully', "status": "Success"}), 200)
        return make_response(jsonify({'message': 'Customer not found', "status": "error"}), 404)
    except Exception as e:
        return make_response(jsonify({'args': e.args, 'message': 'Error updating customer.', "status": "error"}), 500)

@customer.route('/customer_details/<int:id>', methods=['GET'])
@token_required(1, 2, 3, 4)
def customer_details(user_details, id):
    try:
        customer = Customer.query.filter(
            and_(Customer.id == id),
            or_(user_details.company_id == Customer.company_id, user_details.role_id == 1)
        ).first()

        if not customer:
            return make_response(jsonify({'message': 'Customer not found', 'status': 'error'}), 404)

        vehicles = db.session.query(Vehicle).join(CustomerVehicle).filter(CustomerVehicle.customer_id == id).all()

        vehicle_data = []
        for vehicle in vehicles:
            vehicle_id = vehicle.id
            jobcard_count = JobSheet.query.filter_by(customer_id=id, vehicle_id=vehicle_id).count()
            estimate_count = Estimate.query.filter_by(customer_id=id, vehicle_id=vehicle_id).count()
            invoice_count = Invoice.query.filter_by(customer_id=id, vehicle_id=vehicle_id).count()

            vehicle_data.append({
                'id': vehicle.id,
                'vehicle_number': vehicle.vehicle_number,
                'vehicle_name': vehicle.vehicle_name,
                'manufacturers': vehicle.manufacturers,
                'vehicle_id': vehicle.id,
                'jobcard_count': jobcard_count,
                'estimate_count': estimate_count,
                'invoice_count': invoice_count
            })
        vehicle_count = len(vehicle_data)
        serialized_customer = {
            'id': customer.id,
            'company_id': customer.company_id,
            'customer_full_name': customer.full_name,
            'customer_address': customer.address,
            'customer_email': customer.email,
            'customer_mobile_number': customer.mobile_number,
            'vehicles': vehicle_data,
            'alternet_mobile_number': customer.alternet_number,
            'vehicle_count': vehicle_count,
            'created_at': customer.created_at,
            'updated_at': customer.updated_at,
            'deleted_at': customer.deleted_at
        }
        return make_response(jsonify({'customer': serialized_customer}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Unexpected Error: {str(e)}', 'status': 'error'}), 500)

@customer.route('/customer_info/<int:id>', methods=['GET'])
@token_required(1, 2, 3, 4)
def customer_info(user_details, id):
    try:
        filter_type = request.args.get('filter')
        vehicle_id = request.args.get('vehicle_id')
        customer = Customer.query.filter(
            and_(Customer.id == id,
                 or_(user_details.company_id == Customer.company_id, user_details.role_id == 1))
        ).first()

        if not customer:
            return make_response(jsonify({'message': 'Customer not found', 'status': 'error'}), 404)

        if filter_type == "Estimate" and vehicle_id:
            estimates = Estimate.query.filter_by(customer_id=id, vehicle_id=vehicle_id).all()
            estimate_list = []

            for estimate in estimates:
                total = json.loads(estimate.total or '{}')
                estimate_data = {
                    'id': estimate.id,
                    'estimate_number': estimate.estimate_number,
                    'estimateTotal': format(total.get('estimateTotal', 0), ".2f"),
                    'full_name': estimate.customers.full_name,
                    'vehicle_id': vehicle_id,
                    'vehicle_number': estimate.vehicles.vehicle_number,
                    'vehicle_name': estimate.vehicles.vehicle_name,
                }
                estimate_list.append(estimate_data)

            return make_response(jsonify({'customer_info': estimate_list, 'status': 'Success'}), 200)


        elif filter_type == "Invoice":
            invoices = Invoice.query.filter_by(customer_id=id, vehicle_id=vehicle_id).all()
            invoice_list = []

            for invoice in invoices:
                total = json.loads(invoice.total or '{}')
                invoice_data = {
                    'id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'invoiceTotal': format(total.get('invoiceTotal', 0), ".2f"),
                    'full_name': invoice.customers.full_name,
                    'vehicle_id':vehicle_id,
                    'vehicle_number': invoice.vehicles.vehicle_number,
                    'vehicle_name': invoice.vehicles.vehicle_name,
                }
                invoice_list.append(invoice_data)
            return make_response(jsonify({'customer_info': invoice_list, 'status': 'Success'}), 200)

        elif filter_type == "Jobcard":
            jobcards = JobSheet.query.filter_by(customer_id=id, vehicle_id=vehicle_id).all()
            jobcard_list = []

            for jobcard in jobcards:
                jobcard_data = {
                    'id': jobcard.id,
                    'vehicle_manufacturers': jobcard.vehicle.manufacturers,
                    'created_at_date': jobcard.created_at.strftime('%d-%m-%Y'),
                    'created_at_time': jobcard.created_at.strftime('%I:%M%p'),
                    'jobcard_status': jobcard.status,
                    'customer_name': jobcard.customer.full_name,
                    'vehicle_id':vehicle_id,
                    'vehicle_number': jobcard.vehicle.vehicle_number,
                    'vehicle_name': jobcard.vehicle.vehicle_name,
                }
                jobcard_list.append(jobcard_data)
            return make_response(jsonify({'customer_info': jobcard_list, 'status': 'Success'}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid filter value', 'status': 'error'}), 400)

    except Exception as e:
        return make_response(jsonify({'message': f'Error: {e}', 'status': 'error'}), 500)
    
@customer.route('/delete_customer/<int:id>', methods=['DELETE'])
@token_required(1, 2, 3, 4)
def delete_customer(user_details, id):
    return delete_item(Customer, user_details, id,"Customer")


# @customer.route('/upload-csv', methods=['POST'])
# @token_required(1, 2, 3, 4)
# def upload_file(user_details):
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#
#     file = request.files['file']
#
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#
#     if file and file.filename.endswith('.csv'):
#         filepath = os.path.join('app/tmp', file.filename)
#         file.save(filepath)
#         company_id = user_details.company_id
#         data = pd.read_csv(filepath)
#
#         for index, row in data.iterrows():
#             if pd.isna(row['full_name']) or pd.isna(row['mobile_number']):
#                continue
#             else:
#                 new_entry = Customer(
#                     company_id=company_id,
#                     full_name=row['full_name'],
#                     address=row['address'] if not pd.isna(row['address']) else "",
#                     email=row['email'] if not pd.isna(row['email']) else "",
#                     mobile_number=row['mobile_number'],
#                     alternet_number=row['alternet_number'] if not pd.isna(row['alternet_number']) else "",
#                 )
#                 db.session.add(new_entry)
#                 db.session.commit()
#
#         return jsonify({"message": "File successfully uploaded and data added to database"}), 201
#
#     return jsonify({"error": "File type not allowed"}), 400
#
#
#
# @customer.route('/download-csv', methods=['GET'])
# @token_required(1, 2, 3, 4)
# def download_csv(user_details):
#     customers= Customer.query.filter(or_(Customer.company_id == user_details.company_id,
#                                          user_details.role_id==1)).all()
#     output = io.StringIO()
#     writer = csv.writer(output)
#     writer.writerow(['full_name', 'address', 'email', 'mobile_number', 'alternate_number'])
#     if customers:
#         for customer in customers:
#             writer.writerow(
#                 [customer.full_name, customer.address, customer.email, customer.mobile_number, customer.alternet_number])
#     output.seek(0)
#     return send_file(io.BytesIO(output.getvalue().encode()),
#                      mimetype='text/csv',
#                      as_attachment=True,
#                      download_name='customer.csv')