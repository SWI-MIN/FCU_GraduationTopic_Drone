'''
    control tello
        q 退出
        c 拍照
        v 錄影 b 結束錄影
        r 起飛 f 降落
        上下左右 --> 前後左右
        wsad --> 升降轉向
        n 開始導航
        m 取消導航，接管飛機
    畫面大小 : (960, 720)  寬 * 高 OR (720, 960)  高 * 寬
'''
import queue
import pygame
import cv2
import time
import numpy as np
from djitellopy import Tello
from threading import Thread


class ControlTello(Tello):
    def __init__(self, control_queue, take_over):
        '''
            super().__init__() : 初始化父輩 (Tello)
            lr, fb, ud, yv, speed : 控制飛機的參數 (上下轉彎，前後左右，速度)
        '''
        super().__init__()
        self.lr = self.fb = self.ud = self.yv = 0
        self.speed = 50
        self.width = 960
        self.height = 720
        self.img = None
        self.tello_info = np.zeros((720, 960, 3), dtype=np.uint8)
        self.video_On = False 
        self.isZero = False

        # 與 FrontEnd 之間通訊與傳值
        self.control_queue = control_queue
        self.take_over = take_over

        self.dir_queue=queue.Queue()
        self.dir_queue.queue.clear()

    def get_info(self):
        '''
            get battery, height, time
            Will only be referenced internally
        '''
        battery = self.get_battery()
        height = self.get_height()
        get_time = time.strftime("%H:%M:%S",time.localtime())

        return battery, height, get_time

    def print_info(self):
        '''
            print tello info , ex : battery, height, time
            Will only be referenced internally
        '''
        battery, height, get_time = self.get_info()

        InfoText = ("height: {h}, time:{t}".format(h = height, t = get_time))
        cv2.putText(self.tello_info, InfoText, (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)
        
        InfoText = ("battery: {b}%".format(b = battery))
        if battery <= 20:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (10, 20, 255), 1, cv2.LINE_AA)
        elif battery > 20 and battery <= 50:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 215, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 100), 1, cv2.LINE_AA)
        
        InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}".format(lr = self.lr, fb = self.fb, ud = self.ud, yv = self.yv))
        cv2.putText(self.tello_info, InfoText, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        if self.video_On:
            InfoText = ("video On!!!")
            cv2.putText(self.tello_info, InfoText, (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

    def videoRecorder(self):
        # 新版本的 djitellopy，讓畫面的資訊能正常讀取了並保存下來
        # 但是幀數不太對，會變成縮時，暫時找不到原因
        '''
            啟用錄影功能
            Will only be referenced internally
        '''     
        FPS = 30   
        height, width = self.img.shape[:2]
        video = cv2.VideoWriter(".//Film//video-{}.avi".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),
                                cv2.VideoWriter_fourcc(*'XVID'), FPS, (width, height))
        while self.video_On:
            video.write(self.img)
            time.sleep(1 / FPS)
        video.release()

    def getKey(self, keyName):
        ans = False
        for eve in pygame.event.get(): pass
        keyInput = pygame.key.get_pressed()
        myKey = getattr(pygame, 'K_{}'.format(keyName))
        if keyInput[myKey]:
            ans = True
        return ans

    def getKeyboardInput(self):
        self.lr = self.fb = self.ud = self.yv = 0

        if self.getKey("n"):
            self.control_queue.put("n")
        if self.getKey("m"):
            self.take_over.set()
        
        if self.getKey("q"): 
            if self.video_On:
                self.video_On = False
            self.end()
            self.control_queue.put("q")
            return
            
        if self.getKey("c"): 
            cv2.imwrite(".//Picture//capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),self.img)

        if self.getKey("v"): 
            if self.video_On:
                print("The video has been started, please do not start again")
            else:
                self.video_On = True
                recorder = Thread(target=self.videoRecorder)
                recorder.start()

        if self.getKey("b"): 
            self.video_On = False


        if self.getKey("r"): 
            if self.is_flying:
                pass
            else:
                self.takeoff()
        if self.getKey("f"): 
            if self.is_flying:
                self.land()
            else:
                pass
        
        if self.getKey("LEFT"): self.lr = -self.speed
        elif self.getKey("RIGHT"): self.lr = self.speed

        if self.getKey("UP"): self.fb = self.speed
        elif self.getKey("DOWN"): self.fb = -self.speed

        if self.getKey("w"): self.ud = self.speed
        elif self.getKey("s"): self.ud = -self.speed

        if self.getKey("d"): self.yv = self.speed
        elif self.getKey("a"): self.yv = -self.speed

        self.print_info()

        self.updateAct()
        

    def updateAct(self):
        if abs(self.lr) + abs(self.fb) + abs(self.ud) + abs(self.yv) != 0:
            self.isZero = False
            self.send_rc_control(self.lr, self.fb, self.ud, self.yv)
        elif abs(self.lr) + abs(self.fb) + abs(self.ud) + abs(self.yv) == 0 and self.isZero == False:
            self.isZero = True
            self.send_rc_control(self.lr, self.fb, self.ud, self.yv)


if __name__ == '__main__':
    pass
else:
    pygame.init()