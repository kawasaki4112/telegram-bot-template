from aiogram import BaseMiddleware
from aiogram.types import User

from src.data.repositories import user_crud


class ExistsUserMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        this_user: User = data.get("event_from_user")

        if not this_user.is_bot:
            get_user = await user_crud.get(tg_id=this_user.id)

            user_id = this_user.id
            user_login = this_user.username or ""

            if get_user is None:
                await user_crud.create(tg_id=user_id, username=user_login.lower())
            else:
                if get_user.username != user_login.lower():
                    await user_crud.update(
                        filters={"tg_id": get_user.tg_id},
                        updates={"username": user_login.lower()}
                    )

        return await handler(event, data)
