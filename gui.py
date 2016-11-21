from kivy.config import Config
Config.set('graphics','resizable',0)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from valves import pressurize, depressurize, read_valve
from kivy.core.window import Window
from kivy.graphics import Rectangle, Color
from yaml import load
from os.path import sep, expanduser
from filebrowser import FileBrowser
from pymodbus3.client.sync import ModbusTcpClient
import os


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

        # Initialize the automation panel
        controls = AutomationPanel()
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
        self.padding = 5
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
                pressurize(client, button.valve_number)
                for child in button.walk():
                    if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.05, .5, .94, 1.0)
                    if child.id == str(button.valve_number) + "_state_label":
                        child.text = "P"

            # If the button state is False, depressurize it
            else:
                depressurize(client, button.valve_number)
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

            # Read the initial state of the button
            state = read_valve(client, register_number)

            # Update the color and label for each of the buttons
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
        """A function to pressurize all of the buttons under control of the
        program"""
        # For each button
        for button in buttons:

            # Pressurize the valve and update color and label
            pressurize(client, button.valve_number)
            for child in button.walk():
                if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.05, .5, .94, 1.0)
                if child.id == str(button.valve_number) + "_state_label":
                        child.text = "P"

    def depressurize_all_valves(self, instance):
        """A function to depressurize all of the buttons under control of the
        program"""
        # For each button
        for button in buttons:

            # Depressurize the valve and update the color and label
            depressurize(client, button.valve_number)
            for child in button.walk():
                if child.id == str(button.valve_number) + "_valve_button":
                        child.background_color = (.94, .05, .05, 1.0)
                if child.id == str(button.valve_number) + "_state_label":
                        child.text = "D"


class ValveControls(FloatLayout):
    """A class to manage the valve controls within the layout"""
    def __init__(self, *args, **kwargs):
        super(ValveControls, self).__init__(*args, **kwargs)
        self.size = (800, 530)

        # Set the background to eaither white or an image
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(source=device_image,
                      size=self.size,
                      center=self.center)

        # For each label
        for i in labels:

            # Place a button holder with and appropriate button
            button = ButtonHolder(valve_number=valves[i]["valve_number"],
                                  label=i,
                                  initial_state=valves[i]["initial_state"],
                                  x=valves[i]["x_pos"],
                                  y=valves[i]["y_pos"])

            buttons.append(button)
            self.add_widget(button)


class AutomationPanel(BoxLayout):
    """A class to contain the control panel buttons"""
    def __init__(self, *args, **kwargs):
        super(AutomationPanel, self).__init__(*args, **kwargs)

        self.orientation = "vertical"
        self.spacing = 2
        self.padding = 5
        self.size_hint_y = 0.3

        # create a dropdown with 10 buttons
        dropdown = DropDown()
        if script_folder != None:
            for index in os.listdir(script_folder):
                # when adding widgets, we need to specify the height manually (disabling
                # the size_hint_y) so the dropdown can calculate the area it needs.
                btn = Button(text=index, size_hint_y=None, height=25)

                # for each button, attach a callback that will call the select() method
                # on the dropdown. We'll pass the text of the button as the data of the
                # selection.
                btn.bind(on_release=lambda btn: dropdown.select(btn.text))

                # then add the button inside the dropdown
                dropdown.add_widget(btn)

        # create a big main button
        mainbutton = Button(text="Automation Scripts", size_hint=(1, 0.3))

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        mainbutton.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))

        layout = BoxLayout(orientation='horizontal')

        step = Label(text='Step', color=(0, 0, 0, 1.0))
        time = Label(text='0:00', color=(0, 0, 0, 1.0))

        layout.add_widget(step)
        layout.add_widget(time)

        start = Button(text="Start", size_hint=(1, 0.3),
            background_color=(.13, .56, .13, 1.0))
        pause = Button(text="Pause", size_hint=(1, 0.3),
            background_color=(.8, .8, 0, 1.0))
        stop = Button(text="Stop", size_hint=(1, 0.3),
            background_color=(.94, .05, .05, 1.0))

        self.add_widget(mainbutton)
        self.add_widget(layout)
        self.add_widget(start)
        self.add_widget(pause)
        self.add_widget(stop)


class Geppetto(App):
    """Main class for the Geppetto app"""
    def build(self):

        # Quit the program if a control file was not selected
        try:
            config_file
        except NameError:
            self.stop()

        # Open the config file and read the values
        with open(config_file, "r") as config_values:
            config = load(config_values)

        # Define global variables from the config file
        global script_folder
        global valves
        global labels
        global device_image
        global buttons
        global client

        # Pull the values from the config file and load the variables
        if "automation_scripts_folder" in config.keys():
            script_folder = config["automation_scripts_folder"]
        valves = {valve: config["valves"][valve] for valve in config["valves"]}
        labels = [key for key in valves.keys()]
        device_image = config["device_image"]
        buttons = []
        client = ModbusTcpClient(config["ip_address"])

        # Change the background to white and display the layout
        Window.clearcolor = (1, 1, 1, 1)
        layout = MainLayout()
        return layout


class ChooseConfigFile(App):
    """Main class for the config file chooser"""
    def build(self):

        # Define the user paths and home destination
        user_path = expanduser('~') + sep + 'Documents'
        browser = FileBrowser(select_string='Select',
                              favorites=[(user_path, 'Documents')])

        # Bind the action functions and load up the file browser
        browser.bind(
            on_success=self._fbrowser_success,
            on_canceled=self._fbrowser_canceled)
        return browser

    def _fbrowser_canceled(self, instance):
        """Function to close the app if canceled"""
        self.stop()

    def _fbrowser_success(self, instance):
        """Function to pass the config file into the global environment"""
        global config_file
        config_file = instance.selection[0]
        self.stop()


def change_pressure_state(instance):
    """Function to change the pressure state of the button"""

    # Find the label corresponding to the pushed button
    for child in instance.parent.walk():
        if child.id == str(instance.valve_number) + "_state_label":
            label = child

    # Change the pressure state, the color of the button, and the label
    if read_valve(client, instance.valve_number + 512):
        pressurize(client, instance.valve_number)
        instance.background_color = (.05, .5, .94, 1.0)
        label.text = "P"
    else:
        depressurize(client, instance.valve_number)
        instance.background_color = (.94, .05, .05, 1.0)
        label.text = "D"
