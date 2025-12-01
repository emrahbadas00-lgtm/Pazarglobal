# PazarGlobal Database Schema - Deployment Guide

## 📋 Schema Files Overview

1. **`complete_schema.sql`** - Base tables (users, listings, orders, etc.)
2. **`profiles_schema.sql`** - User profiles with Supabase Auth integration ✨ NEW
3. **`security_schema.sql`** - Security (PIN, sessions, audit logs, rate limits) ✨ NEW

---

## 🚀 Deployment Order (Supabase SQL Editor)

### Step 1: Enable Required Extensions

```sql
-- Run these first in Supabase SQL Editor
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";      -- bcrypt for PIN hashing
CREATE EXTENSION IF NOT EXISTS "pg_trgm";       -- Trigram similarity
```

### Step 2: Run Base Schema

```sql
-- Run complete_schema.sql
-- This creates: users, listings, orders, conversations, etc.
```

### Step 3: Run Profiles Schema

```sql
-- Run profiles_schema.sql
-- This creates:
--   - profiles table (linked to auth.users)
--   - Auto-create profile trigger
--   - Helper functions for phone linking
```

### Step 4: Run Security Schema

```sql
-- Run security_schema.sql
-- This creates:
--   - user_security (PIN, session management)
--   - audit_logs (critical operations logging)
--   - rate_limits (per-user daily limits)
--   - Security functions (verify_pin, check_rate_limit, etc.)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│ Supabase Auth (auth.users)                         │
│ - Email/Password signup                             │
│ - Phone/SMS OTP                                     │
│ - Magic link                                        │
└─────────────────┬───────────────────────────────────┘
                  │ (auth.uid)
                  ↓
┌─────────────────────────────────────────────────────┐
│ profiles (public.profiles)                          │
│ - id: UUID (references auth.users.id)              │
│ - phone: TEXT (WhatsApp number)                    │
│ - email: TEXT                                       │
│ - full_name, avatar_url, location                  │
│ - user_role: buyer/seller/admin                    │
│ - preferences, metadata                            │
└─────────────────┬───────────────────────────────────┘
                  │
       ┌──────────┴──────────┐
       ↓                     ↓
┌─────────────────┐   ┌─────────────────┐
│ user_security   │   │ listings        │
│ - PIN (bcrypt)  │   │ - user_id (FK)  │
│ - session token │   │ - title, price  │
│ - failed tries  │   │ - category, etc.│
└─────────────────┘   └─────────────────┘
       │
       ↓
┌─────────────────┐   ┌─────────────────┐
│ audit_logs      │   │ rate_limits     │
│ - all actions   │   │ - daily limits  │
│ - timestamps    │   │ - per action    │
└─────────────────┘   └─────────────────┘
```

---

## 🔐 Authentication Flow

### Frontend Web App:
1. User signs up with **email/password** via Supabase Auth
2. Profile automatically created (trigger: `on_auth_user_created`)
3. User logs in → gets JWT token from Supabase Auth
4. Frontend calls backend with JWT token

### WhatsApp Integration:
1. User sends message from WhatsApp (phone: `+905551234567`)
2. Backend checks if profile exists with this phone
   ```sql
   SELECT * FROM get_user_by_phone('+905551234567');
   ```
3. If no profile → Create profile + ask for PIN registration
4. If profile exists but no PIN → Ask for PIN registration
5. If profile + PIN exists → Ask for PIN to start session
6. After PIN verified → session token generated (10 min TTL)
7. All subsequent requests use session token

---

## 🛡️ Security Features

### 1. PIN Authentication
- 4-6 digit PIN
- Bcrypt hashed (never stored as plaintext)
- 3 failed attempts → 15 min block
- Function: `verify_pin(phone, pin)`

### 2. Session Management
- Session token: 32-byte random hex
- 10 minute timeout
- Function: `is_session_valid(phone, session_token)`

### 3. Rate Limiting
- Per-user, per-action daily limits:
  - `insert_listing`: 20/day
  - `update_listing`: 50/day
  - `delete_listing`: 10/day
  - `search_listings`: 200/day
- Function: `check_rate_limit(user_id, phone, action, max_allowed)`

### 4. Audit Logging
- Every critical operation logged:
  - Who (user_id, phone)
  - What (action, resource_type, resource_id)
  - When (timestamp)
  - Result (success, failed, unauthorized, rate_limited)
- Function: `log_audit(...)`

### 5. RLS (Row Level Security)
- Users can only see/modify their own data
- Listings: `owner_id = auth.uid()`
- Profiles: `id = auth.uid()`
- Security: `phone = current_setting('app.current_phone')`

---

## 🧪 Testing After Deployment

### 1. Test Profile Creation
```sql
-- Create test user manually (simulates auth signup)
INSERT INTO profiles (id, phone, full_name, user_role)
VALUES (
    gen_random_uuid(),
    '+905551234567',
    'Test User',
    'seller'
);
```

### 2. Test PIN Registration
```sql
-- Register PIN for user
INSERT INTO user_security (user_id, phone, pin_hash)
SELECT 
    id,
    phone,
    crypt('1234', gen_salt('bf'))  -- PIN: 1234
FROM profiles
WHERE phone = '+905551234567';
```

### 3. Test PIN Verification
```sql
-- Verify PIN (should return session token)
SELECT * FROM verify_pin('+905551234567', '1234');
```

### 4. Test Session Check
```sql
-- Check if session is valid
SELECT is_session_valid('+905551234567', 'session-token-here');
```

### 5. Test Rate Limiting
```sql
-- Check rate limit for delete action
SELECT * FROM check_rate_limit(
    'user-uuid-here',
    '+905551234567',
    'delete_listing',
    10  -- max 10 per day
);
```

### 6. Test Audit Logging
```sql
-- Log a test action
SELECT log_audit(
    'user-uuid-here',
    '+905551234567',
    'delete_listing',
    'listing',
    'listing-uuid-here',
    'success'
);

-- View audit logs
SELECT * FROM audit_logs 
WHERE phone = '+905551234567' 
ORDER BY created_at DESC;
```

---

## 📱 Frontend Integration Guide

### Email/Password Signup
```typescript
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password',
  options: {
    data: {
      full_name: 'John Doe',
      phone: '+905551234567'  // Optional
    }
  }
})
// Profile auto-created via trigger
```

### Link WhatsApp Phone (After Signup)
```typescript
const { data } = await supabase.rpc('link_phone_to_profile', {
  p_user_id: user.id,
  p_phone: '+905551234567'
})
```

### Check User by Phone (WhatsApp Bot)
```typescript
const { data } = await supabase.rpc('get_user_by_phone', {
  p_phone: '+905551234567'
})

if (!data || data.length === 0) {
  // User doesn't exist → Create profile + ask for PIN
} else if (!data[0].has_pin) {
  // User exists but no PIN → Ask to set PIN
} else {
  // User exists with PIN → Ask for PIN to login
}
```

---

## 🔄 Migration from Old Schema

If you already have data in the old `users` table:

```sql
-- Migrate users → profiles
INSERT INTO profiles (id, phone, email, full_name, location, created_at)
SELECT 
    id,
    phone,
    email,
    name as full_name,
    location,
    created_at
FROM users
ON CONFLICT (id) DO UPDATE SET
    phone = EXCLUDED.phone,
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    location = EXCLUDED.location;

-- Update listings to use profile IDs (if needed)
-- No changes needed if listings.user_id already matches
```

---

## 🚨 Important Notes

1. **pgcrypto Extension**: Must be enabled for bcrypt (`crypt()` function)
2. **Auth Trigger**: Auto-creates profile when user signs up via Supabase Auth
3. **Phone Format**: Always normalize phone numbers (`+905551234567`)
4. **Session Cleanup**: Consider adding a cron job to delete expired sessions
5. **Rate Limit Reset**: Windows reset automatically after 24 hours
6. **Audit Retention**: Consider archiving old audit logs (>90 days)

---

## 📞 Support Contacts

- Backend: MCP Server (pazarglobal_mcp)
- Frontend: React/Next.js (future)
- WhatsApp: Twilio Integration (pazarglobal-whatsapp-bridge)
- Agent: OpenAI Agents SDK (pazarglobal-agent-backend)

---

## ✅ Deployment Checklist

- [ ] Enable pgcrypto extension
- [ ] Run complete_schema.sql
- [ ] Run profiles_schema.sql
- [ ] Run security_schema.sql
- [ ] Test profile creation
- [ ] Test PIN registration
- [ ] Test PIN verification
- [ ] Test session management
- [ ] Test rate limiting
- [ ] Test audit logging
- [ ] Enable Supabase Auth (Email provider)
- [ ] Enable Supabase Auth (Phone provider) - optional
- [ ] Configure RLS policies for production
- [ ] Update MCP server with security tools
- [ ] Update Agent Backend with PINRequestAgent
- [ ] Update WhatsApp Bridge with session management

---

**Last Updated**: 2025-12-01
**Version**: 1.0.0
