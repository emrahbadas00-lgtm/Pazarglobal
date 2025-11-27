import asyncio
from dotenv import load_dotenv

load_dotenv()

from tools.clean_price import clean_price
from tools.insert_listing import insert_listing
from tools.search_listings import search_listings


async def test_updated_tools():
    """Güncellenmiş tools'ları test et"""
    
    print("=" * 60)
    print("🧪 PAZARGLOBAL MCP TOOLS TEST (GÜNCELLENMİŞ)")
    print("=" * 60)
    
    # Test 1: clean_price
    print("\n1️⃣ TEST: clean_price_tool")
    print("-" * 60)
    result = clean_price("54,999 TL")
    print(f"'54,999 TL' → {result}")
    
    # Test 2: insert_listing (yeni kolon isimleriyle)
    print("\n2️⃣ TEST: insert_listing_tool (YENİ ŞEMA)")
    print("-" * 60)
    result = await insert_listing(
        title="iPhone 15 Pro 128GB - MCP Test",
        price=54999,
        condition="new",
        category="Elektronik",
        description="Test ürünü - güncellenmiş şema",
        location="İstanbul",
        stock=5,
    )
    print(f"Success: {result.get('success')}")
    print(f"Status: {result.get('status')}")
    if result.get('success'):
        data = result.get('result')
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            print(f"✅ İlan eklendi:")
            print(f"   ID: {item.get('id')}")
            print(f"   Title: {item.get('title')}")
            print(f"   Price: {item.get('price')} TL")
    else:
        print(f"❌ Error: {result.get('error')}")
        print(f"   Response: {result.get('result')}")
    
    # Test 3: search_listings (yeni kolon isimleriyle)
    print("\n3️⃣ TEST: search_listings_tool (YENİ ŞEMA)")
    print("-" * 60)
    
    print("\n📌 Tüm ilanlar:")
    result = await search_listings(limit=5)
    print(f"Success: {result.get('success')}")
    print(f"Count: {result.get('count')}")
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', [])[:5], 1):
            print(f"  {i}. {item.get('title')} - {item.get('price')} TL - {item.get('condition')}")
    else:
        print(f"  Error: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ TEST TAMAMLANDI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_updated_tools())
