from db import Database
import config
from utils import utils

MIN_mode = True
Chek_email_before_join = True
db = Database(config.BD_name)

Random_str = utils.gen_rnd_str()
interaction_json, answer_json = utils.update_interaction_answer(MIN_mode)
menu_names, answer_names = utils.get_menu_names(interaction_json)
Email_user_list = utils.get_emails_from_file(config.Emails_file_name)
Emails_to_delete = []
