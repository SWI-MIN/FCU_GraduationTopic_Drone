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
from djitellopy import Tello
from ControlTello import ControlTello
from Aruco import Camera
import threading
import queue

# 這裡其實可以不用繼承 ControlTello
class FrontEnd(ControlTello):
    def __init__(self):

        self.control_queue = queue.Queue()
        self.tello = ControlTello(self.control_queue)

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
        self.tello.streamon()
        while True:
            self.tello.img = self.tello.get_frame_read().frame
            self.tello.tello_info = np.zeros((720, 480, 3), dtype=np.uint8) # 高 * 寬

            self.tello.img, adj_directions = self.aruco.aruco(self.tello.img)
            print("Adjust direction: %d, %d, %d, %d" % (adj_directions[0], adj_directions[1], adj_directions[2], adj_directions[3]))
            self.tello.updateMarkerAct(adj_directions)

            if self.tello.getKeyboardInput(): 
                cv2.destroyAllWindows()
                break
            
            # 我認為需要做強制接管的程式，以防巡航時出問題
            # 目前是覺得可以設置一個狀態,當導航開始的時候需要將其設定為某一狀態，當我按下操作飛機的任意按鍵時必須轉換狀態，令導航功能暫停執行
            if not self.control_queue.empty():
                control = self.control_queue.get()
                if control == "n":
                    self.navigation_start.set()


            self.update_display()

            # cv2.imshow("Drone Control Centre1", self.tello.img)
            cv2.imshow("Drone Control Centre2", self.tello.tello_info)
            cv2.waitKey(1)

def main():
    tello = FrontEnd()
    tello.run()

if __name__ == '__main__':
    main()

