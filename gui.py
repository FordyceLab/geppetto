from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from valves import pressurize, depressurize, read_valve, client
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from yaml import load
from os.path import sep, expanduser
from kivy.garden.filebrowser import FileBrowser


class ButtonHolder(BoxLayout):
    """A class to hold and position button components including labels and button

    Args:
        valve_number (int): valve number on setup assigned to button
        label (str): label for button
        initial_state (bool): initial state (pressurized/depressurized) for the
            valve, True = pressurized, False = depressurized
        x (int): x coordinate in pixels from left of screen to place button
        y (int): y coordinate in pixels from bottom of screen to place button
    """
    def __init__(self, valve_number, label, initial_state, x, y, *args,
                 **kwargs):
        super(ButtonHolder, self).__init__(*args, **kwargs)

        # Set the size of the button holder
        self.size = (70, 35)
        self.size_hint = (None, None)

        # Center the button on the given position
        self.center_x = x
        self.center_y = y

        # Set the orientation and pad the labels and internal button from the
        # sides of the button holder
        self.orientation = "horizontal"
        self.padding = 5

        # Set some local variables corresponding to the valve number, label,
        # and initial state
        self.valve_number = valve_number
        self.label = label
        self.initial_state = initial_state

        # Make the button background a transparent gray
        with self.canvas:
            Color(.7, .7, .7, .5)
            Rectangle(size=self.size,
                      pos=self.pos)

        # Begin to arrange the labels and buttons within the holder
        labels = BoxLayout(orientation="vertical")

        # Add the button label to holder
        labels.add_widget(Label(text=label,
                                font_size=10,
                                color=(0, 0, 0, 1)))

        # Add the state label to the holder, initially set to "?" until state
        # is set or read
        labels.add_widget(Label(text="?",
                                font_size=10,
                                color=(0, 0, 0, 1),
                                id=str(valve_number) + "_state_label"))

        # Add the valve number label to the button holder
        labels.add_widget(Label(text=str(valve_number),
                                font_size=10,
                                color=(0, 0, 0, 1)))

        # Add all of the labels to the button holder
        self.add_widget(labels)

        # Add the button to button holder
        button = PressureButton(valve_number, False, size_hint_x=.5)
        button.bind(on_press=change_pressure_state)
        self.add_widget(button)


class PressureButton(Button):
    """A class to hold and control the state/color of the button"""
    def __init__(self, valve_number, initial_state, *args, **kwargs):
        super(PressureButton, self).__init__(*args, **kwargs)

        # Set local variables for the button, including setting the initial
        # color to gray
        self.id = str(valve_number) + "_valve_button"
        self.background_normal = ''
        self.background_color = (.5, .5, .5, 1.0)
        self.valve_number = valve_number


class MainLayout(BoxLayout):
    """A class to control the main layout of the controller"""
    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)

        # Set some aesthetic parameters of for the main layout
        self.orientation = "vertical"
        self.spacing = 10
        self.padding = 20

        # Initialize the control panel
        controls = ControlPanel()
        self.add_widget(controls)

        # Initialize the valve controls
        valves = ValveControls()
        self.add_widget(valves)


class ControlPanel(BoxLayout):
    """A class to contain the control panel buttons"""
    def __init__(self, *args, **kwargs):
        super(ControlPanel, self).__init__(*args, **kwargs)

        # Initialize local parameters for the control panel
        self.orientation = "horizontal"
        self.spacing = 10
        self.padding = 10
        self.size_hint_y = 0.1

        # Add a button to initialize the valve states per the config file
        initialize_valves = Button(text="Initialize Valve States")
        initialize_valves.bind(on_press=self.initialize_valve_states)
        self.add_widget(initialize_valves)

        # Add a button to read the state of the valves and update the button
        # holder information
        read_valves = Button(text="Read Valve States")
        read_valves.bind(on_press=self.read_valve_states)
        self.add_widget(read_valves)

        # Add a button to pressurize all the valves
        pressurize_all = Button(text="Pressurize All")
        pressurize_all.bind(on_press=self.pressurize_all_valves)
        self.add_widget(pressurize_all)

        # Add a button to depressurize all the valves
        depressurize_all = Button(text="Depressurize All")
        depressurize_all.bind(on_press=self.depressurize_all_valves)
        self.add_widget(depressurize_all)

    def initialize_valve_states(self, instance):
        """A function to set all valve states per the config file"""

        # For each button
        for button in buttons:

            # If the button state is True, pressurize it
            if button.initial_state:
                pressurize(button.valve_number)
                for child in button.walk():
                    if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.05, .5, .94, 1.0)
                    if child.id == str(button.valve_number) + "_state_label":
                        child.text = "P"

            # If the button state is False, depressurize it
            else:
                depressurize(button.valve_number)
                for child in button.walk():
                    if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.94, .05, .05, 1.0)
                    if child.id == str(button.valve_number) + "_state_label":
                        child.text = "D"

    def read_valve_states(self, instance):
        """A function to read the current valve states from the Wago controller
        """

        # For each button
        for button in buttons:

            # Set the 512 offset to read the appropriate register
            register_number = 512 + button.valve_number
            state = read_valve(register_number)
            for child in button.walk():
                if child.id == str(button.valve_number) + "_valve_button":
                    if not state:
                        child.background_color = (.05, .5, .94, 1.0)
                    else:
                        child.background_color = (.94, .05, .05, 1.0)
                if child.id == str(button.valve_number) + "_state_label":
                    if not state:
                        child.text = "P"
                    else:
                        child.text = "D"

    def pressurize_all_valves(self, instance):
        """
        """
        for button in buttons:
            pressurize(button.valve_number)
            for child in button.walk():
                if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.05, .5, .94, 1.0)
                if child.id == str(button.valve_number) + "_state_label":
                        child.text = "P"

    def depressurize_all_valves(self, instance):
        """
        """
        for button in buttons:
            depressurize(button.valve_number)
            for child in button.walk():
                if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.94, .05, .05, 1.0)
                if child.id == str(button.valve_number) + "_state_label":
                        child.text = "D"





class ValveControls(FloatLayout):
    """A class to 
    """
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
        with open(config_file, "r") as config_values:
            config = load(config_values)

        global valves
        global labels
        global device_image
        global buttons

        valves = {valve: config["valves"][valve] for valve in config["valves"]}
        labels = [key for key in valves.keys()]
        device_image = config["device_image"]
        buttons = []

        Window.clearcolor = (1, 1, 1, 1)
        layout = MainLayout()
        return layout


class ChooseConfigFile(App):
    def build(self):
        user_path = expanduser('~') + sep + 'Documents'
        browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')])
        browser.bind(
            on_success=self._fbrowser_success,
            on_canceled=self._fbrowser_canceled)
        return browser

    def _fbrowser_canceled(self, instance):
        self.stop()

    def _fbrowser_success(self, instance):
        global config_file
        config_file = instance.selection[0]
        self.stop()


def change_pressure_state(instance):
    for child in instance.parent.walk():
        if child.id == str(instance.valve_number) + "_state_label":
            label = child

    if read_valve(instance.valve_number + 512):
        pressurize(instance.valve_number)
        instance.background_color = (.94, .05, .05, 1.0)
        label.text = "D"
    else:
        depressurize(instance.valve_number)
        instance.background_color = (.05, .5, .94, 1.0)
        label.text = "P"
