from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from typing import List
import redis.asyncio as redis
import uvicorn

from auth import get_current_user
from database import get_db
from schemas import ContactCreate, ContactUpdate, ContactInDB
from crud import (
    create_contact, get_contacts, get_contact, update_contact,
    delete_contact, search_contacts, get_upcoming_birthdays
)
from users import router as users_router

app = FastAPI(title="Contacts API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Укажи домены фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация rate limiter
@app.on_event("startup")
async def startup():
    redis_instance = redis.from_url("redis://redis:6379/0", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)

# Подключение маршрутов пользователей
app.include_router(users_router)

@app.post("/contacts/", response_model=ContactInDB, status_code=status.HTTP_201_CREATED)
def create_new_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_contact(db, contact, current_user.id)

@app.get("/contacts/", response_model=List[ContactInDB])
def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_contacts(db, current_user.id, skip, limit)

@app.get("/contacts/{contact_id}", response_model=ContactInDB)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_contact = get_contact(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=ContactInDB)
def update_existing_contact(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_contact = update_contact(db, contact_id, contact, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.delete("/contacts/{contact_id}", response_model=ContactInDB)
def delete_existing_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_contact = delete_contact(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/search/", response_model=List[ContactInDB])
def search_contacts_endpoint(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return search_contacts(db, query, current_user.id)

@app.get("/contacts/birthdays/", response_model=List[ContactInDB])
def get_upcoming_birthdays_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_upcoming_birthdays(db, current_user.id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
