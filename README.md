# Contacts API

A REST API for managing contacts, built with FastAPI and SQLAlchemy.

## Requirements

- Python 3.11+
- PostgreSQL
- Docker

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd goit-pythonweb-hw-08
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run PostgreSQL in Docker:

   ```bash
   docker run --name postgres-contacts -p 5432:5432 -e POSTGRES_PASSWORD=123456 -d postgres
   ```

4. Set up `.env`:

   ```
   DATABASE_URL=postgresql://postgres:123456@localhost:5432/postgres
   ```

5. Apply migrations:
   ```bash
   alembic upgrade head
   ```

## Running the API

Start the server:

```bash
uvicorn main:app --reload
```

API is available at: `http://127.0.0.1:8000`

Documentation: `http://127.0.0.1:8000/docs`

## Features

- **POST** `/contacts/` — Create a contact
- **GET** `/contacts/` — List all contacts
- **GET** `/contacts/{id}` — Get a contact by ID
- **PUT** `/contacts/{id}` — Update a contact
- **DELETE** `/contacts/{id}` — Delete a contact
- **GET** `/contacts/search/?query=...` — Search by first name, last name, or email
- **GET** `/contacts/birthdays/` — Get contacts with birthdays in the next 7 days
