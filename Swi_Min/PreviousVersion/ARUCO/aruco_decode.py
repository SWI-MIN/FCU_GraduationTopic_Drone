import numpy as np
import time
from cv2 import cv2
# from cv2 import cv2.aruco as aruco
#读取图片
frame=cv2.imread('1399.jpg')
#调整图片大小
frame=cv2.resize(frame,None,fx=0.8,fy=0.8,interpolation=cv2.INTER_CUBIC)
#灰度话
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#设置预定义的字典
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
#使用默认值初始化检测器参数
parameters =  cv2.aruco.DetectorParameters_create()
#使用aruco.detectMarkers()函数可以检测到marker，返回ID和标志板的4个角点坐标
corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
#画出标志位置
cv2.aruco.drawDetectedMarkers(frame, corners,ids)


cv2.imshow("frame",frame)
cv2.waitKey(0)
cv2.destroyAllWindows()


# cv2.aruco.detectMarkers(gray,aruco_dict,parameters=parameters)
# 第一个参数是待检测marker的图像。
# 第二个参数是字典对象，在这一例子中是之前定义的字典 (DICT_6X6_250).