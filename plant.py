# -- coding: utf-8 --

import sys
import threading
import cv2
import numpy as np
from ctypes import *
import datetime
#can't use relative path
sys.path.append("/opt/MVS/Samples/aarch64/Python/MvImport")
from MvCameraControl_class import *
import time
import json
from gps import gps_init, gpsInfo
from sensor import sensor_init, read_temp, getserial
from inout import io_init, btn_capture, btn_print
from filenum import get_cur_num

g_bExit = False
save_path = "/home/pi/Desktop/data/"


# first need to set the cam image format to rgb8 24bit, default is yuv 16bit
# img_w=3072
# img_h=2048
img_w=5472
img_h=3648
img_c=3
dev_id = getserial()
cur_num = get_cur_num()

def app_init():
    io_init()
    print("DEV ID:[%s]"%dev_id)
    gps_init()
    sensor_init()
#opencv转换显示
def work_thread(cam=0, pData=0, nDataSize=0):
    global cur_num
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
    cv2.namedWindow("preview", cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("preview", 800, 480)
    cv2.setWindowProperty("preview",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN) #fullscreen
    t,h = read_temp()
    idx = 0
    while True:
        ret = cam.MV_CC_GetOneFrameTimeout(pData, nDataSize, stFrameInfo, 1000)
        temp = np.asarray(pData)
        temp = temp.reshape((img_h, img_w, img_c))
        raw = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB) #default is bgr
        preview = cv2.resize(raw, (800, 480), interpolation=cv2.INTER_AREA) # for show
        if idx % 10 == 0: # 1sec update
            t,h = read_temp()
            pass

        cv2.putText(preview, '%s%04d'%(datetime.datetime.now().strftime("%Y%m%d"),cur_num), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0xff, 0xff, 0xff), 2)
        if "north" in gpsInfo:
            cv2.putText(preview, '    N:%.3f'%gpsInfo["north"], (500, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0xcc, 0x99), 2)
        if "east" in gpsInfo:
            cv2.putText(preview, '    E:%.3f'%gpsInfo["east"], (500, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0xcc, 0x99), 2)
        
        cv2.putText(preview, ' TEMP:%.1f C'%t, (500, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0xcc, 0x99), 2)
        cv2.putText(preview, 'Humid:%.1f %%'%h, (500, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0xcc, 0x99), 2)
        if btn_capture.is_set():
            cv2.putText(preview, 'captured!', (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (50, 50, 255), 5)
            file ="%s%04d"%(datetime.datetime.now().strftime('%Y%m%d'),cur_num)
            cv2.imwrite(save_path + file + ".jpg",raw)
            j = {}
            j["device_id"] = dev_id
            j["record_time"] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            j["east"] = gpsInfo["east"]
            j["north"] = gpsInfo["north"]
            j["temperature(C)"] = t
            j["humidity(%)"] = h
            j["image_name"] = file + ".jpg"
            with open("%s%s.txt"%(save_path,file),"w") as f:
                json.dump(j, f, indent=2)
            cur_num+=1
            btn_capture.clear()
        if btn_print.is_set():
            cv2.putText(preview, 'print!', (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 3, (50, 50, 255), 5)
            btn_print.clear()
        if g_bExit == True:
            break
        cv2.imshow('preview', preview)
        k = cv2.waitKey(500) & 0xff
        if k == ord('q'):
            cv2.destroyAllWindows()
            break
        idx+=1

if __name__ == "__main__":
 
    SDKVersion = MvCamera.MV_CC_GetSDKVersion()
    print ("SDKVersion[0x%x]" % SDKVersion)
 
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
     
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print ("enum devices fail! ret[0x%x]" % ret)
        sys.exit()
 
    if deviceList.nDeviceNum == 0:
        print ("find no device!")
        sys.exit()
 
    print ("Find %d devices!" % deviceList.nDeviceNum)
 
    nConnectionNum = 0 # default select
 
    if int(nConnectionNum) >= deviceList.nDeviceNum:
        print ("intput error!")
        sys.exit()
 
    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()
     
    # ch:选择设备并创建句柄| en:Select device and create handle
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents
 
    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print ("create handle fail! ret[0x%x]" % ret)
        sys.exit()
 
    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print ("open device fail! ret[0x%x]" % ret)
        sys.exit()
    # ch:设置触发模式为off | en:Set trigger mode as off
    ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
    if ret != 0:
        print ("set trigger mode fail! ret[0x%x]" % ret)
        sys.exit()
 
    # ch:获取数据包大小 | en:Get payload size
    stParam =  MVCC_INTVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
     
    ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
    if ret != 0:
        print ("get payload size fail! ret[0x%x]" % ret)
        sys.exit()
    nPayloadSize = stParam.nCurValue
    # nPayloadSize = img_c*img_h*img_w
    # print(stParam.nCurValue)
    # ch:开始取流 | en:Start grab image
    ret = cam.MV_CC_StartGrabbing()
    if ret != 0:
        print ("start grabbing fail! ret[0x%x]" % ret)
        sys.exit()
    data_buf = (c_ubyte * nPayloadSize)()
    app_init()
    try:
        hThreadHandle = threading.Thread(target=work_thread, args=(cam, data_buf, nPayloadSize))
        hThreadHandle.start()
    except:
        print ("error: unable to start thread")
    print ("press a key to stop grabbing.")
    hThreadHandle.join()
    print("user exit")
    # ch:停止取流 | en:Stop grab image
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print ("stop grabbing fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    # ch:关闭设备 | Close device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print ("close deivce fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    # ch:销毁句柄 | Destroy handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print ("destroy handle fail! ret[0x%x]" % ret)
        del data_buf
        sys.exit()
 
    del data_buf