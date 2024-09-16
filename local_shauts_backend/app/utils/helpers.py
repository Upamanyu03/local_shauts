import boto3
import os
import jwt
from flask import request, jsonify, make_response
from app.users.models import User
from functools import wraps
from sqlalchemy import or_, desc, asc, and_
from datetime import datetime, timezone
from flask import jsonify, make_response
from app import db
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from flask import json 
from datetime import datetime



s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
bucket_name = os.getenv("S3_ASSETS_BUCKET")



def upload_to_s3(file, prefix, filename="", content_type="", acl="public-read"):
    if not filename:
        filename = secure_filename(file.filename)
    if not content_type:
        content_type = file.content_type

    s3_key = f"{prefix}/{filename}".strip('/')

    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=file,
            ContentType=content_type,
            ACL=acl,
            ContentDisposition='inline'
        )
    except ClientError as e:
        return {"errors": str(e)}
    print(s3_key)
    return "success"



def delete_s3_objects(prefix):
    try:
        s3 = boto3.client('s3')
        objects_to_delete = []
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
        while objects_to_delete:
            delete_batch = objects_to_delete[:1000]
            s3.delete_objects(Bucket=bucket_name, Delete={'Objects': delete_batch})
            objects_to_delete = objects_to_delete[1000:]
    except Exception as e:
        print(f"Error deleting files from S3: {str(e)}")



def token_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return make_response(jsonify({"message": "Login required!"}), 401)
            try:
                token = token.split(' ')[1]
                data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
                current_user = User.query.filter_by(id=data['user_id']).first()
                if not current_user:
                    raise Exception("User not found")
                if roles and current_user.role_id not in roles:
                    return make_response(jsonify({"message": "Unauthorized access!"}), 403)
                if current_user.role_id != 1:
                    affilate = current_user.affilate
                    if affilate:
                        date_info = json.loads(affilate.date)
                        sub_end_str = date_info.get('sub_end', "")
                        if sub_end_str:
                            sub_end = datetime.strptime(sub_end_str, '%Y-%m-%d').date()
                            today = datetime.today().date()
                            if sub_end < today:
                                return make_response(jsonify({"subscription": "Expired"}), 403)
                return f(current_user, *args, **kwargs)
            except jwt.ExpiredSignatureError:
                return make_response(jsonify({"message": "Expired token!"}), 401)
            except jwt.InvalidTokenError:
                return make_response(jsonify({"message": "Invalid token!"}), 401)
            except Exception as e:
                return make_response(jsonify({"message": "Error decoding token: {}".format(str(e))}), 401)
        return wrapper
    return decorator

def s3_file_exists(path_to_save, filename):
    import boto3
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket_name, Key=f'{path_to_save}/{filename}')
        return True
    except:
        return False

def query_items(query, user_details, search, direction, timestamp, role_filter_field, search_fields):
    if user_details.role_id != 1:
        query = query.filter_by(affilate_id=user_details.affilate_id)
    if search:
        search_filters = or_(*[field.ilike(f'%{search}%') for field in search_fields])
        query = query.filter(search_filters)
    if timestamp and direction in ['up', 'down']:
        try:
            filter_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
        except (ValueError, OSError):
            filter_time = None
        if filter_time:
            if direction == 'up':
                query = query.filter(role_filter_field > filter_time).order_by(asc(role_filter_field))
            elif direction == 'down':
                query = query.filter(role_filter_field < filter_time).order_by(desc(role_filter_field))
        else:
            query = query.order_by(desc(role_filter_field))
    else:
        query = query.order_by(desc(role_filter_field))
    return query.limit(10).all()


def single_query(model, user_details, id):
    print(model.query.filter(
        and_(
            model.id == id,
            or_(
                user_details.affilate_id == model.affilate_id,
                user_details.role_id == 1
            )
        )
    ))
   

def delete_item(model, user_details, id, message):
    try:
        item = model.query.filter_by(id=id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return make_response(jsonify({'message': f'{message} deleted successfully', 'status': 'success'}), 200)
        return make_response(jsonify({'message': f'{message} not found', 'status': 'error'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting {message}: {e}', 'status': 'error'}), 500)


    
def handle_action(data, action_type='operation'):
    message_type = {
        'create' : 'user created successfully',
        'update' : 'user updated successfully'
    }
    try:
        if action_type == 'create':
            db.session.add(data)

        db.session.commit()
        message = message_type.get(action_type,'operation successfull')
        return make_response(jsonify({'message' :message, 'status' :'success'}), 200)
    except Exception as e:
        return make_response(jsonify({'message' : str(e), 'status':'error'}), 500)

        


   