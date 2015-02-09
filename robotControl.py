import math

def robotMove(centre, height, width, move_tolerance, match_feedback):

    # Calculate distance between current centre and last centre point using Pythagorean theory
    coord_distance = math.hypot(centre[0] - match_feedback['last_centre'][0], centre[1] - match_feedback['last_centre'][1])
    #print coord_distance

    lc = match_feedback['left_counter']
    rc = match_feedback['right_counter']

    if coord_distance < move_tolerance:

        if centre[0] < (width / 5):
            rc = 0
            lc += 1
            if lc > 2:
                lc = 0
                print "Turn Left"
        elif centre[0] > (width / 5 * 4):
            lc = 0
            rc += 1
            if rc > 2:
                rc = 0
                print "Turn Right"
        else:
            if centre[1] < (height / 5):
                print "Look up"
            elif centre[1] > (height / 5 * 4):
                print "Look down"

            print "Move Forward"
    else:
        print "Distance too great"

    match_feedback['left_counter'] = lc
    match_feedback['right_counter'] = rc
    match_feedback['last_centre'] = centre

    return match_feedback
