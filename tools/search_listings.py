# tools/search_listings.py

import os
from typing import Any, Dict, Optional, List

import httpx


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def search_listings(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Supabase'den ilan arama.
    WhatsApp'tan: "iPhone aramak istiyorum" → query="iPhone"
    
    Args:
        query: Arama metni (product_name içinde ara)
        category: Kategori filtresi
        brand: Marka filtresi
        min_price: Minimum fiyat
        max_price: Maximum fiyat
        limit: Sonuç sayısı (default: 10)
        
    Returns:
        İlan listesi veya hata mesajı
    """

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return {
            "success": False,
            "error": "SUPABASE_URL veya SUPABASE_SERVICE_KEY tanımlı değil",
        }

    url = f"{SUPABASE_URL}/rest/v1/listings"
    
    # Supabase query parametreleri
    params: Dict[str, Any] = {"limit": limit, "order": "created_at.desc"}
    
    # Filtreler
    filters: List[str] = []
    
    if query:
        # product_name veya description içinde ara (case-insensitive)
        filters.append(f"or=(product_name.ilike.*{query}*,description.ilike.*{query}*)")
    
    if category:
        filters.append(f"category=eq.{category}")
    
    if brand:
        filters.append(f"brand=eq.{brand}")
    
    if min_price is not None:
        filters.append(f"clean_price=gte.{min_price}")
    
    if max_price is not None:
        filters.append(f"clean_price=lte.{max_price}")
    
    # Filtreleri URL'e ekle
    if filters:
        params.update({f"filter_{i}": f for i, f in enumerate(filters)})

    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params, headers=headers)

        if resp.is_success:
            data = resp.json()
            return {
                "success": True,
                "count": len(data),
                "results": data,
            }
        else:
            return {
                "success": False,
                "status": resp.status_code,
                "error": resp.text,
            }
            
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timeout - Supabase bağlantısı zaman aşımına uğradı",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Beklenmeyen hata: {str(e)}",
        }
