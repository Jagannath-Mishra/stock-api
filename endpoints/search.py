from fastapi import APIRouter, Query, HTTPException, Header, Depends
from pymongo import MongoClient
from typing import Optional, List
from pydantic import BaseModel
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "nse_stock_data")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "live_indian_stock_data")
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 1000))

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
keys_collection = db[os.getenv("API_KEYS_COLLECTION_NAME", "api_keys")]

# Pydantic Models
class Stock(BaseModel):
    symbol: str
    companyName: Optional[str]
    lastPrice: Optional[float]

class SearchResponse(BaseModel):
    results: List[Stock]

# Router Initialization
search_router = APIRouter()

def verify_api_key_with_rate_limit(x_api_key: str = Header(...)):
    api_key_record = keys_collection.find_one({"api_key": x_api_key})
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key.")

    # Rate limiting logic
    current_time = datetime.utcnow()
    last_request_time = api_key_record.get("last_request_time", None)
    request_count = api_key_record.get("request_count", 0)

    if last_request_time:
        elapsed_time = (current_time - last_request_time).total_seconds()
        if elapsed_time < 60 and request_count >= RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

    keys_collection.update_one(
        {"api_key": x_api_key},
        {"$set": {"last_request_time": current_time}, "$inc": {"request_count": 1}}
    )

@search_router.get("/search", response_model=SearchResponse, dependencies=[Depends(verify_api_key_with_rate_limit)])
def search_stocks(
    query: Optional[str] = Query(None, title="Search Query", description="Symbol or company name to search for."),
    limit: Optional[int] = Query(10, title="Limit", description="Maximum number of results to return.")
):
    """
    Search stock records by symbol or company name.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")

    query_regex = {"$regex": query, "$options": "i"}
    results = collection.find({"$or": [{"symbol": query_regex}, {"info.companyName": query_regex}]}, {"_id": 0, "symbol": 1, "info.companyName": 1, "priceInfo.lastPrice": 1}).limit(limit)
    results_list = list(results)

    if not results_list:
        raise HTTPException(status_code=404, detail="No records found.")

    mapped_results = [
        {"symbol": record.get("symbol"), "companyName": record.get("info", {}).get("companyName"), "lastPrice": record.get("priceInfo", {}).get("lastPrice")}
        for record in results_list
    ]

    return {"results": mapped_results}
