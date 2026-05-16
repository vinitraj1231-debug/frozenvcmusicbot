from pyrogram import filters
from core.clients import bot
from core.call_handler import call_py
from services.queue import queue_manager
from services.playback import start_playback, stop_playback
from utils.permissions import is_admin

@bot.on_message(filters.command(["pause", "resume", "skip", "stop"]) & filters.group)
async def control_commands(_, message):
    if not await is_admin(message):
        return await message.reply_text("❌ You must be an admin to use this.")

    command = message.command[0].lower()
    chat_id = message.chat.id

    if command == "pause":
        try:
            await call_py.pause(chat_id)
            await message.reply_text("⏸ Paused.")
        except:
            await message.reply_text("❌ Failed to pause.")

    elif command == "resume":
        try:
            await call_py.resume(chat_id)
            await message.reply_text("▶️ Resumed.")
        except:
            await message.reply_text("❌ Failed to resume.")

    elif command == "skip":
        if queue_manager.is_empty(chat_id):
            return await message.reply_text("❌ Queue is empty.")

        # We don't pop here. We let leave_call trigger stream_end which will pop and start next.
        # But if we want it to be immediate and avoid double pop, we can:
        # 1. Leave call
        # 2. Handler for stream_end will handle the rest.
        try:
            await call_py.leave_call(chat_id)
            await message.reply_text("⏭ Skipped.")
        except:
            # If not in call, maybe just pop and start?
            queue_manager.pop_from_queue(chat_id)
            if not queue_manager.is_empty(chat_id):
                await start_playback(chat_id, message)
                await message.reply_text("⏭ Skipped to next song.")
            else:
                await message.reply_text("⏭ Skipped. Queue is empty.")

    elif command == "stop":
        await stop_playback(chat_id)
        await message.reply_text("⏹ Stopped and queue cleared.")

@bot.on_message(filters.command("volume") & filters.group)
async def volume_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /volume [1-200]")

    vol = int(message.command[1])
    if not (1 <= vol <= 200):
        return await message.reply_text("Volume must be between 1 and 200.")

    try:
        await call_py.change_volume_participant(message.chat.id, vol)
        await message.reply_text(f"🔊 Volume set to {vol}%")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@bot.on_message(filters.command("speed") & filters.group)
async def speed_cmd(_, message: Message):
    await message.reply_text("Changing playback speed requires FFmpeg filter reconfiguration, not currently supported via direct command.")

@bot.on_message(filters.command("seek") & filters.group)
async def seek_cmd(_, message: Message):
    await message.reply_text("Seeking is not yet implemented.")
