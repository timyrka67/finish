import serial
import datetime

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=.1)
on = False
finish = False
global start
global end
ready = 'Ready'
while True:
	data = arduino.readline()[:-2] #the last bit gets rid of the new-line chars
	if(ready in str(data)):
		print("READY TO GO")
	else:
		if data:
			if(on==True):
				on = False
				end = datetime.datetime.now()
				finish = True
			else:
				print(data," start ")
				on = True
				start = datetime.datetime.now()
		if(finish):
			print("Time: ",end-start)
			finish = False
			print(data, " finish ")
