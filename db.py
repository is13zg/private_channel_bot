import sqlite3
import inspect
import create_bot


class Database:
    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def add_user_to_db(self, tlg_user_id, user_getcourse_email):
        try:
            with self.connection:
                return self.cursor.execute(
                    "INSERT INTO `users_in_channel` (`tlg_user_id`, `user_getcourse_email`) VALUES (?,?)",
                    (tlg_user_id, user_getcourse_email,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def add_user_to_del(self, tlg_user_id, user_getcourse_email):
        try:
            with self.connection:
                return self.cursor.execute(
                    "INSERT INTO `users_in_channel_del` (`tlg_user_id`, `user_getcourse_email`) VALUES (?,?)",
                    (tlg_user_id, user_getcourse_email,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def add_reg_user_to_db(self, user_id):
        try:
            with self.connection:
                return self.cursor.execute(
                    "INSERT INTO `users` (`id`) VALUES (?)",
                    (user_id,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def get_user_tlg_id(self, user_getcourse_email):
        try:
            with self.connection:
                res = self.cursor.execute(
                    "SELECT `tlg_user_id` FROM `users_in_channel` WHERE `user_getcourse_email` = ?",
                    (user_getcourse_email,)).fetchmany(1)
                return int(res[0][0])
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def get_user_email(self, user_tlg_id):
        try:
            with self.connection:
                res = self.cursor.execute(
                    "SELECT `user_getcourse_email` FROM `users_in_channel` WHERE `tlg_user_id` = ?",
                    (user_tlg_id,)).fetchmany(1)
                return str(res[0][0])
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def user_exists(self, user_getcourse_email):
        try:
            with self.connection:
                res = self.cursor.execute("SELECT * FROM `users_in_channel` WHERE `user_getcourse_email` = ?",
                                          (user_getcourse_email,)).fetchmany(1)

                return bool(len(res))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def reg_user_exists(self, user_id):
        try:
            with self.connection:
                res = self.cursor.execute("SELECT * FROM `users` WHERE `id` = ?",
                                          (user_id,)).fetchmany(1)

                return bool(len(res))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def del_user_from_db(self, tlg_user_id):
        try:
            with self.connection:

                # получение email по id, чтобы потом сохранить пользователя в таблице удаленных
                email = self.cursor.execute(
                    "SELECT `user_getcourse_email` FROM `users_in_channel` WHERE `tlg_user_id` = ?",
                    (tlg_user_id,)).fetchmany(1)[0][0]
                self.cursor.execute(
                    "INSERT INTO `users_in_channel_del` (`tlg_user_id`, `user_getcourse_email`) VALUES (?,?)",
                    (tlg_user_id, email,))

                # проходит само удаление пользователя
                return self.cursor.execute("DELETE FROM `users_in_channel` WHERE `tlg_user_id` = ?", (tlg_user_id,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def del_user_from_db_email(self, email):
        try:
            with self.connection:
                # получение id по  email, чтобы потом сохранить пользователя в таблице удаленных
                tlg_user_id = self.cursor.execute(
                    "SELECT `tlg_user_id` FROM `users_in_channel` WHERE `user_getcourse_email` = ?",
                    (email,)).fetchmany(1)[0][0]
                self.cursor.execute(
                    "INSERT INTO `users_in_channel_del` (`tlg_user_id`, `user_getcourse_email`) VALUES (?,?)",
                    (tlg_user_id, email,))

                # проходит само удаление пользователя
                return self.cursor.execute("DELETE FROM `users_in_channel` WHERE `user_getcourse_email` = ?", (email,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def count_reg_user(self):
        try:
            with self.connection:
                return self.cursor.execute("SELECT COUNT(*) from `users` ").fetchmany(1)
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def count_tlg_user(self):
        try:
            with self.connection:
                return self.cursor.execute("SELECT COUNT(*) from `users_in_channel` ").fetchmany(1)
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def get_emails(self):
        try:
            with self.connection:
                return self.cursor.execute("SELECT `user_getcourse_email` FROM `users_in_channel`").fetchall()
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)

    def update_email(self, new_email, tlg_id):
        try:
            with self.connection:
                return self.cursor.execute(
                    "UPDATE `users_in_channel` SET `user_getcourse_email` = ? WHERE `tlg_user_id`=?",
                    (new_email, tlg_id,))
        except Exception as e:
            create_bot.print_error_message(__name__, inspect.currentframe().f_code.co_name, e)
