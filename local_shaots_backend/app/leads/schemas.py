from marshmallow import Schema, fields, post_load, validates, ValidationError,validates_schema
from werkzeug.security import check_password_hash

from app.leads.models import Leads
from datetime import datetime, timezone, timedelta



class Lead_Schema(Schema):
    business_name = fields.String(required=True)
    contact_name = fields.String(required=True)
    phone_number = fields.String(required=True)
    email = fields.String(required=True)
    bussiness_address = fields.String(required=True)
    service_interest = fields.Integer(required=True)
    lead_status = fields.Integer(required=True)
    notes = fields.String(required=True)
    assigned_affiliate = fields.Integer(required=True)


    @validates("business_name")
    def business_name_check(self, value):
        if not value.strip():
            raise ValidationError("The Business name is filed required")
        # lead = Leads.query.filter_by(business_name=value).first()
        # if lead:
        #     raise ValidationError("The Business name is filed exist")


    @post_load
    def make_lead(self, data, **kwargs):
        return data

lead_schema = Lead_Schema()