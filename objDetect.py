import numpy as np
import argparse
import cv2
import robotControl as rc
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt

MOVE_TOLERANCE = 100

def matchAndBox(img1,kp1,img2,kp2,matches,alg_params):

    global match_feedback

    # Filter matches to keep only "good" matches
    good_matches = []
    for m,n in matches:
        if m.distance < alg_params['good_distance'] * n.distance:
            good_matches.append(m)

    # Only draw box if number of matches is greater than the set minimum (avoids excessive false alarms)
    if len(good_matches) > alg_params['min_match_num']:
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

            # Draw box around object in image
            img2 = cv2.polylines(img2, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)
            feed_height, feed_width, channels = img2.shape

            # Corner points of mask applied to frame image
            x = [ np.int32(dest[0][0][0]), np.int32(dest[1][0][0]), np.int32(dest[2][0][0]), np.int32(dest[3][0][0])]
            y = [ np.int32(dest[0][0][1]), np.int32(dest[1][0][1]), np.int32(dest[2][0][1]), np.int32(dest[3][0][1])]

            # Calculate approximate centroid
            obj_centre = (sum(x) / len(x), sum(y) / len(y))
            img2 = cv2.circle(img2, obj_centre,5, (0,0,255))

            match_feedback = rc.robotMove(obj_centre, feed_height, feed_width, MOVE_TOLERANCE, match_feedback)

        except AttributeError:
            print "Empty Mask"
    else:
        print "Not enough matches found"
        maskList = None

    return img2

def displayMatch(obj,alg_params):

    global match_feedback

    match_feedback = dict([('left_counter',0),('right_counter',0),('loc_counter',0),('last_centre',(0,0))])

    # Path to object image
    path = 'trainImg/' + obj

    # Load training image as grayscale
    img1 = cv2.imread(path,0)

    # Initiate camera feed (will need to be adapted for robot to keep stream alive)
    cam = cv2.VideoCapture(0)

    # Initiate SURF detector with initial hessian value 
    surf = xf.SURF_create(alg_params['hes_threshold'])
    
    # Setting Upright flags means algorithm does not consider rotation - still good to about 15 degrees
    #surf.setUpright(True)

    # Detect keypoints and compute descriptors using SURF algorithm
    kp1, des1 = surf.detectAndCompute(img1,None)

    # Set up parameters for FLANN matching
    FLANN_INDEX_KDTREE = 0

    # Tell FLANN matcher to use k-dimensional index trees (8) - trees are randomised and searched in parallel
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 8)

    # Specify number of times to recursively traverse index trees
    search_params = dict(checks = 100)

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

        img2 = matchAndBox(img1,kp1,img2,kp2,matches,alg_params)
        #print match_feedback['left_counter']
        #print match_feedback['right_counter']
        #print match_feedback['last_centre']

        cv2.imshow("Live Stream with Detected Objects", img2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

