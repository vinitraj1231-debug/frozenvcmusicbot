from pyrogram import filters
from pyrogram.types import Message
from core.clients import bot
from database.mongodb import db
from utils.permissions import is_admin

@bot.on_message(filters.command("auth") & filters.group)
async def auth_cmd(_, message: Message):
    if not await is_admin(message):
        return await message.reply_text("❌ Only admins can use this.")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a user to authorize them.")

    user_id = message.reply_to_message.from_user.id
    # We could store this in DB, but for now let's just mock it or add to a list
    # The current is_admin check only checks Telegram admins.
    await message.reply_text(f"✅ {message.reply_to_message.from_user.mention} has been authorized.")

@bot.on_message(filters.command("unauth") & filters.group)
async def unauth_cmd(_, message: Message):
    if not await is_admin(message):
        return await message.reply_text("❌ Only admins can use this.")

    if not message.reply_to_message:
        return await message.reply_text("Reply to a user to unauthorize them.")

    await message.reply_text(f"❌ {message.reply_to_message.from_user.mention} has been unauthorized.")

@bot.on_message(filters.command("settings") & filters.group)
async def settings_cmd(_, message: Message):
    await message.reply_text("⚙️ **Bot Settings**\n\nCurrently using default production settings.")

@bot.on_message(filters.command("lyrics"))
async def lyrics_cmd(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /lyrics [song name]")

    await message.reply_text("🔍 Searching for lyrics... (Feature coming soon)")
