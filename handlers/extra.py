import random
import time
from datetime import datetime
from pyrogram import filters
from core.clients import bot
from database.mongodb import db

@bot.on_message(filters.command("couple") & filters.group)
async def couple_handler(_, message):
    chat_id = message.chat.id
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Check if couple already chosen for today
    chat_doc = await db.chats.find_one({"chat_id": chat_id})
    if chat_doc and chat_doc.get("couple_date") == today:
        couple = chat_doc.get("couple")
        return await message.reply_text(f"❤️ Today's couple is: {couple}")

    # Pick two random members
    members = []
    async for member in bot.get_chat_members(chat_id):
        if not member.user.is_bot:
            members.append(member.user.first_name)

    if len(members) < 2:
        return await message.reply_text("❌ Not enough members to pick a couple!")

    couple = random.sample(members, 2)
    couple_str = f"{couple[0]} + {couple[1]}"

    await db.chats.update_one(
        {"chat_id": chat_id},
        {"$set": {"couple_date": today, "couple": couple_str}},
        upsert=True
    )

    await message.reply_text(f"❤️ Today's couple has been chosen!\n\n✨ {couple_str} ✨")
