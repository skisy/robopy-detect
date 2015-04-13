import numpy as np
import cv2
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt

img = cv2.imread('trainImg/Android.jpg',1)
grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

surf = xf.SURF_create(100) # Initialise surf object with minimum hessian threshold
#surf.setUpright(True)

# Detect keypoints and compute detectors for both images
train_kp, train_des = surf.detectAndCompute(grey,None)

cv2.drawKeypoints(img,train_kp,img,(255,0,0),0)
print len(train_kp)

plt.imshow(img),plt.show() 