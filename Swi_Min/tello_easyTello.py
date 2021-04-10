from easytello import tello
import time
myTello = tello.Tello()

myTello.takeoff()
# myTello.forward(80)
# myTello.cw(180)
# myTello.forward(80)
myTello.streamon() #開啟影像串流
# myTello.wait(25.55)  # 開啟 wait 會把後面的指令吃掉
time.sleep(15)         # 用 sleep 不會吃掉後面指令，會先睡完在執行
                       # 目前跑起來，當有在移動的時候畫面會變得很糟糕
# myTello.forward(80)
# myTello.cw(180)
# myTello.forward(80)
# myTello.forward(80)
# myTello.cw(180)
# myTello.forward(80)
myTello.land()
myTello.streamoff() #關閉影像串流