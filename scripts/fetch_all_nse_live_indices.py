import asyncio
import requests
import pymongo
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection Setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client['nse_stock_data']  # Database name
current_collection = db['nse_indices_live']  # Collection for current index data

# NSE API Details
headers = {
    "User-Agent": "Mozilla/5.0",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
}

# NSE API Base URL for Indices
base_url = "https://www.nseindia.com/api/equity-stockIndices?index="

# List of Indices to Fetch
indices = [
    "NIFTY 50", 
    "NIFTY MIDCAP SELECT",
    "NIFTY BANK",
    "NIFTY FINANCIAL SERVICES",
    "NIFTY IPO"
]

# Async Function to Fetch and Store Data
async def fetch_and_store_data():
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # Initial request to set cookies

    while True:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

            for index in indices:
                try:
                    url = base_url + requests.utils.quote(index)  # Encode index name for URL
                    response = session.get(url, headers=headers)
                    data = response.json()

                    if 'data' in data:
                        index_data = data['data']  # Extract index data

                        # Add timestamp to each record
                        for record in index_data:
                            record['timestamp'] = timestamp

                        # Update Current Collection
                        for record in index_data:
                            filter_query = {"symbol": record.get("symbol"), "index": index}
                            current_collection.update_one(
                                filter_query,
                                {"$set": record},
                                upsert=True
                            )

                        print(f"[{timestamp}] Updated {len(index_data)} records for {index}.")
                    else:
                        print(f"[{datetime.now()}] No valid data for index {index}")

                except Exception as e:
                    print(f"[{datetime.now()}] Error fetching data for index {index}: {e}")

        except Exception as e:
            print(f"[{datetime.now()}] General Error: {e}")

        # Wait for the next fetch (e.g., every 5 seconds)
        await asyncio.sleep(5)  # Adjust interval as needed

# Run the Async Function
async def main():
    print("Starting the data fetcher for all indices...")
    await fetch_and_store_data()

if __name__ == "__main__":
    asyncio.run(main())
