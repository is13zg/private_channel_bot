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

router = Router()


@router.message(Command(commands=["request"]))
async def command_addmails_handler(message: Message) -> None:
    gr_id = 2504942
    res = await conections.get_users(gr_id)
    await message.answer("===requestcomand answer==")
    reply = " ".join(res)
    while (len(reply) > 4096):
        x = reply[:4096]
        i = x.rfind('\n')
        await message.answer(x[:i])
        reply = reply[i:]
    if len(reply) > 0:
        await message.answer(reply)


@router.message(Command(commands=["addmails"]))
async def command_addmails_handler(message: Message) -> None:
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer("You can't delete user. You are not admin of channel/")
            return

        if len(message.text.split()) > 1:
            user_emails = message.text.split()[1:]
        else:
            await message.answer("You must write any mails")
            return

        for user_email in user_emails:
            init_data.Email_user_list.append(user_email.strip().lower())
        init_data.add_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        await message.answer("Done!")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["newmails"]))
async def command_newmails_handler(message: Message) -> None:
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer("You can't delete user. You are not admin of channel/")
            return
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
        init_data.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        await message.answer("Done!")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["viewmails"]))
async def command_viewmails_handler(message: Message) -> None:
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer("You are not admin of channel")
            return

        reply = "\n".join(init_data.Email_user_list)
        while (len(reply) > 4096):
            x = reply[:4096]
            i = x.rfind('\n')
            await message.answer(x[:i])
            reply = reply[i:]
        if len(reply) > 0:
            await message.answer(reply)
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["delete"]))
async def command_start_handler(message: Message) -> None:
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer("You can't delete user. You are not admin of channel/")
            return

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

        init_data.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
        init_data.Random_str = init_data.gen_rnd_str()
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


# удаляет пользователей из старого РУМ КЛУБА
@router.message(Command(commands=["delete_from_old_rum_club"]))
async def command_start_handler(message: Message) -> None:
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer("You can't delete user. You are not admin of channel/")
            return

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

        init_data.Random_str = init_data.gen_rnd_str()
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["reserv"]))
async def make_reserv_data(msg: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if msg.from_user.id not in channel_admins_ids:
            await msg.answer(" You are not admin of channel.")
            return
        await bot.send_document(msg.chat.id, FSInputFile(config.BD_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Emails_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Interaction_file_name))
        await bot.send_document(msg.chat.id, FSInputFile(config.Answers_file_name))
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(F.content_type.in_({'document'}))
async def get_files(message: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if message.from_user.id not in channel_admins_ids:
            await message.answer(" You are not admin of channel.")
            return

        file_id = message.document.file_id

        real_file_name = ""
        if message.document.file_name in config.Interaction_file_name:
            real_file_name = config.Interaction_file_name
        elif message.document.file_name in config.Answers_file_name:
            real_file_name = config.Answers_file_name
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

        if real_file_name == config.Interaction_file_name:
            init_data.interaction_json = init_data.unpuck_json(config.Interaction_file_name)
            init_data.menu_names, init_data.answer_names = init_data.get_menu_names()

        if real_file_name == config.Answers_file_name:
            init_data.answer_json = init_data.unpuck_json(config.Answers_file_name)

        if real_file_name == config.Emails_file_name:
            init_data.Email_user_list = init_data.get_emails_from_file(config.Emails_file_name)
            init_data.new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)

        await message.answer(f"File {message.document.file_name} was download")
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["stat"]))
async def command_stat(msg: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if msg.from_user.id not in channel_admins_ids:
            await msg.answer(" You are not admin of channel.")
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


@router.message(Command(commands=["get_free_mails"]))
async def command_stat(msg: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if msg.from_user.id not in channel_admins_ids:
            await msg.answer(" You are not admin of channel.")
            return
        emails = set([x[0] for x in init_data.db.get_emails()])
        free_emails = set(init_data.Email_user_list).difference(emails)
        reply = "\n".join(free_emails)
        while (len(reply) > 4096):
            x = reply[:4096]
            i = x.rfind('\n')
            await msg.answer(x[:i])
            reply = reply[i:]
        if len(reply) > 0:
            await msg.answer(reply)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["get_reg_mails"]))
async def command_stat(msg: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if msg.from_user.id not in channel_admins_ids:
            await msg.answer(" You are not admin of channel.")
            return
        emails = set([x[0] for x in init_data.db.get_emails()])
        reply = "\n".join(emails)
        while (len(reply) > 4096):
            x = reply[:4096]
            i = x.rfind('\n')
            await msg.answer(x[:i])
            reply = reply[i:]
        if len(reply) > 0:
            await msg.answer(reply)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["check_emails"]))
async def command_set_check_handler(message: Message) -> None:
    try:
        if message.from_user.id != config.Owner_id:
            await message.answer("You are not Iskander")
            return

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


@router.message(Command(commands=["set_channel"]))
async def command_set_channel_handler(message: Message) -> None:
    try:
        if message.from_user.id != config.Owner_id:
            await message.answer("You are not Iskander")
            return
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


@router.message(Command(commands=["state"]))
async def command_state(message: Message) -> None:
    try:
        if message.from_user.id != config.Owner_id:
            await message.answer("You are not Iskander")
            return
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


@router.message(Command(commands=["bd_mails_lower"]))
async def command_state(message: Message) -> None:
    try:
        if message.from_user.id != config.Owner_id:
            await message.answer("You are not Iskander")
            return
        emails = set([x[0] for x in init_data.db.get_emails()])
        for mail in emails:
            user_tlg_id = init_data.db.get_user_tlg_id(mail)
            init_data.db.update_email(mail.lower(), user_tlg_id)
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)


@router.message(Command(commands=["helpaa"]))
async def command_helpaa(msg: Message):
    try:
        channel_admins = await bot.get_chat_administrators(config.Chanel_Id)
        channel_admins_ids = set(map(lambda x: x.user.id, channel_admins))
        if msg.from_user.id not in channel_admins_ids:
            await msg.answer(" You are not admin of channel/")
            return
        txt = "Для админов\n" \
              "Чтобы обновить сценарий взаидействия с пользователем отправьте файл interaction.json\n" \
              "\n" \
              "Чтобы обновить ответы отправьте файл answers.json\n" \
              "\n" \
              "Чтобы обновить Емайлы пользователей отправьте файл NEW_LIST_OF_USER_EMAILS.txt\n" \
              "\n" \
              "/reserv - бот выдаст текущие (main.db answers.json interaction.json emails.txt)\n" \
              "/delete [token] [useremail1] [useremail2] ... \n" \
              "    удаляет пользователей с емайлами useremail1 и useremail2 из канала и из базы,\n" \
              "    можно подставить любое кол-во емайлов от 1 до 100\n" \
              "    чтобы получить токен введите /delete\n" \
              "/viewmails - список емайлов, по которым можно попасть в рум клуб\n" \
              "/newmails [token] [useremail1] [useremail2] ...	\n" \
              "    удаляет ВСЕ существующие емайлы по которым выдается доступ\n" \
              "    и создает новый список с емайлами useremail1 и useremail2 .\n" \
              "    можно подставить любое кол-во емайлов от 1 до 100\n" \
              "    чтобы получить токен введите /newmails\n" \
              "/addmails [useremail1] [useremail2] ... 	\n" \
              "добавляет в список с емайлами, емайлы useremail1 и useremail2\n" \
              "можно подставить любое кол-во емайлов от 1 до 100\n" \
              "т.е. список дополнится а не обновится\n" \
              "/stat - покажет общее число пользователей взаимодействоваших с ботом\n" \
              "число людей, которые получили по емайлу ссылку для входа в канала\n" \
              "и число свободных емайлов, по которым никто не вступил\n\n" \
              "/delete_from_old_rum_club [token] удалить пользователей из старого канала РУМКЛУБА\n" \
              "/get_reg_mails список емайлов по которым вступили \n" \
              "/get_free_mails список емайлов по которым еще НЕ вступили \n" \
              "Для Искандера\n" \
              "/set_channel [test, rum, rum2] - выбор канала, для теста или использования\n" \
              "/state - состояние переменных\n" \
              "/check_emails [on, off] - выбор проверять ли емайл для доступа к каналу\n" \
              "/bd_mails_lower - приведет все емайлы к нижнему регистру\n"
        await msg.answer(txt)
        return
    except Exception as e:
        await create_bot.send_error_message(__name__, inspect.currentframe().f_code.co_name, e)
