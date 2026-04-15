"""Supabase database service for VAV Customer Tracker."""

import os
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def insert_customer(data: dict) -> dict:
    """Insert a new customer record."""
    client = get_client()
    result = client.table("customers").insert(data).execute()
    return result.data[0] if result.data else {}


def get_today_customers() -> list[dict]:
    """Get all customer records from today (Central Time)."""
    client = get_client()
    # Central Time is UTC-5 (CDT) or UTC-6 (CST)
    ct_now = datetime.now(timezone(timedelta(hours=-5)))
    today_start = ct_now.replace(hour=0, minute=0, second=0, microsecond=0)

    result = (
        client.table("customers")
        .select("*")
        .gte("recorded_at", today_start.isoformat())
        .order("recorded_at", desc=False)
        .execute()
    )
    return result.data or []


def get_week_customers() -> list[dict]:
    """Get all customer records from the last 7 days."""
    client = get_client()
    ct_now = datetime.now(timezone(timedelta(hours=-5)))
    week_start = (ct_now - timedelta(days=7)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    result = (
        client.table("customers")
        .select("*")
        .gte("recorded_at", week_start.isoformat())
        .order("recorded_at", desc=False)
        .execute()
    )
    return result.data or []


def get_last_n_customers(n: int = 5) -> list[dict]:
    """Get the last N customer records."""
    client = get_client()
    result = (
        client.table("customers")
        .select("*")
        .order("recorded_at", desc=True)
        .limit(n)
        .execute()
    )
    return result.data or []


def delete_last_customer(recorded_by: str) -> bool:
    """Delete the most recent customer record by a specific user."""
    client = get_client()
    # Get last record by this user
    result = (
        client.table("customers")
        .select("id")
        .eq("recorded_by", recorded_by)
        .order("recorded_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        return False

    record_id = result.data[0]["id"]
    client.table("customers").delete().eq("id", record_id).execute()
    return True


def get_all_customers_for_analysis() -> list[dict]:
    """Get all customer records for deep analysis."""
    client = get_client()
    result = (
        client.table("customers")
        .select("*")
        .order("recorded_at", desc=False)
        .execute()
    )
    return result.data or []


# --- SQL for creating the table in Supabase ---
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    recorded_by TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),

    -- Demografik
    age_range TEXT,
    ethnicity TEXT,
    group_size TEXT,

    -- Davranissal
    looked_at TEXT[],
    tried_on BOOLEAN DEFAULT FALSE,
    tried_count INTEGER DEFAULT 0,

    -- Satin Alma
    purchased BOOLEAN DEFAULT FALSE,
    purchased_items TEXT[],
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
"""
