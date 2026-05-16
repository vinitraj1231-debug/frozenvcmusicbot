import os
from pyrogram import filters
from pyrogram.types import Message
from core.clients import bot
from services.downloader import downloader
from services.queue import queue_manager
from services.playback import start_playback
from config.config import config
import isodate

@bot.on_message(filters.command(["play", "vplay"]) & filters.group)
async def play_command(_, message: Message):
    chat_id = message.chat.id
    is_video = message.command[0].lower() == "vplay"

    if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.video):
        m = await message.reply_text("📥 Processing Telegram file...")
        media = message.reply_to_message.audio or message.reply_to_message.video

        file_path = await message.reply_to_message.download(
            file_name=os.path.join("downloads", f"tg_{message.reply_to_message.id}.webm")
        )

        song_info = {
            "title": getattr(media, 'file_name', 'Telegram File'),
            "url": file_path, # Local path works as URL in start_playback downloader
            "file_path": file_path,
            "duration_seconds": media.duration or 0,
            "requester": message.from_user.first_name,
            "thumbnail": config.DEFAULT_THUMBNAIL,
            "is_video": is_video or bool(message.reply_to_message.video)
        }

        pos = queue_manager.add_to_queue(chat_id, song_info)
        if pos == 1:
            await start_playback(chat_id, message)
            await m.delete()
        else:
            await m.edit(f"✅ Added to queue at position {pos-1}")
        return

    query = " ".join(message.command[1:])

    if not query:
        return await message.reply_text("❌ Please provide a song name or URL.")

    m = await message.reply_text("🔎 Searching...")

    try:
        entries = await downloader.search(query)
        if not entries:
            return await m.edit("❌ No results found.")

        if len(entries) > 1:
            await m.edit(f"📥 Processing playlist with {len(entries)} songs...")

        first_pos = None
        for info in entries:
            title = info.get("title", "Unknown")
            url = info.get("url") or info.get("webpage_url") or f"https://www.youtube.com/watch?v={info['id']}"
            duration_seconds = info.get("duration", 0)
            thumbnail = info.get("thumbnail", config.DEFAULT_THUMBNAIL)

            song_info = {
                "title": title,
                "url": url,
                "duration_seconds": duration_seconds,
                "requester": message.from_user.first_name,
                "thumbnail": thumbnail,
                "is_video": is_video
            }

            pos = queue_manager.add_to_queue(chat_id, song_info)
            if first_pos is None:
                first_pos = pos

        if first_pos == 1:
            await m.edit(f"📥 Starting playback...")
            await start_playback(chat_id, message)
            await m.delete()
        else:
            if len(entries) > 1:
                await m.edit(f"✅ Added {len(entries)} songs to queue.")
            else:
                await m.edit(f"✅ Added to queue at position {first_pos-1}\n**Title:** {entries[0].get('title')}")

    except Exception as e:
        await m.edit(f"❌ Error: {e}")
