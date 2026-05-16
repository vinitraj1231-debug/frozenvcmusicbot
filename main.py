import asyncio
import logging
from pyrogram import idle
from core.clients import bot, assistant
from core.call_handler import call_py, init_call_handler
from pytgcalls.types import Update as TgUpdate
from pytgcalls import filters as fl
from services.queue import queue_manager
from services.playback import start_playback, stop_playback, playback_tasks
from utils.cleaner import auto_cleaner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@call_py.on_update(fl.stream_end())
async def stream_end_handler(_, update):
    chat_id = update.chat_id

    if queue_manager.get_loop(chat_id):
        # Re-add the same song to the end or just don't pop?
        # Standard loop usually means repeating the same song.
        # If we don't pop, start_playback will play the same song.
        pass
    else:
        # The song that just finished is at index 0
        queue_manager.pop_from_queue(chat_id)

    if not queue_manager.is_empty(chat_id):
        await start_playback(chat_id, None)
    else:
        # Avoid infinite loop if stop_playback calls leave_call
        try:
            if chat_id in playback_tasks:
                playback_tasks[chat_id].cancel()
                del playback_tasks[chat_id]
        except:
            pass

async def main():
    logger.info("Loading Queues...")
    await queue_manager.load_queues()

    logger.info("Starting Bot...")
    await bot.start()
    logger.info("Bot Started.")

    logger.info("Starting Assistant...")
    await assistant.start()
    logger.info("Assistant Started.")

    logger.info("Starting PyTgCalls...")
    await call_py.start()
    logger.info("PyTgCalls Started.")

    init_call_handler()
    asyncio.create_task(auto_cleaner())

    logger.info("Bot is running!")
    await idle()

    await bot.stop()
    await assistant.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
