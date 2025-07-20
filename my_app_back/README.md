# FastAPI Backend Application

This is a FastAPI-based backend application with a clean architecture.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Run database migrations:
```bash
alembic upgrade head
```

## Running the Application

Development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── alembic/              # Database migrations
├── app/                  # Application package
│   ├── api/             # API routes
│   ├── core/            # Core modules (config, security, etc.)
│   ├── crud/            # CRUD operations
│   ├── db/              # Database setup and models
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── tests/               # Test files
├── .env                 # Environment variables
├── .env.example         # Example environment variables
└── requirements.txt     # Project dependencies
```

## Running Tests

```bash
pytest
``` 