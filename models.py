from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    SQLAlchemy model for storing user information.

    Attributes:
        id (int): Primary key for the user.
        email (str): Email address of the user (unique).
        password (str): Hashed password of the user.
        verified (bool): Whether the user's email is verified.
        avatar (str): URL to the user's avatar (optional).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)
    contacts = relationship("Contact", back_populates="user")

class Contact(Base):
    """
    SQLAlchemy model for storing contact information.

    Attributes:
        id (int): Primary key for the contact.
        first_name (str): First name of the contact.
        last_name (str): Last name of the contact.
        email (str): Email address of the contact (unique).
        phone_number (str): Phone number of the contact.
        birthday (Date): Birthday of the contact.
        additional_info (str): Optional additional information about the contact.
        user_id (int): Foreign key to the user who owns this contact.
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="contacts")
