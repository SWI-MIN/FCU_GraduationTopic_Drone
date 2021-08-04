from cv2 import cv2
import numpy as np
# 生成aruco标记
# 加载预定义的字典
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# 生成标记
markerImage = np.zeros((1000, 1000), dtype=np.uint8)
markerImage = cv2.aruco.drawMarker(dictionary, 21, 200, markerImage, 1)

cv2.imwrite("marker21.png", markerImage)



# EX : cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
#      cv2.aruco.drawMarker(dictionary, 21, 200, markerImage, 1)
# 參數2 : 從250個aruco標記組成的集合中選擇 ID ， 由0~249表示
# 參數3 : 生成的標記大小，EX : 200 --> 200*200 像素的圖像
# 參數4 : 要儲存aruco標記的目標
# 參數5 : 邊界寬度參數

# 意義 : 在 6*6 圖形周圍加上 1 位元的邊界，並以 200*200 像素的圖片中生成 7*7 的aruco圖像