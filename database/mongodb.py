from motor.motor_asyncio import AsyncIOMotorClient
from config.config import config
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        if not config.MONGO_DB_URL:
            logger.warning("MongoDB_url is not set in environment. Database features will be limited.")
            self.client = None
            self.db = None
            return

        try:
            self.client = AsyncIOMotorClient(config.MONGO_DB_URL)
            self.db = self.client["music_bot"]
            self.broadcast = self.db["broadcast"]
            self.state_backup = self.db["state_backup"]
            self.users = self.db["users"]
            self.chats = self.db["chats"]
            logger.info("Connected to MongoDB successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    async def add_chat(self, chat_id, chat_type):
        if self.db is None: return
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"type": chat_type}},
            upsert=True
        )

    async def is_chat_added(self, chat_id):
        if self.db is None: return False
        chat = await self.chats.find_one({"chat_id": chat_id})
        return bool(chat)

    async def get_all_chats(self):
        if self.db is None: return []
        return await self.chats.find().to_list(length=None)

db = MongoDB()
