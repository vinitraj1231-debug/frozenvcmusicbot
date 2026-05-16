from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from core.clients import bot
from core.call_handler import call_py
from services.queue import queue_manager
from services.playback import start_playback, stop_playback
from utils.permissions import is_admin

@bot.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    data = query.data
    chat_id = query.message.chat.id

    if data == "help":
        return await query.message.edit_text("Help Menu: /play, /pause, /resume, /skip, /stop")

    if not await is_admin(query):
        return await query.answer("❌ You are not an admin!", show_alert=True)

    if data == "pause":
        try:
            await call_py.pause(chat_id)
            await query.answer("Paused")
        except:
            await query.answer("Error")

    elif data == "resume":
        try:
            await call_py.resume(chat_id)
            await query.answer("Resumed")
        except:
            await query.answer("Error")

    elif data == "skip":
        if queue_manager.is_empty(chat_id):
            return await query.answer("Queue is empty", show_alert=True)
        try:
            await call_py.leave_call(chat_id)
            await query.answer("Skipped")
        except:
            queue_manager.pop_from_queue(chat_id)
            if not queue_manager.is_empty(chat_id):
                await start_playback(chat_id, query.message)
            await query.answer("Skipped")

    elif data == "stop":
        await stop_playback(chat_id)
        await query.message.reply_text("⏹ Stopped.")
        await query.answer("Stopped")
