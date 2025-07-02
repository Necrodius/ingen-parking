# This file contains the LoginSchema class which is used for validating user login data in a Flask application using Marshmallow.
# It includes fields for email and password, with appropriate validation and error messages.

from marshmallow import Schema, fields

class LoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={"required": "Email is required."}
    )
    
    password = fields.String(
        required=True,
        load_only=True,
        error_messages={"required": "Password is required."}
    )

login_schema = LoginSchema()
