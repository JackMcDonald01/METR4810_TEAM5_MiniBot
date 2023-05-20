import asyncio
from bleak import BleakClient
from METR4810_robot_code.Controller import Controller # import the Controller class from Controller.py file

# Constants
MAC_ADDRESS = '58:CF:79:17:FB:32'
WRITE_CHAR_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
READ_CHAR_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

# Convert an integer list with elements in range 0 to 256 into bytearray
def convert_list_to_bytearray(data_list):
    return bytearray(data_list)

async def connect_to_robot():
    print("Connecting to Team 5's Robot")

    try:
        # Establish the connection
        async with BleakClient(MAC_ADDRESS) as robot_client:
            print("Robot Connected")

            print("Connecting to Controller")
            # Initialize the controller
            controller = Controller()  # Create an instance of Controller class

            while True:
                # Read the controller output
                controller_inputs = controller.get_normalized_values() # Call the method get_normalized_values from the controller object

                # Prepare the data to be sent
                payload = convert_list_to_bytearray(controller_inputs)

                # Transmit the data
                await robot_client.write_gatt_char(WRITE_CHAR_UUID, payload)

                # Debug output
                print('Int', controller_inputs)
                print('Hex', payload, '\n')

                # Throttle the loop
                await asyncio.sleep(0.1)


    except Exception as error:
        print("Failed to connect to Robot: ", error)
        print("Check the device MAC address and your bluetooth connection")

if __name__ == '__main__':
    asyncio.run(connect_to_robot())
