from easytello import tello
import time
myTello = tello.Tello()

myTello.takeoff()
myTello.forward(80)
myTello.cw(180)
myTello.forward(80)
myTello.streamon() #開啟影像串流
myTello.wait(25.55)
myTello.forward(80)
myTello.cw(180)
myTello.forward(80)
myTello.forward(80)
myTello.cw(180)
myTello.forward(80)
myTello.land()
myTello.streamoff() #關閉影像串流