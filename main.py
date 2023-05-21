import asyncio
import time
from math import trunc
import pygame
from bleak import BleakClient

# Device MAC address and UUIDs for BLE GATT services
MAC_ADDRESS = '58:CF:79:17:FB:32'
WRITE_CHAR_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
READ_CHAR_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

class Controller:
    def __init__(self):
        # Initialize Pygame and joystick
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    # Method to return the joystick object
    def get_joystick(self):
        return self.joystick

    # Stream joystick data for debugging
    def stream(self):
        while True:
            pygame.event.pump()
            axes = self._get_axes_values()
            buttons = self._get_button_values()
            print(f"Axes: {axes}")
            print(f"Buttons: {buttons}")
            time.sleep(2)

    # Private method to read axis values from the joystick
    def _get_axes_values(self):
        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    # Private method to read button values from the joystick
    def _get_button_values(self):
        return [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

    # Read and normalize joystick data for transmission
    def get_normalized_values(self):
        pygame.event.pump()
        axes = [(trunc(((self.joystick.get_axis(i) + 1) / 2) * 256)) for i in range(self.joystick.get_numaxes())]
        buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]
        return axes + buttons

# Utility function to convert list of integers into a bytearray for transmission
def convert_list_to_bytearray(data_list):
    return bytearray(data_list)

# Main coroutine to handle BLE communication
async def connect_to_robot():
    print("Connecting to Team 5's Robot")

    try:
        # Connect to BLE device and maintain connection in this context
        async with BleakClient(MAC_ADDRESS) as robot_client:
            print("Robot Connected")

            print("Connecting to Controller")
            controller = Controller()

            while True:
                controller_inputs = controller.get_normalized_values()

                payload = convert_list_to_bytearray(controller_inputs)

                await robot_client.write_gatt_char(WRITE_CHAR_UUID, payload)

                print('Int', controller_inputs)
                print('Hex', payload, '\n')

                await asyncio.sleep(0.1)

    except Exception as error:
        print("Failed to connect to Robot: ", error)
        print("Check the device MAC address and your bluetooth connection")

if __name__ == '__main__':
    asyncio.run(connect_to_robot())
