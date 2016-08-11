from pymodbus3.client.sync import ModbusTcpClient
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from valves import pressurize, depressurize

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


class PressureButton(Button):
    def __init__(self, valve_number, *args, **kwargs):
        super(PressureButton, self).__init__(*args, **kwargs)
        self.pressure_state = True
        self.background_normal = ''
        self.background_color = (.94, .05, .05, 1.0)
        self.valve_number = valve_number


class Geppetto(App):
    def build(self):
        layout = GridLayout(cols=4, row_force_default=True,
                            row_default_height=70)
        for i in labels:
            button = PressureButton(valve_number=valves[i],
                                    text=i,
                                    background_normal='',
                                    background_color=(.94, .05, .05, 1.0))

            button.bind(on_press=change_pressure_state)

            layout.add_widget(button)

        return layout


def change_pressure_state(instance):
    if instance.pressure_state:
        pressurize(instance.valve_number)
        instance.pressure_state = False
        instance.background_color = (.05, .5, .94, 1.0)
    else:
        depressurize(instance.valve_number)
        instance.pressure_state = True
        instance.background_color = (.94, .05, .05, 1.0)
