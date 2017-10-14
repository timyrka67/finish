import cv2
capture = cv2.VideoCapture(1)

while True:
    flag, frame = capture.read()
    print flag

    if flag == 0:
        break
    cv2.imshow("Video", frame)
    key_pressed = cv2.waitKey(10)    #Escape to exit
    if key_pressed == 27:
        break
