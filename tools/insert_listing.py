# tools/insert_listing.py

import os
from typing import Any, Dict, Optional

import httpx


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def insert_listing(
    title: str,
    user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",  # Default test user for development
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Supabase REST API üzerinden 'listings' tablosuna kayıt ekler.
    
    Args:
        title: Ürün başlığı (zorunlu)
        user_id: Kullanıcı UUID (WhatsApp entegrasyonunda otomatik gelecek)
        price: Fiyat (sayısal)
        condition: Durum (örn: "new", "used")
        category: Kategori
        description: Açıklama
        location: Lokasyon
        stock: Stok adedi
        metadata: JSONB metadata (type, brand, model, year, etc.)
        
    Returns:
        Dict içinde success, status ve result anahtarları
        Örnek: {"success": True, "status": 201, "result": {...}}
    """

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return {
            "success": False,
            "status": 500,
            "error": "SUPABASE_URL veya SUPABASE_SERVICE_KEY tanımlı değil",
        }
    
    # TEMPORARY FIX: Always use default UUID until user authentication is implemented
    # This bypasses RLS checks for testing
    print(f"🔧 Original user_id: {user_id}")
    user_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    print(f"🔧 Using default test UUID: {user_id}")

    url = f"{SUPABASE_URL}/rest/v1/listings"

    payload: Dict[str, Any] = {
        "user_id": user_id,
        "title": title,
        "price": price,
        "condition": condition,
        "category": category,
        "description": description,
        "location": location,
        "stock": stock,
        "status": "active",
        "metadata": metadata,
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Prefer": "return=representation",
    }

    try:
        print(f"📡 Attempting POST to: {url}")
        print(f"📦 Payload: {payload}")
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.post(url, json=payload, headers=headers)
        
        print(f"✅ Response status: {resp.status_code}")

        data = None
        try:
            data = resp.json()
        except Exception:
            data = resp.text

        return {
            "success": resp.is_success,
            "status": resp.status_code,
            "result": data,
        }
    except httpx.TimeoutException as e:
        print(f"⏱️ Timeout error: {str(e)}")
        return {
            "success": False,
            "status": 408,
            "error": f"Request timeout - Supabase bağlantısı zaman aşımına uğradı: {str(e)}",
        }
    except httpx.ConnectError as e:
        print(f"🔌 Connection error: {str(e)}")
        return {
            "success": False,
            "status": 503,
            "error": f"Supabase bağlantısı kurulamadı: {str(e)}",
        }
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "status": 500,
            "error": f"Beklenmeyen hata ({type(e).__name__}): {str(e)}",
        }
