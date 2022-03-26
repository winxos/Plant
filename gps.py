# -- coding: utf-8 --

import serial  # 导入模块
import threading
from time import sleep
gpsInfo = {}
gpsInfo["east"] = round(103, 3)
gpsInfo["north"] = round(30, 3)
gpsInfo["error"] = threading.Event()
gpsInfo["connected"] = False

def work_thread():
    while True:
        try:
            ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=t)
            data = ser.readline().decode("utf8")
            # $GNRMC,034820.000,A,3046.6637,N,10355.7521,E,0.00,187.68,230222,,,D*7D\r\n
            if data.startswith("$GNRMC"):
                g = data.split(",")
                v = g[2]
                if v == "A":
                    n = g[3]
                    e = g[5]
                    nf = int(float(n) / 100) + \
                        round((float(n) % 100) / 60, 3)
                    ne = int(float(e) / 100) + \
                        round((float(e) % 100) / 60, 3)
                    # print("DATE:%s N: %.3f E: %.3f" %(uu , nf , ne))
                    gpsInfo["east"] = nf
                    gpsInfo["north"] = ne
                    utct = g[1]
                    utcd = g[9]
                    uu = utcd[4:6] + utcd[2:4] + utcd[0:2]
                    gpsInfo["date"] = uu
                    gpsInfo["connected"] = True
                else:
                    gpsInfo["connected"] = False
            ser.close()  # 关闭串口
        except Exception as e:
            gpsInfo["error"].set()
        sleep(1)

def gps_init():
    hThreadHandle = threading.Thread(target=work_thread,daemon=True)
    hThreadHandle.start()
    print("gps thread start")


if __name__ == "__main__":
    print("gps test")
    gps_init()
    while True:
        print(gpsInfo)
        sleep(1)
