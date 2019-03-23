import kivy
from sqllite_ import DB
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

db = DB()

logged_user = ''

kivy.require('1.8.0')  # replace with your current kivy version !

from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.core.window import Window

Window.size = (400, 130)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class MyPopup(Popup):
    pass

class SignUp(Screen):
    def handle_submit(self, username, passw, v_passw):
        if self.check_input(username,passw,v_passw):
            db.add_user(username,passw)
            popup = MyPopup(title="Successfully signed up!")
            popup.open()

    def check_input(self, username, passw, v_passw):
        if len(username)<4:
            popup = MyPopup(title="Username must contain at least 4 characters")
            popup.open()
            return False
        if len(passw)<4:
            popup = MyPopup(title="Password must contain at least 4 characters")
            popup.open()
            return False
        if passw != v_passw:
            popup = MyPopup(title="Password and validation don't match")
            popup.open()
            return False
        elif db.user_exists(username):
            popup = MyPopup(title="Username already exists")
            popup.open()
            return False
        return True


class SignIn(Screen):
    def handle_submit(self, username, passw):
        if self.check_user_pass(username,passw):
            global logged_user
            logged_user = username
            MyApp.get_running_app().stop()
            Window.close()
    def check_user_pass(self, username, passw):
        if db.check_user_pass(username, passw) == -1:
            popup = MyPopup(title="Username doesn't exists")
            popup.open()
            return False
        if db.check_user_pass(username, passw) == 0:
            popup = MyPopup(title="Username and password don't match")
            popup.open()
            return False
        return True

class MyScreenManager(ScreenManager):
    pass


class MyApp(App):

    def build(self):
        self.root = Builder.load_file('simpleForm.kv')
        self.title="Chatify"
        return self.root

    def get_username(self):
        global logged_user
        return logged_user


if __name__ == '__main__':
    MyApp().run()
