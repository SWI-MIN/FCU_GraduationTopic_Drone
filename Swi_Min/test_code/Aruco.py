import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello
from ControlTello import ControlTello
import pygame
import csv
import Conversion
import queue

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
        self.navigation_start = navigation_start # 這裡需要主程式傳送thread event ，來決定導航狀態是否開啟
        self.main_marker = None # 記錄誰是主要
        self.main_marker_act = None # main_marker 代表的動作
        self.find_new_marker = False # 標記是否需要找尋下一個marker
        self.used_marker = [] # 存放用過的marker
        self.marker_act_queue = marker_act_queue  # 要飛機執行的動作陣列放進這個queue中
        self.adjust_flag = False  # 判斷微調動作是否執行完，執行完了改變狀態並執行marker動作
        self.act_record = act_record(5, 4)  # 將執行過的動作存放進這個物件中，當 marker 不見時，要做相反的動作以找回 marker，目前只保存最近的5條動作
        self.lost_time = 0  # 每次執行導航動作完都記錄一次time，當這個值超過2s沒有更新代表 main_marker OR marker 不見了 2s
        self.act_time = 0   # 給飛機做標籤動作的時間
        # self.tvecfile = open("tvecfile.txt", "w")

        # 取得自己定義的marker，以及參考動作
        self.target = TargetDefine()

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
            sort_id = np.zeros((ids.size, 5), dtype=np.float_) # 存放已經排序過的  
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
                        |  id1  |  距離  |  X  |  Y  |  Z  |
                        |  id2  |  距離  |  X  |  Y  |  Z  |
                        |  id3  |  距離  |  X  |  Y  |  Z  |
                '''
                # 將讀到的 marker id 存到 sort_id 中
                id_list.append(ids[i][0])
                sort_id[i][0] = ids[i][0]

                # 求出各別 marker 到飛機的距離
                sort_id[i][1] = ((tvecs[i][0][0]**2 + tvecs[i][0][1]**2 + tvecs[i][0][2]**2)**0.5)*100
                cv2.putText(frame, "tvecs_x : {}"  .format(int(tvecs[i][0][0]*100)) , (10, (300)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "tvecs_y : {}"  .format(int(tvecs[i][0][1]*100)) , (10, (320)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "tvecs_z : {}"  .format(int(tvecs[i][0][2]*100)) , (10, (340)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

                # 求出各別 marker 與飛機的角度關係
                # 旋轉矩陣
                R_ct    = np.matrix(cv2.Rodrigues(rvecs[i][0])[0])
                R_tc    = R_ct.T
                # 橫滾標記(X)、俯仰標記(Y)、偏航標記 繞(Z)軸旋轉的角度
                roll_marker, pitch_marker, yaw_marker = Conversion.rotationMatrixToEulerAngles(self.R_flip*R_tc)
                
                # 弧度傳換成角度，並存入 sort_id
                sort_id[i][2] = math.degrees(roll_marker)
                sort_id[i][3] = math.degrees(pitch_marker)
                sort_id[i][4] = math.degrees(yaw_marker)

            # 將 sort_id 距離 由短到近優先，id 由小到大次之排序
            sort_id = sort_id[np.lexsort((sort_id[:, 0], sort_id[:, 1]))] 

            for i in range(0, ids.size):
                cv2.putText(frame, str(int(sort_id[i][0]))               , (10, (i*20+40))  , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "D : {:.2f} cm".format(sort_id[i][1]) , (60, (i*20+40))  , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "X : {:+.2f}"  .format(sort_id[i][2]) , (200, (i*20+40)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "Y : {:+.2f}"  .format(sort_id[i][3]) , (300, (i*20+40)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "Z : {:+.2f}"  .format(sort_id[i][4]) , (400, (i*20+40)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

            if self.navigation_start.is_set():  # 導航開始
                # 如果 main marker == None，就把最接近飛機的 marker 作為 main
                # 如果 main marker != None，判斷main_marker是否在used_marker裡面，沒有就加進去
                if self.main_marker != None:
                    if self.main_marker not in self.used_marker:
                        self.used_marker.append(self.main_marker)
                else:
                    self.main_marker = sort_id[0][0]
                    self.main_marker_act = self.target.changeTarget(int(self.main_marker))[0]

                cv2.putText(frame, "find_new_marker : {}"  .format(self.find_new_marker) , (10, (400)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "main_marker : {}"  .format(self.main_marker) , (10, (420)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                cv2.putText(frame, "used_marker : {}"  .format(self.used_marker) , (10, (440)) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                ############################
                
                # 判斷是否需要找新 marker， 不找就畫黃色標示線，並且做動作
                if not self.find_new_marker:
                    if self.main_marker not in sort_id[0:,0:1]:
                        cv2.putText(frame, "main_marker not in sort_id", (10, 460) , cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                        
                        # 當 main_marker 消失2s，再執行 lost_main_marker
                        if time.time() - self.lost_time >= 2: 
                            lost_respond = self.lost_main_marker()
                            if lost_respond == None:
                                cv2.putText(frame, "act_record is None", (10, 480), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                    
                    else:
                        # 畫線
                        id_index = id_list.index(self.main_marker)
                        cx = int((corners[id_index][0][0][0]+corners[id_index][0][1][0]+corners[id_index][0][2][0]+corners[id_index][0][3][0])/4)
                        cy = int((corners[id_index][0][0][1]+corners[id_index][0][1][1]+corners[id_index][0][2][1]+corners[id_index][0][3][1])/4)
                        cv2.line(frame, (int(w/2), int(h/2)), (cx, cy), (0,255,255), 3)

                        # 取出 sort_id 中 屬於 main_marker 的那一列，並傳入navigation
                        main_marker_attitude = np.where(sort_id[:,0] == self.main_marker)
                        self.navigation(sort_id[main_marker_attitude], id_list, tvecs)
                    
                # else 是要找新marker，裡面新增找新marker的要求(條件)
                else:
                    # 如果沒有發現新的 marker 就旋轉尋找( 這個部分不一定要擺在這裡，到時候視情況擺放，但是這是必須要有的 )
                    
                    # 取得非main marker 中最近的一個，並且不能用過
                    for i in range(0, ids.size):
                        new_marker = sort_id[i][0]
                        if new_marker not in self.used_marker:
                            self.main_marker = new_marker
                            self.main_marker_act = self.target.changeTarget(int(self.main_marker))[0]
                            self.find_new_marker = False
                            break
            
        else:
            ### No id found
            cv2.putText(frame, "No Ids", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
            # 當 main_marker 消失2s，再執行 lost_main_marker
            if time.time() - self.lost_time >= 2: 
                lost_respond = self.lost_main_marker()
                if lost_respond == None:
                    cv2.putText(frame, "act_record is None", (10, 100), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

        return frame


    def lost_main_marker(self):
        if self.act_record.act_list.shape[0]-1 >= 0:
            change_sign = self.act_record.get_value()
            for i in range(4):
                change_sign[i] = -change_sign[i]
            self.marker_act_queue.put(change_sign)
        else:
            return None


    def navigation(self, main_marker_attitude, id_list, tvecs):
        directions = np.array([0, 0, 0, 0]) # 前後、左右、高低、轉向
        adjust_speed = 5

        distance = main_marker_attitude[0][1] # 距離
        euler_X = main_marker_attitude[0][2] # 歐拉角 x
        euler_Y = main_marker_attitude[0][3]
        euler_Z = main_marker_attitude[0][4]
        id_index = id_list.index(self.main_marker)
        tvecs_X = int(tvecs[id_index][0][0] * 100) # 位移 x
        tvecs_Y = int(tvecs[id_index][0][1] * 100)
        tvecs_Z = int(tvecs[id_index][0][2] * 100)

        opposite_angle = round(math.degrees(math.asin(tvecs_X / (tvecs_X**2 + tvecs_Z**2)**0.5)), 2)
        angle_dif = euler_Y - opposite_angle

        if not self.adjust_flag:
            # 上下對準maeker
            if tvecs_Y > 0:      # 垂直上下 (X軸) 
                directions[2] -= adjust_speed * 2           # 飛機位置太低，往上(+)
            elif tvecs_Y < 0:
                directions[2] += adjust_speed * 2          # 飛機位置太高，往下(-)
            # 左右對準maeker
            # if angle_dif > 0:
            #     directions[3] -= adjust_speed * 2           # 無人機太靠右，左轉(-)
            # elif angle_dif < 0:
            #     directions[3] += adjust_speed * 2           # 無人機太靠左，右轉(+)
            if tvecs_X > 0:
                directions[3] += adjust_speed * 2           # 無人機太靠右，左轉(-)
            elif tvecs_X < 0:
                directions[3] -= adjust_speed * 2           # 無人機太靠左，右轉(+)

            # if tvecs_Y < 10 and tvecs_Y > -5 and angle_dif < 5 and angle_dif > -5:
            #     # 做其他方向
            #     if distance > 120:
            #         # 向前
            #         directions[0]
            #     elif distance < 100:
            #         # 向後
            #         directions[0]
            #     if tvecs_X > 0:
            #         directions[1]
            #     elif tvecs_X < 0:
            #         directions[1]

            self.marker_act_queue.put(directions)


            # directions 裡面都是0, 代表不需要調整, 準備做標籤動作
            # if np.all(directions == 0):
            #     self.adjust_flag = True
            # # 裡面有東西不等於0的時候, 需要調整
            # else : 
            #     self.marker_act_queue.put(directions)
            #     self.act_record.replace_act(directions)  # 對飛機的做紀錄，當 marker 不見時反向執行

            # self.act_time = time.time()  # 進到這裡就會更新act_time，不進入這裡表示開始計時給飛機做標籤的時間

        # 調整完畢，做標籤動作
        # else:
        #     # self.marker_act_queue.put(self.main_marker_act)
        #     # self.act_record.replace_act(self.main_marker_act)   # 對飛機的做紀錄，當 marker 不見時反向執行

        #     test_act = [0, 0, 0, 40]
        #     self.marker_act_queue.put(test_act)
        #     self.act_record.replace_act(test_act)

        #     # 此處可能會有 put 多次的問題++++++++++++++++++++++++++++
        #     # 給予標籤 2s 時間做動作
        #     if time.time() - self.act_time >= 10: 
        #         self.adjust_flag = False
        #         self.find_new_marker = True

        self.lost_time = time.time()  # 每次進來都會更新lost_time，當進不來的時候就相當於計時


    def reset(self):
        # 如果要重新開始導航時功能相關的變數必須重置
        self.main_marker = None # 記錄誰是主要
        self.main_marker_act = None # main_marker 代表的動作
        self.find_new_marker = False # 標記是否需要找尋下一個marker
        self.used_marker = [] # 存放用過的marker
        self.adjust_flag = False  # 判斷微調動作是否執行完，執行完了改變狀態並執行marker動作
        self.act_record = act_record(5, 4)  # 將執行過的動作存放進這個物件中，當 marker 不見時，要做相反的動作以找回 marker，目前只保存最近的5條動作
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
class TargetDefine():
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
                'Rotate right corner 1': np.array([[0., 0., 0, -10.]]),          # 11 - 15 
                'Rotate right corner 2': np.array([[0., 0., 0, -20.]]),          # 16 - 20 
                'Rotate left corner 1':  np.array([[0., 0., 0, 10.]]),           # 21 - 25 
                'Rotate left corner 2':  np.array([[0., 0., 0, 20.]]),           # 26 - 30
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
