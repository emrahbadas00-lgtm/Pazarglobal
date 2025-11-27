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
    title: str,
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Yeni ilan ekler (Supabase 'listings' tablosuna).
    
    Args:
        title: Ürün başlığı (zorunlu)
        price: Fiyat (opsiyonel)
        condition: Durum (opsiyonel, örn: "new", "used")
        category: Kategori (opsiyonel)
        description: Ürün açıklaması (opsiyonel)
        location: Lokasyon (opsiyonel)
        stock: Stok adedi (opsiyonel)
        
    Returns:
        Dict içinde success, status ve result/error bilgisi
    """

    return await insert_listing_core(
        title=title,
        price=price,
        condition=condition,
        category=category,
        description=description,
        location=location,
        stock=stock,
    )


@mcp.tool()
async def search_listings_tool(
    query: Optional[str] = None,
    category: Optional[str] = None,
    condition: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Supabase'den ilan arar.
    
    WhatsApp kullanım örnekleri:
    - "iPhone aramak istiyorum" → query="iPhone"
    - "5000 TL altı laptop" → query="laptop", max_price=5000
    - "İstanbul'da yeni telefonlar" → location="İstanbul", condition="new"
    
    Args:
        query: Arama metni (opsiyonel)
        category: Kategori filtresi (opsiyonel)
        condition: Durum filtresi (opsiyonel, "new" veya "used")
        location: Lokasyon filtresi (opsiyonel)
        min_price: Minimum fiyat (opsiyonel)
        max_price: Maximum fiyat (opsiyonel)
        limit: Sonuç sayısı (default: 10)
        
    Returns:
        Bulunan ilanların listesi
    """
    return await search_listings_core(
        query=query,
        category=category,
        condition=condition,
        location=location,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
    )


if __name__ == "__main__":
    # Railway PORT değişkenini dinle, yoksa 8000 kullan
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Pazarglobal MCP Server başlatılıyor...")
    print(f"📡 Host: {host}:{port}")
    print(f"🔧 Tools: clean_price_tool, insert_listing_tool, search_listings_tool")
    print(f"🌐 SSE Endpoint: http://{host}:{port}/sse")
    
    # FastMCP run() metodu ile host ve port parametrelerini geçir
    import uvicorn
    
    # FastMCP'nin ASGI app'ini al
    app = mcp._app  # Internal app object
    
    # Uvicorn'u manuel başlat
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
