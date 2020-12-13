#!/usr/bin/env python3

#provides functionality to drive the robot around by using the keyboard
import rospy
from gazebo_msgs.srv import ApplyJointEffort
from gazebo_msgs.srv import GetJointProperties
import curses
import time as t


speedLimit = 3 #maximum speed of the robot
effortStrength = 50 #range of [0,1]. Sets the strength of torque to wheels 

#set up joint ros
msg_topic = '/gazebo/apply_joint_effort'
joint_left_front = 'fourWheeledRobot::left_front_wheel_hinge'
joint_right_front = 'fourWheeledRobot::right_front_wheel_hinge'
joint_left_back = 'fourWheeledRobot::left_back_wheel_hinge'
joint_right_back = 'fourWheeledRobot::right_back_wheel_hinge'
msg_topic_feedback = '/gazebo/get_joint_properties'
pub_feedback = rospy.ServiceProxy(msg_topic_feedback, GetJointProperties)
rospy.init_node('fourWheeledRobot_ctrl', anonymous=True)
pub = rospy.ServiceProxy(msg_topic, ApplyJointEffort)


#set up time values for call to joint effort
start_time = rospy.Time(0,0)
f = float(20)
T = 1/f
Tnano = int(T*1000000000)
end_time = rospy.Time(0,Tnano)
duration = end_time-start_time
rate = rospy.Rate(f)


def decideEffort(wheelFRate, wheelStatus):
    k = 5 #control constant

    #decides how much effort to apply to the wheels
    desired_rate = (speedLimit*wheelStatus)
    error = desired_rate - wheelFRate

    wheelEffort = k * error
    #fixed acceleration up to requested speed
    #if wheelFRate<(speedLimit*wheelStatus):
    #    wheelEffort = effortStrength
    #fixed decelleration down to requested speed
    #if wheelFRate > (speedLimit*wheelStatus):
    #    wheelEffort = -effortStrength
    return wheelEffort


#curses needs to be in a try, finally so that it can close properly and not break the terminal
try:
    #set up curses
    stdscr = curses.initscr() #sets up the standard screen for curses
    curses.cbreak() #inputs will not wait for newline
    curses.noecho() #inputs will not print to screen
    curses.halfdelay(6) #sets to trigger exception after no input for (TenthsSeconds)

    #screen to show current command
    statusScr = curses.newwin(10,35,2,45)

    #create screen for header
    statusHeader = curses.newwin(1,35,0,45)
    statusHeader.clear()
    statusHeader.addstr(0,5,'CURRENT COMMAND')
    statusHeader.refresh()

    #create screen to show input instructions
    instructionsScr = curses.newwin(10,35,0,0)
    instructionsScr.clear()
    instructionsScr.addstr(0,10,'COMMANDS')
    instructionsScr.addstr(3,10,'SPACE = stop')
    instructionsScr.addstr(2,10,'w = forward')
    instructionsScr.addstr(3,0,'a = left')
    instructionsScr.addstr(3,25,'d = right')
    instructionsScr.addstr(4,10,'s = back')
    instructionsScr.addstr(6,10,'q = quit')
    instructionsScr.refresh()


    #main loop
    prevKey  = -1 #default to no new input
    wheelFL = 0
    wheelFR = 0
    wheelBL = 0
    wheelBR = 0
    while True: #loop to look for input from keyboard
        try:
            currKey = statusScr.getch() #returns -1 and creates exception if no input
        except KeyboardInterrupt: #lets ctrl-c work
            break
        except: #clean up exception for no input
            currKey = -1  
        if (currKey == ord('q')):
                break  # Exit the while loop
        if (prevKey != currKey): #check if key has been changed
            statusScr.clear() #clear the screen 
            if (currKey == -1)|(currKey == 32): #spacebar or catch no input if exception
                statusScr.addstr(1,10,'stop')
                wheelFL = 0
                wheelFR = 0
                wheelBL = 0
                wheelBR = 0
            elif (currKey == ord('w')):
                #print('fwd')
                statusScr.addstr(0,10,'forward')
                wheelFL = 1
                wheelFR = 1
                wheelBL = 1
                wheelBR = 1
            elif (currKey == ord('a')):
                #print('lft')
                statusScr.addstr(1,0,'left')
                wheelFL = -1
                wheelFR = 1
                wheelBL = -1
                wheelBR = 1
            elif (currKey == ord('s')):
                #print('bwd')
                statusScr.addstr(2,10,'back')
                wheelFL = -1
                wheelFR = -1
                wheelBL = -1
                wheelBR = -1
            elif (currKey == ord('d')):
                #print('rtt')
                statusScr.addstr(1,25,'right')
                wheelFL = 1
                wheelFR = -1
                wheelBL = 1
                wheelBR = -1
            statusScr.refresh()
            prevKey = currKey    

        #control the robot
        #get rates
        valFrontLeft = pub_feedback(joint_left_front)
        valFrontRight = pub_feedback(joint_right_front)  
        valBackLeft = pub_feedback(joint_left_back)
        valBackRight = pub_feedback(joint_right_back)  

        effortFL = decideEffort(valFrontLeft.rate[0], wheelFL)
        effortFR = decideEffort(valFrontRight.rate[0], wheelFR)
        effortBL = decideEffort(valBackLeft.rate[0], wheelBL)
        effortBR = decideEffort(valBackRight.rate[0], wheelBR)

        pub(joint_left_front, effortFL, start_time, duration)
        pub(joint_right_front, effortFR, start_time, duration)
        pub(joint_left_back, effortBL, start_time, duration)
        pub(joint_right_back, effortBR, start_time, duration)

        #debug printing
        #if valLeft.rate[0]>0:
        #    leftWheelDir = 'forward'
        #else:
        #    leftWheelDir = 'reverse'
        #if valRight.rate[0]>0:
        #    RightWheelDir = 'forward'
        #else:
        #    RightWheelDir = 'reverse'
        #print('Left wheel speed is:', valLeft.rate[0], 'in the ', leftWheelDir, ' direction', 'effort is ', str(effortL))
        #print('Right wheel speed is:', valRight.rate[0], 'in the ', RightWheelDir, ' direction', 'effort is ', str(effortR))


        #rate.sleep()

                 
finally:
    #shut down curses. Extremely important 
    curses.nocbreak()
    curses.echo()
    curses.endwin()
