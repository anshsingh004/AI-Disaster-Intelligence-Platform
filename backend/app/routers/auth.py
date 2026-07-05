from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginInput, VerifyEmailInput, PasswordResetRequest, PasswordResetConfirm
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_refresh_token
from app.core.response import success_response
from app.core.config import settings
from app.core.rate_limit import auth_rate_limiter

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Sets secure HTTP-only cookies on the client response."""
    is_prod = settings.ENV == "production"
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def clear_auth_cookies(response: Response):
    """Removes authentication cookies from the client."""
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")

@router.post("/register", response_model=dict)
def register(data: UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    existing = user_repo.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
        
    user = user_repo.create(data)
    
    # Generate mock email verification token
    user.verification_token = f"verify_{secrets.token_hex(16)}"
    user_repo.update(user)
    
    user_repo.log_security_event(user.email, "REGISTER", "0.0.0.0")
    
    return success_response(data=UserResponse.model_validate(user).model_dump())

@router.post("/login", response_model=dict)
def login(request: Request, response: Response, data: LoginInput, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "0.0.0.0"
    
    # 1. Enforce Rate Limiting
    if not auth_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please wait 5 minutes."
        )
        
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(data.email)
    
    if not user:
        user_repo.log_security_event(data.email, "LOGIN_FAILED_NO_USER", client_ip)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    # 2. Check Account Lockout State
    if user.lockout_until and user.lockout_until > datetime.utcnow():
        lock_remaining = int((user.lockout_until - datetime.utcnow()).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to consecutive failures. Try again in {lock_remaining} minutes."
        )

    # 3. Verify Password credentials
    if not verify_password(data.password, user.hashed_password):
        user_repo.increment_failed_attempts(user)
        user_repo.log_security_event(user.email, "LOGIN_FAILED_BAD_PASSWORD", client_ip)
        
        # Enforce Lockout threshold
        if user.failed_login_attempts >= 5:
            user_repo.lock_account(user, minutes=15)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked for 15 minutes due to consecutive failures."
            )
            
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email or password"
        )

    # 4. Success handling: Reset login counts
    user_repo.reset_failed_attempts(user)
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Track the active refresh token for rotation
    user.current_refresh_token = refresh_token
    user_repo.update(user)
    
    set_auth_cookies(response, access_token, refresh_token)
    user_repo.log_security_event(user.email, "LOGIN_SUCCESS", client_ip)
    
    return success_response(data={
        "user": UserResponse.model_validate(user).model_dump(),
        "access_token": access_token
    })

@router.post("/refresh", response_model=dict)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "0.0.0.0"
    
    # Extract refresh token from cookies
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
        
    payload = decode_refresh_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    email = payload.get("sub")
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    
    if not user or user.current_refresh_token != token:
        # Token rotation violation / reuse detection
        if user:
            user.current_refresh_token = None
            user_repo.update(user)
            user_repo.log_security_event(user.email, "SESSION_REVOKED_COMPROMISED", client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session compromised or expired. Please login again."
        )
        
    # Rotate tokens
    new_access_token = create_access_token(data={"sub": user.email, "role": user.role})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    user.current_refresh_token = new_refresh_token
    user_repo.update(user)
    
    set_auth_cookies(response, new_access_token, new_refresh_token)
    user_repo.log_security_event(user.email, "TOKEN_ROTATION_SUCCESS", client_ip)
    
    return success_response(data={"access_token": new_access_token})

@router.post("/logout", response_model=dict)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if token:
        payload = decode_refresh_token(token)
        if payload:
            email = payload.get("sub")
            user_repo = UserRepository(db)
            user = user_repo.get_by_email(email)
            if user:
                # Revoke token state (Session Invalidation)
                user.current_refresh_token = None
                user_repo.update(user)
                user_repo.log_security_event(user.email, "LOGOUT", request.client.host if request.client else "0.0.0.0")
                
    clear_auth_cookies(response)
    return success_response(data={"message": "Logged out successfully"})

@router.post("/verify-email", response_model=dict)
def verify_email(data: VerifyEmailInput, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_verification_token(data.token)
    if not user or user.email != data.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
        
    user.is_verified = True
    user.verification_token = None
    user_repo.update(user)
    
    user_repo.log_security_event(user.email, "EMAIL_VERIFICATION_SUCCESS", "0.0.0.0")
    
    return success_response(data={"message": "Account verified successfully"})

@router.post("/reset-password-request", response_model=dict)
def reset_password_request(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(data.email)
    if user:
        # Generate reset token
        user.password_reset_token = f"reset_{secrets.token_hex(16)}"
        user_repo.update(user)
        user_repo.log_security_event(user.email, "PASSWORD_RESET_REQUEST", "0.0.0.0")
        
    # Always return success to prevent email enumeration attacks
    return success_response(data={"message": "Password reset instructions sent if email exists"})

@router.post("/reset-password", response_model=dict)
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.get_by_reset_token(data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
        
    user.hashed_password = get_password_hash(data.new_password)
    user.password_reset_token = None
    user.failed_login_attempts = 0
    user.lockout_until = None
    user_repo.update(user)
    
    user_repo.log_security_event(user.email, "PASSWORD_RESET_COMMIT", "0.0.0.0")
    
    return success_response(data={"message": "Password updated successfully"})
