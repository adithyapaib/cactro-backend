"""
models.py - SQLAlchemy ORM models for the Event Booking System.

Three tables:
  - users:    stores organizers and customers
  - events:   stores event details (linked to an organizer)
  - bookings: stores ticket bookings (linked to event + customer)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database import Base


class User(Base):
    """User model — covers both organizers and customers."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # "organizer" or "customer"

    # Relationships
    events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")


class Event(Base):
    """Event model — created and managed by organizers."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    event_date = Column(DateTime, nullable=False)
    total_tickets = Column(Integer, nullable=False)
    available_tickets = Column(Integer, nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    organizer = relationship("User", back_populates="events")
    bookings = relationship("Booking", back_populates="event", cascade="all, delete-orphan")


class Booking(Base):
    """Booking model — records ticket purchases by customers."""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tickets_booked = Column(Integer, nullable=False)
    booking_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    event = relationship("Event", back_populates="bookings")
    customer = relationship("User", back_populates="bookings")
