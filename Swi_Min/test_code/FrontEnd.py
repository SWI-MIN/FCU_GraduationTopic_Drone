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
import time, sys
import numpy as np
from djitellopy import Tello
from ControlTello import ControlTello
from Aruco import Camera
import threading
import queue

# 這裡其實可以不用繼承 ControlTello
class FrontEnd():
    def __init__(self):
        super().__init__()
        self.take_over = threading.Event()
        self.take_over.set()  # 預設接管狀態，當導航開啟時設為 clear()
        self.control_queue = queue.Queue()
        self.tello = ControlTello(self.control_queue, self.take_over)

        pygame.display.set_caption("Tello")
        self.win = pygame.display.set_mode((960, 720)) # 寬 * 高
        '''
            目前設想就是將其餘的功能通通在這層呼叫(以threading的方式建立)，
            因此在實作其他所有功能的時候，通通要做成 class 的形式
        '''        

        # 處理aruco 相關的
        self.navigation_start = threading.Event()
        self.navigation_start.clear()
        self.marker_act_queue = queue.Queue()
        self.aruco = Camera(self.navigation_start, self.marker_act_queue)

        self.isZero = False

    def update_display(self):
        if (self.tello.img.shape[1] != self.tello.width) or (self.tello.img.shape[0] != self.tello.height):
                self.screen=pygame.display.set_mode((self.tello.img.shape[1], self.tello.img.shape[0]))
        frame = cv2.cvtColor(self.tello.img, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = np.flipud(frame)
        frame = pygame.surfarray.make_surface(frame)
        self.win.blit(frame, (0, 0))
        pygame.display.update()

    def run(self):
        self.tello.connect()
        self.tello.set_speed(10)
        if self.tello.stream_on:
            self.tello.streamoff()
        self.tello.streamon()
        
        while True:
            self.tello.img = self.tello.get_frame_read().frame
            self.tello.tello_info = np.zeros((720, 480, 3), dtype=np.uint8) # 高 * 寬

            self.tello.img = self.aruco.aruco(self.tello.img)
            
            # 導航開以及離開程式
            if not self.control_queue.empty():
                control = self.control_queue.get()
                if control == "n":
                    self.navigation_start.set()
                    self.take_over.clear()
                if control == "q":
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit("Quit")
                    
            # 導航關，飛機如果在導航時要判斷是否要接管飛機
            if self.navigation_start.is_set() and self.take_over.is_set():
                self.navigation_start.clear()
                self.aruco.reset()

            # 導航動作
            if self.navigation_start.is_set() and not self.marker_act_queue.empty():  # 無人機導航開啟並且動作queue不為空
                directions = self.marker_act_queue.get()
                # self.tello.send_rc_control(int(directions[0]), int(directions[1]), int(directions[2]), int(directions[3]))
                # self.tello.updateAct(int(directions[0]), int(directions[1]), int(directions[2]), int(directions[3]))
                if abs(int(directions[0])) + abs(int(directions[1])) + abs(int(directions[2])) + abs(int(directions[3])) != 0:
                    self.isZero = False
                    self.tello.send_rc_control(int(directions[0]), int(directions[1]), int(directions[2]), int(directions[3]))
                elif abs(int(directions[0])) + abs(int(directions[1])) + abs(int(directions[2])) + abs(int(directions[3])) == 0 and self.isZero == False:
                    self.isZero = True
                    self.tello.send_rc_control(int(directions[0]), int(directions[1]), int(directions[2]), int(directions[3]))

            # 無人機本身的姿態roll、pitch、yaw ，yaw正北為0
            cv2.putText(self.tello.img, "roll : {}"  .format(self.tello.get_roll()) , (10, (380)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
            cv2.putText(self.tello.img, "pitch : {}"  .format(self.tello.get_pitch()) , (100, (380)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)        
            cv2.putText(self.tello.img, "yaw : {}"  .format(self.tello.get_yaw()) , (200, (380)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
            
            self.tello.getKeyboardInput()
            self.update_display()

            # cv2.imshow("Drone Control Centre1", self.tello.img)
            cv2.imshow("Drone Control Centre2", self.tello.tello_info)
            cv2.waitKey(1)

def main():
    tello = FrontEnd()
    tello.run()

if __name__ == '__main__':
    main()

