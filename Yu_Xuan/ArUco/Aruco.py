import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello
from ControlTello import ControlTello
import pygame
import csv
import Conversion
import queue
import threading

# self.angles_tof = [pitch, roll, yaw, tof]
class Camera():
    def __init__(self, navigation_start, marker_act_queue) -> None:
        self.cam_matrix = None
        self.cam_distortion = None
        # self.aruco_dict  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)# self.aruco_dict  = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
        self.aruco_dict  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.parameters  = cv2.aruco.DetectorParameters_create()
        
        # Marker edge length in meters
        self.marker_size = 0.1

        # 計算旋轉的角度用的矩陣
        self.R_flip  = np.zeros((3,3), dtype=np.float32)
        self.R_flip[0,0] =  1.0
        self.R_flip[1,1] = -1.0
        self.R_flip[2,2] = -1.0

        # about navigation
        self.have_new_marker = threading.Event()
        self.have_new_marker.clear()
        self.navigation_start = navigation_start # 這裡需要主程式傳送thread event ，來決定導航狀態是否開啟
        self.main_marker = None # 記錄誰是主要
        self.main_marker_act = None # main_marker 代表的動作
        self.find_new_marker = False # 標記是否需要找尋下一個marker
        self.used_marker = [] # 存放用過的marker
        self.marker_act_queue = marker_act_queue  # 要飛機執行的動作陣列放進這個queue中
        self.adjust_flag = False  # 判斷微調動作是否執行完，執行完了改變狀態並執行marker動作
        self.act_record = act_record(10, 4)  # 將執行過的動作存放進這個物件中，當 marker 不見時，要做相反的動作以找回 marker，目前只保存最近的10條動作
        self.act_direction = act_record(5, 1)  # 紀錄動作方向，當相反的動作不足以找回main marker 時轉向之用

        self.lost_time = 0  # 每次執行導航動作完都記錄一次time，當這個值超過2s沒有更新代表 main_marker OR marker 不見了 2s

        # self.tvecfile = open("tvecfile.txt", "w")

        # 取得自己定義的marker，以及參考動作
        self.markerdefine = MarkerDefine()

    def aruco(self, frame):
        if np.all(self.cam_matrix== None) or np.all(self.cam_distortion == None):
            calib_path  = ".\\Camera_Correction\\"
            self.cam_matrix   = np.loadtxt(calib_path+'cameraMatrix.txt', delimiter=',')   
            self.cam_distortion   = np.loadtxt(calib_path+'cameraDistortion.txt', delimiter=',')   
        
        # 校正失真，去除失真的部分並將畫面進行校正
        h, w = frame.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(self.cam_matrix,self.cam_distortion,(w,h),1,(w,h))
        frame = cv2.undistort(frame, self.cam_matrix, self.cam_distortion, None, newcameramtx)        # 校正失真
        x,y,w,h = roi
        frame = frame[y:y+h, x:x+w]# 去除失真的部分並將畫面進行校正
    

        # 換成黑白，並取得 id & corners
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(image=gray, dictionary=self.aruco_dict,
                            parameters=self.parameters,cameraMatrix=self.cam_matrix, distCoeff=self.cam_distortion) 

        if np.all(ids != None):
            ### id found
            id_list = [] # 存放原始 id 順序
            sort_id = np.zeros((ids.size, 2), dtype=np.float_) # 存放已經排序過的  
            # rvec旋转矩阵、tvec位移矩阵
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners,
                                self.marker_size, self.cam_matrix, self.cam_distortion)

            # 寫檔看評移矩陣
            # print("%d" % (tvecs), file = self.tvecfile)
            # self.tvecfile.write(str(tvecs))


            # 標記周圍畫正方形
            cv2.aruco.drawDetectedMarkers(frame, corners)

            # Draw axis and 將有需要用到的資訊存入 sort_id 中 
            for i in range(0, ids.size):
                cv2.aruco.drawAxis(frame, self.cam_matrix, self.cam_distortion, rvecs[i], tvecs[i], 0.1)  # Draw axis
                ''' sort_id : 
                        |  id1  |  距離  |
                        |  id2  |  距離  |
                        |  id3  |  距離  |
                '''
                # 將讀到的 marker id 存到 sort_id 中
                id_list.append(ids[i][0])
                sort_id[i][0] = ids[i][0]

                # 求出各別 marker 到飛機的距離
                sort_id[i][1] = ((tvecs[i][0][0]**2 + tvecs[i][0][1]**2 + tvecs[i][0][2]**2)**0.5)*100
  
            # 將 sort_id 距離 由短到近優先，id 由小到大次之排序
            sort_id = sort_id[np.lexsort((sort_id[:, 0], sort_id[:, 1]))] 

            #####################################################################
            # 感覺這裡這樣寫192好像就沒用了

            # 比較 現有 id 與usedid ，確認當前獨到的id中是否有沒用過的
            # 當有尚未使用的id時 self.have_new_marker.is_set()
            # 當沒有尚未使用的id時 clear 
            used_id = set(self.used_marker)           # 已經用過的id
            now_id = set(id_list)                     # 現在看到的id
            new_id = now_id & (used_id ^ now_id)      # 算完後還在的表示為新的沒用過的id
            if len(new_id) != 0:                      # 長度大於0，表示有沒用過的id
                self.have_new_marker.is_set()         # 設定為 is_set()，當為這個狀態時表示無人機可以切換狀態找新的marker
            else:
                self.have_new_marker.clear()
            ######################################################################

            for i in range(0, ids.size):
                cv2.putText(frame, str(int(sort_id[i][0]))               , (10, (i*20+200))  , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "D : {:.2f} cm".format(sort_id[i][1]) , (60, (i*20+200))  , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)


            if self.navigation_start.is_set():  # 導航開始
                # 如果 main marker == None，就把最接近飛機的 marker 作為 main
                # 如果 main marker != None，判斷main_marker是否在used_marker裡面，沒有就加進去
                if self.main_marker != None:
                    if self.main_marker not in self.used_marker:
                        self.used_marker.append(self.main_marker)
                else:
                    self.main_marker = int(sort_id[0][0])
                    self.main_marker_act = self.markerdefine.changeTarget(int(self.main_marker))[0]

                
      

                # 判斷是否需要找新 marker， 不找就畫黃色標示線，並且做動作
                if not self.find_new_marker:
                    if self.main_marker not in sort_id[0:,0:1]:
                        cv2.putText(frame, "main_marker not in sort_id", (10, 60) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        
                        # 當 main_marker 消失2s，再執行 lost_main_marker
                        if time.time() - self.lost_time >= 2: 
                            self.lost_main_marker()
                    
                    else:
                        # 畫線
                        id_index = id_list.index(self.main_marker)   # 標記 main_marker 在 id_list 的位置
                        cx = int((corners[id_index][0][0][0]+corners[id_index][0][1][0]+corners[id_index][0][2][0]+corners[id_index][0][3][0])/4)
                        cy = int((corners[id_index][0][0][1]+corners[id_index][0][1][1]+corners[id_index][0][2][1]+corners[id_index][0][3][1])/4)
                        cv2.line(frame, (int(w/2), int(h/2)), (cx, cy), (0,255,255), 3)
                    
                        R_ct    = np.matrix(cv2.Rodrigues(rvecs[id_index][0])[0])
                        R_tc    = R_ct.T
                        # 橫滾標記(X)、俯仰標記(Y)、偏航標記 繞(Z)軸旋轉的角度
                        roll_marker, pitch_marker, yaw_marker = Conversion.rotationMatrixToEulerAngles(self.R_flip*R_tc)
                        # 弧度傳換成角度，並存入 sort_id
                        euler_X = math.degrees(roll_marker)
                        euler_Y = math.degrees(pitch_marker)
                        euler_Z = math.degrees(yaw_marker)
                        tvecs_X = int(tvecs[id_index][0][0] * 100) # 位移 x
                        tvecs_Y = int(tvecs[id_index][0][1] * 100)
                        tvecs_Z = int(tvecs[id_index][0][2] * 100)

                        

                        cv2.putText(frame, "main : {}         D : {:.2f}cm".format(str(int(sort_id[i][0])), sort_id[i][1]), (10, 40)  , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

                        cv2.putText(frame, " euler_X : {:.2f}   "   .format(euler_X) , (100, 60) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " euler_Y : {:.2f}   "   .format(euler_Y) , (280, 60) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " euler_Z : {:.2f}   "   .format(euler_Z) , (460, 60) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

                        cv2.putText(frame, " tvecs_X : {:.2f}cm " .format(tvecs_X) , (100, 80) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " tvecs_Y : {:.2f}cm " .format(tvecs_Y) , (280, 80) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " tvecs_Z : {:.2f}cm " .format(tvecs_Z) , (460, 80) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

                        cv2.putText(frame, " find_new_marker : {} " .format(self.find_new_marker) , (10, 120) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " main_marker : {} " .format(self.main_marker) , (225, 120) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        cv2.putText(frame, " used_marker : {} " .format(self.used_marker) , (400, 120) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        
                        # 取出 sort_id 中 屬於 main_marker 的那一列，並傳入navigation
                        # main_marker_attitude = np.where(sort_id[:,0] == self.main_marker)
                        self.navigation(euler_X, euler_Y, euler_Z, tvecs_X, tvecs_Y, tvecs_Z)
                    
                # else 是要找新marker，裡面新增找新marker的要求(條件)
                else:
                    # 取得非main marker 中最近的一個，並且不能用過
                    for i in range(0, ids.size):
                        new_marker = int(sort_id[i][0])
                        if new_marker not in self.used_marker:
                            self.main_marker = new_marker
                            self.main_marker_act = self.markerdefine.changeTarget(int(self.main_marker))[0]
                            self.find_new_marker = False
                            break
                    # 如果沒有發現新的 marker 就旋轉尋找( 這個部分不一定要擺在這裡，到時候視情況擺放，但是這是必須要有的 )
                    if self.main_marker_act[3] > 0:
                        self.marker_act_queue.put([0, 0, 0, 10])
                    elif self.main_marker_act[3] < 0 and self.main_marker_act[3] != -1:    
                        self.marker_act_queue.put([0, 0, 0, -10])
            
        else:
            ### No id found
            cv2.putText(frame, "No Ids", (10, 40), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
            # 當 main_marker 消失2s，再執行 lost_main_marker
            if time.time() - self.lost_time >= 2: 
                if self.navigation_start.is_set():  # 必須在導航開啟時才做此動作
                    self.lost_main_marker()

        return frame


    def lost_main_marker(self):
        # 這裡面的轉向都沒有設定回0，可能在某些極端情況下一直轉向(一直找不回main merker)
        if self.act_record.act_list.shape[0]-1 >= 0:
            change_sign = self.act_record.get_value()
            for i in range(4):
                change_sign[i] = -change_sign[i]
            self.marker_act_queue.put(change_sign)

            if change_sign[3] > 0:
                self.act_direction.replace_act(1)
            elif change_sign[3] < 0:
                self.act_direction.replace_act(-1)

        else:   # 如果導航開啟，並且act_record為空，左右尋找
            if self.act_direction.act_list.shape[0]-1 >= 0 and self.act_direction.act_list.shape[0] %2 ==1:       # 如果該空間不為空，並且該空間的值為奇數，則返回第一筆
                act_direction = self.act_direction.get_value()
                while(self.act_direction.act_list.shape[0]-1 >= 0):   # 如果該空間不為空，將剩下的資料都進行返回，並進行相乘
                    direction = self.act_direction.get_value()
                    act_direction *= direction

                # 如果方向為正，表示上方做尋找動作時，最近5筆資料傾向於向右尋找，方向為負則反之
                if act_direction > 0:
                    self.marker_act_queue.put([0, 0, 0, 10])
                elif act_direction < 0:    
                    self.marker_act_queue.put([0, 0, 0, -10])
        


    def navigation(self, euler_X, euler_Y, euler_Z, tvecs_X, tvecs_Y, tvecs_Z):
        t_X, t_Y, t_Z, eu_Y = Conversion.speed_test(tvecs_X,tvecs_Y,tvecs_Z,euler_Y)
        directions = np.array([0, 0, 0, 0]) # 左右、前後、高低、轉向
        adjust_speed = 5

        if not self.adjust_flag:
            # 上下對準maeker
            if tvecs_Y > 0:      # 垂直上下 (X軸) 
                directions[2] -= adjust_speed * t_Y           # 飛機位置太低，往上(+)
            elif tvecs_Y < 0:
                directions[2] += adjust_speed * t_Y          # 飛機位置太高，往下(-)
            if tvecs_X > 0:
                directions[3] += adjust_speed * t_X           # 無人機太靠右，左轉(-)
            elif tvecs_X < 0:
                directions[3] -= adjust_speed * t_X          # 無人機太靠左，右轉(+)
            if tvecs_Z > 100:
                directions[1] += adjust_speed * t_Z           # 向前(+)
            elif tvecs_Z < 100:
                directions[1] -= adjust_speed * t_Z           # 向後(-)
            

            if tvecs_X < 5 and tvecs_X > -5:  
                if euler_Y > 10:
                    directions[0] += adjust_speed * eu_Y  # 向右(+)
                elif euler_Y < -10:
                    directions[0] -= adjust_speed * eu_Y   # 向左(-)

            if tvecs_Y > -5 and tvecs_Y < 10 and tvecs_X > -5 and tvecs_X < 5 and tvecs_Z > 90 and tvecs_Z < 110 and euler_Y < 10 and euler_Y > -10:
                self.adjust_flag = True


        else:
            # 目前想到可以用一個開關進行設定，當畫面中有其他的未使用過的marker的時候就將切換狀態開啟，若是沒有其他未使用過的 marker 則持續做當前marker動作
            # directions = np.array(self.main_marker_act)
            print("調整完了+++++++++++++++++++++++++++++++++")
            # if self.have_new_marker.is_set():
            #     self.adjust_flag = False
            #     self.find_new_marker = True

        self.marker_act_queue.put(directions)
        self.act_record.replace_act(directions)


        self.lost_time = time.time()  # 每次進來都會更新lost_time，當進不來的時候就相當於計時


    def reset(self):
        # 如果要重新開始導航時功能相關的變數必須重置
        self.main_marker = None # 記錄誰是主要
        self.main_marker_act = None # main_marker 代表的動作
        self.find_new_marker = False # 標記是否需要找尋下一個marker
        self.used_marker = [] # 存放用過的marker
        self.adjust_flag = False  # 判斷微調動作是否執行完，執行完了改變狀態並執行marker動作
        self.act_record = act_record(5, 4)  # 將執行過的動作存放進這個物件中，當 marker 不見時，要做相反的動作以找回 marker，目前只保存最近的5條動作
        self.act_direction = act_record(5, 1)
        self.lost_time = 0  # 每次執行導航動作完都記錄一次time，當這個值超過2s沒有更新代表 main_marker OR marker 不見了 2s
        # self.tvecfile.close()
        
class act_record():
    ''' 一組 行(column)*列(row) 的動作紀錄
        replace_act : 只會保留 col * row 大小的紀錄表，col 超過會刪除先進來的動作
                ---------------------    
            --> | 1 | 2 | 3 | 4 | 5 | -->
                ---------------------    
                ---------------------
          6 --> | 1 | 2 | 3 | 4 | 5 | -->
                ---------------------
                ---------------------
            --> | 6 | 1 | 2 | 3 | 4 | --> 5
                ---------------------
        get_value : 從前面向後取得值，取得後會移除該值
    '''
    def __init__(self, col, row) -> None:
        self.col = col
        self.row = row
        self.act_list = np.zeros((0, row), dtype = np.int_)

    def replace_act(self, act): # 更新 act_list
        self.act_list = np.insert(self.act_list, self.act_list.shape[0], act, axis = 0)
        if self.act_list.shape[0] > self.col:
            self.act_list = np.delete(self.act_list, 0, axis = 0)

    def get_value(self):
        value = self.act_list[self.act_list.shape[0]-1]
        self.act_list = np.delete(self.act_list, self.act_list.shape[0]-1, axis = 0)
        return value

# distance from marker in camera Z coordinates
DIST = 0.9
class MarkerDefine():
    def __init__(self):
        with open('MarkerAction/marker_conf.csv', 'rt', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            self.marker_nav = list(reader)

    def changeTarget(self, ID):
        selected = 'Origin'
        for i in self.marker_nav:
            if i[0] == str(ID):
                selected = i[1]
                break

        print(selected + " marker")
                                                    # vx, vy, vz, yaw
        switcher={
                'Origin':                np.array([[0., 0., 0, 0.]]),            # 0
                'Right sideways':        np.array([[20., 0., 0, 0.]]),           # 1 - 5 
                'Left sideways':         np.array([[-20., 0., 0, 0.]]),          # 6 - 10 
                'Rotate right corner 1': np.array([[0., 0., 0, 10.]]),          # 11 - 15 
                'Rotate right corner 2': np.array([[0., 0., 0, 20.]]),          # 16 - 20 
                'Rotate left corner 1':  np.array([[0., 0., 0, -10.]]),           # 21 - 25 
                'Rotate left corner 2':  np.array([[0., 0., 0, -20.]]),           # 26 - 30
                'Forward':               np.array([[0., 10., 0, 0.]]),           # 31 - 35 ; 72
                'Backward':              np.array([[0., -10., 0, 0.]]),          # 36 - 40
                'Up':                    np.array([[0., 0., 10, 0.]]),           # 41 - 45
                'Land':                  np.array([[0., 0., 0, -1.]])            # 50
             }
        return switcher.get(selected, "Invalid marker type")


def main():
    pygame.display.set_caption("Tello")
    pygame.display.set_mode((200, 200)) # 寬 * 高
    tello = ControlTello()
    tello.connect()
    tello.streamon()

    cam = Camera()
    
    while True:
        frame = tello.get_frame_read().frame
        tello.tello_info = np.zeros((720, 480, 3), dtype=np.uint8)
        # 這裡是跑 Camera
        frame = cam.aruco(frame)
        
        if tello.getKeyboardInput(): 
            cv2.destroyAllWindows()
            break

        cv2.imshow('frame', frame)
        cv2.imshow('tello_info', tello.tello_info)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()
else:
    pass