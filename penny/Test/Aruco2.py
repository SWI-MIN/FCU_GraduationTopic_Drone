import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello
from ControlTello import ControlTello
import pygame
import csv
import Conversion

# self.angles_tof = [pitch, roll, yaw, tof]
class Aruco():
    def __init__(self) -> None:
        self.cam_matrix = None
        self.cam_distortion = None
        # self.frame = None
        self.aruco_dict  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
        # self.aruco_dict  = cv2.aruco.Dictionary_get(cv2.aruco.DICT_ARUCO_ORIGINAL)
        self.parameters  = cv2.aruco.DetectorParameters_create()
        
        # Marker edge length in meters
        self.marker_size = 10

        self.target = TargetDefine()

        self.R_flip  = np.zeros((3,3), dtype=np.float32)
        self.R_flip[0,0] =  1.0
        self.R_flip[1,1] = -1.0
        self.R_flip[2,2] = -1.0

        # about navigation
        self.navigation_start = False # 這裡需要主程式傳送thread event ，來決定導航狀態是否開啟
        self.main_marker = None # 記錄誰是主要
        self.find_new_marker = False # 標記是否需要找尋下一個marker
        self.used_marker = [] # 存放用過的marker

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
            # 標記周圍畫正方形
            cv2.aruco.drawDetectedMarkers(frame, corners)
            # Draw axis and 將有需要用到的資訊存入 sort_id 中 
            for i in range(0, ids.size):
                cv2.aruco.drawAxis(frame, self.cam_matrix, self.cam_distortion, rvecs[i], tvecs[i], 10)  # Draw axis
                ''' sort_id : 
                        |  id1  |  距離  |  X  |  Y  |  Z  |
                        |  id2  |  距離  |  X  |  Y  |  Z  |
                        |  id3  |  距離  |  X  |  Y  |  Z  |
                '''
                # 將讀到的 marker id 存到 sort_id 中
                id_list.append(ids[i][0])
                sort_id[i][0] = ids[i][0]

                # 求出各別 marker 到飛機的距離
                sort_id[i][1] = (tvecs[i][0][0]**2 + tvecs[i][0][1]**2 + tvecs[i][0][2]**2)**0.5

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
            
            if self.navigation_start == True:  # 導航開始
                # 如果 main marker == None，就把最接近飛機的 marker 作為 main
                # 如果 main marker != None，判斷main_marker是否在used_marker裡面，沒有就加進去
                if self.main_marker != None:
                    if self.main_marker not in self.used_marker:
                        self.used_marker.append(self.main_marker)
                else:
                    self.main_marker = sort_id[0][0]

                # 判斷是否需要找新 marker， 不找就畫黃色標示線，並且做動作
                if not self.find_new_marker:
                    if self.main_marker not in sort_id[0:,0:1]:
                        pass
                    else:
                        id_index = id_list.index(self.main_marker)
                        cx = int((corners[id_index][0][0][0]+corners[id_index][0][1][0]+corners[id_index][0][2][0]+corners[id_index][0][3][0])/4)
                        cy = int((corners[id_index][0][0][1]+corners[id_index][0][1][1]+corners[id_index][0][2][1]+corners[id_index][0][3][1])/4)
                        cv2.line(frame, (int(w/2), int(h/2)), (cx, cy), (0,255,255), 3)
                    self.navigation(sort_id)
                # else 是要找新marker，裡面新增找新marker的要求(條件)
                else:
                    # 如果沒有發現新的 marker 就旋轉尋找( 這個部分不一定要擺在這裡，到時候視情況擺放，但是這是必須要有的 )
                    pass
                    # 取得非main marker 中最近的一個，並且不能用過
                    for i in range(0, ids.size):
                        new_marker = sort_id[i][0]
                        if new_marker not in self.used_marker:
                            self.main_marker = new_marker
                            self.find_new_marker = False
                            break
            
        else:
            ### No id found
            cv2.putText(frame, "No Ids", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)

        return frame

    def navigation(self, sort_id):
        if self.main_marker not in sort_id:
            # 如果 marker 丟失則按造X軸旋轉尋找，參考code是以記錄time的方式返回尋找
            pass
        # 在這裡做完相應動作並且無人機的位置相對於marker已經在指定範圍內以後
        # 記得要在某些情況下開啟find_new_marker的狀態，才能尋找下一個marker
        # self.find_new_marker = True
        else:
            directions = [0., 0., 0., 0.]
            # adjust attitude
            if sort_id[0][1] > 60 :
                adj_d = sort_id[0][1] - 60              # 距離大於60，前進(+)
            elif sort_id[0][1] < 40 :
                adj_d = sort_id[0][1] - 40              # 距離小於40，往後(-)

            if sort_id[0][2] > 5:
                adj_x = sort_id[0][2] - 5               # 飛機位置太低，往上(+)
            elif sort_id[0][2] < 5:
                adj_x = sort_id[0][2] - 5               # 飛機位置太高，往下(-)

            if sort_id[0][3] > 30:                      # 角度
                adj_y = sort_id[0][3] - 30              # 飛機位置太左，往右(+)
            elif sort_id[0][3] < 30:
                adj_y = sort_id[0][3] - 30              # 飛機位置太右，往左(-)
            
            # 旋轉沒調整
            print("Adjust attitude Dist: %d;X: %d; Y: %d", adj_d, adj_x, adj_y)
            # return id Action
            directions = self.target.changeTarget(self.main_marker)
            return  adj_d, adj_x, adj_y, directions
            



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
                'Origin':                np.array([[0., 0., DIST, 0.]]),
                'Right sideways':        np.array([[0., 0., DIST, -40.]]),
                'Left sideways':         np.array([[0., 0., DIST, 40.]]),
                'Rotate right corner 1': np.array([[0., 0., DIST, 5.]]),
                'Rotate right corner 2': np.array([[0., 0., DIST, -10.]]),
                'Rotate right corner 3': np.array([[0., 0., DIST, -20.]]),
                'Rotate left corner 1':  np.array([[0., 0., DIST, -5.]]),
                'Rotate left corner 2':  np.array([[0., 0., DIST, 10.]]),
                'Rotate left corner 3':  np.array([[0., 0., DIST, 20.]]),
                'End':                   np.array([[0., 0., DIST, 0.]]),
                'Land':                  np.array([[0., 0., DIST, -1.]])
             }
        return switcher.get(selected, "Invalid marker type")

def main():
    pygame.display.set_caption("Tello")
    pygame.display.set_mode((200, 200)) # 寬 * 高
    tello = ControlTello()
    tello.connect()
    tello.streamon()

    cam = Aruco()
    
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
