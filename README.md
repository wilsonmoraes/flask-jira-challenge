# Flask Stock Quote API

A backend challenge project using Flask, following a microservice architecture to provide stock quote information. It consists of two decoupled services:

- **API Service**: Authenticates users, handles requests, stores query history, and exposes endpoints.
- **Stock Service**: Internal service that fetches and parses stock data from the external Stooq API.

---

## Architecture Overview

```
User ──▶ API Service (JWT Auth, DB)
             └──▶ Stock Service (fetch from Stooq)
                          └──▶ External Stooq API
```

- Communication between services is done via HTTP (simple, fast, synchronous).
- Caching is used to improve performance on stats/history endpoints.
- JWT is used instead of Basic Auth for better token-based security.

---

## How to Run

### 1. Setup virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Run the API Service
```bash
cd api_service
flask db upgrade
flask run  # Default: http://127.0.0.1:5000
```

### 3. Run the Stock Service
```bash
cd stock_service
flask run --port 5001
```

---

## Implemented Features

### API Service
- JWT-based authentication (`/auth/login`, `/auth/refresh`)
- Query stock quote from stock service (`/api/v1/stock?q=aapl.us`)
- Save query to DB associated to authenticated user
- Return query history (`/api/v1/users/history`)
- Admin-only stats endpoint (`/api/v1/stats`) showing top 5 queried stocks
- All responses in clean JSON format

### Stock Service
- Receives stock code via query param (`/api/v1/stock?q=aapl.us`)
- Calls external Stooq API and parses JSON response
- Returns structured stock data

---

## Technical Decisions

- **Flask-RESTful** for organizing resources via class-based views
- **JWT** via `flask-jwt-extended` for robust and modern auth
- **Manual caching** with `Flask-Caching` and key-based invalidation
- **In-memory cache** (SimpleCache) to reduce external API calls (can be swapped to Redis easily)
- **Service layer** structure (`services/`, `repositories/`) for separation of concerns
- **Two completely separate apps**, each with their own Flask instance

---

## Example Usage

### 1. Authenticate
```
POST /auth/login
{
  "username": "admin",
  "password": "admin"
}
```
_Response:_ `{ "access_token": "...", "refresh_token": "..." }`

### 2. Get Stock Quote
```
GET /api/v1/stock?q=aapl.us
Authorization: Bearer <access_token>

Response:
{
  "symbol": "AAPL.US",
  "company_name": "APPLE",
  "quote": 123.45
}
```

### 3. Get History
```
GET /api/v1/users/history
Authorization: Bearer <access_token>

Response:
[
  {
    "date": "2025-03-21T10:00:00Z",
    "symbol": "AAPL.US",
    "company_name": "APPLE",
    "open": 123.00,
    "high": 124.00,
    "low": 122.00,
    "close": 123.45
  },
  ...
]
```

### 4. Get Stats (Admin only)
```
GET /api/v1/stats
Authorization: Bearer <admin_token>

Response:
[
  { "stock": "aapl.us", "times_requested": 5 },
  { "stock": "msft.us", "times_requested": 3 }
]
```

---

## Author
Wilson Moraes