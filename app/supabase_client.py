from __future__ import annotations

from supabase import Client
from supabase import create_client

from app.config import Config


url: str = Config.SUPABASE_URL
key: str = Config.SUPABASE_KEY
supabase: Client = create_client(url, key)
