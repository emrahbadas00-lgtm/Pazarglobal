import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def check_supabase():
    """Supabase bağlantısını ve tabloları kontrol et"""
    
    print("🔍 Supabase Kontrol")
    print("=" * 60)
    print(f"URL: {SUPABASE_URL}")
    print(f"Service Key: {SUPABASE_SERVICE_KEY[:20]}...")
    
    # Mevcut tabloları listele
    print("\n📋 Mevcut tablolar:")
    
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    
    # Tüm tabloları almayı dene
    async with httpx.AsyncClient(timeout=20.0) as client:
        # listings tablosunu kontrol et
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/listings",
            headers=headers,
            params={"limit": 1}
        )
        
        print(f"\nlistings tablosu:")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"✅ Tablo mevcut")
            data = resp.json()
            print(f"Kayıt sayısı: {len(data)}")
            if data:
                print(f"İlk kayıt kolonları: {list(data[0].keys())}")
        else:
            print(f"❌ Hata: {resp.text}")


if __name__ == "__main__":
    asyncio.run(check_supabase())
