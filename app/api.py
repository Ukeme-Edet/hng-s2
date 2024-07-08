#!/usr/bin/env python
"""
This file defines all the routes for the API blueprint.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.organisation import Organisation
from app import db

api = Blueprint("api", __name__)

server_error = {
    "status": "failure",
    "message": "An error occurred while processing your request",
}


@api.route("/users/<id>", methods=["GET"], endpoint="get_user")
@jwt_required()
def get_user(id):
    try:
        current_user = User.query.filter_by(
            userId=get_jwt_identity()["userId"]
        ).first()
        user = User.query.filter_by(userId=id).first()
        if user.userId != current_user.userId and not any(
            [
                organisation
                for organisation in current_user.organisations
                if user in organisation.users
            ]
        ):
            return (
                jsonify(
                    {
                        {
                            "status": "Bad Request",
                            "message": "Authentication failed",
                            "statusCode": 401,
                        }
                    }
                ),
                401,
            )
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "data": user.to_dict(),
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify(server_error), 500


@api.route("/organisations", methods=["GET"], endpoint="get_organisations")
@jwt_required()
def get_organisations():
    user_id = get_jwt_identity()["userId"]
    user = User.query.filter_by(userId=user_id).first()
    try:
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Organisations retrieved successfully",
                    "data": {
                        "organisations": [
                            organisation.to_dict()
                            for organisation in user.organisations
                        ]
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify(server_error), 500


@api.route("/organisations/<id>", methods=["GET"], endpoint="get_organisation")
@jwt_required()
def get_organisation(id):
    user_id = get_jwt_identity()["userId"]
    try:
        organisation = Organisation.query.filter_by(org_id=id).first()
        response = (
            jsonify(
                {
                    "status": "success",
                    "message": "Organisation retrieved successfully",
                    "data": organisation.to_dict(),
                }
            )
            if organisation
            and organisation
            in User.query.filter_by(userId=user_id).first().organisations
            else (
                jsonify(
                    {
                        "status": "Bad Request",
                        "message": "Authentication failed",
                        "statusCode": 401,
                    }
                )
                if organisation
                else jsonify(
                    {
                        "status": "failure",
                        "message": "Organisation not found",
                        "statusCode": 404,
                    }
                )
            )
        )
        if response.json["status"] == "failure":
            response.status_code = 404
        if response.json["status"] == "Bad Request":
            response.status_code = 401
        return response
    except Exception as e:
        return jsonify(server_error), 500


@api.route("/organisations", methods=["POST"], endpoint="create_organisation")
@jwt_required()
def create_organisation():
    try:
        data = request.get_json()
        organisation = Organisation(
            name=data["name"], description=data.get("description", "")
        )
        user = User.query.filter_by(
            userId=get_jwt_identity()["userId"]
        ).first()
        user.organisations.append(organisation)
        db.session.add(organisation)
        db.session.commit()
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": organisation.to_dict(),
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify(server_error), 400


@api.route(
    "/organisations/<orgId>/users",
    methods=["POST"],
    endpoint="add_user_to_organisation",
)
def add_user_to_organisation(orgId):
    try:
        data = request.get_json()
        if "userId" not in data:
            return jsonify(
                {
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": 400,
                },
                400,
            )
        organisation = Organisation.query.get(orgId)
        user = User.query.get(data["userId"])
        if not organisation or not user:
            return jsonify(
                {
                    "status": "failure",
                    "message": "Organisation or user not found",
                },
                404,
            )
        user.organisations.append(organisation)
        db.session.commit()
        return jsonify(
            {
                "status": "success",
                "message": "User added to organisation successfully",
            }
        )
    except Exception as e:
        return jsonify(server_error), 500
