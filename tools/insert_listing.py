# tools/insert_listing.py

import os
from typing import Any, Dict, Optional

import httpx


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def insert_listing(
    title: str,
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Supabase REST API üzerinden 'listings' tablosuna kayıt ekler.
    
    Args:
        title: Ürün başlığı (zorunlu)
        price: Fiyat (sayısal)
        condition: Durum (örn: "new", "used")
        category: Kategori
        description: Açıklama
        location: Lokasyon
        stock: Stok adedi
        
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

    url = f"{SUPABASE_URL}/rest/v1/listings"

    payload: Dict[str, Any] = {
        "title": title,
        "price": price,
        "condition": condition,
        "category": category,
        "description": description,
        "location": location,
        "stock": stock,
        "status": "active",
    }

    headers = {
        "Content-Type": "application/json",
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Prefer": "return=representation",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload, headers=headers)

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
    except httpx.TimeoutException:
        return {
            "success": False,
            "status": 408,
            "error": "Request timeout - Supabase bağlantısı zaman aşımına uğradı",
        }
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "error": f"Beklenmeyen hata: {str(e)}",
        }
