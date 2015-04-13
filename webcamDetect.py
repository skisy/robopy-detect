import numpy as np
import argparse
import cv2
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt
import time

minimum_matches = 20
no_match = 0

def matchAndBox(trainImg,orig_kp,queryImg,query_kp,matches):
    global no_match

    # Filter matches to keep only "good" matches
    good_matches = []
    for m,n in matches:
        if m.distance < 0.6 * n.distance:
            good_matches.append(m)

    # Only draw box if number of matches is greater than the set minimum (avoids excessive false alarms)
    if len(good_matches) > minimum_matches:
        # Catch frame errors
        try:
            # Get keypoints of matching descriptors from both images
            source_pts = np.float32([ orig_kp[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
            dest_pts = np.float32([ query_kp[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)

            # Find homography matrix between two images (estimaate transformation of keypoints between image planes)
            H, mask = cv2.findHomography(source_pts, dest_pts, cv2.RANSAC, 5.0)
            maskList = mask.ravel().tolist()

            # Get dimensions of train image
            height, width = trainImg.shape

            # Get points from train image and apply transform to fit mask (based on located keypoints in frame)
            points = np.float32([ [0,0],[0,height-1],[width-1,height-1],[width-1,0] ]).reshape(-1,1,2)
            dest = cv2.perspectiveTransform(points, H)

            # Draw box
            queryImg = cv2.polylines(queryImg, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)

            # Corner points of mask applied to frame image
            x = [ np.int32(dest[0][0][0]), np.int32(dest[1][0][0]), np.int32(dest[2][0][0]), np.int32(dest[3][0][0])]
            y = [ np.int32(dest[0][0][1]), np.int32(dest[1][0][1]), np.int32(dest[2][0][1]), np.int32(dest[3][0][1])]

            # Calculate approximate centroid
            objcentre = (sum(x) / len(x), sum(y) / len(y))
            queryImg = cv2.circle(queryImg, objcentre,5, (0,0,255))
        except AttributeError:
            print "Empty Mask"
            no_match = no_match + 1
    else:
        print "Not enough matches found"
        no_match = no_match + 1
        maskList = None

    return queryImg

if __name__ == "__main__":

    # Set up a parser for command line arguments
    parser = argparse.ArgumentParser( "Detect object" )
    parser.add_argument( "object", default="id", nargs='?', help="The object to detect" )

    args = parser.parse_args()

    path = 'trainImg/' + args.object + ".jpg"

    # Load training image as grayscale
    trainImg = cv2.imread(path,0)

    # Initiate camera feed (will need to be adapted for robot to keep stream alive)
    cam = cv2.VideoCapture(0)

    # Initiate SURF detector with initial hessian threshold value 
    surf = xf.SURF_create(100)

    # Detect keypoints and compute descriptors from train image using SURF algorithm
    orig_kp, orig_des = surf.detectAndCompute(trainImg,None)

    # Set up parameters for FLANN matching
    index_params = dict(algorithm = 0, trees = 5)   # Algorithm selection = Index K-D Tree
    # Specify number of times to recursively traverse index trees - higher = more accurate but slower
    search_params = dict(checks = 70)   

    # Initiate FLANN object with parameters
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    frames = 0
    initiate = False
    # Match and display output loop
    while(True):
        # Get camera stream frame
        ret, queryImg = cam.read()

        # Convert frame to grayscale (algorithm uses pixel gray intensities)
        grey = cv2.cvtColor(queryImg,cv2.COLOR_BGR2GRAY)

        # Detect and compute keypoints/descripts for stream frame
        query_kp, query_des = surf.detectAndCompute(grey,None)

        # Calculate matches with FLANN
        matches = flann.knnMatch(orig_des,query_des,k=2)

        queryImg = matchAndBox(trainImg,orig_kp,queryImg,query_kp,matches)
        cv2.imshow("Live Stream with Detected Objects", queryImg)
        frames = frames + 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print frames
            print no_match
            break
        # Used to sync with recording stream
        if not initiate:
            raw_input("Hit return to intiate")
            initiate = True

    cam.release()
    cv2.destroyAllWindows()