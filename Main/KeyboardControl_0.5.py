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
    def __init__(self):
        '''
            super().__init__() : 初始化父輩 (Tello)
            lr, fb, ud, yv, speed : 控制飛機的參數 (上下轉彎，前後左右，速度)
        '''
        super().__init__()
        self.lr = self.fb = self.ud = self.yv = 0
        self.speed = 50
        self.img = None
        self.tello_info = np.zeros((720, 960, 3), dtype=np.uint8)
        self.video_On = False 

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

    def print_info(self):
        '''
            print tello info , ex : battery, height, time
            Will only be referenced internally
        '''
        battery, height, get_time = self.get_info()
        InfoText = ("battery: {b}%, height: {h}, time:{t}".format(b = battery, h = height, t = get_time))
        cv2.putText(self.tello_info, InfoText, (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}".format(lr = self.lr, fb = self.fb, ud = self.ud, yv = self.yv))
        cv2.putText(self.tello_info, InfoText, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        if self.video_On:
            InfoText = ("video On!!!")
            cv2.putText(self.tello_info, InfoText, (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

    def videoRecorder(self):
        '''
            啟用錄影功能
            Will only be referenced internally
        '''            
        height, width, _ = self.img.shape
        video = cv2.VideoWriter(".//Film//video-{}.avi".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),
                                cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
        while self.video_On:
            video.write(self.img)
            time.sleep(1 / 60)
        video.release()

    def getKeyboardInput(self):
        self.lr = self.fb = self.ud = self.yv = 0

        if kp.getKey("q"): 
            self.video_On = False
            self.land()
            self.end()
            return True

        if kp.getKey("c"): 
            cv2.imwrite(".//Picture//capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),self.img)

        if kp.getKey("v"): 
            if self.video_On:
                print("The video has been started, please do not start again")
            else:
                self.video_On = True
                recorder = Thread(target=self.videoRecorder)
                recorder.start()

        if kp.getKey("b"): self.video_On = False

        if kp.getKey("r"): self.yv = self.takeoff()
        if kp.getKey("f"): self.yv = self.land()
        
        if kp.getKey("LEFT"): self.lr = -self.speed
        elif kp.getKey("RIGHT"): self.lr = self.speed

        if kp.getKey("UP"): self.fb = self.speed
        elif kp.getKey("DOWN"): self.fb = -self.speed

        if kp.getKey("w"): self.ud = self.speed
        elif kp.getKey("s"): self.ud = -self.speed

        if kp.getKey("d"): self.yv = self.speed
        elif kp.getKey("a"): self.yv = -self.speed

        self.print_info()

        self.send_rc_control(self.lr, self.fb, self.ud, self.yv)

def main():
    kp.init() # 初始化按鍵模塊
    tello = ControlTello()
    tello.connect()
    tello.streamon()

    while True:
        tello.img = tello.get_frame_read().frame
        tello.tello_info = np.zeros((720, 480, 3), dtype=np.uint8)

        if tello.getKeyboardInput(): 
            cv2.destroyAllWindows()
            break
        cv2.imshow("Drone Control Centre1", tello.img)
        cv2.imshow("Drone Control Centre2", tello.tello_info)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()

