from flask import Blueprint, request, jsonify, make_response
from app.utils.helpers import token_required
from app.roles.models import Roles
from app.users.models import User

roles = Blueprint('roles', __name__)

@roles.route('/get-roles',methods=['GET'])
@token_required(1, 2)
def get_roles(user_details):
    try:
        search = request.args.get('search')
        if search:
            roles = Roles.query.filter(Roles.role_name.ilike(f'%{search}%')).all()
        else:
            roles = Roles.query.all()
        if roles:
            serialized_roles = [{
                'id': role.id,
                'role_name': role.role_name,
                'created_at': role.created_at,
                'updated_at': role.updated_at,
            } for role in roles]
            return make_response(jsonify({'roles': serialized_roles}), 200)
        return make_response(jsonify({'message': 'roles not found', "status": "error"}), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'error: {e}', "status": "error"}), 500)