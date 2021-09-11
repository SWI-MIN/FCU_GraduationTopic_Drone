from djitellopy import Tello
import cv2 
import time

tello = Tello()
tello.connect()

print(tello.get_battery())


tello.streamon()
tello.set_speed(10)
while 1:
    img = tello.get_frame_read().frame
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27: # ESC
        break





# tello.takeoff()

# tello.move_forward(100)
# tello.rotate_counter_clockwise(90)
# tello.move_forward(100)
# # tello.move_back(100)

# tello.land()