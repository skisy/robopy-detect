import time
import argparse
import dateutil
import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import py_websockets_bot

latest_camera_image = None
neck_pan = 90
neck_tilt = 90

def convertAndDisplay(image, image_time):
	global latest_camera_image
	global neck_pan
	global neck_tilt
	
	grayimage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	grayimage = cv2.GaussianBlur(grayimage,(19, 19),0)
	(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(grayimage)
	cv2.circle(image, maxLoc, 19,(255,0,0),2)
	latest_camera_image = image

# Move robot (motors) to face bright spot
#	if maxLoc[0] > 500:
#		robot.set_motor_speeds(20,-20)
#	elif maxLoc[0] < 100:
#		robot.set_motor_speeds(-20,20)
		
# Move camera (pan/tilt servos) to face bright spot
	if centre > 480 and (neck_pan - 1) > 40:
		neck_pan = neck_pan - 1
	elif centre < 160  and (neck_pan + 1) < 140 :
		neck_pan = neck_pan + 1
	robot.set_neck_angles(pan_angle_degrees=neck_pan, tilt_angle_degrees=neck_tilt)
	if centre < 115 and (neck_tilt + 1) < 160:
		neck_tilt = neck_tilt + 1
	elif centre > 345 and (neck_tilt - 1) > 20:
		neck_tilt = neck_tilt - 1
	robot.set_neck_angles(pan_angle_degrees=neck_pan, tilt_angle_degrees=neck_tilt)	

if __name__ == "__main__":
	p = argparse.ArgumentParser("Tracks brightest spot in image from robot camera feed")
	p.add_argument("hostname", default="192.168.42.1", nargs='?', help="IP of Robot")

	args = p.parse_args()

	robot = py_websockets_bot.WebsocketsBot(args.hostname)
	robot.start_streaming_camera_images(convertAndDisplay)
	robot.centre_neck()

	try:
		while True:
			robot.update()
			if latest_camera_image != None:
					cv2.imshow("image", latest_camera_image)

			cv2.waitKey(1)

	except KeyboardInterrupt:
		pass

	robot.disconnect()