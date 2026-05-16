import os
os.environ['KIVY_METRICS_FONTSCALE'] = '1'
from kivy.core.window import Window
Window.size = (360, 640)  # Mobile dimensions
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.tab import MDTabs
from kivymd.uix.toolbar import MDTopAppBar
from kivy.graphics import Line, Color, Triangle
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer, MDNavigationDrawerMenu
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.gridlayout import MDGridLayout
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.label import Label
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.snackbar import Snackbar
import math
import cmath

# ==========================================
# Safe streaming helper — never cuts inside markup tags
# ==========================================
def _safe_stream_chunks(text):
    """Split text into chunks that are each complete markup-tag units.
    Each chunk is one line (newline included). This prevents the
    ColorParser from seeing partial [color=008... tags."""
    import re
    # Split on newlines but keep the delimiter
    parts = re.split(r'(\n)', text)
    chunks = []
    buf = ""
    for p in parts:
        buf += p
        if p == "\n" or p == parts[-1]:
            if buf:
                chunks.append(buf)
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks


# ==========================================
# 1. Background System (Simplified for performance)
# ==========================================
class SimpleBackground(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Simple solid background color
            Color(0.95, 0.96, 0.98, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
# ==========================================
# 2. Splash Screen (Loading Screen)
# ==========================================
class AppIntroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # استخدام الخلفية البسيطة
        self.bg = SimpleBackground()
        
        # 1. كلمة ترحيب كبيرة في المنتصف
        welcome_box = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        self.welcome_label = MDLabel(
            text="WELCOME",
            halign="center",
            font_style="H2",
            bold=True,
            theme_text_color="Primary"
        )
        welcome_box.add_widget(self.welcome_label)
        
        # 2. معلومات المطور في الأسفل تماماً
        bottom_box = MDBoxLayout(
            orientation='vertical',
            adaptive_height=True,
            spacing=dp(20),
            padding=dp(30),
            pos_hint={"center_x": 0.5, "y": 0.05}
        )
        
        self.name_label = MDLabel(
            text="Developed By: Mohammed Fahmi",
            halign="center",
            font_style="H6",
            theme_text_color="Secondary"
        )
        
        self.dept_label = MDLabel(
            text="Mechatronics Engineering Dept.",
            halign="center",
            font_style="H6",
            theme_text_color="Secondary"
        )
        
        bottom_box.add_widget(self.name_label)
        bottom_box.add_widget(self.dept_label)
        
        self.bg.add_widget(welcome_box)
        self.bg.add_widget(bottom_box)
        self.add_widget(self.bg)

    def on_enter(self):
        self._dot_count = 0
        self._dot_event = Clock.schedule_interval(self._animate_dots, 0.5)
        Clock.schedule_once(self.go_to_home, 6)

    def _animate_dots(self, dt):
        self._dot_count = (self._dot_count + 1) % 4
        self.welcome_label.text = "WELCOME" + "." * self._dot_count

    def go_to_home(self, dt):
        if self._dot_event:
            self._dot_event.cancel()
        self.manager.current = 'home'
# ==========================================
# 3. Home Screen (With Info Dialog)
# ==========================================
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Main Navigation Layout (Handles the drawer and main screen)
        self.add_widget(SimpleBackground())
        self.nav_layout = MDNavigationLayout()
        self.screen_manager = MDScreenManager()
        
        # 2. Main Content Screen
        self.main_content = MDScreen()
        self.bg = SimpleBackground()
        self.layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar with Menu Icon
        toolbar = MDTopAppBar(
            title="MTro AC Helper",
            left_action_items=[["menu", lambda x: self.nav_drawer.set_state("open")]],
            elevation=2
        )
        self.layout.add_widget(toolbar)

        # Scrollable Box for Subject Cards (3 big series tabs)
        scroll = ScrollView()
        self.cards_box = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(15),
            adaptive_height=True,
            size_hint_y=None
        )
        self.cards_box.bind(minimum_height=self.cards_box.setter('height'))
        
        self.build_subject_cards()
        scroll.add_widget(self.cards_box)
        self.layout.add_widget(scroll)
        self.bg.add_widget(self.layout)
        self.main_content.add_widget(self.bg)
        self.screen_manager.add_widget(self.main_content)
        
        # 3. Navigation Drawer (The Left Menu)
        self.nav_drawer = MDNavigationDrawer(radius=(0, 20, 20, 0))
        drawer_menu = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        drawer_menu.add_widget(MDLabel(text="App Settings", font_style="H6", adaptive_height=True))

        # Dark mode toggle row
        dark_row = MDBoxLayout(orientation="horizontal", spacing=dp(10),
                               size_hint_y=None, height=dp(48))
        dark_row.add_widget(MDLabel(text="Dark Mode", size_hint_x=0.7,
                                    theme_text_color="Primary"))
        self.dark_switch = MDSwitch(size_hint_x=0.3, pos_hint={"center_y": 0.5})
        self.dark_switch.bind(active=self.toggle_dark_mode)
        dark_row.add_widget(self.dark_switch)
        drawer_menu.add_widget(dark_row)

        about_btn = MDRaisedButton(text="About App", size_hint_x=1, on_release=self.show_about)
        drawer_menu.add_widget(about_btn)
        
        # Push content to top
        drawer_menu.add_widget(MDBoxLayout()) 
        
        self.nav_drawer.add_widget(drawer_menu)
        self.nav_layout.add_widget(self.screen_manager)
        self.nav_layout.add_widget(self.nav_drawer)
        
        self.add_widget(self.nav_layout)

    def build_subject_cards(self):
        # Make cards smaller to fit 2 in a row
        subjects = [
            {"title": "Ohm's Law", "icon": "omega", "screen": "ohms_law_intro"},
            {"title": "Complex No.", "icon": "math-compass", "screen": "complex_intro"},
            {"title": "AC Circuits", "icon": "sine-wave", "screen": "ac_main"},
            {"title": "MPT", "icon": "lightning-bolt", "screen": "mpt_main"},
            {"title": "Power", "icon": "flash", "screen": "power_main"},
            # Add more subjects here later
        ]
        
        for sub in subjects:
            card = MDCard(
                orientation='vertical',
                size_hint=(1, None),
                size=(Window.width - dp(30), dp(100)), # Full width minus padding
                padding=dp(15),
                radius=[15],
                elevation=2,
                ripple_behavior=True,
                on_release=lambda x, target=sub["screen"]: self.navigate_to(target)
            )
            card.add_widget(MDIconButton(icon=sub["icon"], pos_hint={"center_x": .5}))
            card.add_widget(MDLabel(text=sub["title"], halign="center", bold=True))
            self.cards_box.add_widget(card)

    def toggle_dark_mode(self, instance, value):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.theme_cls.theme_style = "Dark" if value else "Light"

    def navigate_to(self, screen_name):
        self.manager.current = screen_name
   
    def show_about(self, instance):
        
        about_text = (
            "[b]About Mechatronics Hub v2.0[/b]\n\n"
            "1. This application is an advanced engineering tool designed to assist Mechatronics students.\n"
            "2. It features a Smart Inference Engine that not only calculates missing variables but tracks data gaps.\n"
            "3. The architecture relies on standard academic formulas for DC and AC analysis.\n"
            "4. Built with Python and KivyMD, it ensures cross-platform compatibility.\n"
            "5. The Ohm's Law module covers basic linear circuit principles.\n"
            "6. The Complex Numbers module bridges the gap between algebra and phasor analysis.\n"
            "7. The AC Circuits module provides deep dives into Series, Parallel, and Resonance conditions.\n"
            "8. Developed to simplify complex mathematical derivations into visual, step-by-step solutions.\n"
            "9. Ensure you enter numerical values without units in the calculators.\n"
            "10. Designed by Muhamed. All rights reserved."
        )
        dialog = MDDialog(title="Application Manual", text=about_text, buttons=[MDFlatButton(text="CLOSE", on_release=lambda x: dialog.dismiss())])
        dialog.open()
# ==========================================
# 4. Ohms Law Screen
# ==========================================
from kivy.graphics import Line, Color, Triangle

class OhmsLawIntroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        layout.add_widget(MDTopAppBar(title="Ohm's Law: Theory", left_action_items=[["arrow-left", lambda x: self.go_home()]]))
        
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # 12 Lines of Explanation
        intro_text = (
            "[b]The Foundation of Circuit Analysis[/b]\n"
            "1. Ohm's Law states that current is directly proportional to voltage.\n"
            "2. It also states that current is inversely proportional to resistance.\n"
            "3. This linear relationship is mathematically expressed as V = I × R.\n"
            "4. Voltage (V) represents the electrical pressure from the power source.\n"
            "5. Current (I) represents the actual flow of electrons through the wire.\n"
            "6. Resistance (R) is the opposition material offers to electron flow.\n"
            "7. The law strictly applies to purely resistive, linear networks.\n"
            "8. It is used to determine wire thickness required for specific loads.\n"
            "9. It helps engineers calculate voltage drops across long transmission lines.\n"
            "10. It is essential for designing protective circuits like fuses and breakers.\n"
            "11. Knowing any two values allows you to mathematically derive the third.\n"
            "12. Power (P = V × I) is often derived alongside Ohm's Law for thermal analysis."
        )
        content.add_widget(MDLabel(text=intro_text, markup=True, adaptive_height=True))
        
        # Cool Diagram (V-I-R Triangle)
        diagram_card = MDCard(orientation='vertical', size_hint=(1, None), height=dp(150), radius=[15], md_bg_color=(0.1, 0.6, 0.9, 0.1))
        with diagram_card.canvas:
            Color(0.12, 0.58, 0.95, 1)
            # Drawing a simple triangle diagram
            Line(points=[Window.width/2, dp(120), Window.width/2 - dp(50), dp(40), Window.width/2 + dp(50), dp(40)], width=2, close=True)
            Line(points=[Window.width/2 - dp(25), dp(80), Window.width/2 + dp(25), dp(80)], width=2) # Horizontal line
            Line(points=[Window.width/2, dp(80), Window.width/2, dp(40)], width=2) # Vertical line
        
        diagram_card.add_widget(MDLabel(text="V\n\nI       R", halign="center", bold=True, theme_text_color="Primary"))
        content.add_widget(diagram_card)
        
        # Button to open Calculator
        content.add_widget(MDRaisedButton(text="OPEN CALCULATOR", size_hint_x=1, on_release=self.open_calc))
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def go_home(self):
        
        self.manager.current = 'home'

    def open_calc(self, instance):
        
        self.manager.current = 'ohms_law_calc'


# The Calculator (Unchanged logic, just new screen wrapper)
class OhmsLawCalcScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        # Toolbar
        layout.add_widget(MDTopAppBar(
            title="Ohm's Law Calculator", 
            left_action_items=[["arrow-left", lambda x: self.back()]],
            elevation=2
        ))
        
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))

        # --- Formula Card (بدلاً من الرسم) ---
        formula_card = MDCard(
            orientation='vertical', padding=dp(15), radius=[15],
            size_hint=(1, None), height=dp(100), md_bg_color=(0.9, 0.95, 1, 1)
        )
        formula_card.add_widget(MDLabel(
            text="V = I × R  |  I = V / R  |  R = V / I",
            halign="center", bold=True, font_style="H6", theme_text_color="Primary"
        ))
        content.add_widget(formula_card)

        # --- Input Fields ---
        self.v_input = MDTextField(hint_text="Voltage (V)", mode="rectangle", input_filter="float")
        self.i_input = MDTextField(hint_text="Current (I)", mode="rectangle", input_filter="float")
        self.r_input = MDTextField(hint_text="Resistance (R)", mode="rectangle", input_filter="float")
        
        content.add_widget(self.v_input)
        content.add_widget(self.i_input)
        content.add_widget(self.r_input)

        # Calculate + Reset row
        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(10),
                              size_hint_y=None, height=dp(50))
        btn_row.add_widget(MDRaisedButton(
            text="CALCULATE", size_hint_x=0.7, on_release=self.calculate))
        btn_row.add_widget(MDFlatButton(
            text="RESET", size_hint_x=0.3, on_release=self.reset_fields))
        content.add_widget(btn_row)
        
        # Result Card
        self.res_card = MDCard(
            padding=dp(20), radius=[15], size_hint=(1, None), height=dp(80),
            md_bg_color=(1, 1, 1, 1), elevation=1
        )
        self.result_label = MDLabel(
            text="Enter 2 values to calculate", halign="center",
            theme_text_color="Primary", font_style="H6"
        )
        self.res_card.add_widget(self.result_label)
        content.add_widget(self.res_card)

        # History card — last 3 results
        history_card = MDCard(
            orientation="vertical", padding=dp(15), radius=[15],
            size_hint=(1, None), adaptive_height=True,
            md_bg_color=(0.97, 0.97, 1, 1), elevation=1
        )
        history_card.add_widget(MDLabel(
            text="Last 3 Results:", bold=True,
            adaptive_height=True, theme_text_color="Secondary"))
        self.history_label = MDLabel(
            text="No history yet.", adaptive_height=True,
            theme_text_color="Secondary", font_style="Caption")
        history_card.add_widget(self.history_label)
        content.add_widget(history_card)
        self._ohms_history = []

        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def calculate(self, instance):
        v, i, r = self.v_input.text, self.i_input.text, self.r_input.text
        try:
            result_text = ""
            if v and i and not r:
                res = float(v) / float(i)
                result_text = f"Resistance (R) = {res:.4f} Ω"
            elif v and r and not i:
                res = float(v) / float(r)
                result_text = f"Current (I) = {res:.4f} A"
            elif i and r and not v:
                res = float(i) * float(r)
                result_text = f"Voltage (V) = {res:.4f} V"
            else:
                self.result_label.text = "Fill exactly 2 fields"
                return
            self.result_label.text = result_text
            self._ohms_history.append(result_text)
            self._ohms_history = self._ohms_history[-3:]
            self.history_label.text = "\n".join(
                f"{j+1}. {h}" for j, h in enumerate(self._ohms_history))
        except:
            self.result_label.text = "Error: Invalid Numbers"

    def reset_fields(self, instance):
        self.v_input.text = ""
        self.i_input.text = ""
        self.r_input.text = ""
        self.result_label.text = "Enter 2 values to calculate"

    def back(self):
        self.manager.current = 'ohms_law_intro'

class ComplexIntroScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        
        # 1. Toolbar مع زر الرجوع للهوم
        layout.add_widget(MDTopAppBar(
            title="Complex Numbers Analysis",
            left_action_items=[["home", lambda x: self.go_home()]],
            elevation=2
        ))
        
        # إضافة الخلفية البسيطة
        self.main_layout = MDFloatLayout()
        self.main_layout.add_widget(SimpleBackground())
        
        # محتوى الشاشة داخل ScrollView
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # كارت المقدمة
        intro_card = MDCard(
            orientation='vertical', padding=dp(20), radius=[15],
            size_hint=(1, None), height=dp(180), md_bg_color=(0.95, 0.95, 1, 1),
            elevation=1
        )
        intro_card.add_widget(MDLabel(
            text="Why Complex Numbers?",
            font_style="H5", bold=True, theme_text_color="Primary"
        ))
        intro_card.add_widget(MDLabel(
            text="Essential for Mechatronics students to analyze AC Circuits using Phasors. It helps in calculating Impedance (Z), Phase Angle, and Power.",
            theme_text_color="Secondary", font_style="Body1"
        ))
        content.add_widget(intro_card)
        
        # كارت المميزات (Features)
        features_card = MDCard(
            orientation='vertical', padding=dp(20), radius=[15],
            size_hint=(1, None), height=dp(140), md_bg_color=(1, 1, 1, 1),
            elevation=1
        )
        features_card.add_widget(MDLabel(text="Key Tools:", bold=True))
        features_card.add_widget(MDLabel(text="• Rectangular to Polar Converter"))
        features_card.add_widget(MDLabel(text="• Polar to Rectangular Converter"))
        features_card.add_widget(MDLabel(text="• Magnitude & Angle Analysis"))
        content.add_widget(features_card)
        
        # زر الدخول للحاسبة
        content.add_widget(MDRaisedButton(
            text="OPEN COMPLEX CALCULATOR",
            size_hint_x=1, height=dp(55),
            on_release=self.open_calc
        ))
        
        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)
        layout.add_widget(self.main_layout)
        self.add_widget(layout)

    def go_home(self):
        self.manager.current = 'home'

    def open_calc(self, instance):
        self.manager.current = 'complex_calc'

# You will need to build the ComplexCalcScreen logic based on standard math functions.

import math
import cmath

class ComplexCalcScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical')
        
        # --- Toolbar ---
        toolbar = MDTopAppBar(
            title="Complex Number Calculator",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            elevation=2,
            md_bg_color=(0.12, 0.58, 0.95, 1)
        )
        self.layout.add_widget(toolbar)

        # --- Scrollable Content ---
        scroll = ScrollView()
        self.content = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(20), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))

        self.build_converter_card()
        self.build_operations_card()

        scroll.add_widget(self.content)
        self.layout.add_widget(scroll)
        self.add_widget(self.layout)

    def build_converter_card(self):
        # --- CARD 1: CONVERTER (Polar <> Rectangular) ---
        conv_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(20), size_hint=(1, None), adaptive_height=True, radius=[15])
        conv_card.add_widget(MDLabel(text="1. Form Converter", bold=True, font_style="H6"))
        
        # Inputs for Rectangular (R + jX)
        conv_card.add_widget(MDLabel(text="Rectangular to Polar:", theme_text_color="Secondary", font_style="Caption"))
        rect_box = MDBoxLayout(orientation='horizontal', spacing=dp(20), adaptive_height=True)
        self.rect_r = MDTextField(hint_text="Real (R)", mode="rectangle")
        self.rect_x = MDTextField(hint_text="Imaginary (jX)", mode="rectangle")
        rect_box.add_widget(self.rect_r)
        rect_box.add_widget(self.rect_x)
        conv_card.add_widget(rect_box)
        conv_card.add_widget(MDRaisedButton(text="CONVERT TO POLAR", size_hint_x=1, on_release=self.rect_to_polar))

        # Inputs for Polar (|Z| ∠ θ)
        conv_card.add_widget(MDLabel(text="Polar to Rectangular:", theme_text_color="Secondary", font_style="Caption"))
        pol_box = MDBoxLayout(orientation='horizontal', spacing=dp(20), adaptive_height=True)
        self.pol_mag = MDTextField(hint_text="Magnitude |Z|", mode="rectangle")
        self.pol_ang = MDTextField(hint_text="Angle θ (deg)", mode="rectangle")
        pol_box.add_widget(self.pol_mag)
        pol_box.add_widget(self.pol_ang)
        conv_card.add_widget(pol_box)
        conv_card.add_widget(MDRaisedButton(text="CONVERT TO RECTANGULAR", size_hint_x=1, md_bg_color=(0.2, 0.6, 0.8, 1), on_release=self.polar_to_rect))

        # Result Label for Converter
        self.conv_result = MDLabel(text="Conversion result...", markup=True, halign="center", theme_text_color="Primary")
        conv_card.add_widget(self.conv_result)
        
        self.content.add_widget(conv_card)

    def build_operations_card(self):
        # --- CARD 2: MATHEMATICAL OPERATIONS ---
        math_card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(20), size_hint=(1, None), adaptive_height=True, radius=[15])
        math_card.add_widget(MDLabel(text="2. Arithmetic Operations (+, -, ×, ÷)", bold=True, font_style="H6"))
        math_card.add_widget(MDLabel(text="Enter values in Rectangular form (Real, Imaginary):", theme_text_color="Secondary", font_style="Caption"))

        # Z1 Input
        z1_box = MDBoxLayout(orientation='horizontal', spacing=dp(20), adaptive_height=True)
        self.z1_r = MDTextField(hint_text="Z1 Real", mode="rectangle")
        self.z1_i = MDTextField(hint_text="Z1 Imag (j)", mode="rectangle")
        z1_box.add_widget(self.z1_r)
        z1_box.add_widget(self.z1_i)
        math_card.add_widget(z1_box)

        # Z2 Input
        z2_box = MDBoxLayout(orientation='horizontal', spacing=dp(20), adaptive_height=True)
        self.z2_r = MDTextField(hint_text="Z2 Real", mode="rectangle")
        self.z2_i = MDTextField(hint_text="Z2 Imag (j)", mode="rectangle")
        z2_box.add_widget(self.z2_r)
        z2_box.add_widget(self.z2_i)
        math_card.add_widget(z2_box)

        # Buttons Row
        btn_box = MDBoxLayout(orientation='horizontal', spacing=dp(20), adaptive_height=True)
        btn_box.add_widget(MDRaisedButton(text="+", size_hint_x=1, on_release=lambda x: self.calculate_math('+')))
        btn_box.add_widget(MDRaisedButton(text="-", size_hint_x=1, on_release=lambda x: self.calculate_math('-')))
        btn_box.add_widget(MDRaisedButton(text="×", size_hint_x=1, on_release=lambda x: self.calculate_math('*')))
        btn_box.add_widget(MDRaisedButton(text="÷", size_hint_x=1, md_bg_color=(0.8, 0.2, 0.2, 1), on_release=lambda x: self.calculate_math('/')))
        math_card.add_widget(btn_box)

        # Result Label for Math
        self.math_result = MDLabel(text="Math result...", markup=True, halign="center", theme_text_color="Primary")
        math_card.add_widget(self.math_result)
        math_card.add_widget(MDFlatButton(
            text="RESET ALL FIELDS", size_hint_x=1, on_release=self.reset_all))
        self.content.add_widget(math_card)

    # --- LOGIC FUNCTIONS ---
    def rect_to_polar(self, instance):
        try:
            r = float(self.rect_r.text)
            x = float(self.rect_x.text)
            mag = math.hypot(r, x)
            ang = math.degrees(math.atan2(x, r))
            self.conv_result.text = f"[color=008800][b]Result:[/b] {mag:.3f} ∠ {ang:.2f}°[/color]"
        except ValueError:
            self.conv_result.text = "[color=ff0000]Error: Invalid numbers[/color]"

    def polar_to_rect(self, instance):
        try:
            mag = float(self.pol_mag.text)
            ang = math.radians(float(self.pol_ang.text))
            r = mag * math.cos(ang)
            x = mag * math.sin(ang)
            sign = "+" if x >= 0 else "-"
            self.conv_result.text = f"[color=008800][b]Result:[/b] {r:.3f} {sign} j{abs(x):.3f}[/color]"
        except ValueError:
            self.conv_result.text = "[color=ff0000]Error: Invalid numbers[/color]"

    def calculate_math(self, operator):
        try:
            z1 = complex(float(self.z1_r.text), float(self.z1_i.text))
            z2 = complex(float(self.z2_r.text), float(self.z2_i.text))
            
            if operator == '+': res = z1 + z2
            elif operator == '-': res = z1 - z2
            elif operator == '*': res = z1 * z2
            elif operator == '/': 
                if z2 == 0: raise ZeroDivisionError
                res = z1 / z2

            sign = "+" if res.imag >= 0 else "-"
            # Convert result to Polar as well for a complete answer
            mag = abs(res)
            ang = math.degrees(cmath.phase(res))
            
            final_text = f"[color=008800][b]Rectangular:[/b] {res.real:.3f} {sign} j{abs(res.imag):.3f}\n"
            final_text += f"[b]Polar:[/b] {mag:.3f} ∠ {ang:.2f}°[/color]"
            self.math_result.text = final_text

        except ValueError:
            self.math_result.text = "[color=ff0000]Error: Check your inputs[/color]"
        except ZeroDivisionError:
            self.math_result.text = "[color=ff0000]Error: Cannot divide by zero[/color]"

    def reset_all(self, instance):
        for field in [self.rect_r, self.rect_x, self.pol_mag, self.pol_ang,
                      self.z1_r, self.z1_i, self.z2_r, self.z2_i]:
            field.text = ""
        self.conv_result.text = "Conversion result..."
        self.math_result.text = "Math result..."

    def go_back(self):
        self.manager.current = 'complex_intro'

# ==========================================
# 6. Smart AC Circuit Screen (Interactive AI)
# ==========================================
# ==========================================
# 6. Smart AC Circuit Screen (Interactive AI)
# ==========================================
class Tab(MDFloatLayout, MDTabsBase):
    pass


class ACMainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SimpleBackground())
        
        # Streaming effect state
        self.typing_clock = None
        self.typing_text = ""
        self.typing_index = 0
        self.typing_target = None

        layout = MDBoxLayout(orientation="vertical")

        layout.add_widget(
            MDTopAppBar(
                title="Smart AC Circuit Analyzer",
                left_action_items=[["arrow-left", lambda x: self.go_home()]],
                elevation=2,
                md_bg_color=(0.12, 0.58, 0.95, 1),
            )
        )

        self.tabs = MDTabs(
            background_color=(0.12, 0.58, 0.95, 1),
            text_color_normal=(1, 1, 1, 0.7),
            text_color_active=(1, 1, 1, 1),
            indicator_color=(1, 1, 1, 1),
        )
        layout.add_widget(self.tabs)
        self.add_widget(layout)

        self._tab_state = {}

    def on_enter(self):
        if not self.tabs.get_slides():
            self.create_tabs()

    def create_tabs(self):
        intro_text = (
            "1) AC circuits use sinusoidal voltage and current waveforms.\n"
            "2) Frequency (f) controls how fast cycles repeat each second.\n"
            "3) Angular frequency is defined as ω = 2πf.\n"
            "4) Resistor opposition is pure resistance R.\n"
            "5) Inductor opposition is inductive reactance XL = ωL.\n"
            "6) Capacitor opposition is capacitive reactance XC = 1/(ωC).\n"
            "7) Impedance combines R and reactance in one complex value Z.\n"
            "8) Magnitude is |Z| = √(R² + (XL - XC)²).\n"
            "9) Phase angle is θ = arctan((XL - XC)/R).\n"
            "10) RMS values represent effective DC-equivalent levels.\n"
            "11) Vrms = Vmax/√2.\n"
            "12) Irms = Imax/√2.\n"
            "13) Average half-cycle approximations: Vavg = 0.637Vmax, Iavg = 0.637Imax.\n"
            "14) In series circuits, current is shared.\n"
            "15) In parallel circuits, voltage is shared.\n"
            "16) Resonance occurs when XL = XC.\n"
            "17) At resonance, phase angle becomes nearly zero.\n"
            "18) Quality factor and bandwidth measure selectivity.\n"
            "19) Real, reactive, and apparent powers define AC power flow.\n"
            "20) Smart solving means tracking missing variables before final calculation."
        )
        self.add_intro_tab("Introduction", intro_text)

        self.add_engineering_tab(
            title="Series",
            short_intro="Series AC circuit: same current through all elements, source voltage divides across elements.",
            include_resonance=False,
        )
        self.add_engineering_tab(
            title="Parallel",
            short_intro="Parallel AC circuit: same voltage across all branches, source current divides between branches.",
            include_resonance=False,
        )
        self.add_engineering_tab(
            title="Res-Series",
            short_intro="Series resonance: XL = XC, impedance minimum, source current maximum, phase near zero.",
            include_resonance=True,
        )
        self.add_engineering_tab(
            title="Res-Parallel",
            short_intro="Parallel resonance: branch reactive currents cancel, input impedance maximum, phase near zero.",
            include_resonance=True,
        )

    def add_intro_tab(self, title, info_text):
        tab = Tab(title=title)
        root = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))

        card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(1, 1, 1, 0.97),
            elevation=1,
        )
        card.add_widget(
            MDLabel(
                text="AC CIRCUITS INTRODUCTION",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        card.add_widget(
            MDBoxLayout(
                size_hint_y=None,
                height=dp(2),
                md_bg_color=(0.12, 0.58, 0.95, 0.35),
            )
        )
        card.add_widget(
            MDLabel(
                text=info_text,
                adaptive_height=True,
                theme_text_color="Secondary",
            )
        )

        root.add_widget(card)
        tab.add_widget(root)
        self.tabs.add_widget(tab)

    def add_engineering_tab(self, title, short_intro, include_resonance):
        tab = Tab(title=title)
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        formulas_text = self.get_formulas_text(include_resonance=include_resonance)

        explain_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(1, 1, 1, 0.97),
            elevation=1,
            adaptive_height=True,
        )
        explain_card.add_widget(
            MDLabel(
                text=f"{title.upper()} CIRCUIT GUIDE",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        explain_card.add_widget(
            MDBoxLayout(
                size_hint_y=None,
                height=dp(2),
                md_bg_color=(0.12, 0.58, 0.95, 0.35),
            )
        )
        explain_card.add_widget(
            MDLabel(
                text=f"{short_intro}\n\n{formulas_text}",
                adaptive_height=True,
                theme_text_color="Secondary",
            )
        )
        content.add_widget(explain_card)

        calc_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        calc_card.add_widget(
            MDLabel(
                text=f"{title.upper()} SMART CALCULATOR",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        calc_card.add_widget(
            MDLabel(
                text="Enter target variable (example: XL, XC, ZMAG, THETA, VS, IS, VRMS, IRMS, PREAL, PAPP).",
                adaptive_height=True,
                theme_text_color="Secondary",
            )
        )

        target_field = MDTextField(hint_text="Target variable", mode="rectangle")
        calc_card.add_widget(target_field)

        generate_btn = MDRaisedButton(
            text="Generate Required Inputs",
            size_hint_x=1,
            md_bg_color=(0.12, 0.58, 0.95, 1),
        )
        calc_card.add_widget(generate_btn)

        dynamic_box = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True)
        calc_card.add_widget(dynamic_box)

        result_label = MDLabel(
            text="Algorithm result will appear here.",
            adaptive_height=True,
            markup=True,
            theme_text_color="Primary",
        )
        calc_card.add_widget(result_label)

        state = {
            "mode": title,
            "target_field": target_field,
            "dynamic_box": dynamic_box,
            "result_label": result_label,
            "fields": {},
            "include_resonance": include_resonance,
        }
        self._tab_state[title] = state

        generate_btn.bind(on_release=lambda x, t=title: self.generate_dynamic_inputs(t))

        content.add_widget(calc_card)
        scroll.add_widget(content)
        tab.add_widget(scroll)
        self.tabs.add_widget(tab)

    def get_formulas_text(self, include_resonance=False):
        base = (
            "Core formulas:\n"
            "• f = 1/T\n"
            "• ω = 2πf\n"
            "• XL = ωL\n"
            "• XC = 1/(ωC)\n"
            "• Z = R + j(XL - XC)\n"
            "• |Z| = √(R² + (XL - XC)²)\n"
            "• θ = arctan((XL - XC)/R)\n"
            "• Vs = Is × |Z|\n"
            "• Is = Vs/|Z|\n"
            "• Vrms = Vmax/√2\n"
            "• Irms = Imax/√2\n"
            "• Vavg = 0.637Vmax\n"
            "• Iavg = 0.637Imax\n"
            "• Vt = V1 + V2 + ...\n"
            "• Zt = Z1 + Z2 + ... (series)\n"
            "• 1/Zt = 1/Z1 + 1/Z2 + ... (parallel)\n"
            "• Pins = Vs × Is\n"
            "• Preal = Vrms × Irms × cos(θ)\n"
            "• Papp = Vrms × Irms\n"
        )
        if include_resonance:
            base += (
                "Resonance formulas:\n"
                "• fr = 1/(2π√(LC))\n"
                "• ωr = 1/√(LC)\n"
                "• QF(series) = (1/R)√(L/C)\n"
                "• QF(parallel) = R√(C/L)\n"
                "• Bandwidth = fr/QF\n"
            )
        return base

    def get_required_inputs(self, target):
        # Common map for requested variable tracking
        req = {
            "F": ["T"],
            "W": ["F"],
            "XL": ["L"],  # Will add frequency option in UI
            "XC": ["C"],  # Will add frequency option in UI
            "ZMAG": ["R", "XL", "XC"],
            "THETA": ["R", "XL", "XC"],
            "VS": ["IS", "ZMAG"],
            "IS": ["VS", "ZMAG"],
            "VRMS": ["VMAX"],
            "IRMS": ["IMAX"],
            "VAVG": ["VMAX"],
            "IAVG": ["IMAX"],
            "PINS": ["VS", "IS"],
            "PREAL": ["VRMS", "IRMS", "THETA"],
            "PAPP": ["VRMS", "IRMS"],
            "FR": ["L", "C"],
            "WR": ["L", "C"],
            "QF_SERIES": ["R", "L", "C"],
            "QF_PARALLEL": ["R", "L", "C"],
            "BANDWIDTH": ["FR", "QF"],
            "R": ["VS", "IS"],
            "L": ["XL"],  # Will add frequency option in UI
            "C": ["XC"],  # Will add frequency option in UI
            "Z": ["R", "XL", "XC"],
        }
        return req.get(target, [])

    def generate_dynamic_inputs(self, tab_title):
        state = self._tab_state[tab_title]
        target = state["target_field"].text.strip().upper()
        box = state["dynamic_box"]
        box.clear_widgets()
        state["fields"] = {}

        if not target:
            state["result_label"].text = "[color=ff0000]Please enter a target variable first.[/color]"
            return

        needed = self.get_required_inputs(target)
        if not needed:
            state["result_label"].text = (
                "[color=ff0000]Unknown target variable. "
                "Try: F, W, XL, XC, ZMAG, THETA, VS, IS, VRMS, IRMS, VAVG, IAVG, PINS, PREAL, PAPP, FR, WR, QF_SERIES, QF_PARALLEL, BANDWIDTH, R, L, C, Z.[/color]"
            )
            return

        box.add_widget(MDLabel(text=f"Required inputs for {target}:", adaptive_height=True, bold=True))
        
        # Add frequency option for frequency-dependent calculations
        freq_dependent = ["XL", "XC", "L", "C"]
        if target in freq_dependent:
            freq_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
            freq_box.add_widget(MDLabel(text="Frequency input:", size_hint_x=0.4, theme_text_color="Primary"))
            state["freq_button"] = MDRaisedButton(
                text="f (Hz)", size_hint_x=0.6, size_hint_y=None,
                height=dp(48), on_release=lambda x, t=tab_title: self.open_freq_menu(x, t),
            )
            freq_box.add_widget(state["freq_button"])
            box.add_widget(freq_box)
            state["freq_type"] = "f"  # Default to f
            
            # Add frequency input field
            freq_field = MDTextField(hint_text="Frequency value", mode="rectangle")
            state["freq_field"] = freq_field
            box.add_widget(freq_field)
        
        for key in needed:
            field = MDTextField(hint_text=f"Value for {key}", mode="rectangle")
            state["fields"][key] = field
            box.add_widget(field)

        solve_btn = MDRaisedButton(
            text="Run Smart Solve",
            size_hint_x=1,
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=lambda x, t=tab_title: self.run_smart_solver(t),
        )
        box.add_widget(solve_btn)
        state["result_label"].text = "Inputs generated. Fill values and run solver."

    def run_smart_solver(self, tab_title):
        state = self._tab_state[tab_title]
        target = state["target_field"].text.strip().upper()
        fields = state["fields"]

        values = {}
        missing = []

        for k, f in fields.items():
            txt = f.text.strip()
            if txt == "":
                missing.append(k)
            else:
                try:
                    values[k] = float(txt)
                except ValueError:
                    state["result_label"].text = "[color=ff0000]Error: numbers only.[/color]"
                    return

        # Handle frequency input for frequency-dependent calculations
        freq_dependent = ["XL", "XC", "L", "C"]
        if target in freq_dependent:
            freq_txt = state["freq_field"].text.strip()
            if freq_txt == "":
                state["result_label"].text = "[color=ff0000]Error: Please enter frequency value.[/color]"
                return
            try:
                freq_val = float(freq_txt)
                freq_type = state["freq_type"]
                if freq_type == "f":
                    # Convert f to ω
                    values["W"] = 2 * math.pi * freq_val
                    values["F"] = freq_val
                else:
                    # Use ω directly
                    values["W"] = freq_val
                    values["F"] = freq_val / (2 * math.pi)
            except ValueError:
                state["result_label"].text = "[color=ff0000]Error: Invalid frequency value.[/color]"
                return

        if missing:
            steps = self.get_missing_steps(target, missing)
            report = "[color=ff8800][b]DATA GAP DETECTED[/b][/color]\n"
            report += f"Target: [b]{target}[/b]\n"
            report += f"Missing: {', '.join(missing)}\n\n"
            report += "[b]Step-by-step plan:[/b]\n"
            for s in steps:
                report += f"• {s}\n"
            state["result_label"].text = report
            return

        try:
            result_text = self.calculate_target(target, values)
            state["result_label"].text = f"[color=008800][b]SUCCESS[/b][/color]\n{result_text}"
        except ZeroDivisionError:
            state["result_label"].text = "[color=ff0000]Error: division by zero.[/color]"
        except Exception:
            state["result_label"].text = "[color=ff0000]Error: unable to complete calculation.[/color]"

    def calculate_target(self, target, v):
        if target == "F":
            res = 1 / v["T"]
            return f"f = 1/T = {res:.2f} Hz"
        if target == "W":
            res = 2 * math.pi * v["F"]
            return f"ω = 2πf = {res:.2f} rad/s"
        if target == "XL":
            res = v["W"] * v["L"]
            return f"XL = ωL = {res:.2f} Ω"
        if target == "XC":
            res = 1 / (v["W"] * v["C"])
            return f"XC = 1/(ωC) = {res:.2f} Ω"
        if target == "ZMAG":
            res = math.sqrt(v["R"] ** 2 + (v["XL"] - v["XC"]) ** 2)
            return f"|Z| = √(R² + (XL-XC)²) = {res:.2f} Ω"
        if target == "THETA":
            res = math.degrees(math.atan((v["XL"] - v["XC"]) / v["R"]))
            return f"θ = arctan((XL-XC)/R) = {res:.2f} deg"
        if target == "VS":
            res = v["IS"] * v["ZMAG"]
            return f"Vs = Is|Z| = {res:.2f} V"
        if target == "IS":
            res = v["VS"] / v["ZMAG"]
            return f"Is = Vs/|Z| = {res:.2f} A"
        if target == "VRMS":
            res = v["VMAX"] / math.sqrt(2)
            return f"Vrms = Vmax/√2 = {res:.2f} V"
        if target == "IRMS":
            res = v["IMAX"] / math.sqrt(2)
            return f"Irms = Imax/√2 = {res:.2f} A"
        if target == "VAVG":
            res = 0.637 * v["VMAX"]
            return f"Vavg = 0.637Vmax = {res:.2f} V"
        if target == "IAVG":
            res = 0.637 * v["IMAX"]
            return f"Iavg = 0.637Imax = {res:.2f} A"
        if target == "PINS":
            res = v["VS"] * v["IS"]
            return f"Pins = VsIs = {res:.2f} W"
        if target == "PREAL":
            th = math.radians(v["THETA"])
            res = v["VRMS"] * v["IRMS"] * math.cos(th)
            return f"Preal = VrmsIrmscosθ = {res:.2f} W"
        if target == "PAPP":
            res = v["VRMS"] * v["IRMS"]
            return f"Papp = VrmsIrms = {res:.2f} VA"
        if target == "FR":
            res = 1 / (2 * math.pi * math.sqrt(v["L"] * v["C"]))
            return f"fr = 1/(2π√LC) = {res:.2f} Hz"
        if target == "WR":
            res = 1 / math.sqrt(v["L"] * v["C"])
            return f"ωr = 1/√(LC) = {res:.2f} rad/s"
        if target == "QF_SERIES":
            res = (1 / v["R"]) * math.sqrt(v["L"] / v["C"])
            return f"QF(series) = (1/R)√(L/C) = {res:.2f}"
        if target == "QF_PARALLEL":
            res = v["R"] * math.sqrt(v["C"] / v["L"])
            return f"QF(parallel) = R√(C/L) = {res:.2f}"
        if target == "BANDWIDTH":
            res = v["FR"] / v["QF"]
            return f"Bandwidth = fr/QF = {res:.2f} Hz"
        if target == "R":
            res = v["VS"] / v["IS"]
            return f"R = Vs/Is = {res:.2f} Ω"
        if target == "L":
            res = v["XL"] / v["W"]
            freq_note = f" (using ω = {v['W']:.2f} rad/s, f = {v['F']:.2f} Hz)" if "F" in v else ""
            return f"L = XL/ω = {res:.2f} H{freq_note}"
        if target == "C":
            res = 1 / (v["XC"] * v["W"])
            freq_note = f" (using ω = {v['W']:.2f} rad/s, f = {v['F']:.2f} Hz)" if "F" in v else ""
            return f"C = 1/(XCω) = {res:.2f} F{freq_note}"
        if target == "Z":
            z_real = v["R"]
            z_imag = v["XL"] - v["XC"]
            z_complex = complex(z_real, z_imag)
            z_mag = abs(z_complex)
            z_phase = math.degrees(cmath.phase(z_complex))
            sign = "+" if z_imag >= 0 else "-"
            return f"Z = R + j(XL-XC) = {z_real:.2f} {sign} j{abs(z_imag):.2f} Ω\n|Z| = {z_mag:.2f} Ω, θ = {z_phase:.2f}°"

        return "Target not supported."

    def get_missing_steps(self, target, missing):
        plan = []
        # Generic guide
        for m in missing:
            if m == "T":
                plan.append("Find period T from waveform timing, then use f = 1/T.")
            elif m == "F":
                plan.append("Find frequency f directly or compute from T using f = 1/T.")
            elif m == "W":
                plan.append("Compute ω from frequency using ω = 2πf.")
            elif m == "L":
                plan.append("Get inductance L from component value or L = XL/ω.")
            elif m == "C":
                plan.append("Get capacitance C from component value or C = 1/(ωXC).")
            elif m == "R":
                plan.append("Measure resistance R by meter or infer using R = Vs/Is in resistive condition.")
            elif m == "XL":
                plan.append("Compute XL using XL = ωL after finding ω and L.")
            elif m == "XC":
                plan.append("Compute XC using XC = 1/(ωC) after finding ω and C.")
            elif m == "ZMAG":
                plan.append("Compute |Z| from R, XL, XC using |Z| = √(R² + (XL-XC)²).")
            elif m == "THETA":
                plan.append("Compute θ from θ = arctan((XL-XC)/R).")
            elif m == "VMAX":
                plan.append("Find Vmax from source specification or Vmax = √2 × Vrms.")
            elif m == "IMAX":
                plan.append("Find Imax from current waveform or Imax = √2 × Irms.")
            elif m == "VS":
                plan.append("Use Vs = Is × |Z| if Is and |Z| are known.")
            elif m == "IS":
                plan.append("Use Is = Vs / |Z| if Vs and |Z| are known.")
            elif m == "VRMS":
                plan.append("Compute Vrms from Vmax using Vrms = Vmax/√2.")
            elif m == "IRMS":
                plan.append("Compute Irms from Imax using Irms = Imax/√2.")
            elif m == "FR":
                plan.append("Compute resonance frequency fr = 1/(2π√LC).")
            elif m == "QF":
                plan.append("Compute quality factor QF from resonance equations before bandwidth.")
            else:
                plan.append(f"Find {m} from known circuit data, then continue.")

        # Target-specific final step
        plan.append(f"After all missing values are available, calculate {target} directly using its formula.")
        return plan

    def open_freq_menu(self, instance, tab_title):
        state = self._tab_state[tab_title]
        freq_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "f (Hz)",
                "on_release": lambda x="f", t=tab_title: self.set_freq_type(x, t),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "ω (rad/s)",
                "on_release": lambda x="w", t=tab_title: self.set_freq_type(x, t),
            },
        ]
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(
            caller=instance,
            items=freq_items,
            width_mult=4,
        )
        self.menu.open()

    def set_freq_type(self, freq_type, tab_title):
        state = self._tab_state[tab_title]
        state["freq_type"] = freq_type
        if freq_type == "f":
            state["freq_button"].text = "f (Hz)"
            state["freq_field"].hint_text = "Frequency (Hz)"
        else:
            state["freq_button"].text = "ω (rad/s)"
            state["freq_field"].hint_text = "Angular frequency (rad/s)"
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()

    def go_home(self):
        self.manager.current = "home"

    def start_typing_animation(self, target_label, text):
        """Start streaming/typed effect — tag-safe, never cuts inside markup."""
        if self.typing_clock:
            self.typing_clock.cancel()
        self.typing_chunks = _safe_stream_chunks(text)
        self.typing_chunk_idx = 0
        self.typing_target = target_label
        target_label.text = ""
        self.typing_clock = Clock.schedule_interval(self.type_next_character, 0.018)

    def type_next_character(self, dt):
        if self.typing_chunk_idx < len(self.typing_chunks):
            self.typing_chunk_idx += 1
            self.typing_target.text = "".join(
                self.typing_chunks[:self.typing_chunk_idx])
        else:
            if self.typing_clock:
                self.typing_clock.cancel()
                self.typing_clock = None


# ==========================================
# 7. Maximum Power Transfer Screen
# ==========================================

# ==========================================
# 7. Maximum Power Transfer Screen  (REWRITTEN)
# ==========================================
class MPTMainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SimpleBackground())

        # Streaming state
        self.typing_clock  = None
        self.typing_text   = ""
        self.typing_index  = 0
        self.typing_target = None

        # Component rows storage
        self.component_rows = []
        self.menu = None

        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(
            MDTopAppBar(
                title="Maximum Power Transfer",
                left_action_items=[["arrow-left", lambda x: self.go_home()]],
                elevation=2,
                md_bg_color=(0.12, 0.58, 0.95, 1),
            )
        )

        # ── Mode selector card (always visible, outside scroll) ───
        mode_card = MDCard(
            orientation="vertical", padding=dp(12), spacing=dp(8),
            radius=[16], md_bg_color=(0.95, 0.97, 1, 1),
            elevation=1, adaptive_height=True,
        )
        mode_card.add_widget(MDLabel(
            text="SELECT INPUT MODE", bold=True, font_style="H6",
            adaptive_height=True, theme_text_color="Primary",
        ))
        mode_row = MDBoxLayout(orientation="horizontal", spacing=dp(10),
                               size_hint_y=None, height=dp(50))
        self.mode_button = MDRaisedButton(
            text="Direct Input", size_hint_x=0.5,
            size_hint_y=None, height=dp(44),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.open_mode_menu,
        )
        mode_row.add_widget(self.mode_button)
        mode_card.add_widget(mode_row)
        layout.add_widget(mode_card)

        # ── Main scrollable area ───────────────────────────────────
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.content = MDBoxLayout(
            orientation="vertical", padding=dp(14),
            spacing=dp(14), size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        # ── CARD A: Direct input ───────────────────────────────────
        self.direct_card = MDCard(
            orientation="vertical", padding=dp(15), spacing=dp(12),
            radius=[16], md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1, adaptive_height=True,
        )
        self.direct_card.add_widget(MDLabel(
            text="DIRECT INPUT MODE", bold=True, font_style="H6",
            adaptive_height=True, theme_text_color="Primary",
        ))
        for label, attr_mag, attr_ang, hint_m, hint_a in [
            ("V_th (V):", "mpt_vth_mag", "mpt_vth_ang", "Magnitude", "Angle (°)"),
        ]:
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                              size_hint_y=None, height=dp(56))
            row.add_widget(MDLabel(text=label, size_hint_x=0.25,
                                   theme_text_color="Primary"))
            f_mag = MDTextField(hint_text=hint_m, mode="rectangle", size_hint_x=0.375)
            f_ang = MDTextField(hint_text=hint_a, mode="rectangle", size_hint_x=0.375)
            setattr(self, attr_mag, f_mag)
            setattr(self, attr_ang, f_ang)
            row.add_widget(f_mag)
            row.add_widget(f_ang)
            self.direct_card.add_widget(row)

        for label, attr, hint in [
            ("R_th (Ω):", "mpt_rth", "Resistance"),
            ("X_th (Ω):", "mpt_xth", "Reactance (+/-)"),
        ]:
            row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                              size_hint_y=None, height=dp(56))
            row.add_widget(MDLabel(text=label, size_hint_x=0.3,
                                   theme_text_color="Primary"))
            field = MDTextField(hint_text=hint, mode="rectangle", size_hint_x=0.7)
            setattr(self, attr, field)
            row.add_widget(field)
            self.direct_card.add_widget(row)

        self.direct_card.add_widget(MDRaisedButton(
            text="CALCULATE MPT", size_hint_x=1,
            size_hint_y=None, height=dp(46),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.calculate_mpt_direct,
        ))
        self.content.add_widget(self.direct_card)

        # ── CARD B: Component count (always visible in component mode) ─
        self.count_card = MDCard(
            orientation="vertical", padding=dp(15), spacing=dp(12),
            radius=[16], md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1, adaptive_height=True,
            opacity=0, size_hint_y=None, height=0, disabled=True,
        )
        self.count_card.add_widget(MDLabel(
            text="STEP 1 — Number of Impedances", bold=True, font_style="H6",
            adaptive_height=True, theme_text_color="Primary",
        ))
        count_row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                size_hint_y=None, height=dp(56))
        count_row.add_widget(MDLabel(text="Count:", size_hint_x=0.3,
                                     theme_text_color="Primary"))
        self.component_count = MDTextField(
            hint_text="Number of Z (1–10)", mode="rectangle",
            input_filter="int", size_hint_x=0.7)
        count_row.add_widget(self.component_count)
        self.count_card.add_widget(count_row)
        self.count_card.add_widget(MDRaisedButton(
            text="GENERATE Z INPUTS", size_hint_x=1,
            size_hint_y=None, height=dp(46),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.generate_component_inputs,
        ))
        self.content.add_widget(self.count_card)

        # ── CARD C: Z values + Vs + expression (added dynamically) ──
        self.values_card = MDCard(
            orientation="vertical", padding=dp(15), spacing=dp(12),
            radius=[16], md_bg_color=(0.95, 0.98, 1, 1),
            elevation=1, adaptive_height=True,
            opacity=0, size_hint_y=None, height=0, disabled=True,
        )
        self.values_card.add_widget(MDLabel(
            text="STEP 2 — Enter Values & Circuit Expression",
            bold=True, font_style="H6",
            adaptive_height=True, theme_text_color="Primary",
        ))

        # Source voltage row
        vs_title = MDLabel(text="Source Voltage Vs:", bold=True,
                           adaptive_height=True, theme_text_color="Primary")
        self.values_card.add_widget(vs_title)
        vs_row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                             size_hint_y=None, height=dp(56))
        vs_row.add_widget(MDLabel(text="Vs:", size_hint_x=0.15,
                                   theme_text_color="Primary"))
        self.vs_mag = MDTextField(hint_text="Magnitude (V)", mode="rectangle",
                                  size_hint_x=0.425)
        self.vs_ang = MDTextField(hint_text="Angle (°)", mode="rectangle",
                                  size_hint_x=0.425)
        vs_row.add_widget(self.vs_mag)
        vs_row.add_widget(self.vs_ang)
        self.values_card.add_widget(vs_row)

        # Z inputs box (filled dynamically)
        self.z_inputs_box = MDBoxLayout(orientation="vertical", spacing=dp(8),
                                         adaptive_height=True)
        self.values_card.add_widget(self.z_inputs_box)

        # ── Optional: enter Z as L/C components ──────────────────
        self.values_card.add_widget(MDLabel(
            text="Optional: Convert L/C to Z (enter frequency first)",
            bold=True, adaptive_height=True, theme_text_color="Primary",
        ))
        freq_row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                               size_hint_y=None, height=dp(56))
        freq_row.add_widget(MDLabel(text="f (Hz):", size_hint_x=0.25,
                                    theme_text_color="Primary"))
        self.mpt_freq = MDTextField(hint_text="e.g. 50", mode="rectangle",
                                    size_hint_x=0.75, text="50")
        freq_row.add_widget(self.mpt_freq)
        self.values_card.add_widget(freq_row)

        self.values_card.add_widget(MDLabel(
            text="For each Z above, you may enter R+L+C instead of magnitude/angle:",
            adaptive_height=True, theme_text_color="Secondary", font_style="Caption",
        ))
        self.lc_inputs_box = MDBoxLayout(orientation="vertical", spacing=dp(6),
                                          adaptive_height=True)
        self.values_card.add_widget(self.lc_inputs_box)
        self.values_card.add_widget(MDRaisedButton(
            text="CONVERT L/C TO Z VALUES", size_hint_x=1,
            size_hint_y=None, height=dp(42),
            md_bg_color=(0.3, 0.6, 0.4, 1),
            on_release=self.convert_lc_to_z,
        ))

        # Circuit expression string
        self.values_card.add_widget(MDLabel(
            text="Circuit Connection String:",
            bold=True, adaptive_height=True, theme_text_color="Primary",
        ))
        self.values_card.add_widget(MDLabel(
            text='Use + for series, || for parallel.\nExamples: "Vs + Z1 || Z2"  or  "(Z1 + Z2) || Z3"',
            adaptive_height=True, theme_text_color="Secondary",
            font_style="Caption",
        ))
        self.expr_field = MDTextField(
            hint_text="e.g.  Vs + Z1 || Z2 + Z3",
            mode="rectangle",
        )
        self.values_card.add_widget(self.expr_field)
        self.values_card.add_widget(MDRaisedButton(
            text="CALCULATE FROM EXPRESSION", size_hint_x=1,
            size_hint_y=None, height=dp(46),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.calculate_mpt_expression,
        ))
        self.content.add_widget(self.values_card)

        # ── Result card ───────────────────────────────────────────
        result_card = MDCard(
            orientation="vertical", padding=dp(15), spacing=dp(12),
            radius=[16], md_bg_color=(1, 1, 1, 0.95),
            elevation=1, adaptive_height=True,
        )
        result_card.add_widget(MDLabel(
            text="RESULTS", bold=True, font_style="H6",
            adaptive_height=True, theme_text_color="Primary",
        ))
        self.mpt_result = MDLabel(
            text="Results will appear here with step-by-step logic.",
            adaptive_height=True, markup=True, theme_text_color="Secondary",
        )
        result_card.add_widget(self.mpt_result)
        self.content.add_widget(result_card)

        self.scroll.add_widget(self.content)
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    # ── Mode switching ─────────────────────────────────────────────
    def open_mode_menu(self, instance):
        items = [
            {"viewclass": "OneLineListItem", "text": "Direct Input",
             "on_release": lambda: self.set_mode("direct")},
            {"viewclass": "OneLineListItem", "text": "Component List",
             "on_release": lambda: self.set_mode("component")},
        ]
        if self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(caller=instance, items=items, width_mult=4)
        self.menu.open()

    def set_mode(self, mode):
        if mode == "direct":
            self.mode_button.text = "Direct Input"
            self._show_card(self.direct_card)
            self._hide_card(self.count_card)
            self._hide_card(self.values_card)
        else:
            self.mode_button.text = "Component List"
            self._hide_card(self.direct_card)
            self._show_card(self.count_card)
            self._hide_card(self.values_card)  # shown after Generate
        if self.menu:
            self.menu.dismiss()

    def _hide_card(self, card):
        card.opacity = 0
        card.size_hint_y = None
        card.height = 0
        card.disabled = True

    def _show_card(self, card):
        card.opacity = 1
        card.size_hint_y = None
        card.height = card.minimum_height if hasattr(card, 'minimum_height') else dp(200)
        card.disabled = False
        # Let adaptive_height recalculate
        card.size_hint_y = None
        card.bind(minimum_height=card.setter('height'))

    # ── Generate Z inputs (Task 1 fix: count card stays, values card appears below) ─
    def generate_component_inputs(self, instance):
        try:
            count = int(self.component_count.text.strip())
            if not (1 <= count <= 10):
                self.mpt_result.text = "[color=ff0000]Enter 1–10.[/color]"
                return

            self.z_inputs_box.clear_widgets()
            self.component_rows = []

            for i in range(count):
                self.z_inputs_box.add_widget(MDLabel(
                    text=f"Z{i+1}:", bold=True, adaptive_height=True,
                    theme_text_color="Primary",
                ))
                row = MDBoxLayout(orientation="horizontal", spacing=dp(8),
                                  size_hint_y=None, height=dp(56))
                f_mag = MDTextField(hint_text=f"Z{i+1} Magnitude (Ω)",
                                    mode="rectangle", size_hint_x=0.5)
                f_ang = MDTextField(hint_text=f"Z{i+1} Angle (°)",
                                    mode="rectangle", size_hint_x=0.5)
                row.add_widget(f_mag)
                row.add_widget(f_ang)
                self.z_inputs_box.add_widget(row)
                self.component_rows.append({"mag": f_mag, "ang": f_ang})

            # Show values card below count card
            self._show_card(self.values_card)

            # Set default expression as hint
            z_labels = " + ".join([f"Z{i+1}" for i in range(count)])
            self.expr_field.hint_text = f"e.g.  Vs + {z_labels}"

        except ValueError:
            self.mpt_result.text = "[color=ff0000]Enter a valid number.[/color]"

    # ── Expression parser ─────────────────────────────────────────
    def _parse_expression(self, expr_str, z_values, vs):
        """
        Parse a circuit expression string and return (Zeq, steps_list).
        Operators: + (series), || (parallel), parentheses.
        Tokens (case-insensitive):
          Z1, Z2, ...  → replaced with their complex impedance values
          VS, V1, V2, V  → replaced with the source voltage complex value
          All voltage tokens are treated as the same Vs input.
        """
        import re

        steps = []
        expr  = expr_str.strip().upper()

        # Replace Zn tokens with complex impedance values
        for i, z in enumerate(z_values):
            expr = expr.replace(f"Z{i+1}", f"({z.real}+{z.imag}j)")

        # Replace any voltage token (VS, V1, V2, V, V_S, V_1 etc) with Vs complex value
        # Match V followed by optional digit(s) or S — whole word only
        expr = re.sub(r'\bV(?:S|\d*)\b', f"({vs.real}+{vs.imag}j)", expr)

        # Clean up any leftover leading/trailing + from removed tokens
        expr = re.sub(r'^\s*\+\s*', '', expr)
        expr = re.sub(r'\s*\+\s*$', '', expr)

        steps.append("  Substituted all V and Z tokens with complex values.")
        steps.append(f"  Evaluated expression: {expr_str.upper()}")

        def parallel(a, b):
            if a + b == 0:
                raise ZeroDivisionError("Parallel impedance: Z1+Z2 = 0")
            return (a * b) / (a + b)

        try:
            zeq = _circuit_eval(expr, parallel, steps)
            return zeq, steps
        except Exception as ex:
            raise ValueError(f"Expression parse error: {ex}")

    # ── Convert L/C inputs to Z magnitude/angle fields ───────────
    def convert_lc_to_z(self, instance):
        try:
            freq = float(self.mpt_freq.text.strip() or "50")
            w = 2 * math.pi * freq
            converted = 0
            for i, (lc, zrow) in enumerate(zip(self.lc_rows, self.component_rows)):
                r_txt = lc["r"].text.strip()
                l_txt = lc["l"].text.strip()
                c_txt = lc["c"].text.strip()
                if not any([r_txt, l_txt, c_txt]):
                    continue  # skip empty rows
                r = float(r_txt) if r_txt else 0.0
                xl = w * float(l_txt) if l_txt else 0.0
                xc = 1.0 / (w * float(c_txt)) if c_txt else 0.0
                z = complex(r, xl - xc)
                mag = abs(z)
                ang = math.degrees(cmath.phase(z))
                zrow["mag"].text = "%.4f" % mag
                zrow["ang"].text = "%.4f" % ang
                converted += 1
            if converted:
                self.mpt_result.text = (
                    "[color=008800]Converted %d component(s) to Z values. "
                    "Check the Z fields above.[/color]" % converted)
            else:
                self.mpt_result.text = "[color=ff8800]No L/C values entered to convert.[/color]"
        except ValueError as e:
            self.mpt_result.text = "[color=ff0000]Error: %s[/color]" % str(e)

    # -- Main calculation: VDR + Pmax = |Vth|^2 / 4Rth --
    def calculate_mpt_expression(self, instance):
        try:
            vs_mag = float(self.vs_mag.text.strip())
            vs_ang = math.radians(float(self.vs_ang.text.strip()))
            vs     = cmath.rect(vs_mag, vs_ang)

            z_values = []
            for row in self.component_rows:
                mag = float(row["mag"].text.strip())
                ang = math.radians(float(row["ang"].text.strip()))
                z_values.append(cmath.rect(mag, ang))

            # ── Validate all Z inputs are filled ─────────────────
            for idx_v, row in enumerate(self.component_rows):
                if not row["mag"].text.strip():
                    self.mpt_result.text = "[color=ff0000]Error: Z%d magnitude is empty.[/color]" % (idx_v+1)
                    return
                if not row["ang"].text.strip():
                    self.mpt_result.text = "[color=ff0000]Error: Z%d angle is empty.[/color]" % (idx_v+1)
                    return

            expr_str = self.expr_field.text.strip().upper()  # case-insensitive
            if not expr_str:
                self.mpt_result.text = "[color=ff0000]Enter a circuit expression.[/color]"
                return

            # Parse full expression for Zeq
            zeq, parse_steps = self._parse_expression(expr_str, z_values, vs)

            import re as _re
            z_tokens = _re.findall(r'Z\d+', expr_str)

            if len(z_tokens) >= 2:
                # Load = last Z token; Zth = rest of network
                load_idx       = int(z_tokens[-1][1:]) - 1
                z_load         = z_values[load_idx]
                last_tok       = z_tokens[-1]
                zth_expr       = expr_str
                idx_last       = zth_expr.rfind(last_tok)
                zth_expr       = zth_expr[:idx_last] + "(0+0j)" + zth_expr[idx_last+len(last_tok):]
                zth_expr       = _re.sub(r'\|\|\s*\(0\+0j\)', '', zth_expr)
                zth_expr       = _re.sub(r'\(0\+0j\)\s*\|\|', '', zth_expr)
                zth_expr       = _re.sub(r'\+\s*\(0\+0j\)', '', zth_expr)
                zth_expr       = _re.sub(r'\(0\+0j\)\s*\+', '', zth_expr)
                zth_expr       = _re.sub(r'V(?:S|\d*)\s*\+?\s*', '', zth_expr).strip()
                try:
                    zth, zth_steps = self._parse_expression(zth_expr, z_values, vs)
                except Exception:
                    zth = zeq

                z_divider_total = zth + z_load
                if abs(z_divider_total) < 1e-12:
                    raise ZeroDivisionError("Voltage divider total impedance = 0")
                vth = vs * (z_load / z_divider_total)

                vdr_line1 = "  VDR: V_th = Vs x Z_load / (Z_th + Z_load)"
                vdr_line2 = ("  V_th = %.2f ang %.2f deg x (%.2f ang %.2f deg)"
                             " / (%.2f ang %.2f deg)" % (
                    vs_mag, math.degrees(vs_ang),
                    abs(z_load), math.degrees(cmath.phase(z_load)),
                    abs(z_divider_total), math.degrees(cmath.phase(z_divider_total))))
                vdr_line3 = "  V_th = %.2f ang %.2f deg V" % (
                    abs(vth), math.degrees(cmath.phase(vth)))
            else:
                zth    = zeq
                z_load = zeq
                vth    = vs
                vdr_line1 = "  Single element - V_th = Vs (no divider)"
                vdr_line2 = ""
                vdr_line3 = ""

            rth    = zth.real
            xth    = zth.imag
            zl_opt = zth.conjugate()
            p_max  = (abs(vth) ** 2) / (4 * rth) if rth > 0 else 0.0
            circuit_type = "Inductive" if xth > 0 else ("Capacitive" if xth < 0 else "Resistive")

            lines = []
            lines.append("[color=008800][b]STEP-BY-STEP MPT ANALYSIS[/b][/color]\n")
            lines.append("\n[b]Step 1:[/b] Input Parameters:\n")
            lines.append("  Vs = %.2f ang %.2f deg V\n" % (vs_mag, math.degrees(vs_ang)))
            for idx2, z in enumerate(z_values):
                lines.append("  Z%d = %.2f ang %.2f deg = %.2f%+.2fj ohm\n" % (
                    idx2+1, abs(z), math.degrees(cmath.phase(z)), z.real, z.imag))
            lines.append("  Expression: %s\n" % expr_str)

            lines.append("\n[b]Step 2:[/b] Identify Voltage Divider Circuit:\n")
            for s in parse_steps:
                lines.append("%s\n" % s)
            lines.append("  Z_th (source network) = %.2f%+.2fj ohm  (%s)\n" % (
                zth.real, zth.imag, circuit_type))

            lines.append("\n[b]Step 3:[/b] Calculate V_th using VDR:\n")
            lines.append(vdr_line1 + "\n")
            if vdr_line2:
                lines.append(vdr_line2 + "\n")
            if vdr_line3:
                lines.append(vdr_line3 + "\n")
            lines.append("  |V_th| = %.2f V\n" % abs(vth))

            lines.append("\n[b]Step 4:[/b] Thevenin Impedance Z_th:\n")
            lines.append("  Z_th = %.2f%+.2fj ohm\n" % (zth.real, zth.imag))
            lines.append("  R_th = Re(Z_th) = %.2f ohm  (used in P_max formula)\n" % rth)
            lines.append("  X_th = Im(Z_th) = %.2f ohm\n" % xth)
            lines.append("  |Z_th| = %.2f ohm   theta = %.2f deg\n" % (
                abs(zth), math.degrees(cmath.phase(zth))))

            lines.append("\n[b]Step 5:[/b] Apply P_max = |V_th|^2 / (4 x R_th):\n")
            lines.append("  P_max = (%.2f)^2 / (4 x %.2f)\n" % (abs(vth), rth))
            lines.append("  P_max = %.2f / %.2f\n" % (abs(vth)**2, 4*rth))
            lines.append("  P_max = %.2f W\n" % p_max)

            lines.append("\n[b]Step 6:[/b] Optimal Load (Conjugate Matching):\n")
            lines.append("  Z_L = Z_th* = %.2f%+.2fj ohm\n" % (zl_opt.real, zl_opt.imag))

            lines.append("\n[color=008800][b]FINAL RESULTS:[/b][/color]\n")
            lines.append("  V_th  = %.2f ang %.2f deg V\n" % (abs(vth), math.degrees(cmath.phase(vth))))
            lines.append("  Z_th  = %.2f%+.2fj ohm\n" % (zth.real, zth.imag))
            lines.append("  Z_L   = %.2f%+.2fj ohm\n" % (zl_opt.real, zl_opt.imag))
            lines.append("  P_max = |V_th|^2/(4R_th) = %.2f W\n" % p_max)
            lines.append("  PF    = 1.00 (unity at MPT)")

            self.start_typing_animation(self.mpt_result, "".join(lines))

        except ValueError as e:
            self.mpt_result.text = "[color=ff0000]Error: %s[/color]" % str(e)
        except ZeroDivisionError as e:
            self.mpt_result.text = "[color=ff0000]Error: %s[/color]" % str(e)
        except Exception as e:
            self.mpt_result.text = "[color=ff0000]Unexpected error: %s[/color]" % str(e)

    # ── Direct input calculation (unchanged logic, polished output) ─
    def calculate_mpt_direct(self, instance):
        try:
            # ── Validate all fields filled ────────────────────────
            fields = [
                (self.mpt_vth_mag, "V_th Magnitude"),
                (self.mpt_vth_ang, "V_th Angle"),
                (self.mpt_rth,     "R_th"),
                (self.mpt_xth,     "X_th"),
            ]
            for field, name in fields:
                if not field.text.strip():
                    self.mpt_result.text = "[color=ff0000]Error: %s is empty.[/color]" % name
                    return

            vth_mag = float(self.mpt_vth_mag.text.strip())
            vth_ang = float(self.mpt_vth_ang.text.strip())
            rth     = float(self.mpt_rth.text.strip())
            xth     = float(self.mpt_xth.text.strip())

            circuit_type = "Inductive" if xth > 0 else ("Capacitive" if xth < 0 else "Resistive")
            vth     = cmath.rect(vth_mag, math.radians(vth_ang))
            zth     = complex(rth, xth)
            zl      = complex(rth, -xth)
            z_total = zth + zl
            i       = vth / z_total
            p_max   = (abs(vth) ** 2) / (4 * rth) if rth > 0 else 0.0

            r  = "[color=008800][b]STEP-BY-STEP MPT (DIRECT INPUT)[/b][/color]\n\n"
            r += f"[b]Step 1:[/b] Given parameters:\n"
            r += f"  V_th = {vth_mag:.2f} ∠ {vth_ang:.2f}° V\n"
            r += f"  Z_th = {rth:.2f}{xth:+.2f}j Ω  ({circuit_type})\n"
            r += f"\n[b]Step 2:[/b] Optimal load (conjugate):\n"
            r += f"  Z_L = Z_th* = {zl.real:.2f}{zl.imag:+.2f}j Ω\n"
            r += f"\n[b]Step 3:[/b] Total impedance:\n"
            r += f"  Z_total = {z_total.real:.2f}{z_total.imag:+.2f}j Ω\n"
            r += f"\n[b]Step 4:[/b] Current:\n"
            r += f"  I = V_th / Z_total = {abs(i):.2f} ∠ {math.degrees(cmath.phase(i)):.2f}° A\n"
            r += f"\n[b]Step 5:[/b] Maximum power (P_max = |V_th|²/4R_th):\n"
            r += f"  P_max = ({vth_mag:.2f})² / (4 × {rth:.2f}) = {p_max:.2f} W\n"
            r += f"\n[color=008800][b]FINAL RESULTS:[/b][/color]\n"
            r += f"  Z_th  = {zth.real:.2f}{zth.imag:+.2f}j Ω\n"
            r += f"  Z_L   = {zl.real:.2f}{zl.imag:+.2f}j Ω\n"
            r += f"  I     = {abs(i):.2f} ∠ {math.degrees(cmath.phase(i)):.2f}° A\n"
            r += f"  P_max = {p_max:.2f} W   PF = 1.00"

            self.start_typing_animation(self.mpt_result, r)
        except ValueError:
            self.mpt_result.text = "[color=ff0000]Enter valid numeric values.[/color]"
        except ZeroDivisionError:
            self.mpt_result.text = "[color=ff0000]Division by zero — check R_th.[/color]"
        except Exception as e:
            self.mpt_result.text = f"[color=ff0000]Error: {e}[/color]"

    # ── Streaming animation ────────────────────────────────────────
    def start_typing_animation(self, target_label, text):
        """Tag-safe streaming — never renders partial markup tags."""
        if self.typing_clock:
            self.typing_clock.cancel()
        self.typing_chunks    = _safe_stream_chunks(text)
        self.typing_chunk_idx = 0
        self.typing_target    = target_label
        target_label.text     = ""
        self.typing_clock     = Clock.schedule_interval(self.type_next_character, 0.018)

    def type_next_character(self, dt):
        if self.typing_chunk_idx < len(self.typing_chunks):
            self.typing_chunk_idx += 1
            self.typing_target.text = "".join(
                self.typing_chunks[:self.typing_chunk_idx])
        else:
            if self.typing_clock:
                self.typing_clock.cancel()
                self.typing_clock = None

    def go_home(self):
        self.manager.current = "home"


# ── Circuit expression evaluator (module-level helper) ────────────
def _circuit_eval(expr, parallel_fn, steps):
    """
    Evaluate a circuit expression string that uses:
      + for series (addition)
      || for parallel
    Supports parentheses for grouping.
    Returns a complex number.
    """
    import re

    expr = expr.strip()

    # Remove outer parentheses if they wrap the whole expression
    def strip_outer_parens(s):
        s = s.strip()
        if s.startswith('(') and s.endswith(')'):
            depth = 0
            for i, c in enumerate(s):
                if c == '(': depth += 1
                elif c == ')': depth -= 1
                if depth == 0 and i < len(s) - 1:
                    return s   # parens don't wrap whole expr
            return s[1:-1].strip()
        return s

    expr = strip_outer_parens(expr)

    # Find the lowest-precedence operator outside parens
    # Precedence: + (series) < || (parallel)
    # So we split on + first (lowest), then on ||

    def find_split(s, op):
        depth = 0
        i = 0
        positions = []
        while i < len(s):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
            elif depth == 0 and s[i:i+len(op)] == op:
                positions.append(i)
                i += len(op)
                continue
            i += 1
        return positions

    # Try splitting on + (series) — lowest precedence, rightmost split
    plus_pos = find_split(expr, '+')
    if plus_pos:
        split_at = plus_pos[-1]
        left_str  = expr[:split_at].strip()
        right_str = expr[split_at+1:].strip()
        if left_str and right_str:
            left_val  = _circuit_eval(left_str,  parallel_fn, steps)
            right_val = _circuit_eval(right_str, parallel_fn, steps)
            result = left_val + right_val
            steps.append(
                f"  Series:   ({left_val.real:.2f}{left_val.imag:+.2f}j)"
                f" + ({right_val.real:.2f}{right_val.imag:+.2f}j)"
                f" = {result.real:.2f}{result.imag:+.2f}j Ω"
            )
            return result

    # Try splitting on || (parallel)
    par_pos = find_split(expr, '||')
    if par_pos:
        split_at = par_pos[-1]
        left_str  = expr[:split_at].strip()
        right_str = expr[split_at+2:].strip()
        if left_str and right_str:
            left_val  = _circuit_eval(left_str,  parallel_fn, steps)
            right_val = _circuit_eval(right_str, parallel_fn, steps)
            result = parallel_fn(left_val, right_val)
            steps.append(
                f"  Parallel: ({left_val.real:.2f}{left_val.imag:+.2f}j)"
                f" || ({right_val.real:.2f}{right_val.imag:+.2f}j)"
                f" = {result.real:.2f}{result.imag:+.2f}j Ω"
            )
            return result

    # Base case: evaluate as a complex literal
    expr = strip_outer_parens(expr)
    try:
        val = complex(expr)
        return val
    except Exception:
        raise ValueError(f"Cannot evaluate token: '{expr}'")

class PowerMainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(SimpleBackground())
        
        # Streaming effect state
        self.typing_clock = None
        self.typing_text = ""
        self.typing_index = 0
        self.typing_target = None

        layout = MDBoxLayout(orientation="vertical")

        layout.add_widget(
            MDTopAppBar(
                title="Power Analysis",
                left_action_items=[["arrow-left", lambda x: self.go_home()]],
                elevation=2,
                md_bg_color=(0.12, 0.58, 0.95, 1),
            )
        )

        # Tab selection
        self.tabs = MDTabs(
            background_color=(0.12, 0.58, 0.95, 1),
            text_color_normal=(1, 1, 1, 0.7),
            text_color_active=(1, 1, 1, 1),
            indicator_color=(1, 1, 1, 1),
        )
        layout.add_widget(self.tabs)

        self.add_power_analysis_tab()
        self.add_complex_calculator_tab()

        self.add_widget(layout)

    def add_power_analysis_tab(self):
        power_tab = Tab(title="Power Analysis")
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Input Mode Selection
        mode_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.95, 0.97, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        mode_card.add_widget(
            MDLabel(
                text="INPUT MODE",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        
        mode_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        self.power_mode_button = MDRaisedButton(
            text="V-I Method",
            size_hint_x=0.5,
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.open_power_mode_menu,
        )
        mode_box.add_widget(self.power_mode_button)
        mode_card.add_widget(mode_box)
        content.add_widget(mode_card)

        # V-I Method Card
        self.vi_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        self.vi_card.add_widget(
            MDLabel(
                text="V-I METHOD INPUTS",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )

        # V_rms input (magnitude and angle)
        v_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        v_box.add_widget(MDLabel(text="V (V):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_v_mag = MDTextField(hint_text="Mag", mode="rectangle", size_hint_x=0.35)
        self.power_v_ang = MDTextField(hint_text="Angle (°)", mode="rectangle", size_hint_x=0.35)
        v_box.add_widget(self.power_v_mag)
        v_box.add_widget(self.power_v_ang)
        self.vi_card.add_widget(v_box)

        # I_rms input (magnitude and angle)
        i_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        i_box.add_widget(MDLabel(text="I (A):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_i_mag = MDTextField(hint_text="Mag", mode="rectangle", size_hint_x=0.35)
        self.power_i_ang = MDTextField(hint_text="Angle (°)", mode="rectangle", size_hint_x=0.35)
        i_box.add_widget(self.power_i_mag)
        i_box.add_widget(self.power_i_ang)
        self.vi_card.add_widget(i_box)

        self.vi_card.add_widget(
            MDRaisedButton(
                text="CALCULATE POWER",
                size_hint_x=1,
                md_bg_color=(0.12, 0.58, 0.95, 1),
                on_release=self.calculate_power_vi,
            )
        )
        content.add_widget(self.vi_card)

        # Z Method Card (initially hidden)
        self.z_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        self.z_card.add_widget(
            MDLabel(
                text="IMPEDANCE METHOD INPUTS",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )

        # Z format selection
        z_format_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        z_format_box.add_widget(MDLabel(text="Z Format:", size_hint_x=0.3, theme_text_color="Primary"))
        self.z_format_button = MDRaisedButton(
            text="Rectangular",
            size_hint_x=0.7,
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.open_z_format_menu,
        )
        z_format_box.add_widget(self.z_format_button)
        self.z_card.add_widget(z_format_box)

        # V input
        v_z_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        v_z_box.add_widget(MDLabel(text="V (V):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_z_v = MDTextField(hint_text="Voltage Mag", mode="rectangle", size_hint_x=0.7)
        v_z_box.add_widget(self.power_z_v)
        self.z_card.add_widget(v_z_box)

        # Z Rectangular inputs
        self.z_rect_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        self.z_rect_box.add_widget(MDLabel(text="Z (Ω):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_z_r = MDTextField(hint_text="R", mode="rectangle", size_hint_x=0.35)
        self.power_z_x = MDTextField(hint_text="X", mode="rectangle", size_hint_x=0.35)
        self.z_rect_box.add_widget(self.power_z_r)
        self.z_rect_box.add_widget(self.power_z_x)
        self.z_card.add_widget(self.z_rect_box)

        # Z Polar inputs (initially hidden)
        self.z_polar_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        self.z_polar_box.add_widget(MDLabel(text="Z (Ω):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_z_mag = MDTextField(hint_text="Mag", mode="rectangle", size_hint_x=0.35)
        self.power_z_ang = MDTextField(hint_text="Angle (°)", mode="rectangle", size_hint_x=0.35)
        self.z_polar_box.add_widget(self.power_z_mag)
        self.z_polar_box.add_widget(self.power_z_ang)
        self.z_card.add_widget(self.z_polar_box)
        self.z_polar_box.opacity = 0

        # Component values section
        comp_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.95, 0.97, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        comp_card.add_widget(
            MDLabel(
                text="COMPONENT VALUES (Optional)",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )

        # Frequency input
        freq_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        freq_box.add_widget(MDLabel(text="f (Hz):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_freq = MDTextField(hint_text="Frequency", mode="rectangle", size_hint_x=0.7)
        freq_box.add_widget(self.power_freq)
        comp_card.add_widget(freq_box)

        # L and C inputs
        lc_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        lc_box.add_widget(MDLabel(text="L (H):", size_hint_x=0.3, theme_text_color="Primary"))
        self.power_l = MDTextField(hint_text="Inductance", mode="rectangle", size_hint_x=0.35)
        self.power_c = MDTextField(hint_text="C (F)", mode="rectangle", size_hint_x=0.35)
        lc_box.add_widget(self.power_l)
        lc_box.add_widget(self.power_c)
        comp_card.add_widget(lc_box)

        self.z_card.add_widget(comp_card)

        self.z_card.add_widget(
            MDRaisedButton(
                text="CALCULATE POWER",
                size_hint_x=1,
                md_bg_color=(0.12, 0.58, 0.95, 1),
                on_release=self.calculate_power_z,
            )
        )
        content.add_widget(self.z_card)
        self.z_card.opacity = 0

        # Result Card
        result_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(1, 1, 1, 0.95),
            elevation=1,
            adaptive_height=True,
        )
        result_card.add_widget(
            MDLabel(
                text="RESULTS",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        self.power_result = MDLabel(
            text="Results will appear here with step-by-step logic.",
            adaptive_height=True,
            markup=True,
            theme_text_color="Secondary",
        )
        result_card.add_widget(self.power_result)
        content.add_widget(result_card)

        # Power Triangle Card
        triangle_card = MDCard(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(20),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.95, 0.97, 1, 1),
            elevation=1,
            size_hint=(1, None),
            height=dp(300),
        )
        triangle_card.add_widget(
            MDLabel(
                text="POWER TRIANGLE",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        self.power_triangle = PowerTriangleWidget(size_hint=(1, 1))
        triangle_card.add_widget(self.power_triangle)
        content.add_widget(triangle_card)

        scroll.add_widget(content)
        power_tab.add_widget(scroll)
        self.tabs.add_widget(power_tab)

    def add_complex_calculator_tab(self):
        complex_tab = Tab(title="Complex Calc")
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        # Input Card
        input_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.97, 0.99, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        input_card.add_widget(
            MDLabel(
                text="COMPLEX NUMBER CALCULATOR",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )

        # Complex A input
        a_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        a_box.add_widget(MDLabel(text="Complex A:", size_hint_x=0.3, theme_text_color="Primary"))
        self.complex_a = MDTextField(hint_text="e.g., 5+3j or 10<30", mode="rectangle", size_hint_x=0.7)
        a_box.add_widget(self.complex_a)
        input_card.add_widget(a_box)

        # Complex B input
        b_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        b_box.add_widget(MDLabel(text="Complex B:", size_hint_x=0.3, theme_text_color="Primary"))
        self.complex_b = MDTextField(hint_text="e.g., 2-1j or 5<45", mode="rectangle", size_hint_x=0.7)
        b_box.add_widget(self.complex_b)
        input_card.add_widget(b_box)

        # Operation selection
        op_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        op_box.add_widget(MDLabel(text="Operation:", size_hint_x=0.3, theme_text_color="Primary"))
        self.op_button = MDRaisedButton(
            text="Addition",
            size_hint_x=0.7,
            size_hint_y=None,
            height=dp(48),
            md_bg_color=(0.12, 0.58, 0.95, 1),
            on_release=self.open_op_menu,
        )
        op_box.add_widget(self.op_button)
        input_card.add_widget(op_box)

        input_card.add_widget(
            MDRaisedButton(
                text="CALCULATE",
                size_hint_x=1,
                md_bg_color=(0.12, 0.58, 0.95, 1),
                on_release=self.calculate_complex,
            )
        )
        content.add_widget(input_card)

        # Result Card
        result_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(1, 1, 1, 0.95),
            elevation=1,
            adaptive_height=True,
        )
        result_card.add_widget(
            MDLabel(
                text="RESULTS",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        self.complex_result = MDLabel(
            text="Results will appear here.",
            adaptive_height=True,
            markup=True,
            theme_text_color="Secondary",
        )
        result_card.add_widget(self.complex_result)
        content.add_widget(result_card)

        # Conversion Card
        conv_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(0.95, 0.97, 1, 1),
            elevation=1,
            adaptive_height=True,
        )
        conv_card.add_widget(
            MDLabel(
                text="QUICK CONVERSION",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )

        # Complex to convert
        conv_box = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(56))
        conv_box.add_widget(MDLabel(text="Complex:", size_hint_x=0.3, theme_text_color="Primary"))
        self.conv_input = MDTextField(hint_text="e.g., 5+3j or 10<30", mode="rectangle", size_hint_x=0.7)
        conv_box.add_widget(self.conv_input)
        conv_card.add_widget(conv_box)

        conv_card.add_widget(
            MDRaisedButton(
                text="CONVERT (Rect ↔ Polar)",
                size_hint_x=1,
                md_bg_color=(0.12, 0.58, 0.95, 1),
                on_release=self.convert_complex,
            )
        )
        content.add_widget(conv_card)

        # Conversion Result
        conv_result_card = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            radius=[16, 16, 16, 16],
            md_bg_color=(1, 1, 1, 0.95),
            elevation=1,
            adaptive_height=True,
        )
        conv_result_card.add_widget(
            MDLabel(
                text="CONVERSION RESULTS",
                bold=True,
                font_style="H6",
                adaptive_height=True,
                theme_text_color="Primary",
            )
        )
        self.conv_result = MDLabel(
            text="Conversion results will appear here.",
            adaptive_height=True,
            markup=True,
            theme_text_color="Secondary",
        )
        conv_result_card.add_widget(self.conv_result)
        content.add_widget(conv_result_card)

        scroll.add_widget(content)
        complex_tab.add_widget(scroll)
        self.tabs.add_widget(complex_tab)

    def open_power_mode_menu(self, instance):
        mode_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "V-I Method",
                "on_release": lambda x="vi": self.set_power_mode(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Impedance Method",
                "on_release": lambda x="z": self.set_power_mode(x),
            },
        ]
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(
            caller=instance,
            items=mode_items,
            width_mult=4,
        )
        self.menu.open()

    def set_power_mode(self, mode):
        if mode == "vi":
            self.power_mode_button.text = "V-I Method"
            self.vi_card.opacity = 1
            self.z_card.opacity = 0
        else:
            self.power_mode_button.text = "Impedance Method"
            self.vi_card.opacity = 0
            self.z_card.opacity = 1
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()

    def open_z_format_menu(self, instance):
        format_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Rectangular",
                "on_release": lambda x="rect": self.set_z_format(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Polar",
                "on_release": lambda x="polar": self.set_z_format(x),
            },
        ]
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(
            caller=instance,
            items=format_items,
            width_mult=4,
        )
        self.menu.open()

    def set_z_format(self, format_type):
        if format_type == "rect":
            self.z_format_button.text = "Rectangular"
            self.z_rect_box.opacity = 1
            self.z_polar_box.opacity = 0
        else:
            self.z_format_button.text = "Polar"
            self.z_rect_box.opacity = 0
            self.z_polar_box.opacity = 1
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()

    def calculate_power_vi(self, instance):
        """Calculate power using V-I method with complex phasors."""
        try:
            v_mag = float(self.power_v_mag.text)
            v_ang = float(self.power_v_ang.text)
            i_mag = float(self.power_i_mag.text)
            i_ang = float(self.power_i_ang.text)

            # Convert to complex phasors
            v = cmath.rect(v_mag, math.radians(v_ang))
            i = cmath.rect(i_mag, math.radians(i_ang))

            # Calculate complex power: S = V * I* (I conjugate)
            i_conj = i.conjugate()
            s = v * i_conj

            # Extract components
            p = s.real  # Real power
            q = s.imag  # Reactive power
            s_mag = abs(s)  # Apparent power magnitude
            s_ang = math.degrees(cmath.phase(s))  # Power angle

            # Calculate power factor
            pf = math.cos(math.radians(s_ang)) if s_mag > 0 else 0

            # Determine circuit type
            if q > 0:
                circuit_type = "Inductive (Lagging)"
                circuit_color = "0088ff"
            elif q < 0:
                circuit_type = "Capacitive (Leading)"
                circuit_color = "ff8800"
            else:
                circuit_type = "Resistive"
                circuit_color = "00aa00"

            # Build result string
            result = "[color=008800][b]STEP-BY-STEP AC POWER CALCULATION (V-I METHOD)[/b][/color]\n\n"
            result += f"[b]Step 1:[/b] Convert to complex phasors:\n"
            result += f"  V = {v_mag:.2f} ∠ {v_ang:.2f}° = {v.real:.2f} + j{v.imag:.2f} V\n"
            result += f"  I = {i_mag:.2f} ∠ {i_ang:.2f}° = {i.real:.2f} + j{i.imag:.2f} A\n\n"
            result += f"[b]Step 2:[/b] Calculate complex power:\n"
            result += f"  S = V × I* = ({v.real:.2f} + j{v.imag:.2f}) × ({i.real:.2f} - j{i.imag:.2f})\n"
            result += f"  S = {s.real:.2f} + j{s.imag:.2f} VA\n\n"
            result += f"[b]Step 3:[/b] Extract power components:\n"
            result += f"  P (Real) = {p:.2f} W\n"
            result += f"  Q (Reactive) = {q:.2f} VAR\n"
            result += f"  |S| (Apparent) = {s_mag:.2f} VA\n"
            result += f"  θ_s = {s_ang:.2f}°\n\n"
            result += f"[b]Step 4:[/b] Calculate power factor:\n"
            result += f"  PF = cos(θ_s) = {pf:.2f}\n\n"
            result += f"[b]Step 5:[/b] Determine circuit type:\n"
            result += f"  Q = {q:.2f} VAR → [color={circuit_color}]{circuit_type}[/color]\n\n"
            result += f"[color=008800][b]FINAL RESULTS:[/b][/color]\n"
            result += f"  Complex Power (S) = {s.real:.2f} + j{s.imag:.2f} VA\n"
            result += f"  Apparent Power (|S|) = {s_mag:.2f} VA\n"
            result += f"  Real Power (P) = {p:.2f} W\n"
            result += f"  Reactive Power (Q) = {q:.2f} VAR\n"
            result += f"  Power Factor (PF) = {pf:.2f}\n"
            result += f"  Circuit Type: [color={circuit_color}]{circuit_type}[/color]"

            self.start_typing_animation(self.power_result, result)
            self.power_triangle.update_triangle(p, q, s_mag, circuit_color)

        except ValueError:
            self.power_result.text = "[color=ff0000]Error: Please enter valid numeric values.[/color]"
        except Exception as e:
            self.power_result.text = f"[color=ff0000]Error: {str(e)}[/color]"

    def calculate_power_z(self, instance):
        """Calculate power using impedance method with complex phasors."""
        try:
            v_mag = float(self.power_z_v.text)
            
            # Get Z based on format
            if self.z_format_button.text == "Rectangular":
                z_r = float(self.power_z_r.text)
                z_x = float(self.power_z_x.text)
                z = complex(z_r, z_x)
                z_str = f"{z_r:.2f} + j{z_x:.2f} Ω"
            else:
                z_mag = float(self.power_z_mag.text)
                z_ang = float(self.power_z_ang.text)
                z = cmath.rect(z_mag, math.radians(z_ang))
                z_str = f"{z_mag:.2f} ∠ {z_ang:.2f}° Ω"

            # Calculate current: I = V / Z
            v = cmath.rect(v_mag, 0)  # Assume V at 0° reference
            i = v / z

            # Calculate complex power: S = V × I*
            i_conj = i.conjugate()
            s = v * i_conj

            # Extract components
            p = s.real  # Real power
            q = s.imag  # Reactive power
            s_mag = abs(s)  # Apparent power magnitude
            s_ang = math.degrees(cmath.phase(s))  # Power angle

            # Calculate power factor
            pf = math.cos(math.radians(s_ang)) if s_mag > 0 else 0

            # Determine circuit type
            if q > 0:
                circuit_type = "Inductive (Lagging)"
                circuit_color = "0088ff"
            elif q < 0:
                circuit_type = "Capacitive (Leading)"
                circuit_color = "ff8800"
            else:
                circuit_type = "Resistive"
                circuit_color = "00aa00"

            # Build result string
            result = "[color=008800][b]STEP-BY-STEP AC POWER CALCULATION (IMPEDANCE METHOD)[/b][/color]\n\n"
            result += f"[b]Step 1:[/b] Given parameters:\n"
            result += f"  V = {v_mag:.2f} ∠ 0° V\n"
            result += f"  Z = {z_str}\n\n"
            result += f"[b]Step 2:[/b] Calculate current:\n"
            result += f"  I = V / Z = {v_mag:.2f} / ({z.real:.2f} + j{z.imag:.2f})\n"
            result += f"  I = {abs(i):.2f} ∠ {math.degrees(cmath.phase(i)):.2f}° A\n\n"
            result += f"[b]Step 3:[/b] Calculate complex power:\n"
            result += f"  S = V × I* = {v_mag:.2f} × ({abs(i):.2f} ∠ {-math.degrees(cmath.phase(i)):.2f}°)\n"
            result += f"  S = {s.real:.2f} + j{s.imag:.2f} VA\n\n"
            result += f"[b]Step 4:[/b] Extract power components:\n"
            result += f"  P (Real) = {p:.2f} W\n"
            result += f"  Q (Reactive) = {q:.2f} VAR\n"
            result += f"  |S| (Apparent) = {s_mag:.2f} VA\n"
            result += f"  θ_s = {s_ang:.2f}°\n\n"
            result += f"[b]Step 5:[/b] Calculate power factor:\n"
            result += f"  PF = cos(θ_s) = {pf:.2f}\n\n"
            result += f"[b]Step 6:[/b] Determine circuit type:\n"
            result += f"  Q = {q:.2f} VAR → [color={circuit_color}]{circuit_type}[/color]\n"

            # Calculate component values if frequency is provided
            try:
                freq = float(self.power_freq.text)
                l_val = self.power_l.text
                c_val = self.power_c.text
                
                if l_val or c_val:
                    result += "\n[b]Step 7:[/b] Component calculations:\n"
                    omega = 2 * math.pi * freq
                    
                    if l_val:
                        l = float(l_val)
                        x_l = omega * l
                        v_l = abs(i) * x_l
                        result += f"  X_L = ωL = {omega:.2f} × {l:.2f} = {x_l:.2f} Ω\n"
                        result += f"  V_L = I × X_L = {abs(i):.2f} × {x_l:.2f} = {v_l:.2f} V\n"
                    
                    if c_val:
                        c = float(c_val)
                        x_c = 1 / (omega * c) if c > 0 else 0
                        v_c = abs(i) * x_c if x_c > 0 else 0
                        result += f"  X_C = 1/(ωC) = 1/({omega:.2f} × {c:.2f}) = {x_c:.2f} Ω\n"
                        result += f"  V_C = I × X_C = {abs(i):.2f} × {x_c:.2f} = {v_c:.2f} V\n"
            except (ValueError, ZeroDivisionError):
                pass  # Skip component calculations if invalid

            result += f"\n[color=008800][b]FINAL RESULTS:[/b][/color]\n"
            result += f"  Complex Power (S) = {s.real:.2f} + j{s.imag:.2f} VA\n"
            result += f"  Apparent Power (|S|) = {s_mag:.2f} VA\n"
            result += f"  Real Power (P) = {p:.2f} W\n"
            result += f"  Reactive Power (Q) = {q:.2f} VAR\n"
            result += f"  Power Factor (PF) = {pf:.2f}\n"
            result += f"  Circuit Type: [color={circuit_color}]{circuit_type}[/color]"

            self.start_typing_animation(self.power_result, result)
            self.power_triangle.update_triangle(p, q, s_mag, circuit_color)

        except ValueError:
            self.power_result.text = "[color=ff0000]Error: Please enter valid numeric values.[/color]"
        except ZeroDivisionError:
            self.power_result.text = "[color=ff0000]Error: Division by zero. Check impedance value.[/color]"
        except Exception as e:
            self.power_result.text = f"[color=ff0000]Error: {str(e)}[/color]"

    def open_op_menu(self, instance):
        op_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Addition (+)",
                "on_release": lambda x="+": self.set_operation(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Subtraction (-)",
                "on_release": lambda x="-": self.set_operation(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Multiplication (×)",
                "on_release": lambda x="*": self.set_operation(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Division (÷)",
                "on_release": lambda x="/": self.set_operation(x),
            },
        ]
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(
            caller=instance,
            items=op_items,
            width_mult=4,
        )
        self.menu.open()

    def set_operation(self, op):
        op_names = {"+": "Addition", "-": "Subtraction", "*": "Multiplication", "/": "Division"}
        self.op_button.text = op_names.get(op, op)
        self.current_op = op
        if hasattr(self, "menu") and self.menu:
            self.menu.dismiss()

    def calculate_complex(self, instance):
        try:
            a = parse_complex_number(self.complex_a.text)
            b = parse_complex_number(self.complex_b.text)
            op = getattr(self, "current_op", "+")

            if op == "+":
                result = a + b
                op_name = "Addition"
            elif op == "-":
                result = a - b
                op_name = "Subtraction"
            elif op == "*":
                result = a * b
                op_name = "Multiplication"
            elif op == "/":
                if b == 0:
                    self.complex_result.text = "[color=ff0000]Error: Division by zero.[/color]"
                    return
                result = a / b
                op_name = "Division"
            else:
                result = a + b
                op_name = "Addition"

            # Build result string
            result_str = "[color=008800][b]COMPLEX NUMBER CALCULATION[/b][/color]\n\n"
            result_str += f"[b]Operation:[/b] {op_name}\n\n"
            result_str += f"[b]Input A:[/b]\n"
            result_str += f"  Rectangular: {complex_to_rect_str(a)}\n"
            result_str += f"  Polar: {complex_to_polar_str(a)}\n\n"
            result_str += f"[b]Input B:[/b]\n"
            result_str += f"  Rectangular: {complex_to_rect_str(b)}\n"
            result_str += f"  Polar: {complex_to_polar_str(b)}\n\n"
            result_str += f"[b]Result:[/b]\n"
            result_str += f"  Rectangular: {complex_to_rect_str(result)}\n"
            result_str += f"  Polar: {complex_to_polar_str(result)}"

            self.complex_result.text = result_str

        except ValueError as e:
            self.complex_result.text = f"[color=ff0000]Error: {str(e)}[/color]"
        except Exception as e:
            self.complex_result.text = f"[color=ff0000]Error: {str(e)}[/color]"

    def convert_complex(self, instance):
        try:
            z = parse_complex_number(self.conv_input.text)

            rect_str = complex_to_rect_str(z)
            polar_str = complex_to_polar_str(z)

            result = "[color=008800][b]COMPLEX NUMBER CONVERSION[/b][/color]\n\n"
            result += f"[b]Input:[/b] {self.conv_input.text}\n\n"
            result += f"[b]Rectangular Form:[/b]\n"
            result += f"  {rect_str}\n\n"
            result += f"[b]Polar Form:[/b]\n"
            result += f"  {polar_str}\n\n"
            result += f"[b]Magnitude:[/b] {abs(z):.2f}\n"
            result += f"[b]Phase Angle:[/b] {math.degrees(cmath.phase(z)):.2f}°"

            self.conv_result.text = result

        except ValueError as e:
            self.conv_result.text = f"[color=ff0000]Error: {str(e)}[/color]"
        except Exception as e:
            self.conv_result.text = f"[color=ff0000]Error: {str(e)}[/color]"

    def start_typing_animation(self, target_label, text):
        """Start streaming/typed effect — tag-safe, never cuts inside markup."""
        if self.typing_clock:
            self.typing_clock.cancel()
        self.typing_chunks = _safe_stream_chunks(text)
        self.typing_chunk_idx = 0
        self.typing_target = target_label
        target_label.text = ""
        self.typing_clock = Clock.schedule_interval(self.type_next_character, 0.018)

    def type_next_character(self, dt):
        if self.typing_chunk_idx < len(self.typing_chunks):
            self.typing_chunk_idx += 1
            self.typing_target.text = "".join(
                self.typing_chunks[:self.typing_chunk_idx])
        else:
            if self.typing_clock:
                self.typing_clock.cancel()
                self.typing_clock = None

    def go_home(self):
        self.manager.current = "home"


class PowerTriangleWidget(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.p = 0
        self.q = 0
        self.s = 0
        self.color = "0088ff"
        with self.canvas:
            self.triangle_color = Color(0, 0.52, 1, 1)
            self.line = Line(points=[], width=2)
        self.p_label = Label(text="P", pos=(0, 0), size_hint=(None, None), font_size=12)
        self.q_label = Label(text="Q", pos=(0, 0), size_hint=(None, None), font_size=12)
        self.s_label = Label(text="S", pos=(0, 0), size_hint=(None, None), font_size=12)
        self.add_widget(self.p_label)
        self.add_widget(self.q_label)
        self.add_widget(self.s_label)

    def update_triangle(self, p, q, s, color):
        self.p = p
        self.q = q
        self.s = s
        self.color = color

        # Convert hex color to RGB
        r = int(color[0:2], 16) / 255
        g = int(color[2:4], 16) / 255
        b = int(color[4:6], 16) / 255
        self.triangle_color.rgb = (r, g, b)

        # Calculate triangle points (normalized)
        max_val = max(abs(p), abs(q), s, 1)
        scale = 0.8  # Use 80% of available space

        # Origin point (bottom-left for P axis)
        origin_x = self.width * 0.2
        origin_y = self.height * 0.2

        # P point (horizontal axis)
        p_x = origin_x + (abs(p) / max_val) * self.width * scale
        p_y = origin_y

        # Q point (vertical axis)
        q_x = origin_x
        q_y = origin_y + (abs(q) / max_val) * self.height * scale

        # S point (hypotenuse)
        s_x = p_x
        s_y = q_y

        # Update line points
        self.line.points = [origin_x, origin_y, p_x, p_y, s_x, s_y, origin_x, origin_y]

        # Update labels
        self.p_label.text = f"P = {p:.2f} W"
        self.p_label.pos = (p_x / 2, origin_y - 20)
        self.q_label.text = f"Q = {q:.2f} VAR"
        self.q_label.pos = (origin_x - 40, q_y / 2)
        self.s_label.text = f"S = {s:.2f} VA"
        self.s_label.pos = (s_x + 10, s_y + 10)

# ==========================================
# Helper Functions for Complex Number Parsing
# ==========================================
def parse_complex_number(input_str):
    """
    Parse a complex number from string input.
    Supports:
    - Rectangular form: "5+3j", "5-3j", "5+3i", "5-3i"
    - Polar form: "10<30" (magnitude<angle in degrees)
    - Simple numbers: "10", "5.5"
    
    Returns: complex number
    """
    input_str = input_str.strip().replace(' ', '')
    
    # Try polar form (magnitude<angle)
    if '<' in input_str:
        try:
            parts = input_str.split('<')
            mag = float(parts[0])
            angle_deg = float(parts[1])
            angle_rad = math.radians(angle_deg)
            return cmath.rect(mag, angle_rad)
        except:
            raise ValueError(f"Invalid polar format: {input_str}")
    
    # Try rectangular form with j or i
    if 'j' in input_str or 'i' in input_str:
        try:
            # Replace i with j for Python's complex number parsing
            parsed = input_str.replace('i', 'j')
            return complex(parsed)
        except:
            raise ValueError(f"Invalid rectangular format: {input_str}")
    
    # Try simple number
    try:
        return complex(float(input_str), 0)
    except:
        raise ValueError(f"Invalid number format: {input_str}")

def complex_to_polar_str(z):
    """Convert complex number to polar string representation."""
    mag = abs(z)
    angle = math.degrees(cmath.phase(z))
    return f"{mag:.4f}∠{angle:.2f}°"

def complex_to_rect_str(z):
    """Convert complex number to rectangular string representation."""
    real = z.real
    imag = z.imag
    sign = "+" if imag >= 0 else "-"
    return f"{real:.4f}{sign}j{abs(imag):.4f}"

# ==========================================
# 7. Main Application
# ==========================================
class MTroApp(MDApp):
    store = {
        "k_nodes": "", "c_rect_r": "", "c_rect_x": "", 
        "c_pol_mag": "", "c_pol_ang": "", "c_res_r": "", "c_res_x": ""
    }
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light" # البداية بالوضع الفاتح
        sm = MDScreenManager()
        
        # --- إضافة كل الشاشات المسجلة في التطبيق ---
        sm.add_widget(AppIntroScreen(name='intro'))
        sm.add_widget(HomeScreen(name='home'))
        
        # شاشات قانون أوم (تأكد من وجود هذه الكلاسات في ملفك)
        sm.add_widget(OhmsLawIntroScreen(name='ohms_law_intro'))
        sm.add_widget(OhmsLawCalcScreen(name='ohms_law_calc')) # هذا هو السطر الذي كان ينقصك!
        
        # شاشات الأعداد المركبة
        sm.add_widget(ComplexIntroScreen(name='complex_intro'))
        sm.add_widget(ComplexCalcScreen(name='complex_calc'))
        
        # شاشات الـ AC
        sm.add_widget(ACMainScreen(name='ac_main'))
        
        # شاشات MPT و Power
        sm.add_widget(MPTMainScreen(name='mpt_main'))
        sm.add_widget(PowerMainScreen(name='power_main'))
    
# وهكذا لباقي الشاشات..
        sm.current = 'intro'
        return sm
if __name__ == '__main__':
    MTroApp().run()