from pathlib import Path
from os import getenv

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = getenv("BOT_TOKEN")
ADMIN_CHAT_ID = getenv("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

if ADMIN_CHAT_ID:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID)

DATABASE_PATH = BASE_DIR / "database" / "bot.db"

RESTS_THREAD_ID = 55192
DOSSIER_THREAD_ID = 55031
IDEA_THREAD_ID = 55029
CONTACT_THREAD_ID = 55000