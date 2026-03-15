"""
schemas.py - Pydantic schemas for request/response validation.

Pydantic models validate incoming JSON and shape outgoing responses.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────────
#  Auth Schemas
# ──────────────────────────────────────────────

class UserRegister(BaseModel):
    """Schema for user registration."""
    name: str
    email: EmailStr
    password: str
    role: str  # "organizer" or "customer"


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema returned after registration / in token payload context."""
    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


# ──────────────────────────────────────────────
#  Event Schemas
# ──────────────────────────────────────────────

class EventCreate(BaseModel):
    """Schema for creating a new event."""
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: datetime
    total_tickets: int


class EventUpdate(BaseModel):
    """Schema for updating an existing event (all fields optional)."""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    event_date: Optional[datetime] = None
    total_tickets: Optional[int] = None


class EventResponse(BaseModel):
    """Schema for returning event details."""
    id: int
    title: str
    description: Optional[str]
    location: Optional[str]
    event_date: datetime
    total_tickets: int
    available_tickets: int
    organizer_id: int

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
#  Booking Schemas
# ──────────────────────────────────────────────

class BookingCreate(BaseModel):
    """Schema for booking tickets."""
    tickets: int


class BookingResponse(BaseModel):
    """Schema for returning booking details."""
    id: int
    event_id: int
    customer_id: int
    tickets_booked: int
    booking_time: datetime

    model_config = {"from_attributes": True}
