import os
from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha256
from starlette.responses import JSONResponse
from endpoints.search import search_router
from endpoints.details import details_router

# App Initialization
app = FastAPI(
    title="Stock Search API",
    description="API to search stock records by symbol or company name.",
    version="1.0",
)

# CORS Middleware Configuration
origins = [
    "http://localhost:3000",  # Adjust to the URL of your frontend application
    "http://127.0.0.1:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Origins allowed to make cross-origin requests
    allow_credentials=True,  # Allow cookies and credentials
    allow_methods=["*"],  # HTTP methods allowed
    allow_headers=["*"],  # HTTP headers allowed
)

# Security for OpenAPI Docs
security = HTTPBasic()
ADMIN_USERNAME = "admin"  # Replace with your username
ADMIN_PASSWORD = sha256("admin".encode()).hexdigest()  # Replace with your password

# Middleware to restrict `/docs` and `/redoc`
@app.middleware("http")
async def restrict_docs_access(request, call_next):
    if request.url.path in ["/docs", "/redoc"]:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not validate_basic_auth(auth_header):
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required to access /docs or /redoc."},
                headers={"WWW-Authenticate": 'Basic realm="Secure API Docs"'},
            )
    return await call_next(request)

def validate_basic_auth(auth_header: str):
    from base64 import b64decode

    try:
        auth_type, credentials = auth_header.split(" ")
        if auth_type.lower() != "basic":
            return False
        decoded_credentials = b64decode(credentials).decode("utf-8")
        username, password = decoded_credentials.split(":")
        return (
            username == ADMIN_USERNAME and sha256(password.encode()).hexdigest() == ADMIN_PASSWORD
        )
    except Exception:
        return False

@app.get("/login", include_in_schema=False)
def login_prompt():
    return {"message": "Please use Basic Authentication to access /docs or /redoc."}

# Include routers from the `endpoints` folder
app.include_router(search_router)
app.include_router(details_router)
