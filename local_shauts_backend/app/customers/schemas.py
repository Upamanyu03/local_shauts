from marshmallow import fields, Schema

class CustomerSchema(Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    address = fields.String(required=True)
    contact_no = fields.String(required=True)
    gender = fields.String(required=True)
    age = fields.String(required=True)

customer_schema = CustomerSchema()


