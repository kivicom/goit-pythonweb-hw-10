from sqlalchemy import Column, Integer, String, Date
from database import Base

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
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String(255), nullable=True)
    