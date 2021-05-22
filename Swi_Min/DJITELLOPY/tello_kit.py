from djitellopy import Tello
import time
tello = Tello()

tello.connect()
# time.sleep(1)
tello.takeoff()
# time.sleep(1)
tello.move_left(150)
# time.sleep(1)
tello.rotate_counter_clockwise(180)
# time.sleep(1)
tello.move_right(150)
# time.sleep(1)
tello.rotate_counter_clockwise(180)
# time.sleep(1)
tello.land()
