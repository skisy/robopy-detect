import csv
import Tkinter
import cv2
import numpy as np
import math

def processFile(filepath):
	with open(filepath, 'rb') as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		objects = []
		for row in reader:
			objects.append(row)
		return objects

def writeFile(filepath, content):
    with open(filepath,'wb') as csv_file:
    	writer = csv.writer(csv_file, delimiter=',')
    	for obj in content:
    		writer.writerow(obj)

def cropImage(img):
	title = "Crop Image"

	global cursor_pos
	global top_left
	global bottom_right
	global released_once

	cursor_pos = None
	top_left = None
	bottom_right = None
	released_once = False

	cv2.namedWindow(title)

	def onMouse(event, x, y, flags, param):
		global cursor_pos
		global top_left
		global bottom_right
		global released_once

		cursor_pos = (x, y)

		if top_left is not None and not (flags & cv2.EVENT_FLAG_LBUTTON):
			released_once = True

		if flags & cv2.EVENT_FLAG_LBUTTON:
			if top_left is None:
				top_left = cursor_pos
			elif released_once:
				bottom_right = cursor_pos

	cv2.setMouseCallback(title, onMouse)
	cv2.imshow("Crop Image",img)

	while bottom_right is None:
		im_draw = np.copy(img)

		if top_left is not None:
			cv2.rectangle(im_draw, top_left, cursor_pos, (255, 0, 0))

		cv2.imshow(title, im_draw)
		_ = cv2.waitKey(10)

	cv2.destroyWindow(title)

	(width, height) = np.subtract(bottom_right,top_left)
	cropped = img[top_left[1]:top_left[1]+height,top_left[0]:top_left[0]+width]
	return cropped

def calculateFourSidedPolyArea(p1, p2, p3, p4):
	d1to2 = calculateDistanceBetweenPoints(p1,p2)
	print d1to2
	d2to3 = calculateDistanceBetweenPoints(p2,p3)
	print d2to3
	d3to4 = calculateDistanceBetweenPoints(p3,p4)
	print d3to4
	d4to1 = calculateDistanceBetweenPoints(p4,p1)
	print d4to1
	d4to2 = calculateDistanceBetweenPoints(p4,p2)
	print d4to2

	t1a = calculateAreaOfTriangle(d1to2,d4to2,d4to1)
	t2a = calculateAreaOfTriangle(d4to2,d3to4,d2to3)

	area = t1a + t2a

	return area
	

def calculateDistanceBetweenPoints(p1,p2):
	return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def calculateAreaOfTriangle(s1,s2,s3):
	p = (s1 + s2 + s3) / 2
	try:
		area = math.sqrt((p*(p-s1)*(p-s2)*(p-s3)))
	except ValueError:
		area = 0
	return area