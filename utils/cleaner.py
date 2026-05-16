import asyncio
import os
import time
import logging

logger = logging.getLogger(__name__)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

def clean_downloads():
    """
    Cleans up the downloads folder, removing files older than 2 hours.
    Also removes potentially corrupted small files.
    """
    try:
        now = time.time()
        if os.path.exists("downloads"):
            for f in os.listdir("downloads"):
                file_path = os.path.join("downloads", f)
                # Remove if older than 2 hours OR if it's too small (potential corruption)
                if os.stat(file_path).st_mtime < now - 2 * 3600 or os.path.getsize(file_path) < 1024:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error in clean_downloads: {e}")

async def auto_cleaner():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clean_downloads, "interval", hours=1)
    scheduler.start()
