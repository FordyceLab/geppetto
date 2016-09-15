def pressurize(valve_number):
    """Function to pressurize the valve of a given number"""

    # Offset the register number
    register_number = 512 + valve_number

    # Read the state of the valve in question
    state = client.read_coils(register_number, 1).bits[0]

    # Valve is currently depressurized if the register state is True
    if state:
        client.write_coil(valve_number, False)


def depressurize(valve_number):
    """Function to depressurize the valve of a given number"""

    # Offset the register number
    register_number = 512 + valve_number

    # Read the state of the valve in question
    state = client.read_coils(register_number, 1).bits[0]

    # Valve is currently pressurized if the register state is False
    if not state:
        client.write_coil(valve_number, True)


def read_valve(register_number):
    """Functiont to read a specific register number"""
    return client.read_coils(register_number, 1).bits[0]
