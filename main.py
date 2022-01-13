from xml.dom.pulldom import parseString
from models import *

import hashlib, re, requests, json
from datetime import datetime, timedelta

from kivymd.app import MDApp
from kivymd.font_definitions import theme_font_styles
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineAvatarIconListItem
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors import TouchBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDIconButton
from kivymd.uix.list import IconLeftWidget, IconRightWidget


from kivy.core.text import LabelBase
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition

from kivy.core.window import Window

############################################
# screen management
class ScreenManagement(ScreenManager):
    pass

sm = ScreenManagement(transition = SlideTransition())
############################################
class LoginScreen(Screen):
    new_user = BooleanProperty(False)
    user = ObjectProperty(session.query(User).first())
    def __init__(self, *args, **kwargs):
        super(LoginScreen, self).__init__(*args, **kwargs)
        if self.user:
            self.new_user = False
        else:
            self.new_user = True
    def validate(self, obj):
        if len(obj.text) > obj.max_text_length:
            obj.text = obj.text[:-1]
        elif len(obj.text) == obj.max_text_length:
            if self.user:
                # login
                hashcode = hashlib.sha256(obj.text.encode('utf-8')).hexdigest()
                if session.query(User).filter_by(passcode = hashcode).first():
                    sm.current = 'memory'
                else:
                    obj.text = ''
                    self.login_error = Snackbar(
                        text = 'Invalid Passcode',
                        snackbar_x = '10dp',
                        snackbar_y = '10dp',
                        pos_hint = {'center_x': .5}, 
                        duration = 0.2
                    )
                    self.login_error.open()
    def register(self):
        if len(self.ids.passcode.text) == self.ids.passcode.max_text_length:
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
                self.ids.passcode.text = ''
        else:
            self.ids.passcode.text = ''

class ThingTemplate(MDBoxLayout):
    editable = BooleanProperty(False)
    memory = ObjectProperty(None)
    text = StringProperty('')
    iter_id = NumericProperty(-1)
    dialog = ObjectProperty(None)
    content = ObjectProperty(None)
    def __init__(self, memory, iter_id = -1, editable = False, *args, **kwargs):
        self.editable = editable
        self.iter_id = iter_id
        self.memory = memory
        if self.iter_id == 1:
            self.text = self.memory.thing1
        elif self.iter_id == 2:
            self.text = self.memory.thing2
        elif self.iter_id == 3:
            self.text = self.memory.thing3
        else:
            self.text = ''
        super().__init__(*args, **kwargs)
    def edit(self):
        current_text = self.ids.thing_id.text
        if not self.dialog:
            self.content = MDTextField(text = current_text, multiline = True)
            self.dialog = MDDialog(
                type = 'custom',
                content_cls = self.content,
                buttons = [
                    MDIconButton(icon = 'close', on_release = self.dialog_dismiss),
                    MDIconButton(icon = 'content-save-edit', on_release = self.save)
                ],
            )
        self.content.focus = True
        self.dialog.open()
    def dialog_dismiss(self, *args, **kwargs):
        self.dialog.dismiss()
        self.content.text = self.ids.thing_id.text
    def save(self, *args, **kwargs):
        current_text = self.content.text
        # save
        if self.iter_id == 1:
            self.memory.thing1 = current_text
        elif self.iter_id == 2:
            self.memory.thing2 = current_text
        elif self.iter_id == 3:
            self.memory.thing3 = current_text
        session.commit()
        self.dialog_dismiss()
        self.ids.thing_id.text = current_text

class MemoryTemplate(MDSwiperItem):
    memory = ObjectProperty(None)
    day = ObjectProperty(None)
    quote = StringProperty('')
    date_text = StringProperty('')
    def __init__(self, day, *args, **kwargs):
        self.day = day
        self.date_text = MainApp.format_date(self.day, format = 1)
        self.get_or_create_memory()
        super().__init__(*args, **kwargs)
        # quotejson = json.loads(requests.get('https://zenquotes.io/api/random').content)[0]
        # self.quote = f'{quotejson["q"]}\n{quotejson["a"]}'
        # # self.quote = f'{quotejson["q"]}'
        # self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 1, memory = self.memory))
        # self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 2, memory = self.memory))
        # self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 3, memory = self.memory))
        self.build_memory()
    def build_memory(self):
        self.get_or_create_memory()
        quotejson = json.loads(requests.get('https://zenquotes.io/api/random').content)[0]
        self.quote = f'{quotejson["q"]}\n{quotejson["a"]}'
        self.ids.thingsbox_id.clear_widgets()
        self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 1, memory = self.memory))
        self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 2, memory = self.memory))
        self.ids.thingsbox_id.add_widget(ThingTemplate(iter_id = 3, memory = self.memory))
    def get_or_create_memory(self):
        memory = session.query(Memory).filter(func.date(Memory.date) == func.date(self.day)).first()
        if not memory:
            memory = Memory(date = self.day)
            session.add(memory)
            session.commit()
        self.memory = memory
    def set_happiness(self, obj):
        self.memory.happiness = int(obj.value)
        session.commit()

class MemoryScreen(Screen):
    days_count = NumericProperty(3)
    # days_count = NumericProperty(1)
    def __init__(self, *args, **kwargs):
        super(MemoryScreen, self).__init__(*args, **kwargs)
        for d in reversed(range(0, self.days_count)):
            day = datetime.now() - timedelta(days = d)
            self.ids.mdswiper_id.add_widget(
                MemoryTemplate(day = day)
            )

class MemoryList(OneLineAvatarIconListItem):
    memory = ObjectProperty(None)
    # emo_widget = ObjectProperty(None)
    def __init__(self, memory, *args, **kwargs):
        self.memory = memory
        super().__init__(*args, **kwargs)
        # self.emo_widget = self.get_emoticon()
        self.text = memory.date.strftime('%d.%m.%Y')
        self.add_widget(
            IconLeftWidget(icon = 'trash-can', on_release = self.delete, theme_text_color = 'Custom', text_color = '#d90429')
        )
        iconlist = {
            1: {
                'emoticon': 'emoticon-poop',
                'color': '#f94144'
            },
            2: {
                'emoticon': 'emoticon-sad',
                'color': '#f8961e'
            },
            3: {
                'emoticon': 'emoticon-neutral',
                'color': '#f9c74f'
            },
            4: {
                'emoticon': 'emoticon-happy',
                'color': '#90be6d'
            },
            5: {
                'emoticon': 'emoticon-excited',
                'color': '#43aa8b'
            }     
        }
        emo = iconlist[self.memory.happiness]
        self.add_widget(IconRightWidget(icon = emo['emoticon'], text_color = emo['color'], theme_text_color = 'Custom', on_release = self.open))
    def delete(self, *args, **kwargs):
        memory = session.query(Memory).get(self.memory.date)
        session.delete(memory)
        session.commit()
        self.parent.parent.parent.build_memories()
        # print(self.parent.parent.parent)
        # self.parent.parent.parent.remove_widget(self)
    def open(self, *args, **kwargs):
        pass


class MemoriesScreen(Screen):
    def __init__(self, *args, **kwargs):
        super(MemoriesScreen, self).__init__(*args, **kwargs)
        # self.build_memories()
    def build_memories(self):
        self.ids.memories_id.clear_widgets()
        memories = session.query(Memory).all()
        print(memories)
        for memory in memories:
            self.ids.memories_id.add_widget(
                MemoryList(memory = memory)
            )

############################################
class MainApp(MDApp):
    def build(self):
        # window size
        self.window_size = Window.size
        # fonts
        LabelBase.register(
            name = 'Courgette',
            fn_regular='./Courgette-Regular.ttf'
        )
        theme_font_styles.append('Courgette')
        # themes
        self.theme_cls.primary_palette = 'Purple'
        self.theme_cls.font_styles["Courgette"] = [
            "Courgette", 16, False, 0.15,]
        # sm
        sm.add_widget(LoginScreen(name = 'login'))
        sm.add_widget(MemoryScreen(name = 'memory'))
        sm.add_widget(MemoriesScreen(name = 'memories'))
        # sm.current = 'login'
        sm.current = 'memories'
        return sm
    def format_date(day, format = 0):
        current_date = int(day.strftime('%d'))
        if 4 <= current_date <= 20 or 24 <= current_date <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][current_date % 10 - 1]
        if format == 1:
            return day.strftime(f'%d{suffix} %B, %Y\n%A')
    def page(self, string):
        # if string == 'memories':
        #     sm.get_screen(string).build_memories()
        sm.current = string
        # if string == 'memories':
        #     sm.current_screen.build_memories()
############################################
MainApp().run()