import asyncio
import httpx
from agents.data_collector import data_collector

async def diagnostic():
    print("Testing fetch_international_prices...")
    prices = await data_collector.fetch_international_prices()
    print(f"Result: {prices}")
    
    # Try raw Yahoo Finance fetch
    async with httpx.AsyncClient() as client:
        silver_url = "https://query1.finance.yahoo.com/v8/finance/chart/SI=F"
        response = await client.get(silver_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            data = response.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                price = meta.get("regularMarketPrice")
                symbol = meta.get("symbol")
                print(f"Yahoo Symbol: {symbol}, Price: {price}")
        else:
            print(f"Yahoo Error: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(diagnostic())
