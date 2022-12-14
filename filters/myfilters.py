from aiogram.filters import BaseFilter
from aiogram.types import Message
from create_bot import bot
import config


class IsAdmin(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        try:
            if msg.from_user.id == config.Owner_id:
                return True
            channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
            channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
            if msg.from_user.id in channel_admins_ids:
                return True
            else:
                await msg.answer("You are not admin.")
                return False
        except:
            return False


class IsOwner(BaseFilter):
    async def __call__(self, msg: Message) -> bool:
        try:
            if msg.from_user.id == config.Owner_id:
                return True
            else:
                await msg.answer("You are not Owner.")
                return False
        except:
            return False
