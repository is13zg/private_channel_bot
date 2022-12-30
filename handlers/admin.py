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


@router.message(Command(commands=["req"]), myfilters.IsOwner())
async def req_exmp(message: Message) -> None:
    gr_id = 2504942
    msg_ls = message.text.split()

    if len(msg_ls) > 1:
        gr_id = int(msg_ls[1])

    res = await conections.get_users(gr_id)
    await utils.make_response_data(message.chat.id, res, send_name="REQUEST_RESULT")


@router.message(Command(commands=["update_mails_gk"]), myfilters.IsAdmin())
async def mails_update(message: Message = config.Support_chat_id) -> None:
    try:
        user_emails = await conections.get_users(config.rm_club_member_list_gk_group_id)
        user_emails = list(map(lambda x: x.lower(), user_emails))
        # добавляем в полученные из геткурса нз емайлов
        user_emails.extend(init_data.Emails_NZ_list)
        # выбираем в какой чат будем отправлять инфу
        if message is None:
            chat_id = config.Support_chat_id
        else:
            chat_id = message.chat.id

        new_users_emails = set(user_emails).difference(init_data.Email_user_list)
        delete_users_emails = set(init_data.Email_user_list).difference(user_emails).difference(
            set(init_data.Emails_NZ_list))

        # отправляем НОВЫЕ почты
        # await utils.big_send(chat_id, new_users_emails, sep=" ", tag="GK_UPD NEW mails")
        await bot.send_message(chat_id, f"!!! GK_UPD NEW mails = {len(new_users_emails)} !!!")

        # отправляем почты которые будут удаляться из списка разрешенных
        # await utils.big_send(chat_id, delete_users_emails, sep=" ", tag="GK_UPD DEL mails from allowed list")
        await bot.send_message(chat_id, f"!!! GK_UPD DEL mails from allowed list = {len(delete_users_emails)} !!!")

        # отправляем почты которые будут удаляться из канала рум клуба
        delete_users_from_channel = set(init_data.db.get_emails()).intersection(delete_users_emails)
        # await utils.big_send(chat_id, delete_users_from_channel, sep="\n", tag="GK_UPD DEL users from channel ")
        await bot.send_message(chat_id, f"!!! GK_UPD DEL users from channel = {len(delete_users_from_channel)} !!!")

        await bot.send_message(chat_id,
                               f"to delete users, write token {init_data.Random_str} after /delete_gk command in private\n"
                               f"Example: <pre>/delete_gk {init_data.Random_str} </pre>")

        # сохраняем списки для удаления , что то в файл
        init_data.Emails_to_delete_from_channel.extend(delete_users_from_channel)
        init_data.Emails_to_delete_from_allow_list.extend(delete_users_emails)
        utils.new_emails_to_file(init_data.Emails_to_delete_from_allow_list, config.Emails_to_delete_file_name)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


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
            await message.answer(f"deleting user {user_email} ...")
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
        init_data.Email_user_list.extend(init_data.Emails_NZ_list)
        init_data.Emails_new_user_list = [][:]
        utils.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        utils.new_emails_to_file(init_data.Emails_to_delete_from_allow_list, config.Emails_to_delete_file_name)
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
        await bot.send_document(msg.chat.id, FSInputFile(config.Emails_NZ_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Emails_to_delete_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Messages_to_user_file_name))
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
        elif message.document.file_name == "NEW_LIST_OF_NZ_USER_EMAILS.txt":
            real_file_name = config.Emails_NZ_file_name
        elif message.document.file_name == "LIST_OF_DELETE_USERS.txt":
            real_file_name = config.Emails_to_delete_file_name
        elif message.document.file_name == "messages_to_user.json":
            real_file_name = config.Messages_to_user_file_name
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
            init_data.Email_user_list.extend(init_data.Emails_NZ_list)
        elif real_file_name == config.Emails_NZ_file_name:
            init_data.Email_user_list = list(set(init_data.Email_user_list).difference(init_data.Emails_NZ_list))
            init_data.Emails_NZ_list = utils.get_emails_from_file(config.Emails_NZ_file_name)
            utils.new_emails_to_file(init_data.Emails_NZ_list, config.Emails_NZ_file_name)
            init_data.Email_user_list.extend(init_data.Emails_NZ_list)
            
        elif real_file_name == config.Emails_to_delete_file_name:
            init_data.Emails_to_delete_from_allow_list = utils.get_emails_from_file(config.Emails_to_delete_file_name)
            utils.new_emails_to_file(init_data.Emails_to_delete_from_allow_list, config.Emails_to_delete_file_name)
        elif real_file_name == config.Messages_to_user_file_name:
            init_data.messages_to_user = utils.unpuck_json(config.Messages_to_user_file_name)
        else:
            # обновляем все файлы взаимодействия и ответов, независимо от того что загрузили
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
        await msg.answer(f"how_much_users_used_bot: {all_users}\n"
                         f"used_emails: {len(emails)}\n"
                         f"free_emails: {free_emails}\n"
                         f"del_frm_chnl: {len(init_data.Emails_to_delete_from_channel)}\n"
                         f"del_frm_allw_ls: {len(init_data.Emails_to_delete_from_allow_list)}")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["get_mails"]), myfilters.IsAdmin())
async def get_mails_handler(msg: Message):
    try:
        frmt_set = {"f", "msg", "auto"}
        email_list_tag_set = {"all", "reg", "free", "nz", "del_chnl", "del_mails_ls", "newgk", "del"}

        frmt = "auto"
        email_list_tag = "all"

        msg_ls = msg.text.split()

        if len(msg_ls) > 1:
            if msg_ls[1] in frmt_set:
                frmt = msg_ls[1]
            elif msg_ls[1] in email_list_tag_set:
                email_list_tag = msg_ls[1]
        if len(msg_ls) > 2:
            if msg_ls[2] in frmt_set:
                frmt = msg_ls[2]
            elif msg_ls[2] in email_list_tag_set:
                email_list_tag = msg_ls[2]

        print(f"command is {msg_ls[0]} {email_list_tag} {frmt}")

        send_ls_name = email_list_tag.upper() + "_MAILS"
        if email_list_tag == "all":
            await utils.make_response_data(msg.chat.id, init_data.Email_user_list, frmt=frmt, send_name=send_ls_name)
        elif email_list_tag == "reg":
            emails = set([x[0] for x in init_data.db.get_emails()])
            await utils.make_response_data(msg.chat.id, emails, frmt=frmt, send_name=send_ls_name)
        elif email_list_tag == "free":
            emails = set([x[0] for x in init_data.db.get_emails()])
            free_emails = set(init_data.Email_user_list).difference(emails)
            await utils.make_response_data(msg.chat.id, free_emails, frmt=frmt, send_name=send_ls_name)
        elif email_list_tag == "nz":
            await utils.make_response_data(msg.chat.id, init_data.Emails_NZ_list, frmt=frmt, send_name=send_ls_name)
        elif email_list_tag == "del_chnl":
            await utils.make_response_data(msg.chat.id, init_data.Emails_to_delete_from_channel, frmt=frmt,
                                           send_name=send_ls_name)
        elif email_list_tag == "del_mails_ls":
            await utils.make_response_data(msg.chat.id, init_data.Emails_to_delete_from_allow_list, frmt=frmt,
                                           send_name=send_ls_name)
        elif email_list_tag == "del":
            await utils.make_response_data(msg.chat.id, init_data.Emails_to_delete_from_allow_list, frmt=frmt,
                                           send_name="del_mails_ls".upper())
            await utils.make_response_data(msg.chat.id, init_data.Emails_to_delete_from_channel, frmt=frmt,
                                           send_name="del_chnl_mails".upper())
        elif email_list_tag == "newgk":
            await utils.make_response_data(msg.chat.id, init_data.Emails_new_user_list, frmt=frmt,
                                           send_name=send_ls_name)
        else:
            await msg.answer("No response mail list")

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
        txt = "Чтобы обновить сценарий взаидействия с пользователем отправьте  <u>interaction(M).json </u>\n" \
              "\n" \
              "Чтобы обновить ответы - <u>answers.json(M)</u>\n" \
              "\n" \
              "Чтобы обновить Емайлы пользователей - <u>NEW_LIST_OF_USER_EMAILS.txt</u>\n" \
              "\n" \
              "Чтобы обновить НЗ Емайлы  - <u>NEW_LIST_OF_NZ_USER_EMAILS.txt</u>\n" \
              "\n" \
              "Чтобы обновить файл для удаления  - <u>LIST_OF_DELETE_USERS.txt</u>\n" \
              "\n" \
              "Чтобы обновить файл с собщениями  - <u>messages_to_user.json</u>\n" \
              "\n" \
              "/reserv - бот выдаст текущие (main.db answers.json interaction.json emails.txt и пр.)\n" \
              "/stat - покажет кол-во пользователей взаимодействоваших с ботом\n" \
              "   вошедних по емайлу \n" \
              "   свободных емайлов \n" \
              "   для удаления из канала \n" \
              "   для удаления из списка разрешенных \n" \
              "/set_mode [norm, min] - отключение помощника\n" \
              "/get_mails [all*, reg, free, nz,  del_mails_ls, del_chnl, del, newgk] [f, msg, auto*] \n" \
              "    all* - по умолч, список всех емайлов кому доступно вступление \n" \
              "   reg - список емайлов по которым УЖЕ вступили \n" \
              "   free - список емайлов по которым еще НЕ вступили \n" \
              "   nz - список емайлов по которым вход доуступен всегда \n" \
              "   del_mails_ls - список емайлов из ГК для удаления из списка разрешенных \n" \
              "   del_chnl - список емайлов из ГК для удаления из канала  \n" \
              "   del - оба списка для удаления  \n" \
              "   newgk - обновленный список пользователей, которые получены из ГК \n" \
              "   [ f - список файлом, msg - список сообщением, auto* по умолч, зависит от длинны списка, ] \n" \
              "/update_mails_gk  обновляет список из ГК выдает списки del_mails_ls del_chnl newgk \n" \
              "/delete_gk TOKEN  удалит del_chnl из канала, из списка del_mails_ls, обновит список по newgk \n\n" \
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
              "/bd_mails_lower - приведет все емайлы в бд и спмсках нижнему регистру\n" \
              "/req - [group_id] запрос к ГК апи\n"
        await msg.answer(txt, parse_mode="HTML")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
