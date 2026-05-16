from database.mongodb import db
import asyncio

class QueueManager:
    def __init__(self):
        self._queues = {}
        self._lock = asyncio.Lock()

    async def load_queues(self):
        async with self._lock:
            doc = await db.state_backup.find_one({"_id": "queues"})
            if doc:
                self._queues = {int(k): v for k, v in doc["data"].items()}

    async def save_queues(self):
        async with self._lock:
            data = {str(k): v for k, v in self._queues.items()}
            await db.state_backup.update_one(
                {"_id": "queues"},
                {"$set": {"data": data}},
                upsert=True
            )

    def get_queue(self, chat_id: int):
        return self._queues.get(chat_id, [])

    def add_to_queue(self, chat_id: int, song_info: dict):
        if chat_id not in self._queues:
            self._queues[chat_id] = []
        self._queues[chat_id].append(song_info)
        asyncio.create_task(self.save_queues())
        return len(self._queues[chat_id])

    def pop_from_queue(self, chat_id: int):
        if chat_id in self._queues and self._queues[chat_id]:
            song = self._queues[chat_id].pop(0)
            asyncio.create_task(self.save_queues())
            return song
        return None

    def clear_queue(self, chat_id: int):
        if chat_id in self._queues:
            self._queues[chat_id] = []
            asyncio.create_task(self.save_queues())

    def is_empty(self, chat_id: int):
        return not bool(self.get_queue(chat_id))

queue_manager = QueueManager()
