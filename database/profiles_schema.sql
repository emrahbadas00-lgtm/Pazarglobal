-- ============================================================
-- PAZARGLOBAL - PROFILES SCHEMA
-- Generated: 2025-12-01
-- Purpose: User profiles linked to Supabase Auth
-- ============================================================

-- ============================================================
-- TABLE: profiles
-- Kullanıcı profil bilgileri (Supabase Auth ile entegre)
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    phone TEXT UNIQUE,  -- WhatsApp phone number (normalized: +905551234567)
    email TEXT UNIQUE,  -- Email address (from auth.users)
    full_name TEXT,
    display_name TEXT,  -- Public display name
    avatar_url TEXT,  -- Profile picture URL
    location TEXT,  -- City/region
    user_role TEXT DEFAULT 'buyer' CHECK (user_role IN ('buyer', 'seller', 'admin')),
    is_verified BOOLEAN DEFAULT false,  -- Email/phone verified
    is_active BOOLEAN DEFAULT true,  -- Account active status
    bio TEXT,  -- User bio/description
    preferences JSONB DEFAULT '{}'::jsonb,  -- User preferences (notifications, language, etc.)
    metadata JSONB DEFAULT '{}'::jsonb,  -- Additional metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_profiles_phone ON profiles(phone);
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_profiles_user_role ON profiles(user_role);
CREATE INDEX idx_profiles_location ON profiles(location);
CREATE INDEX idx_profiles_created_at ON profiles(created_at DESC);

-- RLS Policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public profiles are viewable by everyone"
    ON profiles FOR SELECT
    USING (true);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can delete own profile"
    ON profiles FOR DELETE
    USING (auth.uid() = id);

-- Auto-update updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- FUNCTION: Auto-create profile on user signup
-- ============================================================
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, email, phone, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.phone,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger: Auto-create profile when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();


-- ============================================================
-- NOTES
-- ============================================================
-- user_security and listings will reference profiles.id
-- These relationships are defined in security_schema.sql
-- Run security_schema.sql AFTER this file


-- ============================================================
-- UPDATE listings to reference profiles instead of users (OPTIONAL)
-- ============================================================
-- First, create a migration path for existing data
-- (This assumes you have existing users table data)

-- Option 1: Keep both relationships (backward compatible)
-- No changes needed, listings.user_id can still reference users.id

-- Option 2: Migrate to profiles only (future approach)
-- ALTER TABLE listings DROP CONSTRAINT IF EXISTS listings_user_id_fkey;
-- ALTER TABLE listings 
--     ADD CONSTRAINT listings_profile_id_fkey 
--     FOREIGN KEY (user_id) 
--     REFERENCES profiles(id) 
--     ON DELETE CASCADE;


-- ============================================================
-- HELPER FUNCTION: Get user by phone
-- ============================================================
-- NOTE: This function requires user_security table
-- Run security_schema.sql before using this function
CREATE OR REPLACE FUNCTION get_user_by_phone(p_phone TEXT)
RETURNS TABLE(
    user_id UUID,
    email TEXT,
    full_name TEXT,
    user_role TEXT,
    has_pin BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.email,
        p.full_name,
        p.user_role,
        false as has_pin  -- Will be updated in security_schema.sql
    FROM profiles p
    WHERE p.phone = p_phone;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- HELPER FUNCTION: Link WhatsApp phone to existing profile
-- ============================================================
CREATE OR REPLACE FUNCTION link_phone_to_profile(
    p_user_id UUID,
    p_phone TEXT
)
RETURNS TABLE(
    success BOOLEAN,
    message TEXT
) AS $$
BEGIN
    -- Check if phone already exists
    IF EXISTS(SELECT 1 FROM profiles WHERE phone = p_phone AND id != p_user_id) THEN
        RETURN QUERY SELECT false, 'Bu telefon numarası başka bir hesapla eşleştirilmiş';
        RETURN;
    END IF;

    -- Update profile with phone
    UPDATE profiles
    SET phone = p_phone, updated_at = NOW()
    WHERE id = p_user_id;

    IF FOUND THEN
        RETURN QUERY SELECT true, 'Telefon numarası başarıyla eşleştirildi';
    ELSE
        RETURN QUERY SELECT false, 'Kullanıcı bulunamadı';
    END IF;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- VIEW: user_with_security
-- Profiles + security info (for admin/debugging)
-- ============================================================
-- NOTE: This view requires user_security table
-- This will be recreated in security_schema.sql
-- Uncomment after running security_schema.sql:
--
-- CREATE OR REPLACE VIEW user_with_security AS
-- SELECT 
--     p.id,
--     p.phone,
--     p.email,
--     p.full_name,
--     p.display_name,
--     p.user_role,
--     p.is_verified,
--     p.is_active,
--     p.location,
--     p.created_at,
--     us.session_token IS NOT NULL as has_active_session,
--     us.session_expires_at,
--     us.failed_attempts,
--     us.blocked_until,
--     us.last_login_at
-- FROM profiles p
-- LEFT JOIN user_security us ON us.user_id = p.id;


-- ============================================================
-- MIGRATION GUIDE
-- ============================================================
-- 1. Run this schema in Supabase SQL Editor
-- 2. Existing users table data can be migrated:
--
--    INSERT INTO profiles (id, phone, email, full_name, location, created_at)
--    SELECT 
--        id,
--        phone,
--        email,
--        name as full_name,
--        location,
--        created_at
--    FROM users
--    ON CONFLICT (id) DO NOTHING;
--
-- 3. Keep users table for backward compatibility (optional)
-- 4. Update user_security.user_id to reference profiles.id
-- 5. Enable Supabase Auth (Email/Phone providers)


-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- 1. Get user by WhatsApp phone
-- SELECT * FROM get_user_by_phone('+905551234567');

-- 2. Link phone to existing profile (after email signup)
-- SELECT * FROM link_phone_to_profile(
--     'user-uuid-here',
--     '+905551234567'
-- );

-- 3. Check user security status
-- SELECT * FROM user_with_security WHERE phone = '+905551234567';

-- 4. Create profile manually (for testing)
-- INSERT INTO profiles (id, phone, full_name, user_role)
-- VALUES (
--     gen_random_uuid(),
--     '+905551234567',
--     'Test User',
--     'seller'
-- );
