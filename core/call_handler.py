from pytgcalls import PyTgCalls
from pytgcalls import filters as fl
from pytgcalls.types import ChatUpdate
from core.clients import assistant
import logging

logger = logging.getLogger(__name__)

call_py = PyTgCalls(assistant)

@call_py.on_update(fl.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
async def closed_handler(client, update):
    chat_id = update.chat_id
    from services.playback import stop_playback
    logger.info(f"Voice chat closed in {chat_id}")
    await stop_playback(chat_id)

@call_py.on_update(fl.chat_update(ChatUpdate.Status.KICKED | ChatUpdate.Status.LEFT_GROUP))
async def kicked_handler(client, update):
    chat_id = update.chat_id
    from services.playback import stop_playback
    logger.info(f"Assistant kicked or left from {chat_id}")
    await stop_playback(chat_id)

def init_call_handler():
    # This can be used to initialize other handlers if needed
    pass
