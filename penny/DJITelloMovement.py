from djitellopy import Tello
from time import sleep

tello = Tello()

tello.connect()
sleep(3)
tello.takeoff()
sleep(5)
# tello.move_left(100)
# sleep(3)
# tello.rotate_counter_clockwise(90)
# sleep(8)
# tello.move_forward(100)
# sleep(3)
# tello.land()

tello.send_rc_control(0, 50, 0, 0)      #29:45 
sleep(2)
tello.send_rc_control(20, 0, 0, 0)
sleep(2)
tello.send_rc_control(0, 0, 0, 0)
tello.land()

