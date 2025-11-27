# Pazarglobal MCP Server (Python)

Railway üzerinde çalışan, Supabase ile entegre Model Context Protocol (MCP) server'ı.

## 📋 Özellikler

- ✅ **clean_price_tool**: Fiyat metinlerini temizler ve sayısal değere dönüştürür
- ✅ **insert_listing_tool**: Supabase'e yeni ilan ekler
- ✅ **search_listings_tool**: Supabase'den ilan arar (query, kategori, fiyat filtreleri)
- ✅ Railway otomatik deployment
- ✅ OpenAI/Claude Agent Builder uyumlu
- ✅ WhatsApp entegrasyonu için hazır

## 🏗️ Proje Yapısı

```
pazarglobal_mcp/
├── server.py                 # MCP server (FastMCP)
├── requirements.txt          # Python bağımlılıkları
├── .env.example             # Örnek environment variables
├── tools/
│   ├── __init__.py
│   ├── clean_price.py       # Fiyat temizleme fonksiyonu
│   ├── insert_listing.py    # Supabase insert fonksiyonu
│   └── search_listings.py   # Supabase search fonksiyonu
└── README.md
```

## 🚀 Railway'de Deployment

### 1. Railway Projesi Oluştur

1. [Railway.app](https://railway.app) hesabınıza giriş yapın
2. **New Project** → **Deploy from GitHub repo**
3. Bu repository'yi seçin

### 2. Environment Variables Ayarla

Railway Dashboard → Variables sekmesinde:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

### 3. Build & Start Ayarları

Railway otomatik algılayacak, ama manuel ayarlamak isterseniz:

**Settings** sekmesinde:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python server.py`
- **Port**: Railway otomatik `PORT` değişkeni sağlar (default: 8000)

### 4. Domain Alın

- **Settings** → **Networking** → **Generate Domain**
- Örnek: `https://pazarglobal-mcp-production.up.railway.app`

## 🔌 Agent Builder'da Kullanım

### OpenAI/Claude Agent Builder

1. **MCP Server Ekle**:
   - URL: `https://your-railway-domain.up.railway.app/`
   - Type: HTTP MCP

2. **Tools Otomatik Görünecek**:
   - `clean_price_tool`
   - `insert_listing_tool`
   - `search_listings_tool`

### Örnek Kullanım

#### clean_price_tool
```json
{
  "price_text": "1,250 TL"
}
```
**Sonuç**:
```json
{
  "clean_price": 1250
}
```

#### insert_listing_tool
```json
{
  "product_name": "iPhone 15 Pro",
  "brand": "Apple",
  "condition": "Yeni",
  "category": "Elektronik",
  "description": "128GB, Siyah Titanyum",
  "original_price_text": "₺54,999",
  "clean_price": 54999
}
```
**Sonuç**:
```json
{
  "success": true,
  "status": 201,
  "result": {
    "id": 123,
    "product_name": "iPhone 15 Pro",
    ...
  }
}
```

#### search_listings_tool
```json
{
  "query": "iPhone",
  "max_price": 50000,
  "limit": 5
}
```
**Sonuç**:
```json
{
  "success": true,
  "count": 3,
  "results": [
    {
      "id": 123,
      "product_name": "iPhone 15 Pro",
      "brand": "Apple",
      "clean_price": 54999,
      ...
    },
    ...
  ]
}
```

## 💬 WhatsApp Kullanım Senaryoları

### Gereksinimler

- Python 3.11+
- pip

### Kurulum

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. .env dosyası oluştur
cp .env.example .env
# .env dosyasını düzenle

# 3. Server'ı çalıştır
python server.py
```

### Test

```bash
# clean_price_tool test
curl -X POST http://localhost:8000/tools/clean_price_tool \
  -H "Content-Type: application/json" \
  -d '{"price_text": "1,250 TL"}'

# insert_listing_tool test
curl -X POST http://localhost:8000/tools/insert_listing_tool \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Ürün",
    "brand": "Test Marka",
    "clean_price": 100
  }'
```

## 🔧 Teknik Detaylar

### FastMCP

Bu proje MCP kütüphanesinin FastMCP arayüzünü kullanır:
- Type hints otomatik JSON Schema'ya dönüşür
- HTTP MCP endpoint'leri otomatik oluşturulur
- OpenAI/Claude Agent Builder ile doğrudan entegre

### Supabase Entegrasyonu

REST API üzerinden doğrudan bağlantı:
- `Authorization: Bearer {SUPABASE_SERVICE_KEY}`
- `Prefer: return=representation` (insert sonucu döndürür)
- Timeout: 20 saniye

### Error Handling

Tüm fonksiyonlar hata durumlarını yönetir:
- Eksik env variables → 500 error
- Network timeout → 408 error
- Genel hatalar → 500 error + detaylı mesaj

## 📝 Supabase Tablo Şeması

`listings` tablosu için örnek şema:

```sql
CREATE TABLE listings (
  id BIGSERIAL PRIMARY KEY,
  product_name TEXT NOT NULL,
  brand TEXT,
  condition TEXT,
  category TEXT,
  description TEXT,
  original_price_text TEXT,
  clean_price INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🐛 Troubleshooting

### Railway Logs Kontrol

```bash
# Railway CLI ile
railway logs

# Veya Railway Dashboard → Deployments → View Logs
```

### Yaygın Hatalar

**1. Module 'mcp' not found**
- Solution: `requirements.txt` eksik, Railway build komutunu kontrol edin

**2. SUPABASE_URL tanımlı değil**
- Solution: Railway environment variables'ı kontrol edin

**3. Connection timeout**
- Solution: Supabase URL'in doğru ve erişilebilir olduğundan emin olun

## 📚 Kaynaklar

- [MCP Documentation](https://modelcontextprotocol.io/)
- [FastMCP Guide](https://github.com/modelcontextprotocol/python-sdk)
- [Railway Docs](https://docs.railway.app/)
- [Supabase REST API](https://supabase.com/docs/guides/api)

## 📄 License

MIT

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

---

**Developed with ❤️ for Pazarglobal**
