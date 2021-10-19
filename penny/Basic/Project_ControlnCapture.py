from djitellopy import Tello
import DJIKeyPressModule as kp
import time
import cv2
# 透過按鍵對飛機下指令
# 36:29

kp.init()
tello = Tello()
tello.connect()
global img
tello.streamon()

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50

    # 上下左右鍵對飛機下前後左右指令
    if kp.getKey("LEFT"): lr = -speed
    elif kp.getKey("RIGHT"): lr = speed

    if kp.getKey("UP"): fb = speed
    elif kp.getKey("DOWN"): fb = -speed

    # wsad鍵對飛機下上下轉向指令
    if kp.getKey("w"): ud = speed
    elif kp.getKey("s"): ud = -speed

    if kp.getKey("a"): yv = speed
    elif kp.getKey("d"): yv = -speed

    # q 是起飛 e 是降落
    if kp.getKey("q"): yv = tello.takeoff()
    if kp.getKey("e"): yv = tello.land(); time.sleep(3)

    # 路徑記得改
    if kp.getKey('z'):
        cv2.imwrite(f'./Resources/Images1020_30/{time.time()}.jpg', img)
        time.sleep(0.3)

    return [lr, fb, ud, yv]


while True:
    
    vals = getKeyboardInput()
    tello.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    img = tello.get_frame_read().frame
    img = cv2.resize(img, (960, 720))       #small size of frame to be faster
    cv2.imshow("Image", img)
    cv2.waitKey(1)
