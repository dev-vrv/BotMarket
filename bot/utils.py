from aiogram import Bot
from aiogram.fsm.state import State, StatesGroup
import logging
from config import ADMIN_IDS

LOGGER = logging.getLogger(__name__)

# Class of states
class BroadcastStates(StatesGroup):
    waiting_for_message_users = State()
    waiting_for_confirmation = State()
    waiting_for_message_groups = State()

# Check if user is admin
async def is_admin(user_id: int):
    return user_id in ADMIN_IDS

# Get admin groups
async def get_admin_groups(bot: Bot):
    groups = []
    async for dialog in bot.get_dialogs():
        if dialog.chat.type in ['group', 'supergroup']:
            try:
                chat_admins = await bot.get_chat_administrators(dialog.chat.id)
                if any(admin.user.id == bot.id and admin.can_post_messages for admin in chat_admins):
                    groups.append(dialog.chat.id)
            except Exception as e:
                LOGGER.error(f"Ошибка при получении админов в чате {dialog.chat.id}: {e}")
    return groups
