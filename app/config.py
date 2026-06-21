import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Optional defaults
DEFAULT_IMAP_EMAIL = os.getenv("DEFAULT_IMAP_EMAIL")
DEFAULT_IMAP_PASSWORD = os.getenv("DEFAULT_IMAP_PASSWORD")

def check_config():
    """
    Returns a dictionary of missing critical configurations, or empty dict if everything is fine.
    """
    missing = {}
    if not SUPABASE_URL:
        missing["SUPABASE_URL"] = "Supabase API Endpoint URL is required."
    if not SUPABASE_KEY:
        missing["SUPABASE_KEY"] = "Supabase Anon/Service Key is required."
    if not GEMINI_API_KEY:
        missing["GEMINI_API_KEY"] = "Google Gemini API Key is required."
    return missing
