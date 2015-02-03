import numpy as np
import argparse
import cv2
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 20

def matchAndBox(img1,kp1,img2,kp2,matches):

    # Filter matches to keep only "good" matches
    good_matches = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    # Only draw box if number of matches is greater than the set minimum (avoids excessive false alarms)
    if len(good_matches) > MIN_MATCH_COUNT:
        # Catch frame errors
        try:
            source_pts = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
            dest_pts = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(source_pts, dest_pts, cv2.RANSAC, 5.0)
            maskList = mask.ravel().tolist()

            # Get dimensions of train image
            height, width = img1.shape

            # Get points from train image and apply transform to fit mask (based on located keypoints in frame)
            points = np.float32([ [0,0],[0,height-1],[width-1,height-1],[width-1,0] ]).reshape(-1,1,2)
            dest = cv2.perspectiveTransform(points, M)

            img2 = cv2.polylines(img2, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)

            # Corner points of mask applied to frame image
            x = [ np.int32(dest[0][0][0]), np.int32(dest[1][0][0]), np.int32(dest[2][0][0]), np.int32(dest[3][0][0])]
            y = [ np.int32(dest[0][0][1]), np.int32(dest[1][0][1]), np.int32(dest[2][0][1]), np.int32(dest[3][0][1])]

            # Calculate approximate centroid
            objcentre = (sum(x) / len(x), sum(y) / len(y))
            img2 = cv2.circle(img2, objcentre,5, (0,0,255))
        except AttributeError:
            print "Empty Mask"
    else:
        print "Not enough matches found"
        maskList = None

    return img2

def displayMatch(obj):

    # Set up a parser for command line arguments
    #parser = argparse.ArgumentParser( "Detect object" )
    #parser.add_argument( "object", default="id", nargs='?', help="The object to detect" )

    #args = parser.parse_args()

    path = 'trainImg/' + obj

    # Load training image as grayscale
    img1 = cv2.imread(path,0)

    # Initiate camera feed (will need to be adapted for robot to keep stream alive)
    cam = cv2.VideoCapture(0)

    # Initiate SURF detector with initial hessian value 
    surf = xf.SURF_create(50)

    # Detect keypoints and compute descriptors using SURF algorithm
    kp1, des1 = surf.detectAndCompute(img1,None)

    # Set up parameters for FLANN matching
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    # Initiate FLANN object with parameters
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # Match and display output loop
    while(True):
        # Get camera stream frame
        ret, img2 = cam.read()

        # Convert frame to grayscale (algorithm uses pixel gray intensities)
        gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

        # Detect and compute keypoints/descripts for stream frame
        kp2, des2 = surf.detectAndCompute(gray,None)

        # Calculate matches with FLANN
        matches = flann.knnMatch(des1,des2,k=2)

        img2 = matchAndBox(img1,kp1,img2,kp2,matches)

        cv2.imshow("Live Stream with Detected Objects", img2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

