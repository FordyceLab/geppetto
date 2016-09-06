from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from valves import pressurize, depressurize
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from yaml import load

with open("BeadSynthesizer.yaml", "r") as config_file:
    config = load(config_file)

valves = {valve: config["valves"][valve] for valve in config["valves"]}

labels = [key for key in valves.keys()]

device_image = config["device_image"]

buttons = []


class ButtonHolder(BoxLayout):
    def __init__(self, valve_number, label, initial_state, x, y, *args,
                 **kwargs):
        super(ButtonHolder, self).__init__(*args, **kwargs)
        self.size = (70, 35)
        self.size_hint = (None, None)
        self.center_x = x
        self.center_y = y
        self.orientation = "horizontal"
        self.padding = 5
        self.valve_number = valve_number
        self.label = label
        self.initial_state = initial_state

        with self.canvas:
            Color(.7, .7, .7, .5)
            Rectangle(size=self.size,
                      pos=self.pos)

        labels = BoxLayout(orientation="vertical")
        labels.add_widget(Label(text=label,
                                font_size=10,
                                color=(0, 0, 0, 1)))
        labels.add_widget(Label(text="?",
                                font_size=10,
                                color=(0, 0, 0, 1),
                                id=str(valve_number) + "_state_label"))
        labels.add_widget(Label(text=str(valve_number),
                                font_size=10,
                                color=(0, 0, 0, 1)))

        self.add_widget(labels)
        button = PressureButton(valve_number, False, size_hint_x=.5)
        button.bind(on_press=change_pressure_state)
        self.add_widget(button)


class PressureButton(Button):
    def __init__(self, valve_number, initial_state, *args, **kwargs):
        super(PressureButton, self).__init__(*args, **kwargs)
        self.id = str(valve_number) + "_valve_button"
        self.pressure_state = initial_state
        self.background_normal = ''
        self.background_color = (.5, .5, .5, 1.0)
        self.valve_number = valve_number


class MainLayout(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        controls = ControlPanel()

        self.add_widget(controls)

        valves = ValveControls()
        self.add_widget(valves)
        print(self.ids)


class ControlPanel(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)
        self.orientation = "horizontal"
        self.spacing = 10
        self.padding = 10
        self.size_hint_y = 0.1

        initialize_valves = Button(text="Initialize Valve States")
        initialize_valves.bind(on_press=initialize_valve_states)
        self.add_widget(initialize_valves)

        read_valves = Button(text="Read Valve States")
        read_valves.bind(on_press=read_valve_states)
        self.add_widget(read_valves)

        pressurize_all = Button(text="Pressurize All")
        pressurize_all.bind(on_press=pressurize_all_valves)
        self.add_widget(pressurize_all)

        depressurize_all = Button(text="Depressurize All")
        depressurize_all.bind(on_press=depressurize_all_valves)
        self.add_widget(depressurize_all)


class ValveControls(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(ValveControls, self).__init__(*args, **kwargs)
        self.size = (800, 530)

        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(source=device_image,
                      size=self.size,
                      center=self.center)

        for i in labels:
            button = ButtonHolder(valve_number=valves[i]["valve_number"],
                                  label=i,
                                  initial_state=valves[i]["initial_state"],
                                  x=valves[i]["x_pos"],
                                  y=valves[i]["y_pos"])

            buttons.append(button)

            self.add_widget(button)


class Geppetto(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        layout = MainLayout()
        print(layout.ids)
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


def read_valve_states(instance):
    for button in buttons:
        register_number = 512 + button.valve_number
        state = client.read_coils(register_number, 1).bits[0]
        for child in button.walk():
            if child.id == str(button.valve_number) + "_valve_button":
                if not state:
                    child.background_color = (.05, .5, .94, 1.0)
                    child.pressure_state = True
                else:
                    child.background_color = (.94, .05, .05, 1.0)
                    child.pressure_state = False
            if child.id == str(button.valve_number) + "_state_label":
                if not state:
                    child.text = "P"
                else:
                    child.text = "D"


def initialize_valve_states(instance):
    for button in buttons:
        if button.initial_state:
            pressurize(button.valve_number)
        else:
            depressurize(button.valve_number)


def pressurize_all_valves(instance):
    for button in buttons:
        pressurize(button.valve_number)
        for child in button.walk():
            if child.id == str(button.valve_number) + "_valve_button":
                    child.background_color = (.05, .5, .94, 1.0)
                    child.pressure_state = True
            if child.id == str(button.valve_number) + "_state_label":
                    child.text = "P"


def depressurize_all_valves(instance):
    for button in buttons:
        depressurize(button.valve_number)
        for child in button.walk():
            if child.id == str(button.valve_number) + "_valve_button":
                    child.background_color = (.94, .05, .05, 1.0)
                    child.pressure_state = False
            if child.id == str(button.valve_number) + "_state_label":
                    child.text = "D"
