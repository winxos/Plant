# -- coding: utf-8 --

import serial  # 导入模块
import queue
from threading import Thread
from time import sleep
gpsInfo = {}


class wGps(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        gpsInfo["east"] = round(103, 3)
        gpsInfo["north"] = round(30, 3)
        try:
            # 端口，GNU / Linux上的/ dev / ttyUSB0 等 或 Windows上的 COM3 等
            portx = "/dev/ttyUSB0"
            # 波特率，标准值之一：50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,19200,38400,57600,115200
            bps = 9600
            # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
            timex = 5
            # 打开串口，并得到串口对象
            ser = serial.Serial(portx, bps, timeout=timex)

            while True:
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
                sleep(0.1)
            ser.close()  # 关闭串口

        except Exception as e:
            print("err:", e)


def gps_init():
    g = wGps()
    g.start()


if __name__ == "__main__":
    print("gps test")
    gps_init()
    while True:
        print(gpsInfo)
        sleep(1)
