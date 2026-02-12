import asyncio
import httpx
import re

async def test_scrape():
    url = "https://rate.bot.com.tw/gold?Lang=zh-TW"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if response.status_code == 200:
                html = response.text
                print(f"HTML received, length: {len(html)}")
                
                rows = re.findall(r'<tr.*?>.*?</tr>', html, re.DOTALL)
                
                # Search for Silver
                print("\nSearching for '白銀' or '銀'...")
                for i, row in enumerate(rows):
                    if '銀' in row or 'Silver' in row:
                        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
                        clean_cells = [re.sub(r'<.*?>', '', c).strip() for c in cells]
                        print(f"Row {i} (Silver?): {clean_cells}")

                # Print all rows with numbers between 50 and 10000
                print("\nScanning for potential prices...")
                for i, row in enumerate(rows):
                    nums = re.findall(r'>\s*(\d{1,2},?\d{3}(?:\.\d+)?)\s*<', row)
                    if nums:
                        cells = re.findall(r'<td.*?>(.*?)</td>', row, re.DOTALL)
                        clean_cells = [re.sub(r'<.*?>', '', c).strip() for c in cells]
                        # Only print if it looks like a price table
                        if any(re.match(r'^\d{4,5}$', c.replace(',', '')) for c in clean_cells if c):
                            print(f"Row {i} has prices: {clean_cells}")
                
            else:
                print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_scrape())
