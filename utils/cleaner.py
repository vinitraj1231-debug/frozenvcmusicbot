import asyncio
import os
import time
import logging

logger = logging.getLogger(__name__)

async def auto_cleaner():
    """
    Cleans up the downloads folder every hour, removing files older than 2 hours.
    """
    while True:
        try:
            now = time.time()
            if os.path.exists("downloads"):
                for f in os.listdir("downloads"):
                    file_path = os.path.join("downloads", f)
                    if os.stat(file_path).st_mtime < now - 2 * 3600:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            logger.info(f"Deleted old file: {file_path}")
        except Exception as e:
            logger.error(f"Error in auto_cleaner: {e}")

        await asyncio.sleep(3600)
