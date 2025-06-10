from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.utils.misc.bot_logging import bot_logger


class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        try:
            return await handler(event, data)
        except Exception as e:
            bot_logger.exception(f"❌ Ошибка в хэндлере {handler.__name__}", exc_info=e)
            message = data.get("message")
            if message:
                await message.answer("Произошла ошибка, попробуйте чуть позже.")

