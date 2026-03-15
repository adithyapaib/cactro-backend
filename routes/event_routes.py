"""
event_routes.py - Event management endpoints.

Organizer-only:  POST /events, PUT /events/{id}, DELETE /events/{id},
                 GET /organizer/events
Public (any authenticated user): GET /events, GET /events/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from schemas import EventCreate, EventUpdate, EventResponse
from models import Event, User, Booking
from dependencies import get_db, get_current_user, require_organizer

router = APIRouter(tags=["Events"])


# ──────────────────────────────────────────────
#  Background task: notify customers of event update
# ──────────────────────────────────────────────

def notify_customers_of_update(event_id: int, event_title: str, db_url: str):
    """
    Simulate sending email notifications to every customer
    who booked tickets for the updated event.
    """
    # Create a fresh session for the background task
    from database import SessionLocal
    db = SessionLocal()
    try:
        bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
        for booking in bookings:
            customer = db.query(User).filter(User.id == booking.customer_id).first()
            if customer:
                print(
                    f"Notifying {customer.email} about updates to event {event_title}"
                )
    finally:
        db.close()


# ──────────────────────────────────────────────
#  Organizer endpoints
# ──────────────────────────────────────────────

@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    organizer: User = Depends(require_organizer),
):
    """Create a new event. Only organizers can access this."""
    new_event = Event(
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        event_date=event_data.event_date,
        total_tickets=event_data.total_tickets,
        available_tickets=event_data.total_tickets,  # starts fully available
        organizer_id=organizer.id,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    organizer: User = Depends(require_organizer),
):
    """
    Update an existing event. Only the organizer who created it can update.
    Triggers a background task to notify customers who booked this event.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Ensure the organizer owns this event
    if event.organizer_id != organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own events",
        )

    # Apply partial updates (only fields that were provided)
    update_fields = event_data.model_dump(exclude_unset=True)

    # If total_tickets is being increased, also increase available_tickets
    if "total_tickets" in update_fields:
        new_total = update_fields["total_tickets"]
        tickets_sold = event.total_tickets - event.available_tickets
        if new_total < tickets_sold:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reduce total tickets below {tickets_sold} (already sold)",
            )
        update_fields["available_tickets"] = new_total - tickets_sold

    for field, value in update_fields.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    # Trigger background notification
    background_tasks.add_task(
        notify_customers_of_update, event.id, event.title, ""
    )

    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    organizer: User = Depends(require_organizer),
):
    """Delete an event. Only the organizer who created it can delete."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    if event.organizer_id != organizer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own events",
        )

    db.delete(event)
    db.commit()
    return None


@router.get("/organizer/events", response_model=List[EventResponse])
def list_organizer_events(
    db: Session = Depends(get_db),
    organizer: User = Depends(require_organizer),
):
    """List all events created by the currently logged-in organizer."""
    events = db.query(Event).filter(Event.organizer_id == organizer.id).all()
    return events


# ──────────────────────────────────────────────
#  Public event browsing (any authenticated user)
# ──────────────────────────────────────────────

@router.get("/events", response_model=List[EventResponse])
def list_events(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Browse all events. Any authenticated user can access."""
    return db.query(Event).all()


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get details of a single event. Any authenticated user can access."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event
