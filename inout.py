# -- coding: utf-8 --

import RPi.GPIO as gpio
import threading
from time import sleep

pin_capture = 37
pin_print = 38

btn_capture = threading.Event()
btn_print = threading.Event()


def cb(c):
    print("key down %d" % c)
    if c == pin_capture:
        btn_capture.set()
    if c == pin_print:
        btn_print.set()


def io_init():
    gpio.setmode(gpio.BOARD)
    gpio.setup(pin_print, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(pin_print, gpio.FALLING, bouncetime=500)
    gpio.add_event_callback(pin_print, cb)
    gpio.setup(pin_capture, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.add_event_detect(pin_capture, gpio.FALLING, bouncetime=500)
    gpio.add_event_callback(pin_capture, cb)
    print("io module loaded")


if __name__ == "__main__":
    print("gpio test")
    io_init()
    while True:
        sleep(1)
