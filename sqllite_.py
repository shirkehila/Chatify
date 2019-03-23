import sqlite3
from pprint import pprint as pp


class DB():
    def __init__(self):
        self._db_name = 'chatify.db'
        self._conn = None
        self._cursor = None

    def connect_db(self):
        self._conn = sqlite3.connect(self._db_name)
        self._cursor = self._conn.cursor()

    def disconnect_db(self):
        self._conn.close()
        self._conn = None
        self._cursor = None

    def add_user(self, username, password):
        self.connect_db()
        self._cursor.execute("INSERT INTO users VALUES ('{}','{}')".format(username, password))
        self._conn.commit()
        self.disconnect_db()

    def user_exists(self, username):
        self.connect_db()
        self._cursor.execute("SELECT COUNT(*) FROM users WHERE username = '{}'".format(username))
        count = self._cursor.fetchall()
        self.disconnect_db()
        if count[0][0] > 0:
            return True
        return False

    def get_all_users(self):
        self.connect_db()
        self._cursor.execute("SELECT * FROM users")
        users = self._cursor.fetchall()
        self.disconnect_db()
        return users

    def check_user_pass(self, username, password):
        if not self.user_exists(username):
            return -1
        self.connect_db()
        self._cursor.execute("SELECT password FROM users WHERE username='{}'".format(username))
        pass_check = self._cursor.fetchall()
        correct = 0
        if password == pass_check[0][0]:
            correct = 1
        self.disconnect_db()
        return correct


db = DB()
pp(db.get_all_users())

