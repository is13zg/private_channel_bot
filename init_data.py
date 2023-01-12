from db import Database
import config
from utils import utils

update_from_gk = False
MIN_mode = True
Chek_email_before_join = True
update_from_gk_time = 60
time_counter = 0
db = Database(config.BD_name)

Random_str = utils.gen_rnd_str()
interaction_json, answer_json = utils.update_interaction_answer(MIN_mode)
menu_names, answer_names = utils.get_menu_names(interaction_json)
messages_to_user = utils.unpuck_json(config.Messages_to_user_file_name)

# список емайлов которые не удаляются
Emails_NZ_list = utils.get_emails_from_file(config.Emails_NZ_file_name)

# текущий список кому разрешено вступать в рум клуб
Email_user_list = utils.get_emails_from_file(config.Emails_file_name)
Email_user_list.extend(Emails_NZ_list)

# список пользователей которые есть в канале или списке разрешенных, но будут удалены из него
Emails_to_delete_from_allow_list = utils.get_emails_from_file(config.Emails_to_delete_file_name)

# список пользователей которые есть в канале, но будут удалены из него
Emails_to_delete_from_channel = list(set(db.get_emails()).difference(Email_user_list))

# список в котором хранится список полученных пользователей из ГК
# Emails_new_user_list = []

# список для рассылки полученных пользователей из ГК
Emails_to_spam_list = []
