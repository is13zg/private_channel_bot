import logging
from create_bot import bot,dp
from aiogram import  types
from aiogram.filters import Command
from aiogram.types import Message
import config
from init_data import db

Chek_email_before_join = True
Email_user_list = ["is-13mozg@inbox.ru", "2","borisov@ya.ru"]



logger = logging.getLogger(__name__)


@dp.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")


@dp.message(Command(commands=["вступить"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, <b>{message.from_user.full_name}!</b>")
    print(message.text)
    user_email = message.text.split()[1]
    print(user_email)
    if db.user_exists(user_email):
        print('user_allready in base')
        await message.answer(config.Url_to_join)
        return

    if Chek_email_before_join:
        if user_email not in Email_user_list:
            await message.answer(f"нельзя")
            return
    db.add_user_to_db(message.from_user.id, user_email)
    await message.answer(config.Url_to_join)
    return


@dp.message(Command(commands=["delete"]))
async def command_start_handler(message: Message) -> None:
    """
    This handler receive messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    print(message.text)
    user_email = message.text.split()[1]
    print(user_email)
    if db.user_exists(user_email):
        user_tlg_id = db.get_user_tlg_id(user_email)
        print(user_tlg_id)
        print(config.Chanel_Id)
        print(type(user_tlg_id))
        print(type(config.Chanel_Id))
        res = await bot.kick_chat_member(config.Chanel_Id, user_tlg_id)
        print(res)
        return
    else:
        await message.answer(f"User with email {user_email} not in base. Can't delete it from channel.")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward received message back to the sender

    By default, message handler will handle all message types (like text, photo, sticker and etc.)
    """
    try:
        # Send copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


def main() -> None:
    # Initialize Bot instance with an default parse mode which will be passed to all API calls
    # And the run events dispatching
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
