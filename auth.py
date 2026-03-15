"""
auth.py - JWT token creation and verification, plus password hashing.

Uses python-jose for JWT and passlib[bcrypt] for password hashing.
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

# ──────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────

# In production, load SECRET_KEY from environment variables.
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-random-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # tokens valid for 1 hour

# ──────────────────────────────────────────────
#  Password hashing
# ──────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ──────────────────────────────────────────────
#  JWT helpers
# ──────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Create a signed JWT containing the supplied data (claims).
    Adds an 'exp' (expiration) claim automatically.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT.
    Returns the payload dict on success, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
