import csv
import Tkinter
import cv2
import numpy as np

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

def cropImage(image_path):
	img = cv2.imread(image_path)
	title = "Crop Image"

	## TEST CODE
	global current_pos
	global top_left
	global bottom_right
	global released_once

	current_pos = None
	top_left = None
	bottom_right = None
	released_once = False

	cv2.namedWindow(title)

	def onMouse(event, x, y, flags, param):
		global current_pos
		global top_left
		global bottom_right
		global released_once

		current_pos = (x, y)

		if top_left is not None and not (flags & cv2.EVENT_FLAG_LBUTTON):
			released_once = True

		if flags & cv2.EVENT_FLAG_LBUTTON:
			if top_left is None:
				top_left = current_pos
			elif released_once:
				bottom_right = current_pos

	cv2.setMouseCallback(title, onMouse)
	cv2.imshow("Crop Image",img)

	while bottom_right is None:
		print current_pos
		im_draw = np.copy(img)

		if top_left is not None:
			cv2.rectangle(im_draw, top_left, current_pos, (255, 0, 0))

		cv2.imshow(title, im_draw)
		_ = cv2.waitKey(10)

		# @TODO Save cropped image

	
