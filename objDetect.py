import numpy as np
import argparse
import cv2
from cv2 import xfeatures2d as xf
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 20

if __name__ == "__main__":

    # Set up a parser for command line arguments
    parser = argparse.ArgumentParser( "Detect object" )
    parser.add_argument( "object", default="id", nargs='?', help="The object to detect" )

    args = parser.parse_args()

    path = 'trainImg/' + args.object + ".jpg"
    img1 = cv2.imread(path,0)

    #img1 = cv2.imread(path,0)
    # Use dictionary or simple input = filename
    #if args.object == "sid":
    #    img1 = cv2.imread('trainImg/sid.jpg',0)
    #elif args.object == "me":
    #    img1 = cv2.imread('trainImg/me.jpg',0)

    #img1 = cv2.imread('trainImg/sid.jpg',0)          # queryImage
    cam = cv2.VideoCapture(0)

    # Initiate SURF detector
    surf = xf.SURF_create(50)

    # find the keypoints and descriptors with SIFT
    kp1, des1 = surf.detectAndCompute(img1,None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    while(True):
        ret, img2 = cam.read()
        gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

        kp2, des2 = surf.detectAndCompute(gray, None)

        matches = flann.knnMatch(des1,des2,k=2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)

        if len(good)>MIN_MATCH_COUNT:
            try:
                src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
                matchesMask = mask.ravel().tolist()

                h,w = img1.shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)

                img2 = cv2.polylines(img2,[np.int32(dst)],True,255,3, cv2.LINE_AA)

                # Defining approximate centroid
                x = []
                y = []

                for p in dst:
                    x.append(np.int32(p[0][0]))
                    y.append(np.int32(p[0][1]))


                objcentre = (sum(x) / len(x), sum(y) / len(y))
                img2 = cv2.circle(img2, objcentre,10, (255,0,0))
        
            except AttributeError:
                print "Empty Mask"
            
        else:
            print "Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT)
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                           singlePointColor = None,
                           matchesMask = matchesMask, # draw only inliers
                           flags = 2)

        #img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)

        cv2.imshow("Good Matches",img2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
       # plt.imshow(img3, 'gray'),plt.show() 

    # When everything done, release the capture
    cam.release()
    cv2.destroyAllWindows()