from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from src.utils.misc.bot_logging import bot_logger


router = Router(name="user_router")

@router.message(F.text == "/start")
async def start_command_handler(message: Message):
    bot_logger.info(f"Received /start command from user {message.from_user.id}")
    await message.answer("Welcome! How can I assist you today?")