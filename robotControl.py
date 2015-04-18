import math
import py_websockets_bot
import time

def minDistanceReached(robot, min_dist):
    status_dict, read_time = robot.get_robot_status_dict()

    sensor_dict = status_dict["sensors"]

    distance = sensor_dict["ultrasonic"]["data"]

    distance_info = "Distance: " + str(distance) + " Minimum Distance: " + str(min_dist) + " Result: " + str(distance <= min_dist)

    print distance_info

    print (distance <= min_dist)

    return (distance <= min_dist)

def robotMoveToObject(robot, centre, height, width, move_tolerance, match_feedback, neck_angles):

    #match_feedback['object_located'] = False
    if (neck_angles['pan'] > 90) and (neck_angles['pan'] < 110):
        neck_angles['pan'] = 100 
        # Calculate distance between current centre and last centre point using Pythagorean theory
        coord_distance = math.hypot(centre[0] - match_feedback['last_centre'][0], centre[1] - match_feedback['last_centre'][1])
        #print coord_distance
        if match_feedback['object_located'] and minDistanceReached(robot, 20):
            print "OBJECT LOCATED"
        else:
            print "Possible Detection"
            if coord_distance < move_tolerance:
                if minDistanceReached(robot, 20):
                    print "OBJECT LOCATED"
                    match_feedback['object_located'] = True
                    # Additional functionality to retrieve object/sound buzzer would be implemented at this point
                else:
                    match_feedback['object_located'] = False
                if centre[0] < (width / 5):
                    robot.set_motor_speeds(-25.0,25.0)
                    print "Turn Left"
                elif centre[0] > (width / 5 * 4):
                    robot.set_motor_speeds(25.0, -25.0)
                    print "Turn Right"
                    time.sleep(0.5)
                elif centre[1] < (height / 4):
                    if (neck_angles['tilt'] - 1) > 20:
                        neck_angles['tilt'] -= 1
                    #print "CURRENT ANGLE UP: ", neck_angles['tilt']
                    robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
                    print "Look up"
                elif centre[1] > (height / 4 * 3):
                    if (neck_angles['tilt'] + 1) < 175:
                        neck_angles['tilt'] += 1
                    #print "CURRENT ANGLE DOWN:", neck_angles['tilt']
                    robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
                    print "Look down"
                elif match_feedback['object_located'] != True:
                    robot.set_motor_speeds(30.0, 30.0)
                    print "Move Forward"  
            else:
                print "Distance too great"

        match_feedback['last_centre'] = centre
    elif neck_angles['pan'] < 90:
        neck_angles['pan'] += 20
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        robot.set_motor_speeds(30.0, -30.0)
    elif neck_angles['pan'] > 110:
        neck_angles['pan'] -= 20
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        robot.set_motor_speeds(-30.0, 30.0)

    return match_feedback, neck_angles

def lookAround(robot, neck_angles, match_feedback):
    # Look left - if no object then look right
    # If still no object detected, look forward, drive back to avoid obstacles and turn right/left (alternating for grid)
    '''if neck_angles['pan'] > 90 and neck_angles['pan'] < 110:
        neck_angles['pan'] = 50
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        match_feedback['no_match'] = 0
    elif neck_angles['pan'] <= 90:
        neck_angles['pan'] = 150
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        match_feedback['no_match'] = 0
    else:
        neck_angles['pan'] = 100
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        match_feedback['no_match'] = 0
        robot.set_motor_speeds(-90.0,-90.0)
        time.sleep(0.8)
        robot.set_motor_speeds(0.0,0.0)
        if match_feedback['last_turn'] == "Left":
            # Turn right
            #print "RIGHT"
            robot.set_motor_speeds(100.0,20.0)
            time.sleep(2.8)
            robot.set_motor_speeds(0.0,0.0)
            match_feedback['last_turn'] = "Right"
        else:
            # Turn left
            #print "LEFT"
            robot.set_motor_speeds(20.0, 100.0)
            time.sleep(1.8)
            robot.set_motor_speeds(0.0,0.0)
            match_feedback['last_turn'] = "Left"
    return neck_angles, match_feedback'''
    if neck_angles['pan'] > 90 and neck_angles['pan'] < 110:
        neck_angles['pan'] = 50
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        time.sleep(0.1)
        match_feedback['no_match'] = 0
    elif neck_angles['pan'] <= 90:
        neck_angles['pan'] = 150
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        time.sleep(0.1)
        match_feedback['no_match'] = 0
    else:
        neck_angles['pan'] = 100
        robot.set_neck_angles(pan_angle_degrees=neck_angles['pan'], tilt_angle_degrees=neck_angles['tilt'])
        time.sleep(0.1)
        if minDistanceReached(robot, 25):
            robot.set_motor_speeds(-50.0, -50.0)
            time.sleep(2)
        robot.set_motor_speeds(50.0,-50.0)
        match_feedback['no_match'] = 0
    return neck_angles, match_feedback