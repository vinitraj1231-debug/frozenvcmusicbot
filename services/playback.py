import os
import time
import asyncio
import logging
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality
from core.call_handler import call_py
from core.clients import bot
from services.queue import queue_manager
from services.downloader import downloader
from utils.formatters import get_progress_bar, format_time, html_escape
from config.config import config

logger = logging.getLogger(__name__)

playback_tasks = {}

async def start_playback(chat_id: int, message: Message = None):
    queue = queue_manager.get_queue(chat_id)
    if not queue:
        return

    song_info = queue[0]
    title = html_escape(song_info['title'])
    url = song_info['url']
    requester = html_escape(str(song_info['requester']))
    thumbnail = song_info.get('thumbnail') or config.DEFAULT_THUMBNAIL
    duration = song_info.get('duration_seconds', 0)
    is_video = song_info.get("is_video", False)

    try:
        if os.path.exists(url):
            file_path = url
        else:
            try:
                file_path = await downloader.download(url)
            except Exception as e:
                logger.error(f"Download failed for {url}: {e}")
                # Try one last time with a search if it was a direct URL that failed
                if url.startswith(("http://", "https://")):
                    logger.info(f"Retrying by searching for title: {song_info['title']}")
                    search_results = await downloader.search(song_info['title'])
                    if search_results:
                        file_path = await downloader.download(search_results[0]['url'])
                    else:
                        raise e
                else:
                    raise e

        song_info['file_path'] = file_path

        # Determine streaming parameters
        audio_params = AudioQuality.STUDIO
        video_params = VideoQuality.HD_720p if is_video else VideoQuality.SD_480p

        # Using ffmpeg for better compatibility
        await call_py.play(
            chat_id,
            MediaStream(
                file_path,
                audio_parameters=audio_params,
                video_parameters=video_params,
                video_flags=MediaStream.Flags.IGNORE if not is_video else MediaStream.Flags.REQUIRED,
                ffmpeg_parameters="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
            )
        )

        base_caption = (
            f"<b>{('🎥' if is_video else '🎧')} Playing Now</b>\n\n"
            f"<b>❍ Title:</b> {title}\n"
            f"<b>❍ Requested by:</b> {requester}\n"
            f"<b>❍ Type:</b> {'Video' if is_video else 'Audio'}"
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

        if chat_id in playback_tasks:
            playback_tasks[chat_id].cancel()

        playback_tasks[chat_id] = asyncio.create_task(
            update_progress(chat_id, playing_msg, duration, base_caption)
        )

        asyncio.create_task(preload_next(chat_id))

    except Exception as e:
        logger.exception(f"Playback error in {chat_id}: {e}")
        await bot.send_message(chat_id, f"❌ Playback Error: {html_escape(str(e))}")
        queue_manager.pop_from_queue(chat_id)
        if not queue_manager.is_empty(chat_id):
            await start_playback(chat_id)

async def update_progress(chat_id: int, message: Message, duration: int, base_caption: str):
    start_time = time.time()
    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > duration or duration == 0:
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
            except Exception:
                # Often occurs if message is deleted or not modified
                pass

            await asyncio.sleep(15)
    except asyncio.CancelledError:
        pass

async def preload_next(chat_id: int):
    queue = queue_manager.get_queue(chat_id)
    if len(queue) > 1:
        next_song = queue[1]
        url = next_song['url']
        if os.path.exists(url):
            return

        try:
            await downloader.download(url)
            logger.info(f"Preloaded: {next_song['title']}")
        except Exception as e:
            logger.error(f"Preload error: {e}")

async def stop_playback(chat_id: int):
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass
    queue_manager.clear_queue(chat_id)
    if chat_id in playback_tasks:
        playback_tasks[chat_id].cancel()
        del playback_tasks[chat_id]
