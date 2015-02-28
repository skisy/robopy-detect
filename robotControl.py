import math
import py_websockets_bot

def robotMove(robot, centre, height, width, move_tolerance, match_feedback):

    # Calculate distance between current centre and last centre point using Pythagorean theory
    coord_distance = math.hypot(centre[0] - match_feedback['last_centre'][0], centre[1] - match_feedback['last_centre'][1])
    #print coord_distance

    lc = match_feedback['left_counter']
    rc = match_feedback['right_counter']

    if coord_distance < move_tolerance:

        if centre[0] < (width / 5):
            rc = 0
            lc += 1
            lc = 0
            print "Turn Left"
        elif centre[0] > (width / 5 * 4):
            lc = 0
            rc += 1
            rc = 0
            print "Turn Right"
        elif centre[1] < (height / 5):
            print "Look up"
        elif centre[1] > (height / 5 * 4):
            print "Look down"
        else:
            robot.set_motor_speeds(30.0, 30.0)
            print "Move Forward"
    else:
        print "Distance too great"

    match_feedback['left_counter'] = lc
    match_feedback['right_counter'] = rc
    match_feedback['last_centre'] = centre

    return match_feedback
