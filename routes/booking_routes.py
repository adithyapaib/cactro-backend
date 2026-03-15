"""
booking_routes.py - Ticket booking endpoints (customers only).
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from schemas import BookingCreate, BookingResponse
from models import Event, Booking, User
from dependencies import get_db, require_customer

router = APIRouter(tags=["Bookings"])


# ──────────────────────────────────────────────
#  Background task: booking confirmation email
# ──────────────────────────────────────────────

def send_booking_confirmation(customer_email: str, event_title: str):
    """Simulate sending a booking confirmation email."""
    print(
        f"Sending booking confirmation email to {customer_email} "
        f"for event {event_title}"
    )


# ──────────────────────────────────────────────
#  Booking endpoint
# ──────────────────────────────────────────────

@router.post(
    "/events/{event_id}/book",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def book_tickets(
    event_id: int,
    booking_data: BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    customer: User = Depends(require_customer),
):
    """
    Book tickets for an event. Only customers can book.

    Validations:
      - Event must exist.
      - Requested tickets must be at least 1.
      - Cannot book more tickets than available.
    """
    # Find the event
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    # Validate ticket count
    if booking_data.tickets < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must book at least 1 ticket",
        )

    if booking_data.tickets > event.available_tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {event.available_tickets} tickets available",
        )

    # Reduce available tickets
    event.available_tickets -= booking_data.tickets

    # Create booking record
    new_booking = Booking(
        event_id=event.id,
        customer_id=customer.id,
        tickets_booked=booking_data.tickets,
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    # Trigger background confirmation email
    background_tasks.add_task(
        send_booking_confirmation, customer.email, event.title
    )

    return new_booking
