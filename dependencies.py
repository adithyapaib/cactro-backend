"""
dependencies.py - FastAPI dependency functions.

Provides:
  - get_db()              → database session per request
  - get_current_user()    → extract and validate JWT from Authorization header
  - require_organizer()   → ensure the current user is an organizer
  - require_customer()    → ensure the current user is a customer
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from auth import decode_access_token

# OAuth2 scheme — expects "Authorization: Bearer <token>" header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    """Yield a database session, ensuring it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT, look up the user in the database,
    and return the User ORM object.
    Raises 401 if the token is invalid or user not found.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_organizer(current_user: User = Depends(get_current_user)) -> User:
    """Allow only users with the 'organizer' role."""
    if current_user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organizers can access this endpoint",
        )
    return current_user


def require_customer(current_user: User = Depends(get_current_user)) -> User:
    """Allow only users with the 'customer' role."""
    if current_user.role != "customer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can access this endpoint",
        )
    return current_user
