"""
Supabase'den TÜM schema bilgisini çek - tablolar, kolonlar, RLS policies
"""
from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import json

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Bilinen tüm tablolar
TABLES = [
    'conversations',
    'listings',
    'notifications',
    'orders',
    'product_embeddings',
    'product_images',
    'users'
]

def fetch_table_data(table_name: str):
    """Fetch sample data from a table"""
    try:
        with httpx.Client() as client:
            resp = client.get(
                f'{SUPABASE_URL}/rest/v1/{table_name}?limit=2',
                headers={
                    'apikey': SUPABASE_KEY,
                    'Authorization': f'Bearer {SUPABASE_KEY}',
                    'Prefer': 'count=exact'
                },
                timeout=10.0
            )
            
            if resp.status_code == 200:
                data = resp.json()
                # Get total count from header
                count_header = resp.headers.get('Content-Range', '0')
                total_count = count_header.split('/')[-1] if '/' in count_header else 'unknown'
                
                return {
                    'status': 'success',
                    'total_rows': total_count,
                    'columns': list(data[0].keys()) if data else [],
                    'sample_data': data
                }
            else:
                return {
                    'status': 'error',
                    'error': f'HTTP {resp.status_code}',
                    'message': resp.text[:200]
                }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    print("🔍 Fetching Complete Supabase Schema...\n")
    print(f"URL: {SUPABASE_URL}\n")
    print("="*60)
    
    all_schema = {}
    
    for table in TABLES:
        print(f"\n📊 Table: {table}")
        print("-" * 60)
        
        result = fetch_table_data(table)
        all_schema[table] = result
        
        if result['status'] == 'success':
            print(f"✅ Rows: {result['total_rows']}")
            print(f"   Columns ({len(result['columns'])}): {', '.join(result['columns'])}")
            
            if result['sample_data']:
                print(f"\n   Sample data:")
                for i, row in enumerate(result['sample_data'][:1], 1):
                    print(f"   Row {i}:")
                    for key, value in row.items():
                        value_str = str(value)[:50]
                        print(f"     • {key}: {value_str}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')}")
    
    # Save to JSON
    output_file = 'database/complete_schema.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_schema, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n" + "="*60)
    print(f"✅ Complete schema saved to: {output_file}")
    print("\n📋 Summary:")
    for table, info in all_schema.items():
        if info['status'] == 'success':
            print(f"  ✓ {table}: {info['total_rows']} rows, {len(info['columns'])} columns")
        else:
            print(f"  ✗ {table}: {info.get('error', 'Failed')}")

if __name__ == "__main__":
    main()
