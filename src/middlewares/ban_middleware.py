from typing import Callable, Dict, Any, Union
from aiogram import BaseMiddleware, types

from src.data.repositories.user_repository import user_crud


class BanCheckMiddleware(BaseMiddleware):
    text = "❌ Вы забанены и не можете пользоваться ботом."

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Union[types.Message, types.CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        if not user_id:
            return await handler(event, data)

        user_ = await user_crud.get(tg_id=user_id)
        user_status = await user_crud.get_user_status(user_.increment)
        if not user_:
            return await handler(event, data)

        if user_status.is_banned:

            if isinstance(event, types.Message):
                await event.answer(self.text)
            else:
                await event.answer(self.text, show_alert=True)
            return
        
        return await handler(event, data)
