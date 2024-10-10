import logging
import os
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from aiogram.fsm.context import FSMContext
from database import add_subscriber, get_all_bot_db
from utils import BroadcastStates, is_admin
from handlers.messages import start_message, help_message, info_message
from config import BASE_DIR

LOGGER = logging.getLogger(__name__)



# Команда /start — регистрация пользователя
async def start_command(message: Message):
    user_id = message.from_user.id
    add_subscriber(user_id)
    is_admin_status = await is_admin(user_id)
    
    # Создаем инлайн-клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Помощь 🆘", callback_data="help")],
        [InlineKeyboardButton(text="Информация ℹ️", callback_data="info")],
    ])
    
    # Если пользователь администратор, добавляем кнопку для рассылки
    if is_admin_status:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Рассылка 📨", callback_data="send")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Получить логи 📝", callback_data="log")])

    # Вызов функции start_message(), чтобы получить текст
    await message.answer(start_message(), reply_markup=keyboard)
    
    LOGGER.info(f"Пользователь {user_id} добавлен в базу данных подписчиков.")

# Обработчик для отправки сообщения подписчикам
async def send_message_to_subscribers(message: Message, state: FSMContext):
    # Получаем сообщение, которое пользователь хотел разослать, из состояния FSM
    data = await state.get_data()
    message_to_send = data.get("message_to_send")  # Сообщение, которое нужно отправить

    subscribers = get_all_bot_db()

    if not subscribers:
        await message.answer("Нет подписчиков для отправки сообщений.")
        LOGGER.info("Попытка отправки сообщения, но подписчиков нет.")
        return

    await message.answer("Отправка сообщений подписчикам началась.")
    LOGGER.info(f"Отправляем сообщение подписчикам: {subscribers}")

    for user_id in subscribers:
        try:
            await message.bot.send_message(chat_id=user_id, text=message_to_send)
            LOGGER.info(f"Сообщение отправлено подписчику {user_id}")
        except Exception as e:
            LOGGER.error(f"Не удалось отправить сообщение подписчику {user_id}: {e}")

    await message.answer("Сообщение отправлено всем подписчикам.")

# Команда /send — запрос сообщения для рассылки
async def request_broadcast_message(message: Message, state: FSMContext):
    await message.answer("Введите сообщение для отправки всем подписчикам.")
    await state.set_state(BroadcastStates.waiting_for_message_users)
    LOGGER.info("Ожидание сообщения для рассылки подписчикам.")

# Обработчик получения сообщения и подтверждения рассылки
async def confirm_broadcast(message: Message, state: FSMContext):
    await state.update_data(message_to_send=message.text)

    # Кнопки подтверждения или отмены
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm_send")],
        [InlineKeyboardButton(text="Отменить ❌", callback_data="cancel_send")]
    ])

    await message.answer("Вы уверены, что хотите отправить это сообщение всем подписчикам?", reply_markup=keyboard)
    await state.set_state(BroadcastStates.waiting_for_confirmation)
    LOGGER.info(f"Сообщение для подтверждения рассылки: {message.text}")

# Callback обработка подтверждения или отмены
async def handle_callback(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data
    data = await state.get_data()
    message_to_send = data.get("message_to_send")

    if action == "confirm_send":
        await callback_query.message.answer("Рассылка подтверждена, отправляем сообщение.")
        await send_message_to_subscribers(callback_query.message, state)
        await state.clear()
    elif action == "cancel_send":
        await callback_query.message.answer("Рассылка отменена.")
        await state.clear()
    elif action == "help":
        await callback_query.message.answer(help_message())
    elif action == "info":
        await callback_query.message.answer(info_message())
    elif action == "send":
        await request_broadcast_message(callback_query.message, state)


    await callback_query.answer()
    LOGGER.info(f"Действие: {action}")

# Регистрация обработчиков
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command("start"))
    dp.message.register(request_broadcast_message, Command("send"))
    dp.message.register(confirm_broadcast, BroadcastStates.waiting_for_message_users)
    dp.callback_query.register(handle_callback)
