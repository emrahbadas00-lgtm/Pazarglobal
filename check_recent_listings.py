import os
import httpx
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

async def check_recent_listings():
    """Son 10 dakikada eklenen ilanları kontrol et"""
    
    # Son 10 dakikayı hesapla
    ten_minutes_ago = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
    
    url = f"{SUPABASE_URL}/rest/v1/listings"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json"
    }
    
    # created_at'e göre sırala, en yeni önce
    params = {
        "order": "created_at.desc",
        "limit": "10"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            listings = response.json()
            
            print(f"\n📊 Toplam {len(listings)} son ilan bulundu:")
            print("=" * 80)
            
            for idx, listing in enumerate(listings, 1):
                created_at = listing.get('created_at', 'N/A')
                title = listing.get('title', 'N/A')
                price = listing.get('price', 'N/A')
                condition = listing.get('condition', 'N/A')
                location = listing.get('location', 'N/A')
                
                # Timestamp'i parse et
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_diff = datetime.now(created_dt.tzinfo) - created_dt
                    minutes_ago = int(time_diff.total_seconds() / 60)
                    time_str = f"{minutes_ago} dakika önce" if minutes_ago < 60 else created_at
                except:
                    time_str = created_at
                
                print(f"\n{idx}. İlan:")
                print(f"   📝 Başlık: {title}")
                print(f"   💰 Fiyat: {price} TL")
                print(f"   🏷️ Durum: {condition}")
                print(f"   📍 Konum: {location}")
                print(f"   🕒 Oluşturma: {time_str}")
                print(f"   🔑 ID: {listing.get('id', 'N/A')}")
                
                # iPhone 15 Pro kontrolü
                if "iPhone 15 Pro" in title and price == 54999:
                    print(f"   ✅ AGENT BUILDER TEST İLANI BULUNDU!")
            
            print("\n" + "=" * 80)
            
            # İstatistik
            recent_count = sum(1 for l in listings if (datetime.utcnow() - datetime.fromisoformat(l['created_at'].replace('Z', '+00:00'))).total_seconds() < 600)
            print(f"\n📈 Son 10 dakikada eklenen: {recent_count} ilan")
            
        else:
            print(f"❌ Hata: {response.status_code}")
            print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(check_recent_listings())
