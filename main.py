import asyncio
import logging
from pyrogram import idle
from core.clients import bot, assistant
from core.call_handler import call_py, init_call_handler
from pytgcalls import filters as fl
from services.queue import queue_manager
from services.playback import start_playback, stop_playback, playback_tasks
from utils.cleaner import auto_cleaner
from utils.patches import patch_pyrogram
from utils.cookie_helper import clean_cookies

# Apply monkeypatches
patch_pyrogram()

# Clean cookies on startup
clean_cookies("cookies.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@call_py.on_update(fl.stream_end())
async def stream_end_handler(_, update):
    chat_id = update.chat_id
    logger.info(f"Stream ended in chat: {chat_id}")

    if queue_manager.get_loop(chat_id):
        # If loop is on, we don't pop the current song
        logger.info(f"Looping current song in {chat_id}")
    else:
        queue_manager.pop_from_queue(chat_id)

    if not queue_manager.is_empty(chat_id):
        await start_playback(chat_id)
    else:
        logger.info(f"Queue empty in {chat_id}, leaving call.")
        try:
            await call_py.leave_call(chat_id)
        except Exception:
            pass

        if chat_id in playback_tasks:
            playback_tasks[chat_id].cancel()
            del playback_tasks[chat_id]

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

    logger.info("Frozen Music Bot is now running!")
    await idle()

    logger.info("Stopping Bot...")
    await bot.stop()
    await assistant.stop()
    await call_py.stop()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
