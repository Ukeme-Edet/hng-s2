#!/usr/bin/env python
"""
This is the main file that will be used to run the server.
"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import environ

load_dotenv(override=True)

db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    """
    This function creates the app and returns it.
    """
    app = Flask(__name__)

    # Configuring the app
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = environ.get("JWT_SECTET_KEY")

    from app.api import api
    from app.auth import auth

    # Registering the blueprints
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(auth, url_prefix="/auth")

    from models.user import User
    from models.organisation import Organisation

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    app.url_map.strict_slashes = False
    return app
