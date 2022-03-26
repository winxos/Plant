# -- coding: utf-8 --

import smbus
from time import sleep
import threading

sensorInfo ={}
sensorInfo["temp"]=20.0
sensorInfo["humid"]=50.0
sensorInfo["error"] = threading.Event()
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

def work_thread():
    addr = 0x44
    try:
        i2c = smbus.SMBus(0)
        i2c.write_byte_data(addr, 0x23, 0x34)
    except:
        print("i2c device not found")
    sleep(1)
    while True:
        sensorInfo["error"].clear()
        try:
            i2c.write_byte_data(addr, 0xe0, 0x0)
            data = i2c.read_i2c_block_data(addr, 0x0, 6)
            rawT = ((data[0]) << 8) | (data[1])
            rawR = ((data[3]) << 8) | (data[4])
            sensorInfo["temp"] = round(-45 + rawT * 175 / 65535, 2)
            sensorInfo["humid"] = round(100 * rawR / 65535, 2)
        except:
            sensorInfo["error"].set()
            try:
                i2c = smbus.SMBus(0)
                i2c.write_byte_data(addr, 0x23, 0x34)
            except:
                pass
        sleep(1)
    
def sensor_init():
    hThreadHandle = threading.Thread(target=work_thread,daemon=True)
    hThreadHandle.start()
    sensorInfo["cpuid"]=getserial()
    print("sensorInfo thread start")
    print("cpuid:%s"%sensorInfo["cpuid"])

if __name__ == "__main__":
    print("sensorInfo test")
    sensor_init()
    while True:
        print("temp:%s humid:%s"%(sensorInfo["temp"],sensorInfo["humid"]))
        sleep(1)
