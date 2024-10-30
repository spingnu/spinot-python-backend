from __future__ import annotations

import os

from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv(verbose=True, override=True)


# Define a Config class to access the environment variables
class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
