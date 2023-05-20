import time
from math import trunc
import pygame

class Controller:
    def __init__(self):
        pygame.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def stream(self):
        while True:
            pygame.event.pump()
            axes = self._get_axes_values()
            buttons = self._get_button_values()
            print(f"Axes: {axes}")
            print(f"Buttons: {buttons}")
            time.sleep(2)

    def _get_axes_values(self):
        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    def _get_button_values(self):
        return [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

    def get_normalized_values(self):
        pygame.event.pump()
        axes = [(trunc(((self.joystick.get_axis(i) + 1) / 2) * 256)) for i in range(self.joystick.get_numaxes())]
        buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]
        return axes + buttons


if __name__ == '__main__':
    controller = Controller()
    while True:
        print(controller.get_normalized_values())
        time.sleep(0.1)
