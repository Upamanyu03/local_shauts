from marshmallow import Schema, fields, post_load, validates, ValidationError
import re
from app.affilates.models import Affilate
from flask import request
from app.users.models import User

class AffilateSchema(Schema):
    affilate_name = fields.String(required=True)
    email = fields.String(required=True)
    mobile_number = fields.String(required=True)
    address = fields.String(required=True)
    affilate_logo = fields.String(required=False)
    date = fields.String(required=False)
   

    @validates("affilate_name")
    def requiredaffilate_name(self, value):
        if not value.strip():
            raise ValidationError("The Affilate Name field is required")

   
    @validates("email")
    def validates_email(self, value):
        if not value.strip():
            raise ValidationError("The Email or Username field is required")
        # if request.method != 'PUT':
        #     if value:
        #         existing_user = Affilate.query.filter_by(email=value).first()
        #         existing_email = User.query.filter_by(email=value).first()
        #     if existing_user or existing_email:
        #         raise ValidationError("Email or Username already exists")
            
    @post_load
    def make_user(self, data, **kwargs):
        return data

affilate_schema = AffilateSchema()
affilate_schemas = AffilateSchema(many=True)