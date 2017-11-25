# USAGE
# python motion_detector.py
# python motion_detector.py --video videos/example_01.mp4

# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
from collections import deque
import threading
import thread
import numpy as np
import tracking
from tracking import Tracking

def update(time):
  print "Frame updated "
  threading.Timer(time, update, (time,)).start()
  global firstFrame, tracking
  tracking.clean()
  firstFrame = None


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=800, help="minimum area size")
args = vars(ap.parse_args())
firstFrame = None
buffer = 32
pts = deque(maxlen=buffer)
print cv2.__version__
counter = 0
(dX, dY) = (0, 0)
direction = ""
tracking = Tracking()

def run():
    global tracking, direction, dX, dY, firstFrame, args, counter
    if args.get("video", None) is None:
        camera = cv2.VideoCapture(1)
        time.sleep(0.25)
    else:
        camera = cv2.VideoCapture(args["video"])

    while True:
        (grabbed, frame) = camera.read()
        text = "Unoccupied"
        if not grabbed:
            break

        # resize the frame, convert it to grayscale, and blur it
        frame = imutils.resize(frame, width=500, height=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if firstFrame is None:
            firstFrame = gray
            continue
        tracking.drawFinishLine(frame, [40, 5], [40, frame.shape[0]-5])
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        #CHAIN_APPROX_TC89_L1, CHAIN_APPROX_TC89_KCOS, CHAIN_APPROX_SIMPLE, CHAIN_APPROX_NONE
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in cnts:
            if cv2.contourArea(c) < args["min_area"]:
                continue
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            x = int((box[2][0]+ box[0][0])/2)
            y = int((box[2][1]+ box[0][1])/2)
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            tracking.add_point(frame, [x,y])
            text = "Occupied"
        tracking.drawLines(frame)
        tracking.drawFinisher(frame)
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%d/%m/%y %I:%M:%S%p"),
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # show the frame and record if the user presses a key
        cv2.imshow("Feed", frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFFF

        if key == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()


try:
    thread.start_new_thread(update, (10,)) ##update every 30 sec
    thread.start_new_thread(run, ())

except:
    print "Error: unable to start thread"
while 1:
   pass
