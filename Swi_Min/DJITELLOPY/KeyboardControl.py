import time
import cv2
from djitellopy import Tello
import KeyPressModule as kp
from time import sleep

kp.init() # 初始化按鍵模塊
tello = Tello()
tello.connect()
tello.streamon()
sleep(5)

def get_info():
    battery = tello.get_battery()
    if type(battery) != bool:
        battery = battery.replace("\n", "").replace("\r", "")

    height = tello.get_height()
    if type(height) != bool:
        # 1dm(公寸) = 10cm 
        height = height.replace("\n", "").replace("\r", "")

    get_time = time.strftime("%H:%M:%S",time.localtime())

    return battery, height, get_time

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey("q"): return True

    # e 拍照
    if kp.getKey("e"): 
        cv2.imwrite(".//capture//capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),img)

    # r 是起飛 f 是降落
    if kp.getKey("r"): yv = tello.takeoff()
    if kp.getKey("f"): yv = tello.land()
    
    # 上下左右鍵對飛機下前後左右指令
    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    # wsad鍵對飛機下升降轉向指令
    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("d"): yv = speed
    elif kp.getKey("a"): yv = -speed

    # 在畫面中顯示飛機的資訊
    battery, height, get_time = get_info()
    InfoText = ("battery: {b}%, height: {h}, time:{t}".format(b = battery, h = height, t = get_time))
    cv2.putText(img, InfoText, (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

    InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}".format(lr = lr, fb = fb, ud = ud, yv = yv))
    cv2.putText(img, InfoText, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

    tello.send_rc_control(lr, fb, ud, yv)

while True:
    img = tello.get_frame_read().frame
    img = cv2.resize(img, (720, 480))
    if getKeyboardInput() == True: 
        tello.land()    # 因為end()裡面的land()沒有作用
        tello.end()
        break
    cv2.imshow("Drone Control Centre", img)
    cv2.waitKey(1)

# control tello
# q 退出
# e 拍照
# r 起飛 f 降落
# 上下左右 --> 前後左右
# wsad --> 升降轉向
