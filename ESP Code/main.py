from machine import Pin, PWM
import ubluetooth

# Constants to denote different events
_IRQ_CENTRAL_CONNECT = 1
_IRQ_CENTRAL_DISCONNECT = 2
_IRQ_GATTS_WRITE = 3

class ESP32_BLE():
    def __init__(self, name):
        # Initialize instance variables
        self.message = []  # Stores the incoming message
        self.name = name  # Name of the BLE server
        self.ble = ubluetooth.BLE()  # BLE instance
        self.ble.active(True)  # Activate the BLE
        self.ble.irq(self.ble_irq)  # Set the BLE interrupt request handler
        self.register()  # Register services and characteristics
        self.advertiser()  # Start advertising the BLE server
        self.connection = 0  # Track the connection status

    def get_msg(self):
        # Return the message if there's one, else return 0
        return self.message if self.message != [] else 0

    def messageDecoder(self, message):
        # Decode the incoming message from bytes to an integer list
        return [i for i in message]

    def ble_irq(self, event, data):
        # Event handler for BLE actions
        if event == _IRQ_CENTRAL_CONNECT:
            # Connection established
            self.connection = 1
            print("Connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # Connection lost
            self.connection = 0
            self.advertiser()
            print("Disconnected")
        elif event == _IRQ_GATTS_WRITE:
            # Data written to characteristic
            buffer = self.ble.gatts_read(self.rx)
            self.message = self.messageDecoder(buffer)
            print(self.message, "\n")

    def register(self):
        # Register the GATT server and its characteristics
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,)
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        # Send a notification to the client with the given data
        self.ble.gatts_notify(24, self.tx, data + '\n')

    def advertiser(self):
        # Start advertising the BLE server
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray(bytes.fromhex('020102')) + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        print(adv_data)
        print("\r\n")
        
class DCMotorController:
    def __init__(self):
        # Motor Pins setup
        self.IN1A = PWM(Pin(6))
        self.IN1B = PWM(Pin(5))
        self.IN2A = PWM(Pin(10))
        self.IN2B = PWM(Pin(1))
        self.STBY = Pin(4, Pin.OUT)  # Standby pin
        self.STBY.value(1)  # Enable motor controller by default

    def scale_speed(self, speed):
        # Convert speed from 0-255 to 0-1023
        return int(speed * 1023 / 255)

    def direction(self, forward, reverse):
        # Determine direction based on forward and reverse signals
        return forward if forward >= reverse else -reverse

    def motor1(self, speed):
        # Control motor 1 with the given speed
        speed = self.scale_speed(speed)
        if speed >= 0:
            self.IN1A.duty(speed)
            self.IN1B.duty(0)
        else:
            self.IN1A.duty(0)
            self.IN1B.duty(-speed)

    def motor2(self, speed):
        # Control motor 2 with the given speed
        speed = self.scale_speed(speed)
        if speed >= 0:
            self.IN2A.duty(speed)
            self.IN2B.duty(0)
        else:
            self.IN2A.duty(0)
            self.IN2B.duty(-speed)

    def standby(self, state):
        # Set the motor controller into standby mode
        self.STBY.value(state)
        
    def bias(self, joystick):
        # Determine motor bias based on joystick position
        left = joystick / 255
        right = (255 - joystick) / 255
        return (left,right)
    
    def spin(self, left, right):
        # This method controls spinning motion based on the given left and right signals
        # If the left signal is active, the robot spins to the left by rotating the motors in opposite directions
        # If the right signal is active, the robot spins to the right by rotating the motors in opposite directions
        if left == 1 and right == 0:
            self.motor1(255)
            self.motor2(-255)
        elif left == 0 and right == 1:
            self.motor1(-255)
            self.motor2(255)


if __name__ == "__main__":
    ble = ESP32_BLE("Team5")
    controller = DCMotorController()
    while True:
        message = ble.get_msg()
        # We process the message only if we received one and its length is at least 2.
        if message != 0 and len(message) >= 2:  
            # Determine the speed direction based on the 5th and 4th element of the received message
            speed = controller.direction(message[5],message[4])
            # Calculate motor bias based on the first element of the message (joystick position)
            bias = controller.bias(message[0])
            # Apply calculated speed and bias to control the motors
            controller.motor1(speed*bias[0])
            controller.motor2(speed*bias[1])
            # Trigger the spin action based on the 15th and 16th elements of the received message
            controller.spin(message[15],message[16])
