from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import ContactCreate, ContactUpdate, ContactInDB
from crud import (
    create_contact, get_contacts, get_contact, update_contact,
    delete_contact, search_contacts, get_upcoming_birthdays
)

app = FastAPI(title="Contacts API")

@app.post("/contacts/", response_model=ContactInDB)
def create_new_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    return create_contact(db, contact)

@app.get("/contacts/", response_model=List[ContactInDB])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_contacts(db, skip, limit)

@app.get("/contacts/{contact_id}", response_model=ContactInDB)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = get_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=ContactInDB)
def update_existing_contact(contact_id: int, contact: ContactUpdate, db: Session = Depends(get_db)):
    db_contact = update_contact(db, contact_id, contact)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.delete("/contacts/{contact_id}", response_model=ContactInDB)
def delete_existing_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = delete_contact(db, contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/search/", response_model=List[ContactInDB])
def search_contacts_endpoint(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return search_contacts(db, query)

@app.get("/contacts/birthdays/", response_model=List[ContactInDB])
def get_upcoming_birthdays_endpoint(db: Session = Depends(get_db)):
    return get_upcoming_birthdays(db)
