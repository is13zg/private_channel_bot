import create_bot
from db import Database
import config
import json
import random, string
import inspect


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


def get_menu_names():
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


db = Database(config.BD_name)
interaction_json = unpuck_json(config.Interaction_file_name)
answer_json = unpuck_json(config.Answers_file_name)
menu_names, answer_names = get_menu_names()
Chek_email_before_join = True
Random_str = gen_rnd_str()
Email_user_list = get_emails_from_file(config.Emails_file_name)
Emails_to_delete = []
MIN_mode = False
