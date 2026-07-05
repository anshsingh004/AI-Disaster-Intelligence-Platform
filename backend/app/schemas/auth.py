from pydantic import BaseModel, Field

class LoginInput(BaseModel):
    email: str = Field(..., description="User sign in email")
    password: str = Field(..., description="User sign in password")

class VerifyEmailInput(BaseModel):
    email: str
    token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=100)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
