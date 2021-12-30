from models import *

import os, hashlib, re
from datetime import datetime, date, timedelta

from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles

from kivymd.uix import dialog
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDFloatingLabel, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch, IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.swiper import MDSwiper, MDSwiperItem

from kivy.core.text import LabelBase
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.pagelayout import PageLayout


# screen management
class ScreenManagement(ScreenManager):
    pass

sm = ScreenManagement(transition = SlideTransition())

# screen classes
class ThingBoxTemplate(MDBoxLayout):
    iter_id = NumericProperty(-1)
    def __init__(self, iter_id, *args, **kwargs):
        self.iter_id = iter_id
        super().__init__(*args, **kwargs)

class MemoryTemplate(MDSwiperItem):
    date_text = StringProperty('')
    iter_id = NumericProperty(-1)
    def __init__(self, date_text, iter_id, *args, **kwargs):
        self.date_text = date_text
        self.iter_id = iter_id
        super().__init__(*args, **kwargs)
        self.ids.thingsbox_id.add_widget(ThingBoxTemplate(iter_id = self.iter_id))

class MemoryScreen(Screen):
    day_count = NumericProperty(3)
    def __init__(self, *args, **kwargs):
        super(MemoryScreen, self).__init__(*args, **kwargs)
        for d in reversed(range(0, self.day_count)):
            day = datetime.now() - timedelta(days = d)
            self.ids.mdswiper_id.add_widget(
                MemoryTemplate(
                    date_text = MainApp.date_format(day, format = 3),
                    iter_id = d
                )
            )
class LoginScreen(Screen):
    register_btn_disabled = BooleanProperty(True)
    register_btn_opacity = NumericProperty(0)
    user = ObjectProperty(session.query(User).first())
    login_error_msg = ObjectProperty(None)
    def __init__(self, *args, **kwargs):
        super(LoginScreen, self).__init__(*args, **kwargs)
        # check if user exist
        if not self.user:
            self.register_btn_disabled = False
            self.register_btn_opacity = 1
    def passcode_validation(self, obj):
        text_output = obj.text
        if len(text_output) > obj.max_text_length:
            text_output = text_output[:-1]
            obj.text = text_output
        elif len(text_output) == obj.max_text_length:
            if self.user:
                # login
                hashcode = hashlib.sha256(text_output.encode('utf-8')).hexdigest()
                if session.query(User).filter_by(passcode = hashcode).first():
                    sm.current = 'memory'
                else:
                    obj.text = ''
                    self.login_error_msg = Snackbar(
                        text = 'Invalid Passcode',
                        snackbar_x = '10dp',
                        snackbar_y = '10dp',
                        pos_hint = {'center_x': .5}, 
                        duration = 0.2
                    )
                    self.login_error_msg.open()
    def register_user(self):
        # check user
        user = session.query(User).first()
        if not user:
            passcode = self.ids.passcode.text
            hashcode = hashlib.sha256(passcode.encode('utf-8')).hexdigest()
            # create user
            user = User(passcode = hashcode)
            session.add(user)
            session.commit()
            sm.current = 'memory'
        else:
            print('user exists')


# main class
class MainApp(MDApp):

    def build(self):
        
        # fonts
        LabelBase.register(
            name = 'Courgette',
            fn_regular='fonts/Courgette-Regular.ttf'
        )
        theme_font_styles.append('Courgette')

        # themes
        self.theme_cls.primary_palette = 'Purple'
        self.theme_cls.font_styles["Courgette"] = [
            "Courgette", 16, False, 0.15,]

        # sm
        sm.add_widget(LoginScreen(name = 'login'))
        sm.add_widget(MemoryScreen(name = 'memory'))

        sm.current = 'memory'
        return sm
    def date_format(current_date, format = 1):
        day = int(current_date.strftime('%d'))
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        if format == 1:
            return current_date.strftime(f'%A, %B %d{suffix}, %Y')
        elif format == 2:
            return current_date.strftime(f'%B %d{suffix}, %Y')
        elif format == 3:
            return current_date.strftime(f'%B %d{suffix}, %Y\n%A')
            

MainApp().run()