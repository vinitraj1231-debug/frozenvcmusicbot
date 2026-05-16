from motor.motor_asyncio import AsyncIOMotorClient
from config.config import config

class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_DB_URL)
        self.db = self.client["music_bot"]
        self.broadcast = self.db["broadcast"]
        self.state_backup = self.db["state_backup"]
        self.users = self.db["users"]
        self.chats = self.db["chats"]

    async def add_chat(self, chat_id, chat_type):
        await self.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"type": chat_type}},
            upsert=True
        )

    async def is_chat_added(self, chat_id):
        chat = await self.chats.find_one({"chat_id": chat_id})
        return bool(chat)

    async def get_all_chats(self):
        return await self.chats.find().to_list(length=None)

db = MongoDB()
