import asyncio
import json
from tools.clean_price import clean_price
from tools.insert_listing import insert_listing
from tools.search_listings import search_listings


async def test_tools():
    """MCP tools'ları test et"""
    
    print("=" * 60)
    print("🧪 PAZARGLOBAL MCP TOOLS TEST")
    print("=" * 60)
    
    # Test 1: clean_price
    print("\n1️⃣ TEST: clean_price_tool")
    print("-" * 60)
    test_prices = [
        "1,250 TL",
        "₺54,999",
        "2.500 TL",
        None,
        "",
        "ABC123",
    ]
    
    for price in test_prices:
        result = clean_price(price)
        print(f"Input: {price!r:20} → Output: {result}")
    
    # Test 2: insert_listing
    print("\n2️⃣ TEST: insert_listing_tool")
    print("-" * 60)
    result = await insert_listing(
        product_name="Test iPhone 15 Pro",
        brand="Apple",
        condition="Yeni",
        category="Elektronik",
        description="Test ürünü - MCP tool testi",
        original_price_text="54,999 TL",
        clean_price=54999,
    )
    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    if result.get('success'):
        print(f"Result: {json.dumps(result.get('result'), indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {result.get('error')}")
    
    # Test 3: search_listings
    print("\n3️⃣ TEST: search_listings_tool")
    print("-" * 60)
    
    # Test 3a: Basit arama
    print("\n📌 Test 3a: Basit arama (query='iPhone')")
    result = await search_listings(query="iPhone", limit=3)
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', [])[:3], 1):
            print(f"  {i}. {item.get('product_name')} - {item.get('clean_price')} TL")
    
    # Test 3b: Fiyat filtresi
    print("\n📌 Test 3b: Fiyat filtresi (max_price=50000)")
    result = await search_listings(max_price=50000, limit=3)
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', [])[:3], 1):
            print(f"  {i}. {item.get('product_name')} - {item.get('clean_price')} TL")
    
    # Test 3c: Marka filtresi
    print("\n📌 Test 3c: Marka filtresi (brand='Apple')")
    result = await search_listings(brand="Apple", limit=3)
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    
    print("\n" + "=" * 60)
    print("✅ TEST TAMAMLANDI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_tools())
