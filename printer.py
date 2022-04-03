# -- coding: utf-8 --
import serial
def serial_hex(ser, n):
    ser.write(bytearray(n))
def build_qrcode(s):
    b = [0x1d,0x6b,0x20,0x01,0x02]
    for c in s:
        b.append(ord(c))
    b.append(0)
    return b
def print_info(s,qr):
    ser = serial.Serial("/dev/ttyAMA0", 9600) #serial 0
    serial_hex(ser, [0x1b,0x40]) #init
    serial_hex(ser, [0x1d,0x57,0x05]) #mag
    serial_hex(ser, [0x1d,0x51,0x00,0x00]) #loc
    serial_hex(ser, build_qrcode(qr))
    serial_hex(ser, [0x0d]) #\n
    serial_hex(ser, [0x1b,0x58,0x02,0x02]) #char size
    ser.write(s.encode('gbk'))
    serial_hex(ser, [0x1b,0x69]) #next page
if __name__ == "__main__":
    print("printer test")
    print_info("你好 world","202203040001")