import numpy as np
import cv2

# cv2.putText(影像,文字,座標,字型,大小,顏色,線條寬度,線條種類)
# 線條種類 : 預設值為 cv2.LINE_8，若設定為 cv2.LINE_AA 則有反鋸齒（anti-aliasing）的效果

# 影像
img = np.zeros((400, 400, 3), np.uint8)
img.fill(90)        # fill 填充 0~255 黑到白
# 文字
text = 'TEST IMG! 123'
# 座標
coordinate =  (10, 80)
# 字型
font = cv2.FONT_HERSHEY_DUPLEX
# 大小
font_size = 0.5
# 顏色 BGR
# font_colour = (255, 255, 0) # 藍綠色
font_colour = (0, 170, 255) # 銘黃色
# 線條寬度
line_width = 1
# 線條種類
line_type = cv2.LINE_AA
cv2.putText(img, text, coordinate, font,
  font_size, font_colour, line_width, line_type)



# # 影像
# img = np.zeros((400, 400, 3), np.uint8)
# img.fill(90)        # fill 填充 0~255 黑到白

# # 文字
# text = 'Hello, OpenCV! 123 456 798'

# # 使用各種字體
# cv2.putText(img, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 80), cv2.FONT_HERSHEY_PLAIN,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 120), cv2.FONT_HERSHEY_DUPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 160), cv2.FONT_HERSHEY_COMPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 200), cv2.FONT_HERSHEY_TRIPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 240), cv2.FONT_HERSHEY_COMPLEX_SMALL,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 280), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)

# cv2.putText(img, text, (10, 320), cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
#   1, (0, 255, 255), 1, cv2.LINE_AA)


cv2.imshow('My Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()