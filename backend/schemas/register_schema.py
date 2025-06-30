# This file contains the RegisterSchema class which defines the schema for user registration data validation using Marshmallow.
# It includes fields for email, password, first name, and last name, with appropriate validation and error messages.
# It is used to ensure that the data provided during user registration meets the required format and constraints.

from marshmallow import Schema, fields

class RegisterSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={"required": "Email is required."}
    )
    password = fields.String(
        required=True,
        load_only=True,
        error_messages={"required": "Password is required."}
    )
    first_name = fields.String(
        required=True,
        error_messages={"required": "First name is required."}
    )
    last_name = fields.String(
        required=True,
        error_messages={"required": "Last name is required."}
    )

register_schema = RegisterSchema()
