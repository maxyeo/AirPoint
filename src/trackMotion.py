################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/win/x64' if sys.maxsize > 2**32 else '../lib/win/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# Custom imports
import als

MIN_DISTANCE_CHANGE = 15
MAX_FRAMES = 200
MINIMUM_VELOCITY = .2
X_LEAP_MOTION = 75 # in millimeters
Y_LEAP_MOTION = 75 # in millimeters



class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    
    

    def getDifference(self, qArray, oldest):
        #print (str(qArray))
        i = oldest
        diff = 0.0#qArray[i-1] - qArray[i]
        geo = 2
        for x in range(0, MAX_FRAMES-1):
            diff = ((qArray[i-1] - qArray[i]) * -1/geo ) + diff
            i = i - 1
            geo = geo*2

        return diff#/len(qArray)

    def on_init(self, controller):
        print "Initialized"
        self.oldX = [0] * MAX_FRAMES
        self.oldY = [0] * MAX_FRAMES
        self.velocityX = [0] * MAX_FRAMES
        self.velocityY = [0] * MAX_FRAMES
        self.oldestFrame = MAX_FRAMES -1
        self.currentFrame = 0


    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    
    def on_frame(self, controller):
        #time.sleep(1)
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        if(len(frame.hands) == 0):
            self.oldX = [0] * MAX_FRAMES
            self.oldY = [0] * MAX_FRAMES
            return #exit early if there are no hands
        
            
        hand = frame.hands.rightmost
        #get latest data
        #x = hand.palm_position[0] + 150
        xRatio = als.SCREEN_WIDTH/X_LEAP_MOTION
        yRatio = als.SCREEN_HEIGHT/Y_LEAP_MOTION
        #newX = x*xRatio
        leapx = hand.palm_position[0]
        leapy = hand.palm_position[1]
        # if(leapx > MIN_LEAP_MOTION):
            # leapx = MIN_LEAP_MOTION
        # elif (leapx < -MIN_LEAP_MOTION):
            # leapx = -MIN_LEAP_MOTION
        if (self.oldX[0] == 0):
            self.oldX = [leapx]* MAX_FRAMES #(hand.palm_position[0] + 150) *( als.SCREEN_WIDTH/300)
            self.oldY = [leapx]* MAX_FRAMES
        else:
            self.oldX[self.currentFrame] = leapx #(hand.palm_position[0] + 150) *( als.SCREEN_WIDTH/300)
            self.oldY[self.currentFrame] = -leapy 
        
            
            
        #self.oldY[self.currentFrame] = hand.palm_position[1] #als.SCREEN_HEIGHT - (hand.palm_position[1] * (als.SCREEN_HEIGHT / 175))
        self.velocityX[self.currentFrame] = hand.palm_velocity[0]/100
        self.velocityY[self.currentFrame] = hand.palm_velocity[1]

        #print("x location: "+ str(hand.palm_position[0]))
        
        #determine the current velocity
        velocity  = sum(self.velocityX) / MAX_FRAMES
        mouse = als.getMousePos()
        x = (mouse[0] ) + (self.getDifference(self.oldX,self.oldestFrame)*xRatio)# *  velocity)#sum(self.oldX) / MAX_FRAMES
        y = (mouse[1] ) + (self.getDifference(self.oldY,self.oldestFrame)*yRatio)
        
        #y = sum(self.oldY) / MAX_FRAMES
        #print (str(velocity))
        #print ("Velocity: " + str(velocity))
        # reset current frame
        self.oldestFrame = self.oldestFrame + 1
        if(self.oldestFrame == MAX_FRAMES):
            self.oldestFrame = 0
            
            
        self.currentFrame = self.currentFrame + 1
        if(self.currentFrame == MAX_FRAMES):
            self.currentFrame = 0
        #update array with locations

        # Calculate the hands grab strength
        strength = hand.grab_strength
        #print "Strength is: %s" %(
        #    strength)
        if (strength > .92):
            if (als.CLICKED == False):
                als.click(int(x), int(y))
                als.CLICKED = True
        else:
            if (als.CLICKED):
                als.CLICKED = False
        
        
        if (x > als.SCREEN_WIDTH): #
            x = als.SCREEN_WIDTH
        elif (x < 0 ):
            x = 0

        if(y > als.SCREEN_HEIGHT):
            y = als.SCREEN_HEIGHT
        elif (y < 0):
            y = 0
            
        #if (velocity > MINIMUM_VELOCITY):
        als.mouse(x, y)
        
        # # Get hands
        # for hand in frame.hands:

            # handType = "Left hand" if hand.is_left else "Right hand"

            # x = hand.palm_position[0]
            # y = hand.palm_position[1]
            
            # # convert screen to width and height
            # x = hand.palm_position[0] + 150
            # xRatio = als.SCREEN_WIDTH/300
            # newX = x*xRatio
            # if (newX > als.SCREEN_WIDTH): #
                # newX = als.SCREEN_WIDTH
            # elif (newX < 0 ):
                # newX = 0
                
            # y = hand.palm_position[1] - 100
            # yRatio = als.SCREEN_HEIGHT / 175
            # newY = als.SCREEN_HEIGHT - y * yRatio
            # if(newY > als.SCREEN_HEIGHT):
                # newY = als.SCREEN_HEIGHT
            # elif (newY < 0):
                # newY = 0
# #            print("x: " + str(x) + " y: "+ str(y))
# #            print ("newX: " + str(newX) + " newY: " + str(newY));
            # if (abs(self.oldX - newX)> MIN_DISTANCE_CHANGE and abs(self.oldY - newY)> MIN_DISTANCE_CHANGE):
                # als.mouse(newX, newY)
                # self.oldX = newX
                # self.oldY = newY
                # print "Frame id: %d, timestamp: %d, hands: %d, gestures: %d" % (
              # frame.id, frame.timestamp, len(frame.hands), len(frame.gestures()))
                # print "  %s, id %d, position: %s" % (
                # handType, hand.id, hand.palm_position)
                
            # # Get the hand's normal vector and direction
            # normal = hand.palm_normal
            # direction = hand.direction

            


            # # Calculate the hand's pitch, roll, and yaw angles
            
# #            print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
# #                direction.pitch * Leap.RAD_TO_DEG,
# #                normal.roll * Leap.RAD_TO_DEG,
# #                direction.yaw * Leap.RAD_TO_DEG)

            # # Get arm bone
            # arm = hand.arm
# #            print "  Arm direction: %s, wrist position: %s, elbow position: %s" % (
# #                arm.direction,
# #                arm.wrist_position,
# #                arm.elbow_position)

            # # Get fingers
            # for finger in hand.fingers:

# #                print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
# #                    self.finger_names[finger.type()],
# #                    finger.id,
# #                    finger.length,
# #                    finger.width)

                # # Get bones
                # for b in range(0, 4):
                    # bone = finger.bone(b)
# #                    print "      Bone: %s, start: %s, end: %s, direction: %s" % (
#                        self.bone_names[bone.type],
#                        bone.prev_joint,
#                        bone.next_joint,
#                        bone.direction)

        # Get tools
        # for tool in frame.tools:

            # print "  Tool id: %d, position: %s, direction: %s" % (
                # tool.id, tool.tip_position, tool.direction)

        # # Get gestures
        # for gesture in frame.gestures():
            # if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                # circle = CircleGesture(gesture)

                # # Determine clock direction using the angle between the pointable and the circle normal
                # if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    # clockwiseness = "clockwise"
                # else:
                    # clockwiseness = "counterclockwise"

                # # Calculate the angle swept since the last frame
                # swept_angle = 0
                # if circle.state != Leap.Gesture.STATE_START:
                    # previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                    # swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                # print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                        # gesture.id, self.state_names[gesture.state],
                        # circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

            # if gesture.type == Leap.Gesture.TYPE_SWIPE:
                # swipe = SwipeGesture(gesture)
                # print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        # gesture.id, self.state_names[gesture.state],
                        # swipe.position, swipe.direction, swipe.speed)

            # if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                # keytap = KeyTapGesture(gesture)
                # print "  Key Tap id: %d, %s, position: %s, direction: %s" % (
                        # gesture.id, self.state_names[gesture.state],
                        # keytap.position, keytap.direction )

            # if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                # screentap = ScreenTapGesture(gesture)
                # print "  Screen Tap id: %d, %s, position: %s, direction: %s" % (
                        # gesture.id, self.state_names[gesture.state],
                        # screentap.position, screentap.direction )

        # if not (frame.hands.is_empty and frame.gestures().is_empty):
            # print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def run():
    # Create a sample listener and controller
    listener = SampleListener()
    listener.oldX = 0
    listener.oldY = 0
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    print (" Screen width: " + str(als.SCREEN_WIDTH))
    print (" Screen height: " + str(als.SCREEN_HEIGHT))

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


#if __name__ == "__main__":
#    main()
