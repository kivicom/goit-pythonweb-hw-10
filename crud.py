"""
CRUD operations for managing contacts and users in the database.

This module provides functions to create, read, update, delete, search contacts,
retrieve contacts with upcoming birthdays, and manage users.
"""

# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract
from passlib.context import CryptContext

# Local application imports
from models import Contact, User
from schemas import ContactCreate, ContactUpdate, UserCreate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, user: UserCreate):
    """
    Create a new user in the database with hashed password.

    Args:
        db (Session): Database session.
        user (UserCreate): User data to create.

    Returns:
        User: Created user object.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user by email.

    Args:
        db (Session): Database session.
        email (str): Email of the user to retrieve.

    Returns:
        User: User object or None if not found.
    """
    return db.query(User).filter(User.email == email).first()

def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Create a new contact in the database for a specific user.

    Args:
        db (Session): Database session.
        contact (ContactCreate): Contact data to create.
        user_id (int): ID of the user who owns the contact.

    Returns:
        Contact: Created contact object.
    """
    db_contact = Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def get_contacts(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of contacts for a specific user with pagination.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user who owns the contacts.
        skip (int): Number of records to skip (default: 0).
        limit (int): Maximum number of records to return (default: 10).

    Returns:
        List[Contact]: List of contacts.
    """
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()

def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Retrieve a single contact by ID for a specific user.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to retrieve.
        user_id (int): ID of the user who owns the contact.

    Returns:
        Contact: Contact object or None if not found.
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()

def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    """
    Update an existing contact by ID for a specific user.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to update.
        contact (ContactUpdate): Updated contact data.
        user_id (int): ID of the user who owns the contact.

    Returns:
        Contact: Updated contact object or None if not found.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Delete a contact by ID for a specific user.

    Args:
        db (Session): Database session.
        contact_id (int): ID of the contact to delete.
        user_id (int): ID of the user who owns the contact.

    Returns:
        Contact: Deleted contact object or None if not found.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact

def search_contacts(db: Session, query: str, user_id: int):
    """
    Search contacts by first name, last name, or email for a specific user.

    Args:
        db (Session): Database session.
        query (str): Search query string.
        user_id (int): ID of the user who owns the contacts.

    Returns:
        List[Contact]: List of matching contacts.
    """
    return db.query(Contact).filter(
        Contact.user_id == user_id,
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")
        )
    ).all()

def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Retrieve contacts with birthdays in the next 7 days for a specific user.

    Args:
        db (Session): Database session.
        user_id (int): ID of the user who owns the contacts.

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=7)

    return db.query(Contact).filter(
        Contact.user_id == user_id,
        or_(
            # Case 1: Birthday is in the current month
            (extract("month", Contact.birthday) == today.month) &
            (extract("day", Contact.birthday) >= today.day) &
            (extract("day", Contact.birthday) <= (
                end_date.day if end_date.month == today.month else 31
            )),
            # Case 2: Birthday is in the next month
            (end_date.month != today.month) &
            (extract("month", Contact.birthday) == end_date.month) &
            (extract("day", Contact.birthday) <= end_date.day)
        )
    ).all()
