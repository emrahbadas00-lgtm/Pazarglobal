-- ============================================================
-- PAZARGLOBAL - SECURITY SCHEMA
-- Generated: 2025-12-01
-- Purpose: PIN authentication, session management, audit logs
-- ============================================================

-- ============================================================
-- TABLE: user_security
-- Kullanıcı güvenlik bilgileri (PIN, session, failed attempts)
-- ============================================================
-- NOTE: This table references profiles.id (which is same as auth.users.id)
-- Run profiles_schema.sql before this file
CREATE TABLE IF NOT EXISTS user_security (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    phone TEXT UNIQUE NOT NULL,  -- WhatsApp phone number (normalized)
    pin_hash TEXT NOT NULL,  -- bcrypt hashed PIN (4-6 digits)
    session_token TEXT,  -- Active session token (10 min TTL)
    session_expires_at TIMESTAMPTZ,  -- Session expiry time
    failed_attempts INTEGER DEFAULT 0,  -- Failed PIN attempts counter
    blocked_until TIMESTAMPTZ,  -- Temporary block until (3 failed attempts)
    last_login_at TIMESTAMPTZ,  -- Last successful login
    last_login_ip TEXT,  -- IP address (for audit)
    device_fingerprint TEXT,  -- Device hash (future: 2FA)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Indexes
CREATE INDEX idx_user_security_user_id ON user_security(user_id);
CREATE INDEX idx_user_security_phone ON user_security(phone);
CREATE INDEX idx_user_security_session_token ON user_security(session_token);
CREATE INDEX idx_user_security_session_expires_at ON user_security(session_expires_at);

-- RLS Policies
ALTER TABLE user_security ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own security data"
    ON user_security FOR SELECT
    USING (phone = current_setting('app.current_phone', true));

CREATE POLICY "Service role can manage security"
    ON user_security FOR ALL
    USING (true)  -- Service role only (MCP backend)
    WITH CHECK (true);

-- Auto-update updated_at
CREATE TRIGGER update_user_security_updated_at
    BEFORE UPDATE ON user_security
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TABLE: audit_logs
-- Kritik işlem logları (silme, güncelleme, yetkisiz erişim)
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    phone TEXT NOT NULL,  -- WhatsApp phone number
    action TEXT NOT NULL,  -- Action type: insert_listing, update_listing, delete_listing, verify_pin, etc.
    resource_type TEXT,  -- Resource type: listing, order, user
    resource_id UUID,  -- ID of affected resource
    source TEXT DEFAULT 'whatsapp',  -- Source: whatsapp, api, admin
    ip_address TEXT,  -- Client IP
    user_agent TEXT,  -- Client user agent (if available)
    request_data JSONB,  -- Request payload (sanitized)
    response_status TEXT,  -- success, failed, unauthorized, rate_limited
    error_message TEXT,  -- Error details (if failed)
    metadata JSONB DEFAULT '{}'::jsonb,  -- Additional context
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_phone ON audit_logs(phone);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_response_status ON audit_logs(response_status);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- RLS Policies
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own audit logs"
    ON audit_logs FOR SELECT
    USING (phone = current_setting('app.current_phone', true));

CREATE POLICY "Service role can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true);  -- Service role only


-- ============================================================
-- TABLE: rate_limits
-- Rate limiting - günlük işlem limitleri
-- ============================================================
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    phone TEXT NOT NULL,  -- WhatsApp phone number
    action TEXT NOT NULL,  -- Action type: insert_listing, delete_listing, update_listing
    count INTEGER DEFAULT 0,  -- Current count for today
    window_start TIMESTAMPTZ DEFAULT NOW(),  -- Rate limit window start
    window_end TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '1 day'),  -- Window end (24h)
    max_allowed INTEGER NOT NULL,  -- Maximum allowed per day
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, action, window_start)
);

-- Indexes
CREATE INDEX idx_rate_limits_user_id ON rate_limits(user_id);
CREATE INDEX idx_rate_limits_phone ON rate_limits(phone);
CREATE INDEX idx_rate_limits_action ON rate_limits(action);
CREATE INDEX idx_rate_limits_window_end ON rate_limits(window_end);

-- RLS Policies
ALTER TABLE rate_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own rate limits"
    ON rate_limits FOR SELECT
    USING (phone = current_setting('app.current_phone', true));

CREATE POLICY "Service role can manage rate limits"
    ON rate_limits FOR ALL
    USING (true)  -- Service role only
    WITH CHECK (true);

-- Auto-update updated_at
CREATE TRIGGER update_rate_limits_updated_at
    BEFORE UPDATE ON rate_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- HELPER FUNCTIONS FOR SECURITY
-- ============================================================

-- Function: Verify PIN (bcrypt comparison)
CREATE OR REPLACE FUNCTION verify_pin(
    p_phone TEXT,
    p_pin TEXT
) RETURNS TABLE(
    success BOOLEAN,
    session_token TEXT,
    message TEXT
) AS $$
DECLARE
    v_user_security RECORD;
    v_new_session_token TEXT;
BEGIN
    -- Get user security record
    SELECT * INTO v_user_security
    FROM user_security
    WHERE phone = p_phone;

    -- Check if user exists
    IF v_user_security IS NULL THEN
        RETURN QUERY SELECT false, NULL::TEXT, 'Kullanıcı bulunamadı';
        RETURN;
    END IF;

    -- Check if blocked
    IF v_user_security.blocked_until IS NOT NULL 
       AND v_user_security.blocked_until > NOW() THEN
        RETURN QUERY SELECT false, NULL::TEXT, 
            'Çok fazla hatalı deneme. ' || 
            EXTRACT(MINUTE FROM (v_user_security.blocked_until - NOW()))::TEXT || 
            ' dakika sonra tekrar deneyin.';
        RETURN;
    END IF;

    -- Verify PIN (using crypt extension)
    IF crypt(p_pin, v_user_security.pin_hash) = v_user_security.pin_hash THEN
        -- PIN correct - generate session token
        v_new_session_token := encode(gen_random_bytes(32), 'hex');
        
        -- Update user_security
        UPDATE user_security
        SET session_token = v_new_session_token,
            session_expires_at = NOW() + INTERVAL '10 minutes',
            failed_attempts = 0,
            blocked_until = NULL,
            last_login_at = NOW(),
            updated_at = NOW()
        WHERE phone = p_phone;
        
        RETURN QUERY SELECT true, v_new_session_token, 'Giriş başarılı';
    ELSE
        -- PIN incorrect - increment failed attempts
        UPDATE user_security
        SET failed_attempts = failed_attempts + 1,
            blocked_until = CASE 
                WHEN failed_attempts + 1 >= 3 THEN NOW() + INTERVAL '15 minutes'
                ELSE NULL
            END,
            updated_at = NOW()
        WHERE phone = p_phone;
        
        -- Check if blocked after this attempt
        IF v_user_security.failed_attempts + 1 >= 3 THEN
            RETURN QUERY SELECT false, NULL::TEXT, 'Çok fazla hatalı deneme. 15 dakika bloklandınız.';
        ELSE
            RETURN QUERY SELECT false, NULL::TEXT, 
                'Hatalı PIN. Kalan deneme: ' || (3 - v_user_security.failed_attempts - 1)::TEXT;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- Function: Check if session is valid
CREATE OR REPLACE FUNCTION is_session_valid(
    p_phone TEXT,
    p_session_token TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM user_security
    WHERE phone = p_phone
      AND session_token = p_session_token
      AND session_expires_at > NOW();
    
    RETURN v_count > 0;
END;
$$ LANGUAGE plpgsql;


-- Function: Check rate limit
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_phone TEXT,
    p_action TEXT,
    p_max_allowed INTEGER
) RETURNS TABLE(
    allowed BOOLEAN,
    current_count INTEGER,
    max_allowed INTEGER,
    resets_at TIMESTAMPTZ
) AS $$
DECLARE
    v_rate_limit RECORD;
BEGIN
    -- Get or create rate limit record
    INSERT INTO rate_limits (user_id, phone, action, count, max_allowed)
    VALUES (p_user_id, p_phone, p_action, 0, p_max_allowed)
    ON CONFLICT (user_id, action, window_start) 
    DO NOTHING;

    -- Get current rate limit
    SELECT * INTO v_rate_limit
    FROM rate_limits
    WHERE user_id = p_user_id
      AND action = p_action
      AND window_end > NOW()
    ORDER BY window_start DESC
    LIMIT 1;

    -- Check if window expired
    IF v_rate_limit IS NULL OR v_rate_limit.window_end <= NOW() THEN
        -- Create new window
        INSERT INTO rate_limits (user_id, phone, action, count, max_allowed)
        VALUES (p_user_id, p_phone, p_action, 0, p_max_allowed)
        RETURNING * INTO v_rate_limit;
    END IF;

    -- Check if limit exceeded
    IF v_rate_limit.count >= v_rate_limit.max_allowed THEN
        RETURN QUERY SELECT false, v_rate_limit.count, v_rate_limit.max_allowed, v_rate_limit.window_end;
    ELSE
        -- Increment counter
        UPDATE rate_limits
        SET count = count + 1, updated_at = NOW()
        WHERE id = v_rate_limit.id;
        
        RETURN QUERY SELECT true, v_rate_limit.count + 1, v_rate_limit.max_allowed, v_rate_limit.window_end;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- Function: Log audit event
CREATE OR REPLACE FUNCTION log_audit(
    p_user_id UUID,
    p_phone TEXT,
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id UUID,
    p_response_status TEXT,
    p_error_message TEXT DEFAULT NULL,
    p_request_data JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO audit_logs (
        user_id, phone, action, resource_type, resource_id,
        response_status, error_message, request_data
    )
    VALUES (
        p_user_id, p_phone, p_action, p_resource_type, p_resource_id,
        p_response_status, p_error_message, p_request_data
    )
    RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================
-- REQUIRED EXTENSIONS
-- ============================================================
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- For bcrypt and gen_random_bytes


-- ============================================================
-- DEFAULT RATE LIMITS (per action per day)
-- ============================================================
-- insert_listing: 20 per day
-- update_listing: 50 per day
-- delete_listing: 10 per day
-- search_listings: 200 per day
-- verify_pin: 10 per day


-- ============================================================
-- USAGE EXAMPLES
-- ============================================================

-- 1. Register user with PIN
-- INSERT INTO user_security (user_id, phone, pin_hash)
-- VALUES (
--     'uuid-here',
--     '+905551234567',
--     crypt('1234', gen_salt('bf'))  -- bcrypt hash of PIN
-- );

-- 2. Verify PIN
-- SELECT * FROM verify_pin('+905551234567', '1234');

-- 3. Check session validity
-- SELECT is_session_valid('+905551234567', 'session-token-here');

-- 4. Check rate limit
-- SELECT * FROM check_rate_limit(
--     'user-id-uuid',
--     '+905551234567',
--     'delete_listing',
--     10  -- max 10 deletes per day
-- );

-- 5. Log audit event
-- SELECT log_audit(
--     'user-id-uuid',
--     '+905551234567',
--     'delete_listing',
--     'listing',
--     'listing-id-uuid',
--     'success'
-- );


-- ============================================================
-- UPDATE get_user_by_phone function (from profiles_schema.sql)
-- ============================================================
-- Now we can properly check if user has PIN
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
        EXISTS(SELECT 1 FROM user_security WHERE user_security.phone = p_phone) as has_pin
    FROM profiles p
    WHERE p.phone = p_phone;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- VIEW: user_with_security (from profiles_schema.sql)
-- ============================================================
CREATE OR REPLACE VIEW user_with_security AS
SELECT 
    p.id,
    p.phone,
    p.email,
    p.full_name,
    p.display_name,
    p.user_role,
    p.is_verified,
    p.is_active,
    p.location,
    p.created_at,
    us.session_token IS NOT NULL as has_active_session,
    us.session_expires_at,
    us.failed_attempts,
    us.blocked_until,
    us.last_login_at
FROM profiles p
LEFT JOIN user_security us ON us.user_id = p.id;

-- RLS for view
ALTER VIEW user_with_security SET (security_invoker = true);
