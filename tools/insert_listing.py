# tools/insert_listing.py

import os
from typing import Any, Dict, Optional

import httpx


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def insert_listing(
    product_name: str,
    brand: Optional[str] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    original_price_text: Optional[str] = None,
    clean_price: Optional[int] = None,
) -> Dict[str, Any]:
    """
    JS'deki insertListing ile aynı işi yapar:
    Supabase REST API üzerinden 'listings' tablosuna kayıt ekler.
    
    Args:
        product_name: Ürün adı (zorunlu)
        brand: Marka
        condition: Durum (örn: "Yeni", "İkinci El")
        category: Kategori
        description: Açıklama
        original_price_text: Orijinal fiyat metni
        clean_price: Temizlenmiş fiyat (sayısal)
        
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
        "product_name": product_name,
        "brand": brand,
        "condition": condition,
        "category": category,
        "description": description,
        "original_price_text": original_price_text,
        "clean_price": clean_price,
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
