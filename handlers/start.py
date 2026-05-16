from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from core.clients import bot
from config.config import config
from utils.formatters import to_bold_unicode
from database.mongodb import db

@bot.on_message(filters.command("start") & filters.private)
async def start_private(_, message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    styled_name = to_bold_unicode(name)

    await db.add_chat(user_id, "private")

    caption = (
        f"👋 нєу {styled_name} 💠,\n\n"
        f">🎶 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 {to_bold_unicode(config.BOT_NAME)}! 🎵\n"
        ">🚀 𝗣𝗥𝗢𝗗𝗨𝗖𝗧𝗜𝗢𝗡-𝗚𝗥𝗔𝗗𝗘 𝗠𝗨𝗦𝗜𝗖 𝗦𝗬𝗦𝗧𝗘𝗠\n"
        ">🔊 𝗖𝗥𝗬𝗦𝗧𝗔𝗟-𝗖𝗟𝗘𝗔𝗥 𝗔𝗨𝗗𝗜𝗢 (𝗦𝗧𝗨𝗗𝗜𝗢 𝗤𝗨𝗔𝗟𝗜𝗧𝗬)\n"
        ">🎥 𝗩𝗜𝗗𝗘𝗢 𝗦𝗧𝗥𝗘𝗔𝗠𝗜𝗡𝗚 𝗦𝗨𝗣𝗣𝗢𝗥𝗧\n"
        ">🍪 𝗬𝗢𝗨𝗧𝗨𝗕𝗘 𝗖𝗢𝗢𝗞𝗜𝗘𝗦 𝗔𝗨𝗧𝗛𝗘𝗡𝗧𝗜𝗖𝗔𝗧𝗘𝗗\n"
        f"๏ ᴄʟɪᴄᴋ help ʙᴇʟᴏᴡ ғᴏʀ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ."
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{config.BOT_USERNAME}?startgroup=true"),
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{config.UPDATES_CHANNEL}")
        ],
        [
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{config.SUPPORT_GROUP}"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ])

    await message.reply_animation(
        animation="https://frozen-imageapi.lagendplayersyt.workers.dev/file/2e483e17-05cb-45e2-b166-1ea476ce9521.mp4",
        caption=caption,
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )

@bot.on_message(filters.command("start") & filters.group)
async def start_group(_, message):
    await db.add_chat(message.chat.id, "group")
    await message.reply_text(f"✨ {config.BOT_NAME} is alive!")
