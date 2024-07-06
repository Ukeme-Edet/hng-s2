#!/usr/bin/env python
"""
This file defines the User model.
"""

import uuid
from flask import Flask
from sqlalchemy import Column, String
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """
    User model.
    """

    __tablename__ = "users"

    userId = Column(
        String(50),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        unique=True,
    )
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(50))
    organisations = db.relationship(
        "Organisation", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(self, firstName, lastName, email, password="", phone=""):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password
        self.phone = phone

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "userId": self.userId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "phone": self.phone,
        }

    def __repr__(self):
        return f"<User {self.email}>"
