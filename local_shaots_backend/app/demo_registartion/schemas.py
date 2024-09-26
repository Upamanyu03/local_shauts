from marshmallow import Schema, fields, post_load, ValidationError, validates_schema
import re

class DemoSchema(Schema):
    full_name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    state = fields.String(required=True)
    demo_date = fields.String(required=True)

    @validates_schema
    def validate_demo_schema(self, data, **kwargs):
        if not data['full_name'].strip():
            raise ValidationError("The Full name field is required", field_name='full_name')
        if not data['phone'].strip():
            raise ValidationError("The Phone number field is required", field_name='phone')
        if not data['state'].strip():
            raise ValidationError("The State name field is required", field_name='state')
        if not data['demo_date'].strip():
            raise ValidationError("The Date field is required", field_name='demo_date')
        if not data['email'].strip():
            raise ValidationError("The Email field is required", field_name='email')
        if not re.match("[^@]+@[^@]+\.[^@]+", data['email']):
            raise ValidationError("Invalid email format", field_name='email')

    @post_load
    def make_demo(self, data, **kwargs):
        return data

demo_schema = DemoSchema()