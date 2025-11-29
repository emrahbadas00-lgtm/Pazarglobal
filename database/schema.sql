-- PazarGlobal Database Schema
-- Supabase PostgreSQL

-- ========================================
-- TABLES
-- ========================================

-- Listings Table (İlanlar)
CREATE TABLE IF NOT EXISTS listings (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- User Reference (Foreign Key - will be linked to users table later)
    user_id UUID NOT NULL,
    
    -- Basic Info
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    
    -- Pricing
    price NUMERIC(10, 2),
    
    -- Inventory
    stock INTEGER DEFAULT 1,
    
    -- Location
    location TEXT,
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('draft', 'active', 'sold', 'inactive')),
    
    -- Condition
    condition TEXT DEFAULT 'used' CHECK (condition IN ('new', 'used', 'refurbished')),
    
    -- Media
    image_url TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Analytics
    view_count INTEGER DEFAULT 0,
    market_price_at_publish NUMERIC(10, 2),
    last_price_check_at TIMESTAMP WITH TIME ZONE
);

-- ========================================
-- INDEXES
-- ========================================

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_listings_user_id ON listings(user_id);
CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_category ON listings(category);
CREATE INDEX IF NOT EXISTS idx_listings_created_at ON listings(created_at DESC);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_listings_title_search ON listings USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_listings_description_search ON listings USING gin(to_tsvector('english', description));

-- ========================================
-- CONSTRAINTS & VALIDATION
-- ========================================

-- Ensure price is positive if provided
ALTER TABLE listings ADD CONSTRAINT check_price_positive 
    CHECK (price IS NULL OR price >= 0);

-- Ensure stock is non-negative
ALTER TABLE listings ADD CONSTRAINT check_stock_non_negative 
    CHECK (stock >= 0);

-- ========================================
-- TRIGGERS
-- ========================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_listings_updated_at 
    BEFORE UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read all active listings
CREATE POLICY "Public listings are viewable by everyone"
    ON listings FOR SELECT
    USING (status = 'active');

-- Policy: Users can insert their own listings
CREATE POLICY "Users can insert their own listings"
    ON listings FOR INSERT
    WITH CHECK (true);  -- Will be: auth.uid() = user_id when auth is implemented

-- Policy: Users can update their own listings
CREATE POLICY "Users can update their own listings"
    ON listings FOR UPDATE
    USING (true);  -- Will be: auth.uid() = user_id when auth is implemented

-- Policy: Users can delete their own listings
CREATE POLICY "Users can delete their own listings"
    ON listings FOR DELETE
    USING (true);  -- Will be: auth.uid() = user_id when auth is implemented

-- ========================================
-- SAMPLE DATA (for development)
-- ========================================

-- Insert sample listing
-- INSERT INTO listings (user_id, title, price, condition, category, description, location, status)
-- VALUES (
--     'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'::UUID,
--     'iPhone 15 Pro 128GB - MCP Test',
--     54999,
--     'new',
--     'elektronik',
--     'Sıfır kutusunda iPhone 15 Pro',
--     'İstanbul',
--     'active'
-- );

-- ========================================
-- FUTURE TABLES (Planned)
-- ========================================

-- Users Table (Phase 2 - WhatsApp Integration)
-- CREATE TABLE users (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     phone_number TEXT UNIQUE NOT NULL,
--     name TEXT,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
--     last_active_at TIMESTAMP WITH TIME ZONE
-- );

-- Messages Table (Phase 2 - WhatsApp Integration)
-- CREATE TABLE messages (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id UUID REFERENCES users(id),
--     message_text TEXT,
--     direction TEXT CHECK (direction IN ('inbound', 'outbound')),
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- Sessions Table (Phase 2 - Context Management)
-- CREATE TABLE sessions (
--     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
--     user_id UUID REFERENCES users(id),
--     context JSONB DEFAULT '{}',
--     expires_at TIMESTAMP WITH TIME ZONE,
--     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
-- );

-- ========================================
-- NOTES
-- ========================================

/*
CURRENT SCHEMA VERSION: 1.0
LAST UPDATED: 2025-11-28

COLUMN DESCRIPTIONS:
- id: Unique identifier (UUID)
- user_id: Owner of the listing (UUID, will link to users table)
- title: Product title/name
- description: Detailed product description
- category: Product category (elektronik, ev, moda, etc.)
- price: Price in TL
- stock: Available quantity
- location: City/region
- status: draft (not published), active (live), sold, inactive
- condition: new (sıfır), used (kullanılmış), refurbished (yenilenmiş)
- image_url: Product image URL
- metadata: Additional flexible JSON data
- created_at: Creation timestamp
- updated_at: Last modification timestamp
- view_count: Number of views (analytics)
- market_price_at_publish: Market price snapshot when published
- last_price_check_at: Last time price was validated

IMPORTANT:
1. user_id is currently NOT enforced as foreign key (no users table yet)
2. RLS policies are permissive (will be: auth.uid() = user_id) - tightened in Phase 2
3. Full-text search enabled on title and description
4. updated_at automatically updates on row modification
*/
