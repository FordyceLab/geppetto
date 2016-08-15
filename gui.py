from pymodbus3.client.sync import ModbusTcpClient
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from valves import pressurize, depressurize
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color
from kivy.uix.scatter import Scatter
from yaml import load

with open("example.yaml", "r") as config_file:
    config = load(config_file)

# client = ModbusTcpClient('192.168.1.3')
client = ModbusTcpClient()

valves = {valve: config["valves"][valve] for valve in config["valves"]}

labels = [key for key in valves.keys()]


class ButtonHolder(BoxLayout):
    def __init__(self, valve_number, label, initial_state, x, y, *args,
                 **kwargs):
        super(ButtonHolder, self).__init__(*args, **kwargs)
        self.size = (80, 40)
        self.size_hint = (None, None)
        self.pos = (x, y)
        self.orientation = "horizontal"
        self.padding = 5

        with self.canvas:
            Color(1, 1, 1, .8)
            Rectangle(size=self.size,
                      pos=self.pos)

        labels = BoxLayout(orientation="vertical")
        labels.add_widget(Label(text=label,
                                font_size=10,
                                color=(0, 0, 0, 1)))
        labels.add_widget(Label(text="D",
                                font_size=10,
                                color=(0, 0, 0, 1),
                                id=str(valve_number) + "_state_label"))
        labels.add_widget(Label(text=str(valve_number),
                                font_size=10,
                                color=(0, 0, 0, 1)))

        self.add_widget(labels)
        button = PressureButton(valve_number, False, size_hint_x=.4)
        button.bind(on_press=change_pressure_state)
        self.add_widget(button)


class PressureButton(Button):
    def __init__(self, valve_number, initial_state, *args, **kwargs):
        super(PressureButton, self).__init__(*args, **kwargs)
        self.pressure_state = initial_state
        self.background_normal = ''
        self.background_color = (.94, .05, .05, 1.0)
        self.valve_number = valve_number


class MainLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        ip_address = TextInput(text="192.168.1.3",
                               size_hint_y=0.06,
                               size_hint_x=0.3)
        self.add_widget(ip_address)

        valves = ValveControls()
        self.add_widget(valves)


class ValveControls(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(ValveControls, self).__init__(*args, **kwargs)
        self.size = (800, 530)

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(source="800x530.jpg",
                      size=self.size,
                      center=self.center)

        for i in labels:
            button = ButtonHolder(valve_number=valves[i]["valve_number"],
                                  label=i,
                                  initial_state=valves[i]["initial_state"],
                                  x=valves[i]["x_pos"],
                                  y=valves[i]["y_pos"])

            self.add_widget(button)


class Geppetto(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        layout = MainLayout()
        return layout


def change_pressure_state(instance):
    for child in instance.parent.walk():
        if child.id == str(instance.valve_number) + "_state_label":
            label = child

    if instance.pressure_state:
        pressurize(instance.valve_number)
        instance.pressure_state = False
        instance.background_color = (.94, .05, .05, 1.0)
        label.text = "D"
    else:
        depressurize(instance.valve_number)
        instance.pressure_state = True
        instance.background_color = (.05, .5, .94, 1.0)
        label.text = "P"
