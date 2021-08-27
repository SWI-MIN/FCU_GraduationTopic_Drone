import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello
from ControlTello import ControlTello
import pygame
import csv


tello = ControlTello()
tello.connect()
tello.streamon()

# self.angles_tof = [pitch, roll, yaw, tof]
class Camera():
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

    def aruco(self, frame):
        if np.all(self.cam_matrix== None) or np.all(self.cam_distortion == None):
        # if self.cam_matrix == None or self.cam_distortion == None:
            calib_path  = ".\\Camera_Correction\\"
            self.cam_matrix   = np.loadtxt(calib_path+'cameraMatrix.txt', delimiter=',')   
            self.cam_distortion   = np.loadtxt(calib_path+'cameraDistortion.txt', delimiter=',')   
        
        # 使用OpenCV进行标定（Python）https://blog.csdn.net/u010128736/article/details/52875137
        # 不確定下方校正是否必要，這段有沒有似乎差別並不會太大
        # new camera intrinsic matrix based on the free scaling parameter(回傳新的相機內部參數)
        h, w = frame.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(self.cam_matrix,self.cam_distortion,(w,h),1,(w,h))
        # 校正失真
        frame = cv2.undistort(frame, self.cam_matrix, self.cam_distortion, None, newcameramtx)
        # 去除失真的部分並將畫面進行校正
        x,y,w,h = roi
        frame = frame[y:y+h, x:x+w]

        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(image=gray, dictionary=self.aruco_dict,
                            parameters=self.parameters,cameraMatrix=self.cam_matrix, distCoeff=self.cam_distortion) 

        # list for all currently seen IDs 列出所有當前看到的 ID
        id_list=[]

        if np.all(ids != None):
            ### id found
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners,
                                self.marker_size, self.cam_matrix, self.cam_distortion)
            directions = [0., 0., 0., 0.]
            
            # 將所有讀到的 id 加到 id_list 中
            for i in range(0, ids.size):
                cv2.aruco.drawAxis(frame, self.cam_matrix, self.cam_distortion, rvecs[i], tvecs[i], 10)  # Draw axis
                id_list.append(ids[i][0])

                # 測試都看到了哪些ids，並印出來
                # Print_ids = str(ids[i][0])
                cv2.putText(frame, str(ids[i][0]), (10, (i*20+40)), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                
                # directions[3] = self.target.changeTarget(ids[i][0])[0][3]
                # cv2.putText(frame, str(directions[3]), (10, 500), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                # if directions[3] ==  -1:
                #     # tello.send_rc_control(vals[0], vals[1], vals[2], vals[3])
                #     # 動作傳到update
                #     print("Directions: " + directions)
                #     tello.updateMarkerAct(self.target.changeTarget(ids[i][0]))
                #     print("tello.land()+++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                directions = self.target.changeTarget(ids[i][0])[0]
                cv2.putText(frame, str(directions[3]), (10, 500), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)
                if directions[3] ==  -1:
                    # tello.send_rc_control(vals[0], vals[1], vals[2], vals[3])
                    # 動作傳到update
                    print("Directions: " + str(directions))
                    tello.updateMarkerAct(directions)
                    print("tello.land()+++++++++++++++++++++++++++++++++++++++++++++++++++++++")

                
                    
                    
                    

            # 標記周圍畫正方形
            cv2.aruco.drawDetectedMarkers(frame, corners)
        else:
            ### No id found
            cv2.putText(frame, "No Ids", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)


        return frame

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
                                        # vx(平)左右, vy(平)前後, vz(垂)上下, yaw轉向
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
    # tello = ControlTello()
    # tello.connect()
    # tello.streamon()

    cam = Camera()
    
    while True:
        frame = tello.get_frame_read().frame
        tello.tello_info = np.zeros((720, 480, 3), dtype=np.uint8)
        # 這裡是跑 Camera
        frame = cam.aruco(frame)
        
        # tello.TelloAct()
        if tello.getKeyboardInput(): 
            cv2.destroyAllWindows()
            break

        cv2.imshow('frame', frame)
        cv2.imshow('tello_info', tello.tello_info)
        cv2.waitKey(1)

    # tello.end()



if __name__ == '__main__':
    main()
else:
    pass