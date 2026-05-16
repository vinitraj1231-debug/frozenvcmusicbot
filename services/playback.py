import os
import time
import asyncio
import logging
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pytgcalls.types import MediaStream
from core.call_handler import call_py
from core.clients import bot
from services.queue import queue_manager
from services.downloader import downloader
from utils.formatters import get_progress_bar, format_time
from config.config import config
logger = logging.getLogger(__name__)

playback_tasks = {}

async def start_playback(chat_id: int, message: Message):
    queue = queue_manager.get_queue(chat_id)
    if not queue:
        return

    song_info = queue[0]
    title = song_info['title']
    url = song_info['url']
    requester = song_info['requester']
    thumbnail = song_info.get('thumbnail', config.DEFAULT_THUMBNAIL)
    duration = song_info.get('duration_seconds', 0)

    try:
        # Check if it's already a local file path
        if os.path.exists(url):
            file_path = url
        else:
            file_path = await downloader.download(url)

        song_info['file_path'] = file_path

        await call_py.play(
            chat_id,
            MediaStream(file_path, video_flags=MediaStream.Flags.IGNORE)
        )

        base_caption = (
            f"<b>🎧 Playing Now</b>\n\n"
            f"<b>❍ Title:</b> {title}\n"
            f"<b>❍ Requested by:</b> {requester}"
        )

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("II", callback_data="pause"),
                InlineKeyboardButton("▷", callback_data="resume"),
                InlineKeyboardButton("⏭", callback_data="skip"),
                InlineKeyboardButton("▢", callback_data="stop")
            ],
            [InlineKeyboardButton(get_progress_bar(0, duration), callback_data="progress")]
        ])

        try:
            playing_msg = await bot.send_photo(
                chat_id,
                photo=thumbnail,
                caption=base_caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}. Sending text message instead.")
            playing_msg = await bot.send_message(
                chat_id,
                text=base_caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )

        # Update progress task
        if chat_id in playback_tasks:
            playback_tasks[chat_id].cancel()

        playback_tasks[chat_id] = asyncio.create_task(
            update_progress(chat_id, playing_msg, duration, base_caption)
        )

    except Exception as e:
        await bot.send_message(chat_id, f"❌ Playback Error: {e}")
        queue_manager.pop_from_queue(chat_id)
        if not queue_manager.is_empty(chat_id):
            await start_playback(chat_id, message)

async def update_progress(chat_id: int, message: Message, duration: int, base_caption: str):
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("II", callback_data="pause"),
                InlineKeyboardButton("▷", callback_data="resume"),
                InlineKeyboardButton("⏭", callback_data="skip"),
                InlineKeyboardButton("▢", callback_data="stop")
            ],
            [InlineKeyboardButton(get_progress_bar(elapsed, duration), callback_data="progress")]
        ])

        try:
            await message.edit_caption(
                caption=base_caption,
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
        except:
            pass

        await asyncio.sleep(15)

async def stop_playback(chat_id: int):
    try:
        await call_py.leave_call(chat_id)
    except:
        pass
    queue_manager.clear_queue(chat_id)
    if chat_id in playback_tasks:
        playback_tasks[chat_id].cancel()
        del playback_tasks[chat_id]
