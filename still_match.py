import numpy as np
import cv2
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt

img1 = cv2.imread('trainImg/strep.jpg',0) # Load train image as greyscale
img2 = cv2.imread('trainImg/strep2.jpg',1) # Load query image in RGB
grey = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY) # Convert query image to greyscale (SURF uses greyscale pixel intensities)

surf = xf.SURF_create(0) # Initialise surf object with minimum hessian threshold

# Detect keypoints and compute detectors for both images
train_kp, train_des = surf.detectAndCompute(img1,None)
query_kp, query_des = surf.detectAndCompute(grey,None)

# Match descriptors with brute force matching
brute_force = cv2.BFMatcher()
matches = brute_force.knnMatch(train_des,query_des,k=2)

counter = 0
# Compare descriptor distance to find good matches
good_matches = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        counter += 1
        good_matches.append([m])

print counter

out_img = cv2.drawMatchesKnn(img1,train_kp,grey,query_kp,matches,None,flags=0)

plt.imshow(out_img),plt.show()