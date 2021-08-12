# 目前有個 BUG 就是錄出來的影片有時會夾雜著，飛機顯示的資訊
'''
control tello
    q 退出
    c 拍照
    v 錄影 b 結束錄影
    r 起飛 f 降落
    上下左右 --> 前後左右
    wsad --> 升降轉向
'''
import cv2
import time
import numpy as np
import KeyPressModule as kp
from djitellopy import Tello
from threading import Thread

class ControlTello(Tello):
    # Class Level : Class層的參數是被所有有初始化 Class 的 Instances 使用，
    # 也就是說當數值改變時其他的 Instance 裡的 Class Level 參數也會跟著改變
    # IMG = None
    # VIDEO = None
    def __init__(self):
        super().__init__()      
        # Instance Level : Instance 作用域只會在初始化後的那個物件身上 
        self.video_On = False 
        self.IMG = np.zeros((720, 960, 3))
        self.VIDEO = self.IMG

    def get_info(self):
        '''
            get battery, height, time
            Will only be referenced internally
        '''
        battery = self.get_battery()
        if type(battery) != bool:
            battery = battery.replace("\n", "").replace("\r", "")

        height = self.get_height()
        if type(height) != bool:
            # 1dm(公寸) = 10cm 
            height = height.replace("\n", "").replace("\r", "")

        get_time = time.strftime("%H:%M:%S",time.localtime())

        return battery, height, get_time

    def videoRecorder(self):
        '''
            啟用錄影功能
            Will only be referenced internally
        '''            
        # create a VideoWrite object, recoring to ./video.avi
        height, width, _ = self.VIDEO.shape
        print(height, width,"+++++++++++++++++++++++++++++++++++++++++++++++++")
        video = cv2.VideoWriter(".//Film//video-{}.avi".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),
                                cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
        while self.video_On:
            video.write(self.VIDEO)
            time.sleep(1 / 60)
        video.release()

    def getKeyboardInput(self):
        lr, fb, ud, yv = 0, 0, 0, 0
        speed = 50

        if kp.getKey("q"): 
            self.video_On = False
            self.land()
            self.end()
            return True

        # c 拍照
        if kp.getKey("c"): 
            cv2.imwrite(".//Picture//capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),self.IMG)

        if kp.getKey("v"): 
            if self.video_On:
                print("The video has been started, please do not start again")
            else:
                self.video_On = True
                recorder = Thread(target=self.videoRecorder)
                recorder.start()

        if kp.getKey("b"): 
            self.video_On = False

        # r 是起飛 f 是降落
        if kp.getKey("r"): yv = self.takeoff()
        if kp.getKey("f"): yv = self.land()
        
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
        battery, height, get_time = self.get_info()
        InfoText = ("battery: {b}%, height: {h}, time:{t}".format(b = battery, h = height, t = get_time))
        cv2.putText(self.IMG, InfoText, (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}".format(lr = lr, fb = fb, ud = ud, yv = yv))
        cv2.putText(self.IMG, InfoText, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        if self.video_On:
            InfoText = ("video On!!!")
            cv2.putText(self.IMG, InfoText, (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)


        self.send_rc_control(lr, fb, ud, yv)

def main():
    kp.init() # 初始化按鍵模塊
    tello = ControlTello()
    tello.connect()
    tello.streamon()
    # time.sleep(5)

    while True:
        tello.IMG = tello.get_frame_read().frame

        if tello.video_On:
            tello.VIDEO = tello.get_frame_read().frame
            
        if tello.getKeyboardInput(): 
            break
        cv2.imshow("Drone Control Centre1", tello.IMG)
        cv2.imshow("Drone Control Centre2", tello.VIDEO)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()

