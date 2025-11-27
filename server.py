# server.py

import os
from typing import Optional, Dict, Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Eğer mcp yüklü değilse, runtime'da yüklenecek
    FastMCP = None  # type: ignore

from tools.clean_price import clean_price as clean_price_core
from tools.insert_listing import insert_listing as insert_listing_core
from tools.search_listings import search_listings as search_listings_core


# FastMCP instance oluştur
if FastMCP:
    mcp = FastMCP("pazarglobal-mcp-python")
else:
    raise ImportError("mcp paketi yüklü değil. 'pip install mcp' çalıştırın.")


@mcp.tool()
async def clean_price_tool(price_text: Optional[str]) -> Dict[str, Optional[int]]:
    """
    Fiyat metnini temizler ve sayısal değeri döndürür.
    
    Örnek kullanım:
    - "1,250 TL" → {"clean_price": 1250}
    - "₺2.500" → {"clean_price": 2500}
    - None veya "" → {"clean_price": None}
    
    Args:
        price_text: Temizlenecek fiyat metni
        
    Returns:
        Temizlenmiş fiyat değeri (int veya None)
    """
    return clean_price_core(price_text)


@mcp.tool()
async def insert_listing_tool(
    product_name: str,
    brand: Optional[str] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    original_price_text: Optional[str] = None,
    clean_price: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Yeni ilan ekler (Supabase 'listings' tablosuna).
    
    Args:
        product_name: Ürün adı (zorunlu)
        brand: Marka (opsiyonel)
        condition: Durum (opsiyonel, örn: "Yeni", "İkinci El")
        category: Kategori (opsiyonel)
        description: Ürün açıklaması (opsiyonel)
        original_price_text: Orijinal fiyat metni (opsiyonel)
        clean_price: Temizlenmiş fiyat sayısı (opsiyonel)
        
    Returns:
        Dict içinde success, status ve result/error bilgisi
    """

    return await insert_listing_core(
        product_name=product_name,
        brand=brand,
        condition=condition,
        category=category,
        description=description,
        original_price_text=original_price_text,
        clean_price=clean_price,
    )


@mcp.tool()
async def search_listings_tool(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Supabase'den ilan arar.
    
    WhatsApp kullanım örnekleri:
    - "iPhone aramak istiyorum" → query="iPhone"
    - "5000 TL altı laptop" → query="laptop", max_price=5000
    - "Yeni Samsung telefonlar" → brand="Samsung", query="telefon"
    
    Args:
        query: Arama metni (opsiyonel)
        category: Kategori filtresi (opsiyonel)
        brand: Marka filtresi (opsiyonel)
        min_price: Minimum fiyat (opsiyonel)
        max_price: Maximum fiyat (opsiyonel)
        limit: Sonuç sayısı (default: 10)
        
    Returns:
        Bulunan ilanların listesi
    """
    return await search_listings_core(
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )


if __name__ == "__main__":
    # Railway PORT değişkenini dinle, yoksa 8000 kullan
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Pazarglobal MCP Server başlatılıyor...")
    print(f"📡 Host: {host}")
    print(f"📡 Port: {port}")
    print(f"🔧 Tools: clean_price_tool, insert_listing_tool, search_listings_tool")
    print(f"🌐 Transport: SSE (Server-Sent Events)")
    
    # FastMCP server'ı SSE ile çalıştır (Railway/uzak server için)
    mcp.run(transport="sse", host=host, port=port)  # type: ignore
