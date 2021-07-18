# 擷取 webcam 的畫面
import cv2

while 1:

    video = cv2.VideoCapture(0)
    matrix, frame = video.read()
    print(frame)
    cv2.imshow("Capture", frame)
    # cv2.waitKey(0)
    cv2.waitKey(1)
    # key = cv2.waitKey(1)
    # if key == ord("q"):
    #     break

video.release()
cv2.destroyAllWindows()