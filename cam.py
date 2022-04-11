import os.path
import sys

#os imigrade
if os.path.exists("/opt/MVS/Samples/armhf"):
    #can't use relative path
    sys.path.append("/opt/MVS/Samples/armhf/Python/MvImport")
elif os.path.exists("/opt/MVS/Samples/aarch64"):
    sys.path.append("/opt/MVS/Samples/aarch64/Python/MvImport")
else:
    print("camara driver package is missing, cam exit.")
    exit
from MvCameraControl_class import *
from time import sleep
import threading
import numpy as np
import cv2
from inout import btns
camInfo ={}
camInfo["error"] = threading.Event()
CAM_W=5472
CAM_H=3648
def get_cam():
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
     
    # ch:枚举设备 | en:Enum device
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0:
        print ("enum devices fail! ret[0x%x]" % ret)
        return None
 
    if deviceList.nDeviceNum == 0:
        print ("camera not found!")
        return None
 
    print ("Find %d devices!" % deviceList.nDeviceNum)
 
    nConnectionNum = 0 # default select
 
    # ch:创建相机实例 | en:Creat Camera Object
    cam = MvCamera()
     
    # ch:选择设备并创建句柄| en:Select device and create handle
    stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents
 
    ret = cam.MV_CC_CreateHandle(stDeviceList)
    if ret != 0:
        print ("create handle fail! ret[0x%x]" % ret)
        return None
 
    # ch:打开设备 | en:Open device
    ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
    if ret != 0:
        print ("open device fail! ret[0x%x]" % ret)
        return None
    return cam
def get_cam_imageload(cam):
    # ch:获取数据包大小 | en:Get payload size
    stParam =  MVCC_INTVALUE()
    memset(byref(stParam), 0, sizeof(MVCC_INTVALUE))
     
    ret = cam.MV_CC_GetIntValue("PayloadSize", stParam)
    if ret != 0:
        print ("get payload size fail! ret[0x%x]" % ret)
        sys.exit()
    p = stParam.nCurValue
    ret = cam.MV_CC_GetIntValue("Width", stParam)
    if ret != 0:
        print ("get Width size fail! ret[0x%x]" % ret)
        sys.exit()
    w = stParam.nCurValue
    ret = cam.MV_CC_GetIntValue("Height", stParam)
    if ret != 0:
        print ("get Height size fail! ret[0x%x]" % ret)
        sys.exit()
    h = stParam.nCurValue
    return (p,w,h)
def cam_release(cam):
    # ch:停止取流 | en:Stop grab image
    ret = cam.MV_CC_StopGrabbing()
    if ret != 0:
        print ("stop grabbing fail! ret[0x%x]" % ret)
 
    # ch:关闭设备 | Close device
    ret = cam.MV_CC_CloseDevice()
    if ret != 0:
        print ("close deivce fail! ret[0x%x]" % ret)
 
    # ch:销毁句柄 | Destroy handle
    ret = cam.MV_CC_DestroyHandle()
    if ret != 0:
        print ("destroy handle fail! ret[0x%x]" % ret)

def work_thread():
    camInfo["preview"] = np.zeros((480,800, 3), np.uint8)
    idx = 0
    while True:
        sleep(1)
        cam = get_cam() #check online
        if not cam:
            camInfo["error"].set()
            continue
        print("camera online")
        # cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_OFF)
        sz,CAM_W,CAM_H = get_cam_imageload(cam)
        print("payload:%d,width:%d,height:%d"%(sz,CAM_W,CAM_H))
        cam.MV_CC_StartGrabbing() # ch:开始取流 | en:Start grab image
        pData = (c_ubyte * sz)()
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
        while True:
            ret = cam.MV_CC_GetOneFrameTimeout(pData, sz, stFrameInfo, 1000)
            if ret !=0: # error
                print("camera offline")
                camInfo["error"].set()
                cam_release(cam)
                break
            camInfo["error"].clear()
            temp = np.asarray(pData)
            temp = temp.reshape((CAM_H, CAM_W, 3))
            raw = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB) #default is bgr
            camInfo["raw"] = raw
            if btns[0].is_set():
                idx += 1
                btns[0].clear()
            if idx % 2 != 0:
                camInfo["preview"] = raw[CAM_H//2-240:CAM_H//2+240,CAM_W//2-400:CAM_W//2+400] # mid area
            else:
                camInfo["preview"] = cv2.resize(raw, (800, 480), interpolation=cv2.INTER_AREA) # small
            sleep(1)
        del pData

def cam_init():
    print("cam init")
    h = threading.Thread(target=work_thread,daemon=True)
    h.start()
    return h

if __name__ == "__main__":
    print("cam test")
    h = cam_init()
    while True:
        print("camera state: %d"%camInfo["error"].is_set())
        sleep(5)