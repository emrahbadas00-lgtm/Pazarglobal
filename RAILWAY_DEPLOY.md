# 🚂 Railway Deployment Rehberi

## 📋 Ön Hazırlık

### ✅ Kontrol Listesi:
- [x] GitHub'a kod yüklendi
- [x] `requirements.txt` hazır
- [x] `railway.json` konfigürasyonu mevcut
- [x] `.railwayignore` oluşturuldu
- [x] Tools test edildi ve çalışıyor

## 🚀 Adım Adım Railway Deploy

### 1️⃣ Railway Hesabı ve Proje Oluşturma

1. **Railway'e giriş yap**: https://railway.app/login
   - GitHub hesabınla giriş yap
   
2. **New Project** butonuna tıkla

3. **Deploy from GitHub repo** seçeneğini seç

4. **Pazarglobal** repository'sini bul ve seç
   - Repository listesinde görünmüyorsa:
     - "Configure GitHub App" → Pazarglobal repo'suna erişim ver

### 2️⃣ Environment Variables Ekleme

Deploy başlamadan ÖNCE environment variables ekle:

1. Proje açıldıktan sonra **Variables** sekmesine git

2. Şu değişkenleri ekle (sağ üstte "+ New Variable"):

```
SUPABASE_URL
```
Değer:
```
https://snovwbffwvmkgjulrtsm.supabase.co
```

```
SUPABASE_SERVICE_KEY
```
Değer:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNub3Z3YmZmd3Zta2dqdWxydHNtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzIzNTc0NCwiZXhwIjoyMDc4ODExNzQ0fQ.JlgKvo9PYDOix7HYjPUo59RvrCdjruf5PxCdxgPklCs
```

### 3️⃣ Build ve Deploy Ayarları

Railway otomatik algılayacak ama kontrol etmek için:

1. **Settings** sekmesine git

2. **Build Command** (otomatik):
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Command** (otomatik):
   ```bash
   python server.py
   ```

4. **Python Version** (otomatik `runtime.txt`'den):
   ```
   3.11
   ```

### 4️⃣ Deploy'u Başlat

1. Railway otomatik deploy başlatacak
   
2. **Deployments** sekmesinde ilerlemeyi izle:
   - 📦 Building...
   - 🚀 Deploying...
   - ✅ Success!

3. Logları kontrol et:
   - "View Logs" butonuna tıkla
   - Şunu görmeli:
   ```
   🚀 Pazarglobal MCP Server başlatılıyor...
   📡 Host: 0.0.0.0:XXXX
   🔧 Tools: clean_price_tool, insert_listing_tool, search_listings_tool
   ```

### 5️⃣ Domain (URL) Oluşturma

1. **Settings** sekmesine git

2. **Networking** bölümünde:
   - "Generate Domain" butonuna tıkla
   
3. Domain oluşturulacak:
   ```
   https://pazarglobal-mcp-production.up.railway.app
   ```
   (Sizinki farklı olabilir)

4. **Bu URL'i kopyala** - Agent Builder'da kullanacaksın!

### 6️⃣ Test Etme

Railway terminalinde test:

1. **Deployments** → **View Logs**

2. Server loglarını kontrol et

3. Hata varsa:
   - Environment variables doğru mu?
   - Build başarılı mı?
   - Python versiyonu uyumlu mu?

## 🔗 Agent Builder Entegrasyonu

### OpenAI Agent Builder'da Kullanım:

1. **Agent Builder** → Settings → **MCP Servers**

2. **Add Server**:
   - **Type**: HTTP
   - **URL**: `https://your-domain.up.railway.app`
   - **Name**: Pazarglobal MCP

3. **Save** → Tools otomatik yüklenecek:
   - `clean_price_tool`
   - `insert_listing_tool`
   - `search_listings_tool`

### Test Sorguları:

```
"Supabase'e yeni bir ilan ekle: iPhone 15 Pro, fiyat 55000 TL"

"Otomotiv kategorisindeki tüm ilanları listele"

"Fiyatı 54,999 TL olarak temizle"
```

## 🐛 Sorun Giderme

### Build Hatası:
```bash
# Railway logs'ta kontrol et:
"Module not found" → requirements.txt eksik
"Python version mismatch" → runtime.txt kontrol et
```

### Runtime Hatası:
```bash
"SUPABASE_URL tanımlı değil" → Variables sekmesini kontrol et
"Connection refused" → PORT değişkeni Railway tarafından inject ediliyor
```

### MCP Connection Hatası:
```bash
# Agent Builder'da:
- URL doğru mu? (https:// ile başlamalı)
- Railway deploy'u running durumda mı?
- Logs'ta server çalışıyor mu kontrol et
```

## 📊 Railway Dashboard Özellikleri

### Metrics:
- CPU kullanımı
- Memory kullanımı
- Network trafiği

### Logs:
- Real-time log streaming
- Error filtreleme
- Log download

### Deployments:
- Deployment history
- Rollback imkanı
- Manual redeploy

## 💰 Maliyet

Railway Free Tier:
- $5 kredi/ay
- Sleep after inactivity (kendi hesabınızda değiştirilebilir)
- MCP server bu krediye sığar

## 🔄 Otomatik Deploy

GitHub'a her push'ta otomatik deploy:

1. Kod değişikliği yap
2. Git commit + push
3. Railway otomatik yeniden deploy eder
4. Zero-downtime deployment

## ✅ Deploy Tamamlandı!

Şimdi hazırsınız:
- ✅ Railway'de çalışan MCP server
- ✅ 3 tool hazır ve test edilmiş
- ✅ Agent Builder entegrasyonu için URL
- ✅ WhatsApp bot'unuz için hazır backend

---

**Başarılar! 🎉**
