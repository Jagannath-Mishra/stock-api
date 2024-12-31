from fastapi import APIRouter, HTTPException, Header, Depends
from pymongo import MongoClient
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "nse_stock_data")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "live_indian_stock_data")
API_KEYS_COLLECTION_NAME = os.getenv("API_KEYS_COLLECTION_NAME", "api_keys")

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
keys_collection = db[API_KEYS_COLLECTION_NAME]

# Router Initialization
details_router = APIRouter()

# Security for API Key
def verify_api_key(x_api_key: str = Header(...)):
    api_key_record = keys_collection.find_one({"api_key": x_api_key})
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key.")

# Pydantic Models
class StockDetails(BaseModel):
    symbol: str
    companyName: Optional[str]
    lastPrice: Optional[float]
    additionalInfo: Optional[dict]

@details_router.get(
    "/details/{symbol}",
    response_model=StockDetails,
    summary="Get Stock Details",
    description="Retrieve detailed information for a specific stock. Requires a valid X-API-Key."
)
def get_stock_details(
    symbol: str,
    x_api_key: str = Header(..., description="API key for authentication")
):
    """
    Get detailed information about a specific stock by symbol.
    """
    # Verify the API key
    verify_api_key(x_api_key)

    # Fetch stock details
    stock = collection.find_one({"symbol": symbol}, {"_id": 0})
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found.")

    return {
        "symbol": stock.get("symbol"),
        "companyName": stock.get("info", {}).get("companyName"),
        "lastPrice": stock.get("priceInfo", {}).get("lastPrice"),
        "additionalInfo": stock
    }
