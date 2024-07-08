#!/usr/bin/env python
"""
This file defines the Organisation model.
"""

import uuid
from sqlalchemy import Column, ForeignKey, String, Table
from app import db

organisation_user_table = Table(
    "organisation_user",
    db.Model.metadata,
    Column("org_id", String(50), ForeignKey("organisations.org_id")),
    Column("user_id", String(50), ForeignKey("users.userId")),
)


class Organisation(db.Model):
    """
    Organisation model.
    """

    __tablename__ = "organisations"

    org_id = Column(
        String(50),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
        unique=True,
    )
    # create a many to many relationship with the User model
    users = db.relationship(
        "User",
        back_populates="organisations",
        secondary=organisation_user_table,
    )
    name = Column(String(50), nullable=False)
    description = Column(String(50))

    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "orgId": self.org_id,
            "name": self.name,
            "description": self.description,
        }

    def __repr__(self):
        return f"<Organisation {self.name}>"
