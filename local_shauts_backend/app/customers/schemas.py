from marshmallow import Schema, fields, post_load, ValidationError, validates
import re

class CustomerSchema(Schema):
    full_name = fields.String(required=True)
    address = fields.String(required=True)
    company_id = fields.String(required=True)
    email = fields.String(required=True)
    mobile_number = fields.String(required=True)
    alternet_number = fields.String(required=True)

    @validates("full_name")
    def validates_name(self, value):
        if not value.strip():
            raise ValidationError("The Full name field is required", field_name='full_name')

    @validates("mobile_number")
    def validates_mobile_number(self, value):
        if not value.strip():
            raise ValidationError("The Mobile number field is required", field_name='mobile_number')

    @post_load
    def make_customer(self, data, **kwargs):
        return data

customer_schema = CustomerSchema()
