from marshmallow import Schema, fields, post_load, validates, ValidationError

class ProductSchema(Schema):
    company_id = fields.String(required=True)
    product_name = fields.String(required=True)
    product_type = fields.String(required=True)
    manufacturer = fields.String(required=True)
    price=fields.String(required=True)

    @validates("product_name")
    def requiredfirst_name(self, value):
        if not value:
            raise ValidationError("The Product Name field is required")

    @post_load
    def make_user(self, data, **kwargs):
        return data

product_schema = ProductSchema()
product_schemas = ProductSchema(many=True)