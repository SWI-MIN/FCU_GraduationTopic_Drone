from djitellopy import Tello
import cv2 
import time
tello = Tello()

tello.connect()

print(tello.get_battery())
tello.streamon()
while 1:
    img = tello.get_frame_read().frame
    img = cv2.resize(img,(360,240))
    cv2.imshow("Image", img)
    cv2.waitKey(1)





# tello.takeoff()

# tello.move_forward(100)
# tello.rotate_counter_clockwise(90)
# tello.move_forward(100)
# # tello.move_back(100)

# tello.land()