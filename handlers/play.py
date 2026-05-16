import os
import logging
from pyrogram import filters
from pyrogram.types import Message
from core.clients import bot
from services.downloader import downloader
from services.queue import queue_manager
from services.playback import start_playback
from config.config import config
from utils.formatters import html_escape

logger = logging.getLogger(__name__)

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(_, message: Message):
    chat_id = message.chat.id
    is_video = message.command[0].lower() == "vplay"

    # Handle Telegram files (audio/video)
    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.video):
        m = await message.reply_text("📥 Processing Telegram file...")
        media = message.reply_to_message.audio or message.reply_to_message.video

        try:
            file_path = await message.reply_to_message.download(
                file_name=os.path.join("downloads", f"tg_{message.reply_to_message.id}.webm")
            )

            song_info = {
                "title": getattr(media, 'file_name', 'Telegram File') or 'Telegram File',
                "url": file_path,
                "file_path": file_path,
                "duration_seconds": media.duration or 0,
                "requester": message.from_user.first_name if message.from_user else "Unknown",
                "thumbnail": config.DEFAULT_THUMBNAIL,
                "is_video": is_video or bool(message.reply_to_message.video)
            }

            pos = queue_manager.add_to_queue(chat_id, song_info)
            if pos == 1:
                await start_playback(chat_id)
                await m.delete()
            else:
                await m.edit(f"<b>✅ Added to queue at position {pos-1}</b>")
        except Exception as e:
            logger.exception(f"Error processing Telegram file: {e}")
            await m.edit(f"❌ Error: {html_escape(str(e))}")
        return

    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("❌ Please provide a song name or URL.")

    m = await message.reply_text("🔎 Searching...")

    try:
        entries = await downloader.search(query)
        if not entries:
            return await m.edit("❌ No results found.")

        # Filter out None entries
        entries = [e for e in entries if e]

        if not entries:
             return await m.edit("❌ No playable results found.")

        if len(entries) > 1:
            await m.edit(f"📥 Processing playlist with {len(entries)} items...")

        first_pos = None
        added_count = 0

        for info in entries:
            # Basic validation
            if not info: continue

            title = info.get("title", "Unknown")
            # Get best available URL
            url = info.get("url") or info.get("webpage_url") or (f"https://www.youtube.com/watch?v={info['id']}" if 'id' in info else None)

            if not url:
                continue

            duration_seconds = info.get("duration", 0)
            thumbnail = info.get("thumbnail") or config.DEFAULT_THUMBNAIL

            song_info = {
                "title": title,
                "url": url,
                "duration_seconds": duration_seconds,
                "requester": message.from_user.first_name if message.from_user else "Unknown",
                "thumbnail": thumbnail,
                "is_video": is_video
            }

            pos = queue_manager.add_to_queue(chat_id, song_info)
            added_count += 1
            if first_pos is None:
                first_pos = pos

        if first_pos == 1:
            await m.edit(f"<b>📥 Starting playback...</b>")
            await start_playback(chat_id)
            await m.delete()
        else:
            if added_count > 1:
                await m.edit(f"<b>✅ Added {added_count} songs to queue.</b>")
            elif added_count == 1:
                title = html_escape(entries[0].get('title', 'Unknown'))
                await m.edit(f"<b>✅ Added to queue at position {first_pos-1}</b>\n<b>❍ Title:</b> {title}")
            else:
                await m.edit("<b>❌ No songs could be added to the queue.</b>")

    except Exception as e:
        logger.exception(f"Search error: {e}")
        await m.edit(f"❌ Error: {html_escape(str(e))}")
