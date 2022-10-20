import sqlite3
import inspect


class Database:
    def __init__(self, db_file):
        try:
            self.connection = sqlite3.connect(db_file)
            self.cursor = self.connection.cursor()
        except Exception as e:
            pass

    def create_new_pswd_table(self, table_name):
        try:
            with self.connection:
                print(table_name)
                self.cursor.execute(f""" CREATE TABLE IF NOT EXISTS "{table_name}" (
                                        id         INTEGER PRIMARY KEY AUTOINCREMENT
                                                           UNIQUE,
                                        name       TEXT,
                                        login      TEXT,
                                        E_pswd     TEXT    NOT NULL,
                                        url        TEXT,
                                        E_secret   TEXT,
                                        comment    TEXT,
                                        E_who_view TEXT
                                    ); """)
        except Exception as e:
            pass

    def get_all_pswds(self, name: str) -> list:
        try:
            with self.connection:
                return self.cursor.execute(f"SELECT * FROM `{name}`").fetchall()
        except Exception as e:
            pass

    def get_filter_pswds(self, table_name: str, search_str: str) -> list:
        all_pswd = self.get_all_pswds(table_name)
        res = []
        for record in all_pswd:
            pass

    def add_user_to_db(self, tlg_user_id, user_getcourse_email):
        try:
            with self.connection:
                return self.cursor.execute(
                    "INSERT INTO `users_in_channel` (`tlg_user_id`, `user_getcourse_email`) VALUES (?,?)",
                    (tlg_user_id, user_getcourse_email,))
        except Exception as e:
            print(f"Module: {__name__}\n"
                  f"Func: {inspect.currentframe().f_code.co_name}\n"
                  f"Excep: {e}\n")

    def get_user_tlg_id(self, user_getcourse_email):
        try:
            with self.connection:
                res = self.cursor.execute(
                    "SELECT `tlg_user_id` FROM `users_in_channel` WHERE `user_getcourse_email` = ?",
                    (user_getcourse_email,)).fetchmany(1)
                return int(res[0][0])
        except Exception as e:
            print(f"Module: {__name__}\n"
                  f"Func: {inspect.currentframe().f_code.co_name}\n"
                  f"Excep: {e}\n")

    def user_exists(self, user_getcourse_email):
        try:
            with self.connection:
                res = self.cursor.execute("SELECT * FROM `users_in_channel` WHERE `user_getcourse_email` = ?",
                                          (user_getcourse_email,)).fetchmany(1)

                print(res)
                return bool(len(res))
        except Exception as e:
            print(f"Module: {__name__}\n"
                  f"Func: {inspect.currentframe().f_code.co_name}\n"
                  f"Excep: {e}\n")

    def add_pswd_view(self, table_name, key, E_who_view):
        try:
            with self.connection:
                self.cursor.execute(f"UPDATE `{table_name}` SET `E_who_view` = '{E_who_view}' WHERE `id`='{key}'")
        except Exception as e:
            pass

            def book_exists(self, name):
                with self.connection:
                    res = self.cursor.execute("SELECT * FROM `books_view_count` WHERE `name` = ?", (name,)).fetchmany(1)
                    return bool(len(res))

            def add_book_view(self, name):
                with self.connection:
                    return self.cursor.execute(
                        "UPDATE `books_view_count` SET `view_count` = `view_count` + 1 WHERE `name`=?",
                        (name,))

            def get_books_stat(self):
                with self.connection:
                    return self.cursor.execute("SELECT `name`, `view_count` FROM `books_view_count`").fetchall()

            def user_exists(self, user_id):
                with self.connection:
                    res = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchmany(1)
                    return bool(len(res))

            def add_user(self, user_id):
                with self.connection:
                    return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))

            def count_users(self):
                with self.connection:
                    return self.cursor.execute("SELECT COUNT(*) from `users`").fetchmany(1)

            def count_active_user(self):
                with self.connection:
                    return self.cursor.execute("SELECT COUNT(*) from `users`  WHERE `active` = 1").fetchmany(1)

            def set_active(self, user_id, active):
                with self.connection:
                    return self.cursor.execute("UPDATE `users` SET `active` = ? WHERE `user_id`=?", (active, user_id,))

            def get_users(self):
                with self.connection:
                    return self.cursor.execute("SELECT `user_id`, `active` FROM `users`").fetchall()

            def admin_exists(self, admin_id):
                with self.connection:
                    res = self.cursor.execute("SELECT * FROM `admins` WHERE `admin_id` = ?", (admin_id,)).fetchmany(1)
                    return bool(len(res))

            def add_admin(self, admin_id, name):
                with self.connection:
                    return self.cursor.execute("INSERT INTO `admins` (`admin_id`,name) VALUES (?,?)", (admin_id, name,))

            def del_admin(self, admin_id):
                with self.connection:
                    return self.cursor.execute("DELETE FROM `admins` WHERE `admin_id` = ?", (admin_id,))

            def get_admins(self):
                with self.connection:
                    return self.cursor.execute("SELECT `admin_id`,`name` FROM `admins`").fetchall()
