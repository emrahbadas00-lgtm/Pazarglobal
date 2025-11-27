import asyncio
from dotenv import load_dotenv

load_dotenv()

from tools.insert_listing import insert_listing
from tools.search_listings import search_listings


async def test_automotive_category():
    """Otomotiv kategorisinde ilan ekleme ve arama testi"""
    
    print("=" * 60)
    print("🚗 OTOMOTİV KATEGORİSİ TEST")
    print("=" * 60)
    
    # Önce birkaç otomotiv ilanı ekleyelim
    print("\n1️⃣ OTOMOTİV İLANLARI EKLEME")
    print("-" * 60)
    
    test_listings = [
        {
            "title": "2020 Toyota Corolla 1.6 Dream",
            "price": 850000,
            "condition": "used",
            "category": "otomativ",
            "description": "Az km'de, hasarsız, full bakımlı Toyota Corolla",
            "location": "İstanbul",
            "stock": 1,
        },
        {
            "title": "2018 BMW 3.20i",
            "price": 1250000,
            "condition": "used",
            "category": "otomativ",
            "description": "Borusan çıkışlı, bakımlı, temiz BMW",
            "location": "Ankara",
            "stock": 1,
        },
        {
            "title": "2021 Renault Clio 1.0 TCe Touch",
            "price": 650000,
            "condition": "used",
            "category": "otomativ",
            "description": "2021 model, az kullanılmış, garantili",
            "location": "İzmir",
            "stock": 1,
        },
        {
            "title": "2019 Volkswagen Passat 1.6 TDI",
            "price": 950000,
            "condition": "used",
            "category": "otomativ",
            "description": "Dizel, ekonomik, full+full",
            "location": "Bursa",
            "stock": 1,
        },
    ]
    
    added_count = 0
    for listing in test_listings:
        result = await insert_listing(**listing)
        if result.get('success'):
            added_count += 1
            print(f"✅ Eklendi: {listing['title']}")
        else:
            print(f"❌ Eklenemedi: {listing['title']} - {result.get('error')}")
    
    print(f"\n📊 Toplam {added_count}/{len(test_listings)} ilan eklendi")
    
    # Şimdi otomotiv kategorisindeki tüm ilanları arayalım
    print("\n2️⃣ OTOMOTİV KATEGORİSİNDE ARAMA")
    print("-" * 60)
    
    result = await search_listings(category="otomativ", limit=20)
    
    print(f"Success: {result.get('success')}")
    print(f"Bulunan ilan sayısı: {result.get('count')}")
    
    if result.get('success') and result.get('results'):
        print("\n📋 BULUNAN OTOMOTİV İLANLARI:")
        print("-" * 60)
        
        for i, item in enumerate(result.get('results', []), 1):
            title = item.get('title')
            price = item.get('price')
            condition = item.get('condition', 'N/A')
            location = item.get('location', 'N/A')
            
            print(f"\n{i}. {title}")
            print(f"   💰 Fiyat: {price:,.0f} TL")
            print(f"   📍 Lokasyon: {location}")
            print(f"   🏷️  Durum: {condition}")
    else:
        print(f"❌ Arama hatası: {result.get('error')}")
    
    # Fiyat aralığında arama
    print("\n3️⃣ OTOMOTİV - FİYAT FİLTRESİ (700,000 - 1,000,000 TL)")
    print("-" * 60)
    
    result = await search_listings(
        category="otomativ",
        min_price=700000,
        max_price=1000000,
        limit=20
    )
    
    print(f"Bulunan ilan sayısı: {result.get('count')}")
    
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', []), 1):
            print(f"{i}. {item.get('title')} - {item.get('price'):,.0f} TL")
    
    # Lokasyon filtresi
    print("\n4️⃣ OTOMOTİV - LOKASYON FİLTRESİ (İstanbul)")
    print("-" * 60)
    
    result = await search_listings(
        category="otomativ",
        location="İstanbul",
        limit=20
    )
    
    print(f"İstanbul'daki otomotiv ilanları: {result.get('count')}")
    
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', []), 1):
            print(f"{i}. {item.get('title')} - {item.get('location')}")
    
    # Arama sorgusu ile
    print("\n5️⃣ OTOMOTİV - ARAMA (BMW)")
    print("-" * 60)
    
    result = await search_listings(
        category="otomativ",
        query="BMW",
        limit=20
    )
    
    print(f"BMW araması: {result.get('count')} sonuç")
    
    if result.get('success') and result.get('results'):
        for i, item in enumerate(result.get('results', []), 1):
            print(f"{i}. {item.get('title')} - {item.get('price'):,.0f} TL")
    
    print("\n" + "=" * 60)
    print("✅ OTOMOTİV KATEGORİSİ TESTİ TAMAMLANDI")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_automotive_category())
