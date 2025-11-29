"""
Supabase schema'yı çek
"""
from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import asyncio
import json

async def get_listings_schema():
    """Get one listing to see all columns"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    async with httpx.AsyncClient() as client:
        # Get one listing to see structure
        resp = await client.get(
            f'{url}/rest/v1/listings?limit=1',
            headers={
                'apikey': key,
                'Authorization': f'Bearer {key}'
            }
        )
        
        if resp.status_code == 200:
            listings = resp.json()
            if listings:
                print("=== LISTINGS TABLE STRUCTURE ===")
                print(json.dumps(listings[0], indent=2, default=str))
                print("\n=== COLUMN NAMES ===")
                print(list(listings[0].keys()))
            else:
                print("No listings found")
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)

if __name__ == "__main__":
    asyncio.run(get_listings_schema())
