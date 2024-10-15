from __future__ import annotations

import os

from dotenv import load_dotenv

# Load environment variables from .env file into os.environ
load_dotenv(verbose=True)


# Define a Config class to access the environment variables
class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_SERVER_URL = os.getenv("AI_SERVER_URL")
