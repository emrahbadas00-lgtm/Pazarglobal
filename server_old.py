# server.py

import os
from typing import Optional, Dict, Any

# CRITICAL FIX: Disable host validation for Railway
# Set this BEFORE importing FastMCP
os.environ["MCP_DISABLE_HOST_CHECK"] = "1"

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
    user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Yeni ilan ekler (Supabase 'listings' tablosuna).
    
    Args:
        title: Ürün başlığı (zorunlu)
        user_id: Kullanıcı UUID (WhatsApp entegrasyonunda otomatik gelecek)
        price: Fiyat (opsiyonel)
        condition: Durum (opsiyonel, örn: "new", "used")
        category: Kategori (opsiyonel)
        description: Ürün açıklaması (opsiyonel)
        location: Lokasyon (opsiyonel)
        stock: Stok adedi (opsiyonel)
        metadata: JSONB metadata - örn: {"type": "vehicle", "brand": "BMW", "model": "320i", "year": 2018}
        
    Returns:
        Dict içinde success, status ve result/error bilgisi
    """
    print(f"🔧 insert_listing_tool called with: title={title}, user_id={user_id}, price={price}, condition={condition}, category={category}, location={location}, metadata={metadata}")
    
    result = await insert_listing_core(
        title=title,
        user_id=user_id,
        price=price,
        condition=condition,
        category=category,
        description=description,
        location=location,
        stock=stock,
        metadata=metadata,
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
    metadata_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Supabase'den ilan arar.
    
    WhatsApp kullanım örnekleri:
    - "iPhone aramak istiyorum" → query="iPhone"
    - "5000 TL altı laptop" → query="laptop", max_price=5000
    - "İstanbul'da yeni telefonlar" → location="İstanbul", condition="new"
    - "araba var mı" → category="Otomotiv", metadata_type="vehicle"
    - "otomotiv yedek parçası" → category="Otomotiv", metadata_type="part"
    
    Args:
        query: Arama metni (opsiyonel)
        category: Kategori filtresi (opsiyonel)
        condition: Durum filtresi (opsiyonel, "new" veya "used")
        location: Lokasyon filtresi (opsiyonel)
        min_price: Minimum fiyat (opsiyonel)
        max_price: Maximum fiyat (opsiyonel)
        limit: Sonuç sayısı (default: 10)
        metadata_type: Tip filtresi - "vehicle", "part", "accessory" (opsiyonel)
        
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
        metadata_type=metadata_type,
    )


@mcp.tool()
async def update_listing_tool(
    listing_id: str,
    user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    title: Optional[str] = None,
    price: Optional[int] = None,
    condition: Optional[str] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    stock: Optional[int] = None,
    status: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Mevcut bir ilanı günceller.
    
    WhatsApp kullanım örnekleri:
    - "ilanımın fiyatını 22 bin yap" → update_listing_tool(listing_id="...", price=22000)
    - "açıklamasını değiştir" → update_listing_tool(listing_id="...", description="...")
    - "durumunu satıldı yap" → update_listing_tool(listing_id="...", status="sold")
    - "metadata güncelle" → update_listing_tool(listing_id="...", metadata={"type": "vehicle", "brand": "BMW"})
    
    Args:
        listing_id: Güncellenecek ilanın UUID'si (zorunlu)
        user_id: Kullanıcı UUID (RLS validation için, WhatsApp phase'de aktif olacak)
        title: Yeni başlık (opsiyonel)
        price: Yeni fiyat (opsiyonel)
        condition: Yeni durum (opsiyonel)
        category: Yeni kategori (opsiyonel)
        description: Yeni açıklama (opsiyonel)
        location: Yeni lokasyon (opsiyonel)
        stock: Yeni stok (opsiyonel)
        status: Yeni durum - draft/active/sold/inactive (opsiyonel)
        metadata: Yeni metadata - {"type": "vehicle", "brand": "BMW", ...} (opsiyonel)
        
    Returns:
        success, status_code, result/error
    """
    print(f"🔧 update_listing_tool called for listing_id={listing_id}, user_id={user_id}, metadata={metadata}")
    
    result = await update_listing_core(
        listing_id=listing_id,
        user_id=user_id,
        title=title,
        price=price,
        condition=condition,
        category=category,
        description=description,
        location=location,
        stock=stock,
        status=status,
        metadata=metadata,
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


# ============================================================
# SECURITY TOOLS
# ============================================================

# TEMPORARILY DISABLED - bcrypt not installed in Railway
# @mcp.tool()
# async def verify_pin(phone: str, pin: str) -> Dict[str, Any]:
#     """
#     Kullanıcı PIN doğrulama ve session oluşturma.
#     
#     WhatsApp kullanım:
#     - "1234" → verify_pin(phone="+905551234567", pin="1234")
#     
#     Args:
#         phone: WhatsApp telefon numarası (örn: "+905551234567")
#         pin: 4-6 haneli PIN kodu
#         
#     Returns:
#         success, session_token, message, blocked_until
#     """
#     print(f"🔐 verify_pin called for phone={phone}")
#     result = await verify_pin_tool(phone, pin)
#     print(f"✅ verify_pin result: {result}")
#     return result


# @mcp.tool()
# async def check_session(phone: str, session_token: str) -> Dict[str, Any]:
#     """
#     Session geçerliliğini kontrol et.
#     
#     Args:
#         phone: WhatsApp telefon numarası
#         session_token: verify_pin'den dönen token
#         
#     Returns:
#         valid, expires_at, message
#     """
#     print(f"🔐 check_session called for phone={phone}")
#     result = await check_session_tool(phone, session_token)
#     print(f"✅ check_session result: {result}")
#     return result


# @mcp.tool()
# async def check_rate_limit(
#     user_id: str,
#     phone: str,
#     action: str,
#     max_allowed: int
# ) -> Dict[str, Any]:
#     """
#     Rate limit kontrolü ve artırma.
#     
#     Args:
#         user_id: Kullanıcı UUID
#         phone: WhatsApp telefon numarası
#         action: İşlem tipi (örn: "delete_listing", "insert_listing")
#         max_allowed: Günlük maksimum limit
#         
#     Returns:
#         allowed, current_count, max_allowed, resets_at, message
#     """
#     print(f"⚡ check_rate_limit called for action={action}, user={user_id}")
#     result = await check_rate_limit_tool(user_id, phone, action, max_allowed)
#     print(f"✅ check_rate_limit result: {result}")
#     return result


# @mcp.tool()
# async def log_audit(
#     user_id: str,
#     phone: str,
#     action: str,
#     resource_type: str,
#     resource_id: Optional[str] = None,
#     response_status: str = "success",
#     error_message: Optional[str] = None
# ) -> Dict[str, Any]:
#     """
#     Audit log kaydı oluştur.
#     
#     Args:
#         user_id: Kullanıcı UUID
#         phone: WhatsApp telefon numarası
#         action: İşlem tipi (örn: "delete_listing")
#         resource_type: Kaynak tipi (örn: "listing")
#         resource_id: Kaynak UUID (opsiyonel)
#         response_status: Durum (success, failed, unauthorized, rate_limited)
#         error_message: Hata detayı (opsiyonel)
#         
#     Returns:
#         success, log_id, message
#     """
#     print(f"📝 log_audit called for action={action}")
#     result = await log_audit_tool(
#         user_id, phone, action, resource_type,
#         resource_id, response_status, error_message
#     )
#     print(f"✅ log_audit result: {result}")
#     return result


# @mcp.tool()
# async def register_user_pin(user_id: str, phone: str, pin: str) -> Dict[str, Any]:
#     """
#     Yeni kullanıcı için PIN kaydı (ilk kurulum).
#     
#     WhatsApp kullanım:
#     - Kullanıcı ilk kez PIN belirliyor
#     
#     Args:
#         user_id: Kullanıcı UUID
#         phone: WhatsApp telefon numarası
#         pin: 4-6 haneli PIN kodu
#         
#     Returns:
#         success, message
#     """
#     print(f"🔐 register_user_pin called for phone={phone}")
#     result = await register_user_pin_tool(user_id, phone, pin)
#     print(f"✅ register_user_pin result: {result}")
#     return result


# @mcp.tool()
# async def get_user_by_phone(phone: str) -> Dict[str, Any]:
#     """
#     Telefon numarasından kullanıcı bilgisi getir.
#     
#     Args:
#         phone: WhatsApp telefon numarası
#         
#     Returns:
#         success, user_id, has_pin, message
#     """
#     print(f"👤 get_user_by_phone called for phone={phone}")
#     result = await get_user_by_phone_tool(phone)
#     print(f"✅ get_user_by_phone result: {result}")
#     return result


if __name__ == "__main__":
    # Railway PORT değişkenini dinle, yoksa 8000 kullan
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Pazarglobal MCP Server başlatılıyor...")
    print(f"📡 Host: {host}:{port}")
    print(f"🔧 Listing Tools: clean_price_tool, insert_listing_tool, search_listings_tool, update_listing_tool, delete_listing_tool, list_user_listings_tool")
    # print(f"🔐 Security Tools: verify_pin, check_session, check_rate_limit, log_audit, register_user_pin, get_user_by_phone")
    print(f"🌐 SSE Endpoint: http://{host}:{port}/sse")
    print("⚠️  Host validation DISABLED for Railway compatibility")
    
    # CRITICAL FIX: Monkey-patch FastMCP's host validation
    # Railway's proxy infrastructure requires this
    import mcp.server.sse
    
    # Store original function
    _original_connect_sse = mcp.server.sse.connect_sse
    
    # Create patched version that skips host validation
    async def _patched_connect_sse(scope, receive, send):
        """
        Patched version of connect_sse that bypasses host validation.
        Necessary for Railway deployment where proxy sends internal hostnames.
        """
        from contextlib import asynccontextmanager
        from mcp.server.sse import SseServerTransport
        
        @asynccontextmanager
        async def _inner():
            # Create transport directly, bypassing validation
            transport = SseServerTransport("/messages", scope, receive, send)
            try:
                yield transport
            finally:
                await transport.close()
        
        return _inner()
    
    # Replace the function
    mcp.server.sse.connect_sse = _patched_connect_sse
    
    # Now get the app - it will use our patched function
    import uvicorn
    mcp_sse_app = mcp.sse_app()
    
    uvicorn.run(
        mcp_sse_app,
        host=host,
        port=port,
        log_level="info"
    )
