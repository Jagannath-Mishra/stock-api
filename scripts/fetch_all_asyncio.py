import asyncio
import aiohttp
import pymongo
import json
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection Setup
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI if remote
db = client['nse_stock_data']  # Database name
current_collection = db['live_indian_stock_data']  # Collection for current stock data

# Updated NSE API Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}
base_url = "https://www.nseindia.com/api/quote-equity?symbol="

# Load symbols from an external JSON file
def load_symbols_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['symbols']

# Load symbols
symbol_file = 'symbols.json'  # Path to the JSON file
nse_symbols = load_symbols_from_json(symbol_file)
print(f"Loaded {len(nse_symbols)} symbols.")

# Async Function to Fetch Stock Data
async def fetch_stock_data(symbol, session):
    """
    Fetch live data for a single stock from NSE.
    """
    try:
        async with session.get(base_url + symbol, headers=headers) as response:
            if response.status == 200:
                stock_data = await response.json()
                return symbol, stock_data
            else:
                print(f"Error fetching data for {symbol}: {response.status}")
                return symbol, None
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return symbol, None

# Async Function to Fetch and Store Data for All Stocks in Parallel
async def fetch_and_store_all_stock_data():
    """
    Fetch live data for all stocks in parallel and update MongoDB.
    """
    async with aiohttp.ClientSession() as session:
        # Initial request to set cookies
        await session.get("https://www.nseindia.com", headers=headers)

        while True:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp

            # Create tasks for parallel fetching
            tasks = [fetch_stock_data(symbol, session) for symbol in nse_symbols]
            results = await asyncio.gather(*tasks)

            # Process results
            for symbol, stock_data in results:
                if stock_data:
                    # Add timestamp to the stock data
                    stock_data['timestamp'] = timestamp

                    # Update Current Collection
                    current_collection.update_one(
                        {"symbol": symbol},  # Match stock by symbol
                        {"$set": stock_data},  # Update the data
                        upsert=True  # Insert if not already present
                    )

                    print(f"[{timestamp}] Updated DB data for {symbol}")

            # Wait for the next fetch (e.g., every 5 seconds)
            await asyncio.sleep(5)

# Run the Async Function
async def main():
    print("Starting the stock data fetcher...")
    await fetch_and_store_all_stock_data()

if __name__ == "__main__":
    asyncio.run(main())
