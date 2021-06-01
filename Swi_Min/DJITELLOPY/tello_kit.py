from djitellopy import Tello
from time import sleep
tello = Tello()

tello.connect()
sleep(1)
print(tello.get_battery())
sleep(1)
tello.takeoff()
sleep(8)

tello.move_left(25)
sleep(3)
tello.move('left',25)
sleep(3)
tello.rotate_clockwise(360)
sleep(8)
tello.move_right(50)
sleep(3)
tello.land()
