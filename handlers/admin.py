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

router = Router()


@router.message(Command(commands=["request"]), myfilters.IsOwner())
async def command_addmails_handler(message: Message) -> None:
    gr_id = 2504942
    res = await conections.get_users(gr_id)
    await utils.big_send(message.chat.id, res, tag="REQST ANSW")


@router.message(Command(commands=["add_mails"]), myfilters.IsAdmin())
async def command_addmails_handler(message: Message) -> None:
    try:

        if len(message.text.split()) > 1:
            user_emails = message.text.split()[1:]
        else:
            await message.answer("You must write any mails")
            return

        for user_email in user_emails:
            init_data.Email_user_list.append(user_email.strip().lower())
        utils.add_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        await message.answer("Done!")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["update_mails_gk"]), myfilters.IsAdmin())
async def update_mails_gk(message: Message) -> None:
    await mails_update(message)


async def mails_update(message: Message = None) -> None:
    try:
        user_emails = await conections.get_users(config.rm_club_member_list_gk_group_id)
        user_emails = list(map(lambda x: x.lower(), user_emails))
        # добавляем в полученные из геткурса нз емайлов
        user_emails.extend(init_data.Emails_NZ_list)
        # выбираем в какой чат будем отправлять инфу
        if message == None:
            chat_id = config.Support_chat_id
        else:
            chat_id = message.chat.id

        new_users_emails = set(user_emails).difference(init_data.Email_user_list)
        delete_users_emails = set(init_data.Email_user_list).difference(user_emails)

        # отправляем НОВЫЕ почты
        # await utils.big_send(chat_id, new_users_emails, sep=" ", tag="GK_UPD NEW mails")
        await bot.send_message(chat_id, f"!!! GK_UPD NEW mails = {len(new_users_emails)} !!!")

        # отправляем почты которые будут удаляться из списка разрешенных
        # await utils.big_send(chat_id, delete_users_emails, sep=" ", tag="GK_UPD DEL mails from allowed list")
        await bot.send_message(chat_id, f"!!! GK_UPD DEL mails from allowed list = {len(delete_users_emails)} !!!")

        # отправляем почты которые будут удаляться из канала рум клуба
        current_users_in_channel = init_data.db.get_emails()
        delete_users_from_channel = set(current_users_in_channel).intersection(delete_users_emails)
        # await utils.big_send(chat_id, delete_users_from_channel, sep="\n", tag="GK_UPD DEL users from channel ")
        await bot.send_message(chat_id, f"!!! GK_UPD DEL users from channel = {len(delete_users_from_channel)} !!!")

        await bot.send_message(chat_id, f"Write token {init_data.Random_str} after /delete_gk command in private\n"
                                        f"Example: <pre>/delete_gk {init_data.Random_str} </pre>")

        init_data.Emails_to_delete_from_channel = delete_users_from_channel[:]
        init_data.Emails_to_delete_from_allow_list = delete_users_emails[:]
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["get_gkupd"]), myfilters.IsAdmin())
async def view_emails_after_gk_update(message: Message) -> None:
    # отправляем НОВЫЕ почты
    await utils.big_send(message.chat.id, init_data.Emails_new_user_list, sep=" ", tag="GK_UPD NEW mails")

    # отправляем почты которые будут удаляться из списка разрешенных
    await utils.big_send(message.chat.id, init_data.Emails_to_delete_from_allow_list, sep=" ",
                         tag="GK_UPD DEL mails from allowed list")

    # отправляем почты которые будут удаляться из канала рум клуба
    await utils.big_send(message.chat.id, init_data.Emails_to_delete_from_channel, sep="\n",
                         tag="GK_UPD DEL users from channel ")


# /delete_gk TOKEN  удалит лишних после обновления базы из GK
@router.message(Command(commands=["delete_gk"]), myfilters.IsAdmin())
async def command_start_handler(message: Message) -> None:
    try:

        user_emails = message.text.split()
        if len(user_emails) == 1:
            user_emails.append("")
        if user_emails[1] != init_data.Random_str:
            await message.answer(f"Write token {init_data.Random_str} after /delete_gk command\n"
                                 f"Example: <pre>/delete_gk {init_data.Random_str} </pre>")
            return

        if len(init_data.Emails_to_delete_from_channel) == 0:
            await message.answer("list to delete is empty")
            return

        user_emails = init_data.Emails_to_delete_from_channel
        for user_email in user_emails:
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
            await asyncio.sleep(1)

        init_data.Random_str = utils.gen_rnd_str()
        init_data.Emails_to_delete_from_allow_list = [][:]
        init_data.Emails_to_delete_from_channel = [][:]
        init_data.Email_user_list = init_data.Emails_new_user_list[:]
        init_data.Emails_new_user_list = [][:]
        utils.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["new_mails"]), myfilters.IsAdmin())
async def command_newmails_handler(message: Message) -> None:
    try:

        user_emails = message.text.split()
        if len(user_emails) == 1:
            user_emails.append("")
        if user_emails[1] != init_data.Random_str:
            await message.answer(f"WARNING! ALL OLD EMAILS WILL BE DELETED !!!\n"
                                 f"Write token {init_data.Random_str} after /newmails command\n"
                                 f"Example: <pre>/newmails {init_data.Random_str} ivanov92@mail.ru petrov@gmail.com </pre>")
            return

        if len(user_emails) == 2:
            await message.answer("You must write TOKEN and any mails")
            return

        user_emails = user_emails[2:]
        init_data.Email_user_list = []
        for user_email in user_emails:
            init_data.Email_user_list.append(user_email.strip().lower())
        utils.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        await message.answer("Done!")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# /get_mails - список загруженных емайлов
@router.message(Command(commands=["get_mails"]), myfilters.IsAdmin())
async def command_viewmails_handler(message: Message) -> None:
    try:

        await utils.big_send(message.chat.id, init_data.Email_user_list, tag="CRNT_MAILS")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["delete"]), myfilters.IsAdmin())
async def command_start_handler(message: Message) -> None:
    try:

        user_emails = message.text.split()
        if len(user_emails) == 1:
            user_emails.append("")
        if user_emails[1] != init_data.Random_str:
            await message.answer(f"Write token {init_data.Random_str} after /delete command\n"
                                 f"Example: <pre>/delete {init_data.Random_str} ivanov92@mail.ru</pre>")
            return

        if len(user_emails) == 2:
            await message.answer("You must write TOKEN and any mails")
            return

        user_emails = user_emails[2:]
        for user_email in user_emails:
            if init_data.db.user_exists(user_email):
                user_tlg_id = init_data.db.get_user_tlg_id(user_email)
                user_kicked = await bot.kick_chat_member(config.Chanel_Id, user_tlg_id)
                if user_kicked:
                    init_data.db.del_user_from_db(user_tlg_id)
                    await message.answer(f"User {user_email} delete from channel.")
                else:
                    chat_member = await bot.get_chat_member(config.Chanel_Id, user_tlg_id)
                    await message.answer(
                        f"User {user_email} with id {user_tlg_id} in BD, but Can't delete it from channel. His status is {chat_member.status}")
            else:
                await message.answer(f"User {user_email} NOT in BD. Can't delete it from channel.")
            init_data.Email_user_list.remove(user_email)
            await message.answer(f"User email {user_email} delete from user emails list\n.")

        utils.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        init_data.Random_str = utils.gen_rnd_str()
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# удаляет пользователей из старого РУМ КЛУБА
@router.message(Command(commands=["delete_from_old_rum_club"]), myfilters.IsOwner())
async def command_start_handler(message: Message) -> None:
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


@router.message(Command(commands=["reserv"]), myfilters.IsAdmin())
async def make_reserv_data(msg: Message):
    try:
        await bot.send_document(msg.chat.id, FSInputFile(config.BD_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Emails_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Interaction_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Answers_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Interaction_file_nameM))
        await bot.send_document(msg.chat.id, FSInputFile(config.Answers_file_nameM))
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(F.content_type.in_({'document'}), myfilters.IsAdmin())
async def get_files(message: Message):
    try:

        file_id = message.document.file_id

        print(message.document.file_name)
        real_file_name = ""
        if message.document.file_name in config.Interaction_file_name:
            real_file_name = config.Interaction_file_name
        elif message.document.file_name in config.Answers_file_name:
            real_file_name = config.Answers_file_name
        elif message.document.file_name in config.Interaction_file_nameM:
            real_file_name = config.Interaction_file_nameM
        elif message.document.file_name in config.Answers_file_nameM:
            real_file_name = config.Answers_file_nameM
        elif message.document.file_name == "NEW_LIST_OF_USER_EMAILS.txt":
            real_file_name = config.Emails_file_name
        else:
            return

        ls = real_file_name.split("/")
        ls[-1] = "OLD_" + ls[-1]
        old_file_path = "/".join(ls)

        if pathlib.Path(old_file_path).is_file():
            pathlib.Path(old_file_path).unlink()
        pathlib.Path(real_file_name).replace(old_file_path)

        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, message.document.file_name)

        # перенос скаченного файла в папку
        # pathlib.Path(message.document.file_name).replace(real_file_name)
        shutil.move(message.document.file_name, real_file_name)

        if real_file_name == config.Emails_file_name:
            init_data.Email_user_list = utils.get_emails_from_file(config.Emails_file_name)
            utils.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        else:
            # обновляем все файлы, независимо от того что загрузили
            init_data.interaction_json, init_data.answer_json = utils.update_interaction_answer(init_data.MIN_mode)
            init_data.menu_names, init_data.answer_names = utils.get_menu_names(init_data.interaction_json)

        await message.answer(f"File {message.document.file_name} was download")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["stat"]), myfilters.IsAdmin())
async def command_stat(msg: Message):
    try:
        all_users = init_data.db.count_reg_user()[0][0]
        emails = set([x[0] for x in init_data.db.get_emails()])
        free_emails = len(set(init_data.Email_user_list).difference(emails))
        tlg_users = init_data.db.count_tlg_user()[0][0]
        await msg.answer(f"how_much_users_used_bot: {all_users}\n"
                         f"used_emails: {len(emails)}\n"
                         f"user_joined: {tlg_users}\n"
                         f"free_emails: {free_emails}")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["get_free_mails"]), myfilters.IsAdmin())
async def command_stat(msg: Message):
    try:
        emails = set([x[0] for x in init_data.db.get_emails()])
        free_emails = set(init_data.Email_user_list).difference(emails)
        await utils.big_send(msg.chat.id, free_emails, tag="FREE_MAILS")
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["get_reg_mails"]), myfilters.IsAdmin())
async def command_stat(msg: Message):
    try:
        emails = set([x[0] for x in init_data.db.get_emails()])
        await utils.big_send(msg.chat.id, emails, tag="REG_MAILS")
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["check_emails"]), myfilters.IsOwner())
async def command_set_check_handler(message: Message) -> None:
    try:
        if len(message.text.split()) > 1:
            check = message.text.split()[1].lower()
        else:
            await message.answer("WHERE ON|OFF ?")
            return
        if check == "on":
            init_data.Chek_email_before_join = True
            await message.answer("Check_email = True")

        if check == "off":
            init_data.Chek_email_before_join = False
            await message.answer("Check_email = False")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["set_mode"]), myfilters.IsAdmin())
async def command_set_channel_handler(message: Message) -> None:
    try:
        if len(message.text.split()) > 1:
            mode = message.text.split()[1].lower()
        else:
            await message.answer("WHERE norm | min ?")
            return

        if mode == "min":
            init_data.MIN_mode = True
            await message.answer("Set min mode")

        if mode == "norm":
            init_data.MIN_mode = False
            await message.answer("Set norm mode")

        init_data.interaction_json, init_data.answer_json = utils.update_interaction_answer(init_data.MIN_mode)
        init_data.menu_names, init_data.answer_names = utils.get_menu_names(init_data.interaction_json)

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

        txt = f"Channel_id={t1}\nCheck_emails={init_data.Chek_email_before_join}"
        await message.answer(txt)
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["bd_mails_lower"]), myfilters.IsOwner())
async def command_state(message: Message) -> None:
    try:
        emails = set([x[0] for x in init_data.db.get_emails()])
        for mail in emails:
            user_tlg_id = init_data.db.get_user_tlg_id(mail)
            init_data.db.update_email(mail.lower(), user_tlg_id)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["helpaa"]), myfilters.IsAdmin())
async def command_helpaa(msg: Message):
    try:
        txt = "Для админов\n\n" \
              "Чтобы обновить сценарий взаидействия с пользователем отправьте  <u>interaction.json</u>\n" \
              "\n" \
              "Чтобы обновить ответы - <u>answers.json</u>\n" \
              "\n" \
              "Чтобы обновить Емайлы пользователей - <u>NEW_LIST_OF_USER_EMAILS.txt</u>\n" \
              "\n" \
              "Чтобы обновить НЗ Емайлы  - <u>NEW_LIST_OF_NZ_USER_EMAILS.txt</u>\n" \
              "\n" \
              "Чтобы обновить файл для удаления  - <u>LIST_OF_DELETE_USERS.txt</u>\n" \
              "\n" \
              "Чтобы обновить файл с собщениями  - <u>messages_to_user.json</u>\n" \
              "\n" \
              "/reserv - бот выдаст текущие (main.db answers.json interaction.json emails.txt)\n" \
              "/stat - покажет общее число пользователей взаимодействоваших с ботом\n" \
              "     число людей, которые получили по емайлу ссылку для входа в канала\n" \
              "    и число свободных емайлов, по которым никто не вступил\n" \
              "/get_mails [f, msg, auto]- список всех емайлов кому доступно вступление без НЗ емайлов\n" \
              "/get_reg_mails [f, msg, auto] список емайлов по которым УЖЕ вступили \n" \
              "/get_free_mails [f, msg, auto] список емайлов по которым еще НЕ вступили \n" \
              "/update_mails_gk  формирует обновленный список пользователей, и пользователей для удаления из канала и из списка разрешенных \n" \
              "/get_gkupd  выдаст обновленный список пользователей, и пользователей для удаления из канала и из списка разрешенных \n" \
              "/delete_gk TOKEN  удалит  пользоваелей из списка разрешенных и из канала по списку удаляемых\n" \
              "/set_mode [norm, min] - отключение помощника\n\n" \
              "/helpss - список специфических команд\n"
        await msg.answer(txt, parse_mode="HTML")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)

@router.message(Command(commands=["helpss"]), myfilters.IsAdmin())
async def command_helpaa(msg: Message):
    try:
        txt = "/set_channel [test, rum, rum2] - выбор канала, для теста или использования\n" \
              "/state - состояние переменных\n" \
              "/check_emails [on, off] - выбор проверять ли емайл для доступа к каналу\n" \
              "/delete_from_old_rum_club [token] удалить пользователей из старого канала РУМКЛУБА\n" \
              "/bd_mails_lower - приведет все емайлы в бд и спмсках нижнему регистру\n"
        await msg.answer(txt, parse_mode="HTML")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)