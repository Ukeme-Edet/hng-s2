#!/usr/bin/env python
"""
This file defines all the routes for the authentication blueprint.
"""
from datetime import datetime
import datetime as dt
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models.organisation import Organisation
from models.user import User
from app import db

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
def register():
    """
    This route is used to register a new user.

    Returns:
        A JSON response with the user data and access token
    """
    required = ["firstName", "lastName", "email", "password"]
    data = request.get_json()
    err = {"errors": []}
    if not all(key in data for key in required):
        for key in required:
            if key not in data:
                err["errors"].append(
                    {"field": key, "message": f"{key} is required"}
                )
            elif not data[key]:
                err["errors"].append(
                    {"field": key, "message": f"{key} cannot be empty"}
                )
    if "email" in data and User.query.filter_by(email=data["email"]).first():
        err["errors"].append(
            {"field": "email", "message": "Email already exists"}
        )
    if err["errors"]:
        return jsonify(err), 422
    user = User(
        firstName=data["firstName"],
        lastName=data["lastName"],
        email=data["email"],
        phone=data["phone"] if "phone" in data else None,
    )
    user.set_password(data["password"])
    db.session.add(user)
    try:
        users_org = Organisation(
            name=f"{user.firstName}'s Organisation",
        )
        user.organisations.append(users_org)
        db.session.add(users_org)
        db.session.commit()
        access_token = create_access_token(
            {
                "userId": user.userId,
                "sub": user.userId,
                "exp": datetime.now(dt.UTC) + dt.timedelta(minutes=5),
            }
        )
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": access_token,
                        "user": user.to_dict(),
                    },
                }
            ),
            201,
        )
    except Exception as e:
        print(e)
        return (
            jsonify(
                {
                    "status": "Bad Request",
                    "message": "Registration was not successful",
                    "statusCode": 400,
                }
            ),
            400,
        )


@auth.route("/login", methods=["POST"])
def login():
    """
    This route is used to login a user.

    Returns:
        A JSON response with the user data and access token
    """
    required = ["email", "password"]
    bad_request = {
        "status": "Bad Request",
        "message": "Authentication failed",
        "statusCode": 401,
    }
    err = {"errors": []}
    data = request.get_json()
    if not all(key in data for key in required):
        for key in required:
            if key not in data:
                err["errors"].append(
                    {"field": key, "message": f"{key} is required"}
                )
            elif not data[key]:
                err["errors"].append(
                    {"field": key, "message": f"{key} cannot be empty"}
                )
        return jsonify(err), 422
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify(bad_request), 401
    access_token = create_access_token(
        identity={
            "userId": user.userId,
            "sub": user.userId,
            "exp": datetime.now(dt.UTC) + dt.timedelta(minutes=5),
        }
    )
    return (
        jsonify(
            {
                "status": "success",
                "message": "Login successful",
                "data": {"accessToken": access_token, "user": user.to_dict()},
            }
        ),
        200,
    )
