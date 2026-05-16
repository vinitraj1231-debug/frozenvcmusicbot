from pytgcalls import PyTgCalls
from core.clients import assistant
import logging

logger = logging.getLogger(__name__)

call_py = PyTgCalls(assistant)

@call_py.on_closed_voice_chat()
async def closed_handler(client, chat_id):
    from services.playback import stop_playback
    logger.info(f"Voice chat closed in {chat_id}")
    await stop_playback(chat_id)

@call_py.on_kicked()
async def kicked_handler(client, chat_id):
    from services.playback import stop_playback
    logger.info(f"Assistant kicked from {chat_id}")
    await stop_playback(chat_id)

def init_call_handler():
    pass
