#from pyglet import input

#devices = input.get_joysticks()

#print(devices)

import pygame_test
import time

pygame.joystick.init()

count = pygame.joystick.get_count()

index = count - 1
while index >= 0:
    print()
    print(pygame.joystick.Joystick(index).get_name() + ", " + str(
        pygame.joystick.Joystick(index).get_numaxes()) + ", " + str(index))
    index = index - 1

pygame.joystick.Joystick(0).rumble(1, 1, 0)

while True:
    a = pygame.joystick.Joystick(3).get_axis(0)
    b = pygame.joystick.Joystick(3).get_axis(1)
    c = pygame.joystick.Joystick(3).get_axis(2)
    d = pygame.joystick.Joystick(3).get_axis(3)
    e = pygame.joystick.Joystick(3).get_axis(4)
    f = pygame.joystick.Joystick(3).get_axis(5)
    g = pygame.joystick.Joystick(3).get_axis(6)
    h = pygame.joystick.Joystick(3).get_axis(7)
    print(a, b, c, d, e, f, g, h)
    time.sleep(0.5)
