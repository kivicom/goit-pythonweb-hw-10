"""
CRUD operations for managing contacts in the database.

This module provides functions to create, read, update, delete, search contacts,
and retrieve contacts with upcoming birthdays.
"""

# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract

# Local application imports
from models import Contact
from schemas import ContactCreate, ContactUpdate


def create_contact(db: Session, contact: ContactCreate):
    """
    Create a new contact in the database.

    Args:
        db (Session): Database session.
        contact (ContactCreate): Contact data to create.

    Returns:
        Contact: Created contact object.
    """
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of contacts with pagination.

    Args:
        db (Session): Database session.
        skip (int): Number of records to skip (default: 0).
        limit (int): Maximum number of records to return (default: 10).

    Returns:
        List[Contact]: List of contacts.
    """
    return db.query(Contact).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int):
    """
    Retrieve a single contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to retrieve.

    Returns:
        Contact: Contact object or None if not found.
    """
    return db.query(Contact).filter(Contact.id == contact_id).first()


def update_contact(db: Session, contact_id: int, contact: ContactUpdate):
    """
    Update an existing contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to update.
        contact (ContactUpdate): Updated contact data.

    Returns:
        Contact: Updated contact object or None if not found.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int):
    """
    Delete a contact by ID.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to delete.

    Returns:
        Contact: Deleted contact object or None if not found.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


def search_contacts(db: Session, query: str):
    """
    Search contacts by first name, last name, or email.

    Args:
        db (Session): Database session.
        query (str): Search query string.

    Returns:
        List[Contact]: List of matching contacts.
    """
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")
        )
    ).all()


def get_upcoming_birthdays(db: Session):
    """
    Retrieve contacts with birthdays in the next 7 days.

    Args:
        db (Session): Database session.

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=7)

    # Extract month and day from birthday and compare with the range
    return db.query(Contact).filter(
        or_(
            # Case 1: Birthday is in the current month
            (extract("month", Contact.birthday) == today.month) &
            (extract("day", Contact.birthday) >= today.day) &
            (extract("day", Contact.birthday) <= (
                end_date.day if end_date.month == today.month else 31
            )),

            # Case 2: Birthday is in the next month (if the range crosses a month)
            (end_date.month != today.month) &
            (extract("month", Contact.birthday) == end_date.month) &
            (extract("day", Contact.birthday) <= end_date.day)
        )
    ).all()
