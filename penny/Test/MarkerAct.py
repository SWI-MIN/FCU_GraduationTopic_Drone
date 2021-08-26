import csv
import numpy as np 
import cv2
import sys, time, math
from djitellopy import Tello

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
        print("test")
        return switcher.get(selected, "Invalid marker type")


def main():
    tello = Tello()
    tello.connect()
    tello.streamon()
    while True:
        frame = tello.get_frame_read().frame
        cv2.imshow('frame', frame)

        #--- use 'q' to quit
        key = cv2.waitKey(1)
        if key == ord('q'):
            tello.end()
            cv2.destroyAllWindows()
            break
        #--- use 'r' to takeoff
        elif key == ord('r'):
            tello.takeoff()
            target = TargetDefine()
            # 開始找標籤, 把標籤傳進target
            calib_path  = ".\\Camera_Correction\\"
            cam_matrix   = np.loadtxt(calib_path+'cameraMatrix.txt', delimiter=',')   
            cam_distortion   = np.loadtxt(calib_path+'cameraDistortion.txt', delimiter=',')   
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            aruco_dict  = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)      # original
            parameters  = cv2.aruco.DetectorParameters_create()
            corners, ids, rejected = cv2.aruco.detectMarkers(image=gray, dictionary=aruco_dict, parameters=parameters,
                              cameraMatrix=cam_matrix, distCoeff=cam_distortion)

            # (平)左右, (平)前後, (垂)上下, 轉向
            # tello.send_rc_control(vals[0], vals[1], vals[2], vals[3])
            # Target_ID = self.target.changeTarget(ids[i][0])[0][3]
            if target.changeTarget(ids)[0][3] ==  -1:
                tello.land()
            break



if __name__ == '__main__':
    main()
else:
    pass


