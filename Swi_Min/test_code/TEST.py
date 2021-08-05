'''
control tello
    q 退出
    c 拍照
    v 錄影 b 結束錄影
    r 起飛 f 降落
    上下左右 --> 前後左右
    wsad --> 升降轉向
'''
import time
import cv2
import KeyPressModule as kp
from djitellopy import Tello
from djitellopy import BackgroundFrameRead
from threading import Thread


class ControlTello(Tello):
    def __init__(self):
        super().__init__()        

    def getKeyboardInput(self):
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 50
        
        if kp.getKey("q"): 
            # if self.video_on:
            #     self.video_on = False
            return True

        # r 是起飛 f 是降落
        if kp.getKey("r"): yv = self.takeoff()
        if kp.getKey("f"): yv = self.land()

        self.send_rc_control(lr, fb, ud, yv)

def main():
    kp.init() # 初始化按鍵模塊
    tello = ControlTello()
    tello.connect()
    tello.streamon()
    time.sleep(5)

    while True:
        img = tello.get_frame_read().frame
        img = cv2.resize(img, (720, 480))
        if tello.getKeyboardInput() == True: 
            tello.land()    # 因為end()裡面的land()沒有作用，原因不明
            tello.end()
            break
        cv2.imshow("Drone Control Centre", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()

'''
有一點點眉目嘞
繼承TELLO這個東東，然後要大量改寫......


'''