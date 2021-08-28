'''
    control tello
        q 退出
        c 拍照
        v 錄影 b 結束錄影
        r 起飛 f 降落
        上下左右 --> 前後左右
        wsad --> 升降轉向
    畫面大小 : (960, 720)  寬 * 高 OR (720, 960)  高 * 寬
'''
import pygame
import cv2
import time
import numpy as np
import queue
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
        self.width = 960
        self.height = 720
        self.img = None
        self.tello_info = np.zeros((720, 960, 3), dtype=np.uint8)
        self.video_On = False 
        self.dir_queue=queue.Queue()
        self.dir_queue.queue.clear()

        self.time_s = 0
        self.time_e = 0

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

        InfoText = ("height: {h}, time:{t}".format(h = height, t = get_time))
        cv2.putText(self.tello_info, InfoText, (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)
        
        InfoText = ("battery: {b}%".format(b = battery))
        if int(battery) <= 20:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (10, 20, 255), 1, cv2.LINE_AA)
        elif int(battery) > 20 and int(battery) <= 50:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 215, 255), 1, cv2.LINE_AA)
        else:
            cv2.putText(self.tello_info, InfoText, (370, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 100), 1, cv2.LINE_AA)
        
        InfoText = ("Command: lr:{lr} fb:{fb} ud:{ud} yv:{yv}".format(lr = self.lr, fb = self.fb, ud = self.ud, yv = self.yv))
        cv2.putText(self.tello_info, InfoText, (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

        if self.video_On:
            InfoText = ("video On!!!")
            cv2.putText(self.tello_info, InfoText, (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255), 1, cv2.LINE_AA)

    def videoRecorder(self):
        # 目前錄影幀數好奇(很低很低)，再來就是我大該知道為甚麼錄影時資訊會亂跳亂跳了，
        # 因為兩邊幀數對不上，有時取到的是有加上info 的，有的取道的是沒加的(但是我不知道為什麼，加 info 的時候都會添加到最底層的那個圖片)
        # 目前我認為要徹底解決這個問題就必須像我們參考的那份code作者一樣對原始的code 進行修改或自己寫，
        # 不然兩邊幀數以及添加到最底層圖片的問題會很難處理(或許用queue??改天試試)
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
        # pygame.surfarray.make_surface(self.img)
        # pygame.display.update()
        return ans

    def getKeyboardInput(self):
        self.lr = self.fb = self.ud = self.yv = 0

        if self.getKey("q"): 
            self.video_On = False
            self.land()
            self.end()
            return True

        if self.getKey("c"): 
            cv2.imwrite(".//Picture//capture-{}.jpg".format(time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())),self.img)

        if self.getKey("v"): 
            if self.video_On:
                print("The video has been started, please do not start again")
            else:
                self.video_On = True
                recorder = Thread(target=self.videoRecorder)
                recorder.start()

                self.time_s = time.time()

        if self.getKey("b"): 
            self.video_On = False
            self.time_e = time.time()
            print('time cost', (self.time_e - self.time_s), 's  +++++++++++++++++++++++++++++++++++++++++++++++++++++')

        if self.getKey("r"): self.yv = self.takeoff()
        if self.getKey("f"): self.yv = self.land()
        
        if self.getKey("LEFT"): self.lr = -self.speed
        elif self.getKey("RIGHT"): self.lr = self.speed

        if self.getKey("UP"): self.fb = self.speed
        elif self.getKey("DOWN"): self.fb = -self.speed

        if self.getKey("w"): self.ud = self.speed
        elif self.getKey("s"): self.ud = -self.speed

        if self.getKey("d"): self.yv = self.speed
        elif self.getKey("a"): self.yv = -self.speed

        self.print_info()

        self.send_rc_control(self.lr, self.fb, self.ud, self.yv)
        

    def updateMarkerAct(self, directions):
        # 把新的標籤動作加入queue
        # print("in update"+ str(directions))
        self.dir_queue.put(directions)
        x, y, z, yaw = self.dir_queue.get()
        print("///////////////////////////////Update directions: ")
        if yaw == -1:
            self.yv = self.speed
            self.send_rc_control(self.lr, self.fb, self.ud, self.yv)
            # self.land()

    def TelloAct(self):
        # 判別標籤動作或鍵盤動作
        if  not self.dir_queue.empty():                     # queue還有標籤的指令還沒做
            self.land()
        else :                                              # 做鍵盤指令
            self.getKeyboardInput()
            cv2.destroyAllWindows()
            self.send_rc_control(self.lr, self.fb, self.ud, self.yv)
            
            





if __name__ == '__main__':
    pass
else:
    pygame.init()