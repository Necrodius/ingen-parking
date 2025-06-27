# This file defines the configuration for the Flask application, including the database URI.

import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
