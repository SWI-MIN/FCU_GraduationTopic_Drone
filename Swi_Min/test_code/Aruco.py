import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello
from ControlTello import ControlTello
import pygame


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

    def aruco(self, frame):
        if np.all(self.cam_matrix== None) or np.all(self.cam_distortion == None):
        # if self.cam_matrix == None or self.cam_distortion == None:
            calib_path  = ".\\Camera_Correction\\"
            self.cam_matrix   = np.loadtxt(calib_path+'cameraMatrix.txt', delimiter=',')   
            self.cam_distortion   = np.loadtxt(calib_path+'cameraDistortion.txt', delimiter=',')   
        
        # 使用OpenCV进行标定（Python）https://blog.csdn.net/u010128736/article/details/52875137
        h, w = frame.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(self.cam_matrix,self.cam_distortion,(w,h),1,(w,h))
        # Undistort
        frame = cv2.undistort(frame, self.cam_matrix, self.cam_distortion, None, newcameramtx)
        # Crop image
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
            
            # 將所有讀到的 id 加到 id_list 中
            for i in range(0, ids.size):
                cv2.aruco.drawAxis(frame, self.cam_matrix, self.cam_distortion, rvecs[i], tvecs[i], 10)  # Draw axis
                id_list.append(ids[i][0])
            # 標記周圍畫正方形
            cv2.aruco.drawDetectedMarkers(frame, corners)
        else:
            ### No id found
            cv2.putText(frame, "No Ids", (10, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 170, 255),1,cv2.LINE_AA)


        return frame

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
        # frame = aruco(frame)
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