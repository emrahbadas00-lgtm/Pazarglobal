import asyncio
from dotenv import load_dotenv

load_dotenv()

from tools.search_listings import search_listings


async def show_real_listings():
    """Supabase'deki gerçek ilanları göster"""
    
    print("=" * 60)
    print("📊 SUPABASE'DEKİ GERÇEK İLANLAR")
    print("=" * 60)
    
    # 1. Tüm ilanlar
    print("\n1️⃣ TÜM İLANLAR")
    print("-" * 60)
    
    result = await search_listings(limit=50)
    
    if result.get('success'):
        results = result.get('results', [])
        print(f"Toplam ilan sayısı: {len(results)}")
        
        if results:
            print("\n📋 İLAN LİSTESİ:")
            print("-" * 60)
            
            for i, item in enumerate(results, 1):
                title = item.get('title', 'N/A')
                price = item.get('price')
                category = item.get('category', 'N/A')
                condition = item.get('condition', 'N/A')
                location = item.get('location', 'N/A')
                created_at = item.get('created_at', 'N/A')
                
                print(f"\n{i}. {title}")
                print(f"   💰 Fiyat: {price:,.0f} TL" if price else "   💰 Fiyat: Belirtilmemiş")
                print(f"   📁 Kategori: {category}")
                print(f"   🏷️  Durum: {condition}")
                print(f"   📍 Lokasyon: {location}")
                print(f"   📅 Tarih: {created_at[:10] if created_at != 'N/A' else 'N/A'}")
        else:
            print("❌ Henüz hiç ilan yok")
    else:
        print(f"❌ Hata: {result.get('error')}")
    
    # 2. Kategorilere göre grupla
    if result.get('success') and result.get('results'):
        print("\n2️⃣ KATEGORİLERE GÖRE DAĞILIM")
        print("-" * 60)
        
        categories = {}
        for item in result.get('results', []):
            cat = item.get('category', 'Belirtilmemiş')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"📁 {cat}: {count} ilan")
    
    # 3. Otomotiv kategorisi varsa göster
    print("\n3️⃣ OTOMOTİV KATEGORİSİ")
    print("-" * 60)
    
    result = await search_listings(category="otomativ", limit=50)
    
    if result.get('success'):
        count = result.get('count', 0)
        results = result.get('results', [])
        
        print(f"Otomotiv ilanı sayısı: {count}")
        
        if results:
            for i, item in enumerate(results, 1):
                title = item.get('title', 'N/A')
                price = item.get('price')
                location = item.get('location', 'N/A')
                
                print(f"\n{i}. {title}")
                print(f"   💰 {price:,.0f} TL" if price else "   💰 Belirtilmemiş")
                print(f"   📍 {location}")
        else:
            print("ℹ️  Henüz otomotiv ilanı yok")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(show_real_listings())
