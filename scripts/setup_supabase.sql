-- VAV Customer Tracker — Supabase Table Setup
-- Bu SQL'i Supabase Dashboard > SQL Editor'de calistir

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    recorded_by TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),

    -- Demografik
    age_range TEXT,
    ethnicity TEXT,
    group_size TEXT,

    -- Davranissal
    looked_at TEXT[] DEFAULT '{}',
    tried_on BOOLEAN DEFAULT FALSE,
    tried_count INTEGER DEFAULT 0,

    -- Satin Alma
    purchased BOOLEAN DEFAULT FALSE,
    purchased_items TEXT[] DEFAULT '{}',
    price_segment TEXT,
    amount_range TEXT,
    exact_amount DECIMAL(10,2),
    price_reaction TEXT,

    -- Genel
    mood TEXT,
    time_spent_min INTEGER,
    notes TEXT,

    -- Meta
    input_mode TEXT DEFAULT 'quick',
    raw_message TEXT
);

-- Performans icin index'ler
CREATE INDEX IF NOT EXISTS idx_customers_recorded_at ON customers(recorded_at);
CREATE INDEX IF NOT EXISTS idx_customers_recorded_by ON customers(recorded_by);
CREATE INDEX IF NOT EXISTS idx_customers_ethnicity ON customers(ethnicity);
CREATE INDEX IF NOT EXISTS idx_customers_purchased ON customers(purchased);
