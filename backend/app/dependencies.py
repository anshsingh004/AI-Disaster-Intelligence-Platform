from fastapi import Depends, HTTPException, Request, status
  from sqlalchemy.orm import Session
  from typing import Optional, List
  
  from app.db import get_db
  from app.core.security import decode_access_token
  from app.repositories.user_repository import UserRepository
  from app.models.user import User
  
  def get_token_from_request(request: Request) -> Optional[str]:
      """Helper to resolve access token from either header or HTTP-only cookie."""
      auth_header = request.headers.get("Authorization")
      if auth_header and auth_header.startswith("Bearer "):
          return auth_header.split(" ")[1]
          
      # Fallback to secure HTTP-only cookies
      cookie_token = request.cookies.get("access_token")
      if cookie_token:
          return cookie_token
          
      return None
  
  def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
      """FastAPI dependency to extract and validate the current authenticated user session."""
      token = get_token_from_request(request)
      if not token:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Not authenticated"
          )
          
      payload = decode_access_token(token)
      if not payload:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid or expired access token"
          )
          
      email = payload.get("sub")
      if not email:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid token payload credentials"
          )
          
      user_repo = UserRepository(db)
      user = user_repo.get_by_email(email)
      if not user:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="User session profile not found"
          )
          
      if not user.is_active:
          raise HTTPException(
              status_code=status.HTTP_403_FORBIDDEN,
              detail="User account is currently deactivated"
          )
          
      return user
  
  class RequireRole:
      """FastAPI dependency wrapper checking RBAC roles constraint."""
      
      def __init__(self, allowed_roles: List[str]):
          self.allowed_roles = allowed_roles
  
      def __call__(self, current_user: User = Depends(get_current_user)) -> User:
          if current_user.role not in self.allowed_roles:
              raise HTTPException(
                  status_code=status.HTTP_403_FORBIDDEN,
                  detail=f"Operation not permitted. Required roles: {self.allowed_roles}"
              )
          return current_user
