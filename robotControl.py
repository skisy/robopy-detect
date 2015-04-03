import math
import py_websockets_bot
import time

def minDistanceReached(robot, min_dist):
    status_dict, read_time = robot.get_robot_status_dict()

    sensor_dict = status_dict["sensors"]

    distance = sensor_dict["ultrasonic"]["data"]

    print distance

    return (distance <= min_dist)

def robotMove(robot, centre, height, width, move_tolerance, match_feedback, neck_angles):

    object_found = False

    # Calculate distance between current centre and last centre point using Pythagorean theory
    coord_distance = math.hypot(centre[0] - match_feedback['last_centre'][0], centre[1] - match_feedback['last_centre'][1])
    #print coord_distance

    lc = match_feedback['left_counter']
    rc = match_feedback['right_counter']

    if coord_distance < move_tolerance:
        if minDistanceReached(robot, 15):
            print "OBJECT FOUND!"
            object_found = True

        if centre[0] < (width / 5):
            rc = 0
            lc += 1
            lc = 0
            robot.set_motor_speeds(-15.0,15.0)
            time.sleep(0.5)
            print "Turn Left"
        elif centre[0] > (width / 5 * 4):
            lc = 0
            rc += 1
            rc = 0
            robot.set_motor_speeds(15.0, -15.0)
            print "Turn Right"
            time.sleep(0.5)
        elif centre[1] < (height / 5):
            if (neck_angles['tilt'] - 1) > 20:
                neck_angles['tilt'] -= 1
            #print "CURRENT ANGLE UP: ", neck_angles['tilt']
            robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
            print "Look up"
        elif centre[1] > (height / 5 * 4):
            if (neck_angles['tilt'] + 1) < 175:
                neck_angles['tilt'] += 1
            #print "CURRENT ANGLE DOWN:", neck_angles['tilt']
            robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
            print "Look down"
        elif object_found != True:
            robot.set_motor_speeds(15.0, 15.0)
            print "Move Forward"  
    else:
        print "Distance too great"

    match_feedback['left_counter'] = lc
    match_feedback['right_counter'] = rc
    match_feedback['last_centre'] = centre

    return match_feedback, neck_angles
