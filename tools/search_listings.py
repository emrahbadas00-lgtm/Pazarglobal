# tools/search_listings.py

import os
from typing import Any, Dict, Optional

import httpx


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


async def search_listings(
    query: Optional[str] = None,
    category: Optional[str] = None,
    condition: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Supabase'den ilan arama.
    WhatsApp'tan: "iPhone aramak istiyorum" → query="iPhone"
    
    Args:
        query: Arama metni (title içinde ara)
        category: Kategori filtresi
        condition: Durum filtresi ("new", "used")
        location: Lokasyon filtresi
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
    params: Dict[str, str] = {"limit": str(limit), "order": "created_at.desc"}
    
    # Filtreler - Supabase PostgREST syntax
    if query:
        # Synonym expansion for generic terms
        query_lower = query.lower()
        
        # "araba" / "otomobil" → DON'T expand brands, use category filter instead
        # Let agent handle category search fallback
        if query_lower in ["araba", "otomobil", "araç", "oto"]:
            # Remove query, agent should use category="Otomotiv" instead
            # But if agent didn't set category, search in title/description anyway
            if not category:
                params["or"] = f"(title.ilike.*{query}*,description.ilike.*{query}*,category.ilike.*otom*)"
        else:
            # Normal search: title veya description içinde ara (case-insensitive)
            params["or"] = f"(title.ilike.*{query}*,description.ilike.*{query}*)"
    
    if category:
        # Category normalization - case insensitive match
        params["category"] = f"ilike.{category}"
    
    if condition:
        params["condition"] = f"eq.{condition}"
    
    if location:
        params["location"] = f"eq.{location}"
    
    if min_price is not None:
        params["price"] = f"gte.{min_price}"
    
    if max_price is not None:
        if "price" in params:
            # Hem min hem max varsa
            params["price"] = f"gte.{min_price}&price=lte.{max_price}"
        else:
            params["price"] = f"lte.{max_price}"

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
