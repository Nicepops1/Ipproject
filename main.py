from kivy.config import Config
Config.set("graphics","width", 300)
Config.set("graphics","height", 500)
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
import datetime
import pymysql

class P(FloatLayout):
    pass

class mysqlConnector:
    def __init__(self, **kwargs):
        super(mysqlConnector, self).__init__(**kwargs)
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="1234567",
            database="personalities",
            cursorclass=pymysql.cursors.DictCursor
        )
    def login_check(self, username, password):
        select_user_rows = "SELECT Username,Passwd FROM profiles"
        with self.connection.cursor() as cursor:
            cursor.execute(select_user_rows)
            rows = cursor.fetchall()
            for row in rows:
                if row["Username"] == username and row["Passwd"] == password:
                    return True
    def user_create(self, username, password):
        select_id = "SELECT idProfiles FROM profiles"
        with self.connection.cursor() as cursor:
            cursor.execute(select_id)
            rows = cursor.fetchall()
            self.id = len(rows)+1
            print(self.id)
        with self.connection.cursor() as cursor:
            create_new_user = f"INSERT INTO profiles (idProfiles, Username, Passwd) VALUES ('{self.id}', '{username}', '{password}') ;"
            cursor.execute(create_new_user)
            self.connection.commit()
            return True
    def note_list(self, username):
        check_note = f"SELECT owner, notename, content FROM notes"
        with self.connection.cursor() as cursor:
            cursor.execute(check_note)
            rows = cursor.fetchall()
            list_of_content = []
        for row in rows:
            if row["owner"] == username:
                list_of_content.append([row["notename"], row["content"]])
        return list_of_content


class note_list(MDList):
    def __init__(self,username, **kwargs):
        super(note_list, self).__init__(**kwargs)
        self.id = "note_list"
        list_of_notes = mysqlConnector().note_list(username)
        for note in list_of_notes:
            txt = f"{note[0]}: {note[1]}"
            self.add_widget(OneLineListItem(text = txt))



class RegistrationWindow(Screen):
    pass

class LoginWindow(Screen):
    pass

class CalendarWindow(Screen):
    pass

class NoteMakerWindow(Screen):
    pass


class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        self.transition = NoTransition()


class IpprojectApp(MDApp):
    def build(self):
        self.default_theme = "Темная тема"
        self.theme_cls.theme_style = "Light"
        self.default_theme_light = True
        self.mainwindow = Builder.load_file("typicalkivy.kv")
        return self.mainwindow
    def dark_theme(self):
        if self.default_theme_light:
            self.theme_cls.theme_style = "Dark"
            self.root.ids.dark_theme.text = "Светлая тема"
            self.root.ids.icon.icon = "toggle-switch-outline"
            self.default_theme_light = False
        else:
            self.theme_cls.theme_style = "Light"
            self.root.ids.dark_theme.text = "Темная тема"
            self.root.ids.icon.icon = "toggle-switch-off-outline"
            self.default_theme_light = True

    def swaptologin(self):
        self.root.current = "login"

    def log_out(self):
        self.root.ids.md_box_layout.remove_widget(self.note_list)
        self.root.ids.md_box_layout.remove_widget(self.scroll)
        self.root.current = "login"

    def swaptoregistr(self):
        self.root.current = "register"

    def swaptocalendar(self):
        self.root.current = "calendar"

    def go_to_note_maker(self):
        self.root.current = "note_maker"

    def registerfunc(self):
        self.username = self.root.ids.register_username.text
        self.password = self.root.ids.register_passwd.text
        self.current_passwd = self.root.ids.current_passwd.text
        if self.password == self.current_passwd:
            if mysqlConnector().user_create(self.username,self.password):
                self.swaptocalendar()
                self.root.ids.md_box_layout.add_widget(note_list(self.username))

    def enterfunc(self):
        self.username = self.root.ids.login_username.text
        self.password = self.root.ids.login_passwd.text
        if mysqlConnector().login_check(self.username, self.password):
            self.root.current = "calendar"
            self.note_list = note_list(self.username)
            self.scroll = ScrollView()
            self.root.ids.md_box_layout.add_widget(self.note_list)
            self.root.ids.md_box_layout.add_widget(self.scroll)
        else:
            show = P()

            popupWindow = Popup(title = "Сообщение", content = show, size_hint = (None,None), size=(200,200))

            popupWindow.open()


if __name__ == '__main__':
    IpprojectApp().run()
