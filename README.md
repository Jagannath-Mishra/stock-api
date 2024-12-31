# Stock Search API

A FastAPI application to search stock records by symbol or company name. This project demonstrates how to build a secure and scalable API using FastAPI.

## Features

- Search for stock records by symbol or company name
- Secure OpenAPI documentation with Basic Authentication
- CORS enabled for frontend integration
- Modular architecture with routers

---

## Table of Contents

1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Run the Application](#run-the-application)
4. [Testing](#testing)
5. [Environment Variables](#environment-variables)
6. [Project Structure](#project-structure)
7. [License](#license)

---

## Requirements

- Python 3.9+
- pip or a similar package manager
- PostgreSQL (if used for the database)

---

## Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2. **Create a virtual environment**:(not required optional)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the project root and add the following variables:
    ```plaintext
    DATABASE_URL=postgresql://username:password@localhost:5432/yourdb
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=admin
    ```

---

## Run the Application

1. **Start the server**:
    ```bash
    uvicorn main:app --reload
    ```

2. **Access the API documentation**:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

3. **Authentication for API docs**:
   Use the Basic Authentication credentials defined in your `.env` file to access `/docs` or `/redoc`.

---

## Testing

1. **Run unit tests**:
    ```bash
    pytest
    ```

2. **Test endpoints manually**:
   Use tools like [Postman](https://www.postman.com/) or [cURL](https://curl.se/) to test the endpoints.

3. **Test example request**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/search?symbol=AAPL" -H "accept: application/json"
