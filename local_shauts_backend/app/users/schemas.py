from marshmallow import Schema, fields, post_load, validates, ValidationError,validates_schema
from werkzeug.security import check_password_hash
import re
from app.users.models import User
# from app.companies.models import Company
from flask import request
class UserSchema(Schema):
    affilate_id=fields.Integer(required=False)
    name = fields.String(required=True)
    role_id = fields.Integer(required=False)
    email=fields.String(required=True)
    password = fields.Str(required=True)
    confirm_password=fields.Str(required=True)

    @validates("name")
    def required_name(self, value):
        if not value.strip():
            raise ValidationError("The Name field is required")

    @validates("confirm_password")
    def required_confirmpassword(self, value):
        if not value.strip():
            raise ValidationError("The confirm password field is required")

    @validates_schema()
    def validate_password(self, value,**kwargs):
        if value['password'] != value['confirm_password']:
            raise ValidationError("Password does not match")

    @validates("password")
    def validatespassword(self, value):
        if not value:
            raise ValidationError("The Password field is required")
        if len(value) < 6:
            raise ValidationError("Password must longer than 6")
        
    @validates("email")
    def validates_email(self, value):
        if not value:
            raise ValidationError("The Email or Username field is required")
        # if request.method != 'PUT' and value:
        #     existing_user = User.query.filter_by(email=value).first()
            # existing_email = Company.query.filter_by(email=value).first()
            # if existing_user or existing_email:
            #     raise ValidationError("Email or Username already exists")
        
    @post_load
    def make_user(self, data, **kwargs):
        return data
    
user_schema = UserSchema()
users_schema = UserSchema(many=True)

class LoginSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)
    @validates("password")
    def validatespassword(self, value):
        if not value:
            raise ValidationError("Please enter Password.")
        existing_user = User.query.filter_by(password=value).first()
        if existing_user and not check_password_hash(existing_user.password, self.password):
            raise ValidationError("Invalid Credentials")
        
    @validates("email")
    def validates_email(self, value):
        if not value:
            raise ValidationError("Please enter email address or username.")

    def make_user(self, data, **kwargs):
        return data
    
login_schema = LoginSchema()
login_schemas = LoginSchema(many=True)

class UserUpdateSchema(Schema):
    name = fields.String(required=True)
    phone_num = fields.String(required=True)
    address = fields.String(required=True)
    role_id = fields.Integer(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    confirmPassword = fields.String(required=True)

    @validates("name")
    def required_name(self, value):
        if not value:
            raise ValidationError("The name field is required")

    @validates("phone_num")
    def requiredfirst_name(self, value):
        if not value:
            raise ValidationError("The phone_num field is required")
        
    @validates("role_id")
    def requiredrole_id(self, value):
        if not value:
            raise ValidationError("The role id field is required")
        
    @validates("address")
    def requiredlast_name(self, value):
        if not value:
            raise ValidationError("The address field is required")
        
    @validates("confirmPassword")
    def requierd_confirmpassword(self, value):
        if not value:
            raise ValidationError("The confirm password field is required")
        
    @validates_schema()
    def validate_password(self, value, **kwargs):
        if value['password'] != value['confirmPassword']:
            raise ValidationError("Password does not match")
        
    @validates("password")
    def validatespassword(self, value):
        if not value:
            raise ValidationError("The Password field is required")
        if len(value) < 6:
            raise ValidationError("Password must longer than 6")
    
    @validates("email")
    def validates_email(self, value):
        if not value:
            raise ValidationError("The Email or Username field is required")
        # if request.method != 'PUT' and value:
        #     existing_user = User.query.filter_by(email=value).first()
        #     existing_email = Company.query.filter_by(email=value).first()
        #     if existing_user or existing_email:
        #         raise ValidationError("Email or Username already exists")
        
    @post_load
    def make_user(self, data, **kwargs):
        return data

user_update_schema = UserUpdateSchema()
users_update_schemas = UserUpdateSchema(many=True)


class PasswordSchema(Schema):
    password=fields.String(required=True)
    confirmPassword = fields.String(required=True)

    @validates("confirmPassword")
    def requierd_confirmpassword(self, value):
        if not value:
            raise ValidationError("The confirm password field is required")
        
    @validates_schema()
    def validate_password(self, value, **kwargs):
        if value['password'] != value['confirmPassword']:
            raise ValidationError("Password does not match")
        
    @validates("password")
    def validatespassword(self, value):
        if not value:
            raise ValidationError("The password field is required")
        if len(value) < 6:
            raise ValidationError("Password must longer than 6")

    @post_load
    def make_user(self, data, **kwargs):
        return data
    
password_schema = PasswordSchema()
password_schemas = PasswordSchema(many=True)