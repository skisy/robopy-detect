import numpy as np
import argparse
import helper as h
import cv2
import robotControl as rc
from cv2 import xfeatures2d as xf
#rom matplotlib import pyplot as plt
import py_websockets_bot
import py_websockets_bot.mini_driver
import py_websockets_bot.robot_config
import time

MOVE_TOLERANCE = 100
neck_angles = dict([('tilt',150),('pan',100)])
latest_camera_image = None
robot = None

def getLastImage(image, image_time):
    global latest_camera_image

    latest_camera_image = image

def matchAndBox(img1,kp1,img2,kp2,matches,alg_params):

    global match_feedback
    global neck_angles
    global robot

    # Filter matches to keep only "good" matches
    good_matches = []
    for m,n in matches:
        if m.distance < alg_params['good_distance'] * n.distance:
            good_matches.append(m)

    # Only draw box if number of matches is greater than the set minimum (avoids excessive false alarms)
    if len(good_matches) > alg_params['min_match_num']:
        match_feedback['no_match'] = 0
        # Catch frame errors
        try:
            # Get keypoints of matching descriptors from both images
            source_points = np.float32([ kp1[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
            dest_points = np.float32([ kp2[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)

            # Find homography matrix between two images (estimaate transformation of keypoints between image planes)
            hom_matrix, mask = cv2.findHomography(source_points, dest_points, cv2.RANSAC, 5.0)
            #maskList = mask.ravel().tolist()

            # Get dimensions of train image
            height, width = img1.shape

            points = np.float32([ [0,0],[0,height-1],[width-1,height-1],[width-1,0] ]).reshape(-1,1,2)
            # Map keypoints by applying perspective transformation to matrix
            dest = cv2.perspectiveTransform(points, hom_matrix)

            # Draw box around object in image using homography matrix with perspective tranformation applied
            img2 = cv2.polylines(img2, [np.int32(dest)], True, 255, 3, cv2.LINE_AA)
            feed_height, feed_width, channels = img2.shape

            p1 = dest[0][0]
            p2 = dest[1][0]
            p3 = dest[2][0]
            p4 = dest[3][0]

            # Get corner points of box around object in frame
            x = [ np.int32(p1[0]), np.int32(p2[0]), np.int32(p3[0]), np.int32(p4[0])]
            y = [ np.int32(p1[1]), np.int32(p2[1]), np.int32(p3[1]), np.int32(p4[1])]

            ## Area was initially used to attempt to determine whether the robot was close enough to stop looking
            ## May still be of some use as descriptor matching is less likely to work effectively if object takes up
            ## more than 100% of the image
            #area = h.calculateFourSidedPolyArea(p1,p2,p3,p4)
            #area_percent = area / (feed_width * feed_height) * 100
            
            # Change to use object distance (with ultrasonic range finder)
            #if area_percent > 40:
                #print "Object Found"
                #robot.set_motor_speeds(0.0,0.0)

            #print str(area) + "/" + str(feed_width * feed_height)
            #print area_percent

            # Calculate approximate centroid
            obj_centre = (sum(x) / len(x), sum(y) / len(y))
            img2 = cv2.circle(img2, obj_centre,5, (0,0,255))

            # Move robot and keep track of current state
            match_feedback, neck_angles = rc.robotMove(robot, obj_centre, feed_height, feed_width, MOVE_TOLERANCE, match_feedback, neck_angles)

        except AttributeError:
            print "Empty Mask"
            robot.set_motor_speeds(20.0,-20.0)
    else:
        print "Not enough matches found"
        #print match_feedback['no_match']
        if (match_feedback['no_match'] > 20):
            neck_angles['tilt'] = 150
            robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
            match_feedback['no_match'] = 0
            robot.set_motor_speeds(20.0, -20.0)
            #time.sleep(0.8)
            #robot.set_motor_speeds(0,0)
        match_feedback['no_match'] += 1
        #maskList = None

    return img2

def setupMatch(obj,alg_params):

    global match_feedback
    global neck_angles
    global robot

    match_feedback = dict([('left_counter',0), ('right_counter',0), ('loc_counter',0), ('last_centre',(0,0)), ('no_match',0)])

    # Path to object image
    path = 'trainImg/' + obj

    # Load training image as grayscale
    img1 = cv2.imread(path,0)

    # Initiate camera feed (will need to be adapted for robot to keep stream alive)
    #cam = cv2.VideoCapture(0)

    # Initiate SURF detector with initial hessian value  (set by default or through UI)
    # Larger threshold should render fewer more salient points, smaller more but less salient points
    surf = xf.SURF_create(alg_params['hes_threshold'])

    # Set to use 128 descriptor size
    surf.setExtended(True)

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

    # Establish connection to robot via Websockets
    robot = py_websockets_bot.WebsocketsBot("192.168.42.1")

    # Create mini driver sensor configuration
    # Used to configure the inputs on the mini driver board
    sensorConfig = py_websockets_bot.mini_driver.SensorConfiguration(
        configD12 = py_websockets_bot.mini_driver.PIN_FUNC_ULTRASONIC_READ)

    robot_config = robot.get_robot_config()
    robot_config.miniDriverSensorConfiguration = sensorConfig
    robot.set_robot_config(robot_config)
    robot.start_streaming_camera_images(getLastImage)

    # Sets neck degrees to initial values (should centre neck if servos configured correctly)
    robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
    feed_error = 0

    # Main loop processes current frame and matches features from original image
    while(True):
        try:
            robot.update()

            if latest_camera_image != None:
                img2 = latest_camera_image
                # Convert frame to grayscale (algorithm uses pixel gray intensities)
                gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

                # Detect and compute keypoints/descripts for stream frame
                kp2, des2 = surf.detectAndCompute(gray,None)

                # Calculate descriptor matches with FLANN
                matches = flann.knnMatch(des1,des2,k=2)

                # Send keypoints/matching descriptors to find location of object in image and return image with bounding box around image
                img2 = matchAndBox(img1,kp1,img2,kp2,matches,alg_params)
                #print match_feedback['left_counter']
                #print match_feedback['right_counter']
                #print match_feedback['last_centre']

                # Display frame
                cv2.imshow("Live Stream with Detected Objects", img2)
                feed_error = 0 
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except cv2.error:
            if feed_error > 5:
                robot.set_motor_speeds(20.0, -20.0)
            feed_error += 1
            match_feedback['no_match'] = 0            
            print "Please check camera feed - ensure it is not obscured"
    robot.disconnect()
    cv2.destroyAllWindows()

