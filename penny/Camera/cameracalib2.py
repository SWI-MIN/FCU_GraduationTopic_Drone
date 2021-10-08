import cv2
import numpy as np
import glob
# 設定尋找亞畫素角點的引數，採用的停止準則是最大迴圈次數30和最大誤差容限0.001
criteria = (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS,30,0.001)
# 獲取標定板角點的位置
objp = np.zeros((6 * 9,3),np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2) # 將世界座標系建在標定板上，所有點的Z座標全部為0，所以只需要賦值x和y
obj_points = [] # 儲存3D點
img_points = [] # 儲存2D點
images = glob.glob("D:\Academic\GraduationTopic\FCU_GraduationTopic_Drone\penny\Camera\Images1008_50random/*.jpg")
for fname in images:

  img = cv2.imread(fname)
  cv2.imshow('img',img)
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  size = gray.shape[::-1]
  ret,corners = cv2.findChessboardCorners(gray,(6,9),None)
  print(ret)

  if ret:
    obj_points.append(objp)
    corners2 = cv2.cornerSubPix(gray,corners,(5,5),(-1,-1),criteria) # 在原角點的基礎上尋找亞畫素角點

    #print(corners2)
    if [corners2]:
      img_points.append(corners2)
    else:
      img_points.append(corners)

 

    cv2.drawChessboardCorners(img,(9,6),corners2,ret) # 記住，OpenCV的繪製函式一般無返回值
    cv2.imshow('img',img)
    cv2.waitKey(2000)

print(len(img_points))

cv2.destroyAllWindows()

# 標定

ret,mtx,dist,rvecs,tvecs = cv2.calibrateCamera(obj_points,img_points,size,None,None)

print("ret:",ret)
print("mtx:\n",mtx) # 內參數矩陣
print("dist:\n",dist) # 畸變係數  distortion cofficients = (k_1,k_2,p_1,p_2,k_3)
print("rvecs:\n",rvecs) # 旋轉向量 # 外引數
print("tvecs:\n",tvecs ) # 平移向量 # 外引數
print("-----------------------------------------------------")
