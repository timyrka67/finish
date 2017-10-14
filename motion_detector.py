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

def update(time):
  print "Frame updated "
  threading.Timer(time, update, (time,)).start()
  global firstFrame
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

def run():
    global direction, dX, dY, firstFrame, args, counter
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
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if firstFrame is None:
            firstFrame = gray
            continue

        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        #CHAIN_APPROX_TC89_L1, CHAIN_APPROX_TC89_KCOS, CHAIN_APPROX_SIMPLE, CHAIN_APPROX_NONE
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            pts.appendleft(center)

        for i in np.arange(1, len(pts)):
            if pts[i - 1] is None or pts[i] is None:
                continue
            thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 0), thickness)

        for c in cnts:
            if cv2.contourArea(c) < args["min_area"]:
                continue
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)

            text = "Occupied"

        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%d/%m/%y %I:%M:%S%p"),
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # show the frame and record if the user presses a key
        cv2.imshow("Feed", frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
    camera.release()
    cv2.destroyAllWindows()


try:
    thread.start_new_thread(update, (1000,)) ##update every 30 sec
    thread.start_new_thread(run, ())

except:
    print "Error: unable to start thread"
while 1:
   pass
