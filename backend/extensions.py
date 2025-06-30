# This file defines the extensions used in the Flask application, such as SQLAlchemy for database interactions and JWTManager for handling JSON Web Tokens.
# It initializes these extensions so they can be used throughout the application.

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db  = SQLAlchemy()
jwt = JWTManager()