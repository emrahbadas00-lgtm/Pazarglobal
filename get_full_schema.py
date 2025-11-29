"""
Supabase'den TÜM schema bilgisini çek
"""
from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import asyncio
import json

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

async def get_all_tables():
    """Get all table names from Supabase"""
    async with httpx.AsyncClient() as client:
        # Supabase otomatik olarak tüm tabloları REST endpoint'leri olarak expose eder
        # Her tablo için metadata çekebiliriz
        
        # Önce listings'i biliyoruz, diğerlerini test edelim
        tables_to_check = [
            'listings',
            'users',
            'messages',
            'sessions',
            'categories',
            'favorites',
            'reviews',
            'transactions',
            'notifications'
        ]
        
        print("=== CHECKING TABLES ===\n")
        
        found_tables = []
        
        for table in tables_to_check:
            try:
                resp = await client.get(
                    f'{SUPABASE_URL}/rest/v1/{table}?limit=1',
                    headers={
                        'apikey': SUPABASE_KEY,
                        'Authorization': f'Bearer {SUPABASE_KEY}'
                    },
                    timeout=5.0
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    found_tables.append(table)
                    print(f"✅ {table}")
                    if data:
                        print(f"   Columns: {list(data[0].keys())}")
                        print(f"   Sample: {json.dumps(data[0], indent=4, default=str)[:200]}...")
                    else:
                        print(f"   (empty table)")
                    print()
                elif resp.status_code == 404:
                    print(f"❌ {table} - Not found")
                else:
                    print(f"⚠️  {table} - Status: {resp.status_code}")
                    
            except Exception as e:
                print(f"❌ {table} - Error: {e}")
        
        print(f"\n=== FOUND TABLES: {len(found_tables)} ===")
        print(found_tables)
        return found_tables

async def get_table_structure(table_name):
    """Get full structure of a specific table"""
    async with httpx.AsyncClient() as client:
        # Get all rows to see full structure
        resp = await client.get(
            f'{SUPABASE_URL}/rest/v1/{table_name}?limit=100',
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}'
            }
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"\n=== TABLE: {table_name.upper()} ===")
            print(f"Row count: {len(data)}")
            if data:
                print(f"Columns: {list(data[0].keys())}")
                print("\nSample rows:")
                for i, row in enumerate(data[:3]):
                    print(f"\nRow {i+1}:")
                    print(json.dumps(row, indent=2, default=str))
            return data
        else:
            print(f"Error fetching {table_name}: {resp.status_code}")
            return None

async def main():
    print("🔍 Fetching Supabase Database Schema...\n")
    print(f"URL: {SUPABASE_URL}\n")
    
    # Check all tables
    found_tables = await get_all_tables()
    
    # Get detailed structure for each found table
    print("\n" + "="*50)
    print("DETAILED TABLE STRUCTURES")
    print("="*50)
    
    all_schema = {}
    for table in found_tables:
        data = await get_table_structure(table)
        if data:
            all_schema[table] = {
                'row_count': len(data),
                'columns': list(data[0].keys()) if data else [],
                'sample_data': data[:2]
            }
    
    # Save to JSON
    with open('database/supabase_schema_dump.json', 'w', encoding='utf-8') as f:
        json.dump(all_schema, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n✅ Schema saved to: database/supabase_schema_dump.json")
    print(f"\n📊 Summary:")
    for table, info in all_schema.items():
        print(f"  - {table}: {info['row_count']} rows, {len(info['columns'])} columns")

if __name__ == "__main__":
    asyncio.run(main())
