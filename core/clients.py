from pyrogram import Client
from config.config import config

bot = Client(
    "music_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="handlers")
)

assistant = Client(
    "assistant_account",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.ASSISTANT_SESSION
)
