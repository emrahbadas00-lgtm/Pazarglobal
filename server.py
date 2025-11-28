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
from tools.update_listing import update_listing as update_listing_core
from tools.delete_listing import delete_listing as delete_listing_core
from tools.list_user_listings import list_user_listings as list_user_listings_core


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
    print(f"🔧 clean_price_tool called with: {price_text}")
    result = clean_price_core(price_text)
    print(f"✅ clean_price_tool result: {result}")
    return result


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
    print(f"🔧 insert_listing_tool called with: title={title}, price={price}, condition={condition}, category={category}, location={location}")
    
    result = await insert_listing_core(
        title=title,
        price=price,
        condition=condition,
        category=category,
        description=description,
        location=location,
        stock=stock,
    )
    
    print(f"✅ insert_listing_tool result: {result}")
    return result


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


@mcp.tool()
async def update_listing_tool(
    listing_id: str,
    title: Optional[str] = None,
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Mevcut bir ilanı günceller.
    
    WhatsApp kullanım örnekleri:
    - "ilanımın fiyatını 22 bin yap" → update_listing_tool(listing_id="...", price=22000)
    - "açıklamasını değiştir" → update_listing_tool(listing_id="...", description="...")
    - "durumunu satıldı yap" → update_listing_tool(listing_id="...", status="sold")
    
    Args:
        listing_id: Güncellenecek ilanın UUID'si (zorunlu)
        title: Yeni başlık (opsiyonel)
        price: Yeni fiyat (opsiyonel)
        condition: Yeni durum (opsiyonel)
        category: Yeni kategori (opsiyonel)
        description: Yeni açıklama (opsiyonel)
        location: Yeni lokasyon (opsiyonel)
        stock: Yeni stok (opsiyonel)
        status: Yeni durum - draft/active/sold/inactive (opsiyonel)
        
    Returns:
        success, status_code, result/error
    """
    print(f"🔧 update_listing_tool called for listing_id={listing_id}")
    
    result = await update_listing_core(
        listing_id=listing_id,
        title=title,
        price=price,
        condition=condition,
        category=category,
        description=description,
        location=location,
        stock=stock,
        status=status,
    )
    
    print(f"✅ update_listing_tool result: {result}")
    return result


@mcp.tool()
async def delete_listing_tool(listing_id: str) -> Dict[str, Any]:
    """
    Bir ilanı siler.
    
    WhatsApp kullanım örnekleri:
    - "iPhone ilanımı sil"
    - "bu ilanı kaldır"
    
    Args:
        listing_id: Silinecek ilanın UUID'si
        
    Returns:
        success, status_code, message/error
    """
    print(f"🔧 delete_listing_tool called for listing_id={listing_id}")
    
    result = await delete_listing_core(listing_id=listing_id)
    
    print(f"✅ delete_listing_tool result: {result}")
    return result


@mcp.tool()
async def list_user_listings_tool(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Kullanıcının tüm ilanlarını listeler.
    
    Update ve delete işlemleri için önce bu tool ile kullanıcının ilanlarını listele,
    sonra kullanıcıya seçim yaptır.
    
    WhatsApp kullanım örnekleri:
    - "ilanlarımı göster" → list_user_listings_tool(user_id="phone_number")
    - "satılanları listele" → list_user_listings_tool(user_id="...", status="sold")
    
    Args:
        user_id: Kullanıcı ID'si (telefon numarası veya UUID)
        status: İlan durumu filtresi - draft/active/sold/inactive (opsiyonel)
        limit: Maksimum sonuç sayısı (default: 50)
        
    Returns:
        success, status_code, listings, count
    """
    print(f"🔧 list_user_listings_tool called for user_id={user_id}, status={status}")
    
    result = await list_user_listings_core(
        user_id=user_id,
        status=status,
        limit=limit,
    )
    
    print(f"✅ list_user_listings_tool result: {result}")
    return result


if __name__ == "__main__":
    # Railway PORT değişkenini dinle, yoksa 8000 kullan
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Pazarglobal MCP Server başlatılıyor...")
    print(f"📡 Host: {host}:{port}")
    print(f"🔧 Tools: clean_price_tool, insert_listing_tool, search_listings_tool, update_listing_tool, delete_listing_tool, list_user_listings_tool")
    print(f"🌐 SSE Endpoint: http://{host}:{port}/sse")
    
    # FastMCP'nin SSE ASGI app'ini al
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import RedirectResponse
    from starlette.routing import Route, Mount
    
    # FastMCP SSE app'i
    mcp_app = mcp.sse_app()
    
    # POST /sse için redirect handler
    async def sse_post_redirect(request):
        return RedirectResponse(url="/sse", status_code=307)
    
    # Starlette app oluştur - POST ve GET destekli
    app = Starlette(
        routes=[
            Route("/sse", endpoint=sse_post_redirect, methods=["POST"]),
            Mount("/", app=mcp_app),
        ]
    )
    
    # Uvicorn'u manuel başlat
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
