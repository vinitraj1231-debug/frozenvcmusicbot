import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "")
    OWNER_ID = int(os.environ.get("OWNER_ID", "5268762773"))
    MONGO_DB_URL = os.environ.get("MongoDB_url", "")

    BOT_NAME = os.environ.get("BOT_NAME", "Frozen Music")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "vcmusiclubot")
    BOT_LINK = f"https://t.me/{BOT_USERNAME}"

    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "Frozensupport1")
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "vibeshiftbots")

    DEFAULT_THUMBNAIL = "https://i.ibb.co/TBTk7BvK/4b6e433b651f.jpg"

    QUEUE_LIMIT = 20
    MAX_DURATION_SECONDS = 900  # 15 minutes

    YDL_OPTS = {
        "format": "251/250/249/bestaudio",
        "quiet": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "noplaylist": True,
        "extract_flat": False,
        "default_search": "ytsearch",
        "source_address": "0.0.0.0",
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        }
    }

config = Config()
