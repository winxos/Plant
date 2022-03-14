# -- coding: utf-8 --

import smbus
from time import sleep
i2c = None
addr = 0x44


def read_temp():
    temp = 20.0
    RH = 50.0
    try:
        i2c.write_byte_data(addr, 0xe0, 0x0)
        data = i2c.read_i2c_block_data(addr, 0x0, 6)
        rawT = ((data[0]) << 8) | (data[1])
        rawR = ((data[3]) << 8) | (data[4])
        temp = round(-45 + rawT * 175 / 65535, 2)
        RH = round(100 * rawR / 65535, 2)
    except:
        pass
    return (temp, RH)


def getserial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/sys/firmware/devicetree/base/serial-number', 'r')
        cpuserial = f.readline()[:-1]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial


def sensor_init():
    try:
        i2c = smbus.SMBus(0)
        i2c.write_byte_data(addr, 0x23, 0x34)
    except:
        pass


if __name__ == "__main__":
    print("sensor test")
    print("dev id: %s"%getserial())
    sensor_init()
    while True:
        print(read_temp())
        sleep(1)
