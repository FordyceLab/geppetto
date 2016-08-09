from pymodbus3.client.sync import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1')


def pressurize(valve_number):
    state = client.read_coils(valve_number, 1)
    if state.bits[0]:
        client.write_coil(1, False)


def depressurize(valve_number):
    state = client.read_coils(valve_number, 1)
    if not state.bits[0]:
        client.write_coil(1, True)
