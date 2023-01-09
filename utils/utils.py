import os

from create_bot import bot
import create_bot
import json
import inspect
import random
import string
import config
import asyncio
from aiogram.types import FSInputFile
import init_data


async def spam(users: list, msg: str):
    try:
        for user in users:
            res = await bot.send_message(chat_id=user, text=msg)
            await bot.send_message(chat_id=config.Support_chat_id, text=str(res))
            await asyncio.sleep(0.13)
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


async def big_send(chat_id, content, sep="\n", tag=""):
    await bot.send_message(chat_id, f"!!! {tag} = len {len(content)} !!!", disable_notification=True)
    reply = sep.join(content)
    if len(reply) > 4096:
        await bot.send_message(chat_id, f"== {tag} BEGIN ==", disable_notification=True)

        while len(reply) > 4096:
            x = reply[:4096]
            i = x.rfind(sep)
            await bot.send_message(chat_id, x[:i], disable_notification=True)
            await asyncio.sleep(0.3)
            reply = reply[i:]
        if len(reply) > 0:
            await bot.send_message(chat_id, reply, disable_notification=True)

        await bot.send_message(chat_id, f"== {tag} END ==", disable_notification=True)
    else:
        await bot.send_message(chat_id, reply)


def unpuck_json(file_name: str) -> dict:
    try:
        with open(file_name, "r", encoding='utf-8') as jsonr:
            return json.load(jsonr)
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def get_emails_from_file(file_name: str) -> list:
    try:
        res = []
        with open(file_name, "r", encoding='utf-8') as txtf:
            # считываем все строки
            lines = txtf.readlines()
            # итерация по строкам
            for line in lines:
                res.append(line.strip().lower())
        return res
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def add_emails_to_file(mails: list, file_name: str):
    try:
        with open(file_name, "a", encoding='utf-8') as txtf:
            # итерация по строкам
            txtf.write("\n".join(list(map(lambda x: x.lower(), mails))))
            return
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def new_emails_to_file(mails: list, file_name: str):
    try:
        with open(file_name, "w", encoding='utf-8') as txtf:
            # итерация по строкам
            txtf.write("\n".join(list(map(lambda x: x.lower(), mails))))
            return
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def get_menu_names(interaction_json: json):
    try:
        menus = dict()
        answers = dict()
        for k in interaction_json['menus']:
            for key, value in k.items():
                for item in value:
                    if item['type'] == 'menu':
                        menus[item['menu_name']] = item['text']
                    if item['type'] == 'text':
                        answers[item['answer']] = item['text']
        menus["menu0"] = "Начальное меню"
        return menus, answers
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def gen_rnd_str(n=5):
    try:
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)


def update_interaction_answer(mode):
    if mode:
        return unpuck_json(config.Interaction_file_nameM), unpuck_json(config.Answers_file_nameM)
    else:
        return unpuck_json(config.Interaction_file_name), unpuck_json(config.Answers_file_name)


def update_mails_list():
    # сохраняем в файл
    new_emails_to_file(init_data.Email_user_list, config.Emails_file_name)
    # добавляем в текущий список НЗ емайлы
    init_data.Email_user_list.extend(init_data.Emails_NZ_list)
    # смотрим кого надо удалить из канала
    init_data.Emails_to_delete_from_channel = list(
        set([x[0] for x in init_data.db.get_emails()]).difference(init_data.Email_user_list))


def clear_delete_list_and_file():
    init_data.Emails_to_delete_from_channel = [][:]
    init_data.Emails_to_delete_from_allow_list = [][:]
    new_emails_to_file(init_data.Emails_to_delete_from_allow_list, config.Emails_to_delete_file_name)


async def make_response_data(chat_id: int, data: list, frmt: str = "auto", send_name: str = "current_list") -> None:
    try:
        if len(data) == 0:
            await bot.send_message(chat_id, text=f"{send_name} is empty !!!", disable_notification=True)
            return
        if (frmt == 'f') or (frmt == "auto" and len(data) >= 100):
            with open(send_name + ".txt", "w", encoding='utf-8') as txtf:
                txtf.write("\n".join(list(map(lambda x: x.lower(), data))))
            await bot.send_document(chat_id, FSInputFile(send_name + ".txt"), disable_notification=True)
            os.remove(send_name + ".txt")

        elif (frmt == "msg") or (frmt == "auto" and len(data) < 100):
            await big_send(chat_id, data, tag=send_name)

    except Exception as e:
        create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)
