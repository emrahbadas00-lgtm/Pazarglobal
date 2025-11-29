# Supabase Storage Buckets - Configuration

## Overview
Pazarglobal projesi 2 storage bucket kullanır:
- **product-images**: Ürün görselleri (public)
- **user-documents**: Kullanıcı belgeleri (private)

---

## 1. product-images Bucket

### Ayarlar
```yaml
Name: product-images
Public: Yes
File Size Limit: 5 MB
Allowed MIME Types:
  - image/jpeg
  - image/png
  - image/webp
  - image/jpg
Number of Policies: 2
```

### Policy 1: Public Read Access
```sql
-- Name: Anyone can view product images
-- Operation: SELECT
-- Policy Definition:
CREATE POLICY "Anyone can view product images"
ON storage.objects FOR SELECT
USING (bucket_id = 'product-images');
```

### Policy 2: Authenticated Upload/Delete
```sql
-- Name: Users can upload/delete own images
-- Operation: INSERT, UPDATE, DELETE
-- Policy Definition:
CREATE POLICY "Users can upload/delete own images"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'product-images' AND
    auth.role() = 'authenticated'
);

CREATE POLICY "Users can delete own images"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'product-images' AND
    auth.uid()::text = (storage.foldername(name))[1]
);
```

### Kullanım
```python
# Upload image
supabase.storage.from_('product-images').upload(
    path=f'{user_id}/{listing_id}/image1.jpg',
    file=image_bytes,
    file_options={'content-type': 'image/jpeg'}
)

# Get public URL
url = supabase.storage.from_('product-images').get_public_url(
    f'{user_id}/{listing_id}/image1.jpg'
)

# Delete image
supabase.storage.from_('product-images').remove([
    f'{user_id}/{listing_id}/image1.jpg'
])
```

---

## 2. user-documents Bucket

### Ayarlar
```yaml
Name: user-documents
Public: No
File Size Limit: 10 MB
Allowed MIME Types:
  - application/pdf
  - image/jpeg
  - image/png
Number of Policies: 4
```

### Policy 1: View Own Documents
```sql
-- Name: Users can view own documents
-- Operation: SELECT
-- Policy Definition:
CREATE POLICY "Users can view own documents"
ON storage.objects FOR SELECT
USING (
    bucket_id = 'user-documents' AND
    auth.uid()::text = (storage.foldername(name))[1]
);
```

### Policy 2: Upload Own Documents
```sql
-- Name: Users can upload own documents
-- Operation: INSERT
-- Policy Definition:
CREATE POLICY "Users can upload own documents"
ON storage.objects FOR INSERT
WITH CHECK (
    bucket_id = 'user-documents' AND
    auth.uid()::text = (storage.foldername(name))[1]
);
```

### Policy 3: Update Own Documents
```sql
-- Name: Users can update own documents
-- Operation: UPDATE
-- Policy Definition:
CREATE POLICY "Users can update own documents"
ON storage.objects FOR UPDATE
USING (
    bucket_id = 'user-documents' AND
    auth.uid()::text = (storage.foldername(name))[1]
);
```

### Policy 4: Delete Own Documents
```sql
-- Name: Users can delete own documents
-- Operation: DELETE
-- Policy Definition:
CREATE POLICY "Users can delete own documents"
ON storage.objects FOR DELETE
USING (
    bucket_id = 'user-documents' AND
    auth.uid()::text = (storage.foldername(name))[1]
);
```

### Kullanım
```python
# Upload document
supabase.storage.from_('user-documents').upload(
    path=f'{user_id}/invoice.pdf',
    file=pdf_bytes,
    file_options={'content-type': 'application/pdf'}
)

# Download document (private, requires auth)
response = supabase.storage.from_('user-documents').download(
    f'{user_id}/invoice.pdf'
)

# Create signed URL (temporary access)
signed_url = supabase.storage.from_('user-documents').create_signed_url(
    path=f'{user_id}/invoice.pdf',
    expires_in=3600  # 1 hour
)
```

---

## Storage Path Conventions

### product-images
```
{user_id}/
├── {listing_id}/
│   ├── primary.jpg       # Ana görsel
│   ├── image-1.jpg       # Ek görseller
│   ├── image-2.jpg
│   └── thumbnail.webp    # Küçük boyut
```

### user-documents
```
{user_id}/
├── invoices/
│   ├── 2025-11-29-order-{order_id}.pdf
│   └── ...
├── id-verification/
│   ├── front.jpg
│   └── back.jpg
└── receipts/
    └── ...
```

---

## MCP Tools ile Entegrasyon

### Gelecek Tool'lar

#### 1. upload_product_image
```python
@mcp.tool()
async def upload_product_image(
    listing_id: str,
    image_data: str,  # Base64 encoded
    is_primary: bool = False
) -> dict:
    """Upload product image to storage"""
    # 1. Decode base64
    # 2. Upload to product-images bucket
    # 3. Insert record to product_images table
    # 4. Update listings.image_url if primary
    pass
```

#### 2. delete_product_image
```python
@mcp.tool()
async def delete_product_image(
    image_id: str,
    listing_id: str
) -> dict:
    """Delete product image from storage"""
    # 1. Get storage_path from product_images table
    # 2. Delete from storage bucket
    # 3. Delete record from product_images table
    pass
```

#### 3. list_product_images
```python
@mcp.tool()
async def list_product_images(
    listing_id: str
) -> dict:
    """List all images for a listing"""
    # Return: [
    #   {
    #     "id": "uuid",
    #     "url": "https://...",
    #     "is_primary": true,
    #     "display_order": 0
    #   }
    # ]
    pass
```

---

## Security Notes

### Current State (Development)
- ✅ Bucket yapılandırmaları aktif
- ⚠️ RLS policies `auth.uid()` kullanıyor ama auth henüz yok
- ⚠️ Şu an service_role key ile bypass ediliyor

### Production Requirements
1. **Supabase Auth Integration**
   - WhatsApp ile user authentication
   - JWT token yönetimi
   - Session tracking

2. **Rate Limiting**
   - Upload frequency limits
   - File size validation
   - MIME type enforcement

3. **Content Moderation**
   - Image scanning for inappropriate content
   - Virus scanning for documents
   - Metadata stripping (EXIF removal)

4. **Backup Strategy**
   - Daily bucket backups
   - Versioning for critical documents
   - CDN integration for product images

---

## Testing Commands

### Upload Test Image
```bash
# Using curl
curl -X POST \
  'https://snovwbffwvmkgjulrtsm.supabase.co/storage/v1/object/product-images/test-user/test-listing/test.jpg' \
  -H 'Authorization: Bearer YOUR_SERVICE_KEY' \
  -H 'Content-Type: image/jpeg' \
  --data-binary '@test-image.jpg'
```

### List Bucket Contents
```bash
# Using supabase-py
from supabase import create_client
supabase = create_client(url, key)
files = supabase.storage.from_('product-images').list()
print(files)
```

### Get Storage Stats
```bash
# Via Supabase dashboard
# Settings → Storage → product-images
# Shows:
# - Total files
# - Total size
# - Public URL count
```

---

## Migration Plan

### Phase 1: Current (Development)
- [x] Bucket'lar oluşturuldu
- [x] Temel policy'ler set edildi
- [x] product_images table hazır
- [ ] MCP tools yazılacak

### Phase 2: WhatsApp Integration
- [ ] Auth.uid() entegrasyonu
- [ ] User-specific folders
- [ ] Image upload agent tool
- [ ] Automatic thumbnail generation

### Phase 3: Production
- [ ] CDN integration (Cloudflare)
- [ ] Image optimization pipeline
- [ ] Content moderation
- [ ] Backup automation

---

## Troubleshooting

### Error: "new row violates row-level security policy"
**Cause**: Auth.uid() is null  
**Solution**: Use service_role key or implement auth

### Error: "File size exceeds limit"
**Cause**: File > 5MB (product-images) or > 10MB (user-documents)  
**Solution**: Compress image or split document

### Error: "MIME type not allowed"
**Cause**: Trying to upload unsupported format  
**Solution**: Convert to JPEG/PNG/WEBP (images) or PDF (documents)

---

## Related Files
- `database/complete_schema.sql` - Database schema with storage references
- `tools/insert_listing.py` - Will use image_url from storage
- `tools/update_listing.py` - Can update image references
- Future: `tools/upload_image.py`, `tools/delete_image.py`
