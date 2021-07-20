import time
import cv2
from djitellopy import Tello
import KeyPressModule as kp
from time import sleep

tello = Tello()
tello.connect()
tello.streamon()
# tello.LOGGER.setLevel(logging.ERROR)    # 只顯示錯誤訊息
kp.init()                                 # 初始化按鍵模塊
sleep(5)
quit = False

# 初始化顯示文字
# 字型
font = cv2.FONT_HERSHEY_DUPLEX
# 大小
font_size = 0.5
# 顏色 BGR
font_colour = (0, 170, 255) # 銘黃色
# 線條寬度
font_width = 1
# 線條種類
font_type = cv2.LINE_AA

def get_info():
    battery = tello.get_battery()
    if type(battery) != bool:
        battery = battery.replace("\n", "").replace("\r", "")

    height = tello.get_height()
    if type(height) != bool:
        # 1dm = 10cm 
        # 因為每次出問題都是這段，應該是返回值與我預期不同導致，所以我決定保留 dm 不換成 cm
        height = height.replace("\n", "").replace("\r", "")

    get_time = time.strftime("%H:%M:%S",time.localtime())

    return battery, height, get_time

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    if kp.getKey("q"): quit = True

    if kp.getKey("e"): 
        cv2.imwrite("./capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),img)

    # r 是起飛 f 是降落
    if kp.getKey("r"): yv = tello.takeoff()
    if kp.getKey("f"): yv = tello.land()
    
    # control tello
    # 上下左右鍵對飛機下前後左右指令
    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    # wsad鍵對飛機下升降轉向指令
    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("a"): yv = speed
    elif kp.getKey("d"): yv = -speed

    # 在畫面中顯示飛機的資訊
    battery, height, get_time = get_info()
    InfoText = ("battery: {b}%, height: {h}, time:{t}"
                .format(b = battery, h = height, t = get_time))
    cv2.putText(img, InfoText, (10, 20), font, font_size, font_colour, font_width, font_type)
    InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}"
                .format(lr = lr, fb = fb, ud = ud, yv = yv))
    cv2.putText(img, InfoText, (10, 40), font, font_size, font_colour, font_width, font_type)

    tello.send_rc_control(lr, fb, ud, yv)

while True:
    img = tello.get_frame_read().frame
    img = cv2.resize(img, (720, 480))
    getKeyboardInput()
    cv2.imshow("Drone Control Centre", img)
    cv2.waitKey(1)

    if quit == True: 
        tello.land()
        sleep(0.5)
        tello.streamoff()
        sleep(0.5)
        tello.end()
        break
