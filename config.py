# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print(f"📁 Looking for .env at: {ENV_PATH}")
print(f"📁 .env exists: {ENV_PATH.exists()}")

load_dotenv(dotenv_path=ENV_PATH, override=True)

GROQ_API_KEY        = os.getenv("GROQ_API_KEY")
GROQ_MODEL          = "llama-3.3-70b-versatile"
DB_PATH             = str(BASE_DIR / "nefersurvey.db")
EMBEDDING_MODEL     = "all-MiniLM-L6-v2"
TOP_K_RESULTS       = 5
MAX_FEEDBACK_LENGTH = 2000

print(f"🔑 Key loaded: {repr(GROQ_API_KEY)}")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

print(f"✅ Config loaded | Model: {GROQ_MODEL} | DB: {DB_PATH}")
