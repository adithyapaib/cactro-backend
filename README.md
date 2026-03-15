# Event Booking System

A simple backend API for managing events and booking tickets, built with **FastAPI**, **SQLite**, and **SQLAlchemy**.

---

## System Overview

The system supports two user roles:

| Role | Capabilities |
|------|-------------|
| **Organizer** | Create, update, and delete events; view their own events |
| **Customer** | Browse all events; book tickets for events |

Authentication is handled via **JWT tokens**. Every request (except registration and login) requires a valid `Authorization: Bearer <token>` header.

---

## Database Schema

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    users      │       │     events        │       │    bookings       │
├──────────────┤       ├──────────────────┤       ├──────────────────┤
│ id (PK)      │       │ id (PK)          │       │ id (PK)          │
│ name         │──┐    │ title            │   ┌───│ event_id (FK)    │
│ email (UQ)   │  │    │ description      │   │   │ customer_id (FK) │
│ password_hash│  │    │ location         │   │   │ tickets_booked   │
│ role         │  │    │ event_date       │   │   │ booking_time     │
└──────────────┘  │    │ total_tickets    │   │   └──────────────────┘
                  │    │ available_tickets │   │
                  └───>│ organizer_id (FK)│<──┘
                       └──────────────────┘
```

- **users.role** — either `"organizer"` or `"customer"`
- **events.available_tickets** — decremented on each booking
- **bookings.booking_time** — set automatically at creation (UTC)

---

## Role-Based Access Control

| Endpoint | Method | Allowed Roles |
|----------|--------|---------------|
| `/register` | POST | Public |
| `/login` | POST | Public |
| `/events` | GET | Any authenticated user |
| `/events/{id}` | GET | Any authenticated user |
| `/events` | POST | Organizer only |
| `/events/{id}` | PUT | Organizer (owner only) |
| `/events/{id}` | DELETE | Organizer (owner only) |
| `/organizer/events` | GET | Organizer only |
| `/events/{id}/book` | POST | Customer only |

---

## Background Tasks

| Task | Trigger | Behaviour |
|------|---------|-----------|
| **Booking Confirmation** | Successful ticket booking | Prints: `Sending booking confirmation email to <email> for event <title>` |
| **Event Update Notification** | Event details updated | Finds all customers who booked the event and prints: `Notifying <email> about updates to event <title>` |

Both tasks run asynchronously via FastAPI's `BackgroundTasks` and simulate email delivery with `print()`.

---

## Project Structure

```
project/
├── main.py            # App entry point
├── database.py        # SQLAlchemy engine & session
├── models.py          # ORM models (User, Event, Booking)
├── schemas.py         # Pydantic request/response schemas
├── auth.py            # JWT creation/verification, password hashing
├── dependencies.py    # FastAPI dependency injection helpers
├── requirements.txt   # Python dependencies
├── routes/
│   ├── auth_routes.py     # /register, /login
│   ├── event_routes.py    # Event CRUD endpoints
│   └── booking_routes.py  # Ticket booking endpoint
└── README.md
```

---

## How to Run

### 1. Prerequisites

- Python 3.10 or higher

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the server

```bash
uvicorn main:app --reload
```

The API will be available at **http://127.0.0.1:8000**.

Interactive docs (Swagger UI) at **http://127.0.0.1:8000/docs**.

---

## Example API Requests (curl)

### Register an organizer

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "secret123", "role": "organizer"}'
```

### Register a customer

```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Bob", "email": "bob@example.com", "password": "secret123", "role": "customer"}'
```

### Login (get JWT token)

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

> Save the `access_token` value — you'll pass it as a Bearer token in subsequent requests.

### Create an event (organizer)

```bash
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ORGANIZER_TOKEN>" \
  -d '{
    "title": "Rock Concert",
    "description": "An evening of classic rock",
    "location": "City Arena",
    "event_date": "2026-06-15T19:00:00",
    "total_tickets": 100
  }'
```

### Update an event (organizer)

```bash
curl -X PUT http://127.0.0.1:8000/events/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ORGANIZER_TOKEN>" \
  -d '{"title": "Rock Concert - Updated!", "location": "Grand Arena"}'
```

### Delete an event (organizer)

```bash
curl -X DELETE http://127.0.0.1:8000/events/1 \
  -H "Authorization: Bearer <ORGANIZER_TOKEN>"
```

### List organizer's events

```bash
curl http://127.0.0.1:8000/organizer/events \
  -H "Authorization: Bearer <ORGANIZER_TOKEN>"
```

### Browse all events (any user)

```bash
curl http://127.0.0.1:8000/events \
  -H "Authorization: Bearer <TOKEN>"
```

### Get event details

```bash
curl http://127.0.0.1:8000/events/1 \
  -H "Authorization: Bearer <TOKEN>"
```

### Book tickets (customer)

```bash
curl -X POST http://127.0.0.1:8000/events/1/book \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  -d '{"tickets": 2}'
```

---

## Notes

- The SQLite database file (`bookings.db`) is created automatically in the project root on first run.
- In production, replace the `SECRET_KEY` in `auth.py` with a strong random value via the `SECRET_KEY` environment variable.
- Background tasks simulate emails with `print()` — replace with a real email service (SendGrid, SES, etc.) for production use.
