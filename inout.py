# -- coding: utf-8 --

import RPi.GPIO as gpio
import threading
from time import sleep

pins = [36,37,38]
btns = [threading.Event() for i in range(len(pins))]
def cb(c):
    print("key down %d" % c)
    if c in pins:
        k = pins.index(c)
        btns[k].set()


def io_init():
    gpio.setmode(gpio.BOARD)
    for k in pins:
        gpio.setup(k, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(k, gpio.FALLING, bouncetime=500)
        gpio.add_event_callback(k, cb)
    print("keys",pins)
    print("io module loaded")


if __name__ == "__main__":
    print("gpio test")
    io_init()
    while True:
        sleep(1)
