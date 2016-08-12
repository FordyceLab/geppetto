from pymodbus3.client.sync import ModbusTcpClient
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from valves import pressurize, depressurize
from kivy.core.window import Window

# client = ModbusTcpClient('192.168.1.3')
client = ModbusTcpClient()

labels = ["PBS",
          "Antibody",
          "bBSA",
          "Neutravidin",
          "Extra 1",
          "Extra 2",
          "Protein",
          "Waste",
          "Buttons 1",
          "Buttons 2",
          "Sandwiches 1",
          "Sandwiches 2",
          "Neck",
          "In",
          "Out"]

valves = {"PBS": 0,
          "Antibody": 1,
          "bBSA": 2,
          "Neutravidin": 3,
          "Extra 1": 4,
          "Extra 2": 5,
          "Protein": 6,
          "Waste": 7,
          "Buttons 1": 8,
          "Buttons 2": 9,
          "Sandwiches 1": 10,
          "Sandwiches 2": 11,
          "Neck": 12,
          "In": 13,
          "Out": 14}


class ButtonHolder(BoxLayout):
    def __init__(self, valve_number, label, initial_state, *args, **kwargs):
        super(ButtonHolder, self).__init__(*args, **kwargs)
        self.orientation = "horizontal"
        self.padding = 20
        self.background_color = (1, 1, 1, 1)

        labels = BoxLayout(orientation="vertical")
        labels.add_widget(Label(text=label,
                                font_size=10,
                                color=(0, 0, 0, 1)))
        labels.add_widget(Label(text="Depressurized",
                                font_size=10,
                                color=(0, 0, 0, 1),
                                id=str(valve_number) + "_state_label"))
        labels.add_widget(Label(text="Valve: " + str(valve_number),
                                font_size=10,
                                color=(0, 0, 0, 1)))

        self.add_widget(labels)
        button = PressureButton(valve_number, False)
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
                               size_hint_y=0.1,
                               size_hint_x=0.3)
        self.add_widget(ip_address)

        valves = ValveControls()
        self.add_widget(valves)


class ValveControls(GridLayout):
    def __init__(self, *args, **kwargs):
        super(ValveControls, self).__init__(*args, **kwargs)
        self.cols = 4
        self.row_force_default = True
        self.row_default_height = 70
        self.size_x = 800
        self.size_y = 800

        for i in labels:
            button = ButtonHolder(valve_number=valves[i],
                                  label=i,
                                  initial_state=False)

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
        label.text = "Depressurized"
    else:
        depressurize(instance.valve_number)
        instance.pressure_state = True
        instance.background_color = (.05, .5, .94, 1.0)
        label.text = "Pressurized"
