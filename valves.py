from pymodbus3.client.sync import ModbusTcpClient

# client = ModbusTcpClient('127.0.0.1')
client = ModbusTcpClient('192.168.1.3')


def pressurize(valve_number):
    register_number = 512 + valve_number
    # state = client.read_coils(register_number, 1).bits[0]
    state = True
    if state:
        pass
        # client.write_coil(valve_number, False)


def depressurize(valve_number):
    register_number = 512 + valve_number
    # state = client.read_coils(register_number, 1).bits[0]
    state = False
    if not state:
        pass
        # client.write_coil(valve_number, True)

def startup():
    for i in range(48):
        client.write_coil(i, True)
