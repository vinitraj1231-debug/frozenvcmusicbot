from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatType, ChatMemberStatus
from typing import Union
from config.config import config

async def is_admin(obj: Union[Message, CallbackQuery]) -> bool:
    if isinstance(obj, CallbackQuery):
        message = obj.message
        user = obj.from_user
    elif isinstance(obj, Message):
        message = obj
        user = obj.from_user
    else:
        return False

    if not user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
        return True # In private chats, user is admin of the conversation

    trusted_ids = [777000, config.OWNER_ID]
    if user.id in trusted_ids:
        return True

    client = message._client
    chat_id = message.chat.id
    user_id = user.id

    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False
