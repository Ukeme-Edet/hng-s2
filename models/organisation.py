#!/usr/bin/env python
"""
This file defines the Organisation model.
"""

import uuid
from sqlalchemy import Column, String
from app import db


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
    # define foreign key
    owner_id = Column(
        String(50), db.ForeignKey("users.userId"), nullable=False
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
