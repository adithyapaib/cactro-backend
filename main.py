"""
main.py - Application entry point.

Creates the FastAPI app, registers routes, and initialises the database.
Run with:  uvicorn main:app --reload
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import engine, Base
from routes import auth_routes, event_routes, booking_routes

# Create all database tables (no-op if they already exist)
Base.metadata.create_all(bind=engine)

# Initialise the FastAPI application
app = FastAPI(
    title="Event Booking System",
    description="A simple backend for managing events and ticket bookings.",
    version="1.0.0",
)

# Register API route modules
app.include_router(auth_routes.router)
app.include_router(event_routes.router)
app.include_router(booking_routes.router)

# Serve the frontend
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Frontend"])
def serve_frontend():
    """Serve the single-page frontend."""
    return FileResponse(STATIC_DIR / "index.html")
