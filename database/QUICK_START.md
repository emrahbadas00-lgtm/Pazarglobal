# 🚀 Quick Start - Supabase SQL Deployment

## ⚡ COPY-PASTE ORDER

### Step 1: Enable Extensions
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Step 2: Create Helper Function (if not exists)
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Step 3: Run profiles_schema.sql
- Copy ENTIRE `profiles_schema.sql` content
- Paste into Supabase SQL Editor
- Run

### Step 4: Run security_schema.sql
- Copy ENTIRE `security_schema.sql` content
- Paste into Supabase SQL Editor
- Run

---

## ✅ Verification

After running both files, test:

```sql
-- 1. Create test profile
INSERT INTO profiles (id, phone, full_name, user_role)
VALUES (
    gen_random_uuid(),
    '+905551234567',
    'Test User',
    'seller'
);

-- 2. Register PIN
INSERT INTO user_security (user_id, phone, pin_hash)
SELECT 
    id,
    phone,
    crypt('1234', gen_salt('bf'))
FROM profiles
WHERE phone = '+905551234567';

-- 3. Test PIN verification
SELECT * FROM verify_pin('+905551234567', '1234');

-- 4. Check user by phone
SELECT * FROM get_user_by_phone('+905551234567');

-- 5. View user with security info
SELECT * FROM user_with_security WHERE phone = '+905551234567';
```

---

## 🆘 Common Errors

### Error: "relation user_security does not exist"
**Solution:** Run `profiles_schema.sql` BEFORE `security_schema.sql`

### Error: "function crypt does not exist"
**Solution:** Enable pgcrypto extension:
```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Error: "function update_updated_at_column does not exist"
**Solution:** Run Step 2 above (create helper function)

---

## 📝 What Gets Created

**profiles_schema.sql:**
- `profiles` table
- `handle_new_user()` function + trigger
- `link_phone_to_profile()` function

**security_schema.sql:**
- `user_security` table
- `audit_logs` table  
- `rate_limits` table
- `verify_pin()` function
- `is_session_valid()` function
- `check_rate_limit()` function
- `log_audit()` function
- `get_user_by_phone()` function (updated)
- `user_with_security` view

---

## ⏭️ Next Steps

After successful deployment:
1. Update MCP server with security tools
2. Add PINRequestAgent to Agent Backend
3. Add session management to WhatsApp Bridge
4. Test full flow: WhatsApp → PIN → Session → Tools
