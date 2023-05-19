from create_bot import bot
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router
from aiogram import F
import init_data
import config
import pathlib
import create_bot
import inspect
import shutil
import conections
from filters import myfilters
from utils import utils
import asyncio
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.message(Command(commands=["add_gk_gr"]), myfilters.IsOwner())
async def add_gk_gr(message: Message) -> None:
    msg_ls = message.text.split()
    if len(msg_ls) < 2:
        await message.answer("need gk group id")
        return
    else:
        if msg_ls[1].isdigit():
            config.all_gk_group_ids.append(int(msg_ls[1]))
            utils.new_emails_to_file(config.all_gk_group_ids, config.Gk_group_ids_file_name)
            await message.answer("new gk update group added ")
            return
        else:
            await message.answer("gk group id not int")
            return


@router.message(Command(commands=["del_gk_gr"]), myfilters.IsOwner())
async def del_gk_gr(message: Message) -> None:
    msg_ls = message.text.split()
    if len(msg_ls) < 2:
        await message.answer("need gk group id")
        return
    else:
        if msg_ls[1].isdigit():
            if int(msg_ls[1]) in config.all_gk_group_ids:
                config.all_gk_group_ids.remove(int(msg_ls[1]))
                utils.new_emails_to_file(config.all_gk_group_ids, config.Gk_group_ids_file_name)
                await message.answer("new gk update group added ")
            else:
                await message.answer("gk group id not in bot memory")

            return
        else:
            await message.answer("gk group id not int")
            return


@router.message(Command(commands=["testt"]), myfilters.IsOwner())
async def testt(message: Message) -> None:
    await message.answer(text=init_data.messages_to_user["bye"])


@router.message(Command(commands=["req"]), myfilters.IsOwner())
async def req_exmp(message: Message) -> None:
    gr_id = 2504942
    msg_ls = message.text.split()

    if len(msg_ls) > 1:
        gr_id = int(msg_ls[1])

    res = await conections.get_users(gr_id)
    await utils.make_response_data(message.chat.id, res, send_name="REQUEST_RESULT")


@router.message(Command(commands=["ismember"]), myfilters.IsOwner())
async def ismember(message: Message) -> None:
    msg_ls = message.text.split()
    if len(msg_ls) < 2:
        await message.answer("need id or mail")
        return
    else:
        if msg_ls[1].isdigit():
            user_id = int(msg_ls[1])
        elif init_data.db.user_exists(msg_ls[1]):
            user_id = int(init_data.db.get_user_tlg_id())
        else:
            await message.answer("need id or mail")
            return

        chat_member = await bot.get_chat_member(config.Chanel_Id, user_id)
        await message.answer(text=chat_member.status)


# удаляет пользователей из старого РУМ КЛУБА
@router.message(Command(commands=["delete_from_old_rum_club"]), myfilters.IsOwner())
async def delete_from_old_rum_club(message: Message) -> None:
    try:

        msg = message.text.split()
        if len(msg) == 1:
            await message.answer(f"Write token {init_data.Random_str} after /delete command\n"
                                 f"Example: <pre>/delete_from_old_rum_club {init_data.Random_str}</pre>")
            return
        elif msg[1] != init_data.Random_str:
            await message.answer(f"Write token {init_data.Random_str} after /delete command\n"
                                 f"Example: <pre>/delete_from_old_rum_club {init_data.Random_str}</pre>")
            return

        user_emails = set([x[0] for x in init_data.db.get_emails()])
        for user_email in user_emails:
            user_tlg_id = init_data.db.get_user_tlg_id(user_email)
            chat_member2 = await bot.get_chat_member(config.Rum_club_Chanel_Id,
                                                     user_tlg_id)
            if chat_member2.status == "member":
                user_kicked = await bot.kick_chat_member(config.Rum_club_Chanel_Id, user_tlg_id)
                if user_kicked:
                    await message.answer(f"User {user_email} delete from OLD RUM_ClUB channel .")
                else:
                    await message.answer(f"User {user_email} in OLD RUMCLUB, but Can't delete it from channel.")
            else:
                await message.answer(f"User {user_email} NOT member in OLD RUMCLUB")

        init_data.Random_str = utils.gen_rnd_str()
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["set_channel"]), myfilters.IsOwner())
async def command_set_channel_handler(message: Message) -> None:
    try:
        if len(message.text.split()) > 1:
            chnl = message.text.split()[1].lower()
        else:
            await message.answer("WHERE test|rum|rum2 ?")
            return

        if chnl == "test":
            config.Chanel_Id = config.Test_Chanel_Id
            await message.answer("Set channel id to test")

        if chnl == "rum":
            config.Chanel_Id = config.Rum_club_Chanel_Id
            await message.answer("Set channel id to RUM")

        if chnl == "rum2":
            config.Chanel_Id = config.Rum_club_20_Chanel_Id
            await message.answer("Set channel id to RUM 2.0")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["state"]), myfilters.IsOwner())
async def command_state(message: Message) -> None:
    try:
        t1 = ""
        if config.Chanel_Id == config.Test_Chanel_Id:
            t1 = "test"
        if config.Chanel_Id == config.Rum_club_Chanel_Id:
            t1 = "Rum"

        if config.Chanel_Id == config.Rum_club_20_Chanel_Id:
            t1 = "Rum2.0"

        txt = f"Channel_id={t1}\nCheck_emails={init_data.Chek_email_before_join}\n" \
              f"Min_mid={init_data.MIN_mode}\nAuto_upd_from_gk={init_data.update_from_gk}\n" \
              f"upd_time_from_gk = {init_data.update_from_gk_time}"
        await message.answer(txt)
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["bd_mails_lower"]), myfilters.IsOwner())
async def bd_mails_lower(message: Message) -> None:
    try:
        emails = set([x[0] for x in init_data.db.get_emails()])
        for mail in emails:
            user_tlg_id = init_data.db.get_user_tlg_id(mail)
            init_data.db.update_email(mail.lower(), user_tlg_id)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# /delete_gk USER_MAIL TOKEN  удалит одного пользователя
@router.message(Command(commands=["delete_user"]), myfilters.IsAdmin())
async def delete_user(message: Message) -> None:
    try:
        # проверка токена и емайла
        msg_ls = message.text.split()
        if len(msg_ls) < 3:
            await message.answer("Write token and user@mail.com")
            return
        if msg_ls[2] != init_data.Random_str:
            await message.answer(f"Write token {init_data.Random_str} after /delete_user command\n"
                                 f"Example: <pre>/delete_user USER@MAIL.COM {init_data.Random_str} </pre>")
            return

        user_email = msg_ls[1]

        try:
            # удаляем обычного полдьзователя по емайлу
            if init_data.db.user_exists(user_email):
                user_tlg_id = init_data.db.get_user_tlg_id(user_email)
                user_kicked = await bot.kick_chat_member(config.Chanel_Id, user_tlg_id)
                if user_kicked:
                    init_data.db.del_user_from_db(user_tlg_id)
                    await message.answer(f"User {user_email} delete from channel.")
                    await bot.send_message(chat_id=user_tlg_id, text=init_data.messages_to_user["bye"])
                else:
                    chat_member = await bot.get_chat_member(config.Chanel_Id, user_tlg_id)
                    await message.answer(
                        f"User {user_email} with id {user_tlg_id} in BD, but Can't delete it from channel. His status is {chat_member.status}")
            else:
                await message.answer(f"User {user_email} NOT in BD. Can't delete it from channel.")

            # проверяем пользователя с двойкой
            if init_data.db.user_exists(user_email + "2"):
                await message.answer(f" also delete user {user_email}2 ")
                user_tlg_id = init_data.db.get_user_tlg_id(user_email + "2")
                user_kicked = await bot.kick_chat_member(config.Chanel_Id, user_tlg_id)
                if user_kicked:
                    init_data.db.del_user_from_db(user_tlg_id)
                    await message.answer(f"User {user_email}2 delete from channel.")
                    await bot.send_message(chat_id=user_tlg_id, text=init_data.messages_to_user["bye"])
                else:
                    chat_member = await bot.get_chat_member(config.Chanel_Id, user_tlg_id)
                    await message.answer(
                        f"User {user_email}2 with id {user_tlg_id} in BD, but Can't delete it from channel. His status is {chat_member.status}")

        except Exception as e:
            await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
        init_data.Random_str = utils.gen_rnd_str()
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
