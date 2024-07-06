#!/usr/bin/env python
"""
This file defines all the tests for the authentication blueprint.
"""
import unittest
from datetime import datetime, timedelta
import datetime as dt
from flask import current_app, json
from app import create_app, db
from models.user import User
from models.organisation import Organisation
import jwt


class AuthTestCase(unittest.TestCase):
    """
    Test cases for the authentication blueprint.
    """

    def setUp(self):
        """
        Set up the test cases.
        """
        # Create the app and set the testing configuration
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """
        Tear down the test cases.
        """
        # Drop all tables and remove the session
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_token_generation(self):
        """
        Test token generation.
        """
        # Test that a token is generated successfully
        with self.app.app_context():
            user = User(
                firstName="John", lastName="Doe", email="john@test.com"
            )
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # Generate a token
            expiration = datetime.now(dt.UTC) + timedelta(minutes=5)
            token = jwt.encode(
                {"userId": user.userId, "sub": user.userId, "exp": expiration},
                current_app.config["JWT_SECRET_KEY"],
                algorithm="HS256",
            )

            # Decode the token
            decoded_token = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )

            # Check that the token is decoded correctly
            self.assertEqual(decoded_token["userId"], user.userId)
            self.assertAlmostEqual(
                decoded_token["exp"], expiration.timestamp(), delta=1
            )

    def test_register_user_successfully_with_default_organisation(self):
        """
        Test registering a user successfully.
        """
        # Check that the user is registered successfully
        response = self.client.post(
            "/auth/register",
            json={
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@test.com",
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        # Check that the response contains the expected data
        self.assertIn("accessToken", data["data"])
        self.assertEqual(data["data"]["user"]["firstName"], "John")
        self.assertEqual(data["data"]["user"]["lastName"], "Doe")
        self.assertEqual(data["data"]["user"]["email"], "john@test.com")

        # Check that the default organisation was created
        with self.app.app_context():
            user = User.query.filter_by(email="john@test.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(len(user.organisations), 1)
            self.assertEqual(user.organisations[0].name, "John's Organisation")

    def test_login_user_successfully(self):
        """
        Test logging in a user successfully.
        """
        with self.app.app_context():
            user = User(
                firstName="John", lastName="Doe", email="john@test.com"
            )
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
        # Check that the user is logged in successfully
        response = self.client.post(
            "/auth/login",
            json={"email": "john@test.com", "password": "password"},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        # Check that the response contains the expected data
        self.assertIn("accessToken", data["data"])
        self.assertEqual(data["data"]["user"]["email"], "john@test.com")

    def test_user_login_and_access_organisation(self):
        """
        Test user login and access organisation.
        """
        with self.app.app_context():
            user = User(
                firstName="John",
                lastName="Doe",
                email="john1@test.com",
                phone="1234567890",
            )
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

            # log in user
            response = self.client.post(
                "/auth/login",
                json={"email": f"{user.email}", "password": "password"},
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            token = data["data"]["accessToken"]
            headers = {"Authorization": f"Bearer {token}"}

            # create organisation
            response = self.client.post(
                "/api/organisations",
                json={"name": "John's Org"},
                headers=headers,
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data)
            org_id = data["data"]["orgId"]

            # get organisation
            response = self.client.get(
                f"/api/organisations/{org_id}", headers=headers
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data["data"]["name"], "John's Org")

    def test_register_fails_if_required_fields_are_missing(self):
        """
        Test case to verify that registration fails if required fields are missing.
        """
        required_fields = ["firstName", "lastName", "email", "password"]
        # Check that registration fails if required fields are missing
        for field in required_fields:
            user_data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@test.com",
                "password": "password",
            }
            user_data.pop(field)
            response = self.client.post("/auth/register", json=user_data)
            self.assertEqual(response.status_code, 422)
            data = json.loads(response.data)
            self.assertTrue(
                any(error["field"] == field for error in data["errors"])
            )

    def test_register_fails_if_duplicate_email(self):
        """
        Test case to verify that registration fails if a duplicate email is used.
        """
        with self.app.app_context():
            user = User(
                firstName="John", lastName="Doe", email="john@test.com"
            )
            user.set_password("password")
            db.session.add(user)
            db.session.commit()

        # Check that registration fails if a duplicate email is used
        response = self.client.post(
            "/auth/register",
            json={
                "firstName": "Jane",
                "lastName": "Doe",
                "email": "john@test.com",
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 422)
        data = json.loads(response.data)

        # Check that the response contains the expected data
        self.assertTrue(
            any(error["field"] == "email" for error in data["errors"])
        )

    def test_organisation_access_control(self):
        """
        Test organisation access control.
        """
        # Check that a user can only access their own organisation
        with self.app.app_context():
            user1 = User(
                firstName="John", lastName="Doe", email="john@test.com"
            )
            user2 = User(
                firstName="Jane", lastName="Doe", email="jane@test.com"
            )
            org1 = Organisation(name="John's Org")
            org2 = Organisation(name="Jane's Org")
            user1.organisations.append(org1)
            user2.organisations.append(org2)
            user1.set_password("password")
            user2.set_password("password")
            db.session.add_all([user1, user2, org1, org2])
            db.session.commit()

            # Log in user1
            response = self.client.post(
                "/auth/login",
                json={"email": "john@test.com", "password": "password"},
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            token = data["data"]["accessToken"]
            headers = {"Authorization": f"Bearer {token}"}

            # Check that user1 can access org1 but not org2
            response = self.client.get(
                f"/api/organisations/{org2.org_id}", headers=headers
            )
            self.assertEqual(response.status_code, 401)

            # Check that user1 can access org1
            response = self.client.get(
                f"/api/organisations/{org1.org_id}", headers=headers
            )
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
