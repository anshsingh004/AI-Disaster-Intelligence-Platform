import unittest
import os
import sys
from datetime import datetime

# Ensure root path is configured for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import Base, get_db
from app.models.user import User

# Configure isolated testing SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        cls.client = TestClient(app)
        
        # Mock auth rate limiter to always allow requests during unit testing
        from app.core.rate_limit import auth_rate_limiter
        cls._original_is_allowed = auth_rate_limiter.is_allowed
        auth_rate_limiter.is_allowed = lambda ip: True

    @classmethod
    def tearDownClass(cls):
        from app.core.rate_limit import auth_rate_limiter
        auth_rate_limiter.is_allowed = cls._original_is_allowed
        
        # Dispose connection pool to release test SQLite file lock on Windows
        engine.dispose()
        if os.path.exists("./test_auth.db"):
            try:
                os.remove("./test_auth.db")
            except PermissionError:
                pass

    def test_01_user_registration_and_login(self):
        # 1. Test Register Endpoint
        register_payload = {
            "name": "EOC Incident Commander",
            "email": "commander@terra-aura.dev",
            "password": "securepassword123",
            "role": "EOC_LEAD",
            "clearance_level": "Beta"
        }
        res = self.client.post("/api/v1/auth/register", json=register_payload)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()
        self.assertTrue(res_data["success"])
        self.assertEqual(res_data["data"]["email"], "commander@terra-aura.dev")
        self.assertEqual(res_data["data"]["role"], "EOC_LEAD")

        # 2. Test Login Endpoint
        login_payload = {
            "email": "commander@terra-aura.dev",
            "password": "securepassword123"
        }
        res_login = self.client.post("/api/v1/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        cookies = res_login.cookies
        self.assertIn("access_token", cookies)
        self.assertIn("refresh_token", cookies)
        
        login_data = res_login.json()
        self.assertTrue(login_data["success"])
        self.assertEqual(login_data["data"]["user"]["email"], "commander@terra-aura.dev")

    def test_02_login_invalid_credentials_and_lockout(self):
        bad_login = {
            "email": "commander@terra-aura.dev",
            "password": "wrongpassword"
        }
        # First 4 attempts fail with 400
        for i in range(4):
            res = self.client.post("/api/v1/auth/login", json=bad_login)
            self.assertEqual(res.status_code, 400)
            self.assertIn("Invalid email or password", res.json()["error"])
            
        # 5th attempt locks the account with 403 status code
        res_lock = self.client.post("/api/v1/auth/login", json=bad_login)
        self.assertEqual(res_lock.status_code, 403)
        self.assertIn("locked", res_lock.json()["error"])

    def test_03_email_verification_flow(self):
        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == "commander@terra-aura.dev").first()
        token = user.verification_token
        db.close()

        verify_payload = {
            "email": "commander@terra-aura.dev",
            "token": token
        }
        res = self.client.post("/api/v1/auth/verify-email", json=verify_payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])
        self.assertIn("verified successfully", res.json()["data"]["message"])

    def test_04_password_reset_flow(self):
        # 1. Reset Request
        req_payload = {"email": "commander@terra-aura.dev"}
        res_req = self.client.post("/api/v1/auth/reset-password-request", json=req_payload)
        self.assertEqual(res_req.status_code, 200)
        self.assertTrue(res_req.json()["success"])

        db = TestingSessionLocal()
        user = db.query(User).filter(User.email == "commander@terra-aura.dev").first()
        reset_token = user.password_reset_token
        db.close()

        # 2. Reset Password Confirm
        confirm_payload = {
            "token": reset_token,
            "new_password": "newsecurepassword456"
        }
        res_confirm = self.client.post("/api/v1/auth/reset-password", json=confirm_payload)
        self.assertEqual(res_confirm.status_code, 200)
        self.assertTrue(res_confirm.json()["success"])

        # 3. Verify Login with New Password
        login_payload = {
            "email": "commander@terra-aura.dev",
            "password": "newsecurepassword456"
        }
        res_login = self.client.post("/api/v1/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
