import time, cv2
from threading import Thread
from djitellopy import Tello

tello = Tello()

tello.connect()

video_On = False
tello.streamon()
img = tello.get_frame_read().frame

def videoRecorder():
    # create a VideoWrite object, recoring to ./video.avi
    height, width, _ = img.shape
    video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))

    while video_On:
        video.write(img)
        time.sleep(1 / 30)

    video.release()

# we need to run the recorder in a seperate thread, otherwise blocking options
#  would prevent frames from getting added to the video
# recorder = Thread(target=videoRecorder)
# recorder.start()
while 1:
    img = tello.get_frame_read().frame
    cv2.imshow("Drone Control Centre", img)
    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        tello.land()    # 因為end()裡面的land()沒有作用
        tello.end()
        break
    elif key == ord('v'):
        video_On = True
        recorder = Thread(target=videoRecorder)
        recorder.start()
    elif key == ord('b'):
        video_On = False
        # recorder.join()
# recorder.join()
