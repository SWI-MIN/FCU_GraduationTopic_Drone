from cv2 import cv2
import numpy as np
# 生成aruco标记
# 加载预定义的字典
dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)

# 生成标记
markerImage = np.zeros((1000, 1000), dtype=np.uint8)
markerImage = cv2.aruco.drawMarker(dictionary, 21, 2000, markerImage, 1)
cv2.imwrite("marker21.png", markerImage)
