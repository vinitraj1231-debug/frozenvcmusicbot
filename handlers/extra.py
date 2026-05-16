from pyrogram import filters
from pyrogram.types import Message
from core.clients import bot
from services.queue import queue_manager
import random

@bot.on_message(filters.command("queue") & filters.group)
async def queue_cmd(_, message: Message):
    chat_id = message.chat.id
    queue = queue_manager.get_queue(chat_id)
    if not queue:
        return await message.reply_text("Queue is empty.")

    text = "**Current Queue:**\n\n"
    for i, song in enumerate(queue):
        text += f"{i+1}. {song['title']} (Requested by: {song['requester']})\n"
        if i == 10:
            text += f"... and {len(queue) - 11} more"
            break
    await message.reply_text(text)

@bot.on_message(filters.command("shuffle") & filters.group)
async def shuffle_cmd(_, message: Message):
    chat_id = message.chat.id
    queue = queue_manager.get_queue(chat_id)
    if len(queue) <= 2:
        return await message.reply_text("Not enough songs to shuffle.")

    # Keep the current song (index 0)
    to_shuffle = queue[1:]
    random.shuffle(to_shuffle)
    queue[1:] = to_shuffle
    await queue_manager.save_queues()
    await message.reply_text("🔀 Queue shuffled.")

@bot.on_message(filters.command("loop") & filters.group)
async def loop_cmd(_, message: Message):
    chat_id = message.chat.id
    current = queue_manager.get_loop(chat_id)
    new_state = not current
    queue_manager.set_loop(chat_id, new_state)
    await message.reply_text(f"🔂 Loop {'enabled' if new_state else 'disabled'}.")

@bot.on_message(filters.command("ping"))
async def ping_cmd(_, message: Message):
    import time
    start = time.time()
    m = await message.reply_text("Pinging...")
    end = time.time()
    await m.edit(f"🏓 Pong! {(end - start) * 1000:.2f}ms")

@bot.on_message(filters.command("stats"))
async def stats_cmd(_, message: Message):
    import psutil
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    await message.reply_text(
        f"📊 **System Stats:**\n\n"
        f"🖥 CPU: {cpu}%\n"
        f"💾 RAM: {ram}%\n"
        f"📁 Disk: {disk}%"
    )

@bot.on_message(filters.command("song"))
async def song_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /song [song name]")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔎 Searching...")

    from services.downloader import downloader
    try:
        results = await downloader.search(query)
        if not results:
            return await m.edit("❌ No results found.")

        info = results[0]
        title = info.get("title", "Unknown")
        url = info.get("url") or info.get("webpage_url") or f"https://www.youtube.com/watch?v={info['id']}"

        await m.edit(f"**Found Song:**\n\nTitle: {title}\nLink: {url}")
    except Exception as e:
        await m.edit(f"❌ Error: {e}")
