import asyncio
import requests
import pymongo
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection Setup
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client['nse_stock_data']  # Database name
current_collection = db['nifty_options_chain_live']  # Collection for current data
#historical_collection = db['nifty_options_historical']  # Collection for historical data

# NSE API Details
headers = {
    "User-Agent": "Mozilla/5.0",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
}
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

# Async Function to Fetch and Store Data
async def fetch_and_store_data():
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)  # Initial request to set cookies

    while True:
        try:
            response = session.get(url, headers=headers)
            data = response.json()

            if 'records' in data:
                option_data = data['records']['data']  # Extract option chain data
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

                # Add timestamp to each record
                for record in option_data:
                    record['timestamp'] = timestamp

                # Update Current Collection
                for record in option_data:
                    filter_query = {
                        "strikePrice": record.get("strikePrice"),
                        "expiryDate": record.get("expiryDate"),
                        "CE.identifier": record.get("CE", {}).get("identifier"),
                        "PE.identifier": record.get("PE", {}).get("identifier"),
                    }
                    current_collection.update_one(
                        filter_query,
                        {"$set": record},
                        upsert=True
                    )

                # Store Historical Data
                #historical_collection.insert_many(option_data)

                print(f"[{timestamp}] Updated {len(option_data)} records in current collection.")
                #print(f"[{timestamp}] Inserted {len(option_data)} records into historical collection.")

            else:
                print(f"[{datetime.now()}] No valid data in response")

        except Exception as e:
            print(f"[{datetime.now()}] Error fetching data: {e}")

        # Wait for the next fetch (e.g., every 3 seconds)
        await asyncio.sleep(3)  # Adjust interval as needed

# Run the Async Function
async def main():
    print("Starting the data fetcher...")
    await fetch_and_store_data()

if __name__ == "__main__":
    asyncio.run(main())
