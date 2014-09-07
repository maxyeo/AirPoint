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
MAX_FRAMES = 400
MINIMUM_VELOCITY = .3
X_LEAP_MOTION_MAX = 150.0 # in millimeters
X_LEAP_MOTION_MIN = -150.0 # in millimeters
Y_LEAP_MOTION_MIN = 100.0 # in millimeters
Y_LEAP_MOTION_MAX = 200.0 # in millimeters
MAX_VELOCITY_FRAMES = 200



class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    
    

    def getDifference(self, qArray, oldest):
        #print (str(qArray))
        i = oldest
        diff = 0.0
        geo = 2
        for x in range(0, len(qArray)-1):
            diff = ((qArray[i-1] - qArray[i]) * -1/geo ) + diff
            i = i - 1
            geo = geo*2

        return diff#/len(qArray)

    def weightedAverage(self, qArray, oldest):
        i = oldest
        diff = 0.0
        geo = 2
        for x in range(0, len(qArray)-1):
            diff = (qArray[i] * 1/geo ) + diff
            i = i -1
            geo = geo*2
        
        return diff
        
    def on_init(self, controller):
        print "Initialized"
        self.oldX = [0] * MAX_FRAMES
        self.oldY = [0] * MAX_FRAMES
        self.velocityX = [0] * MAX_VELOCITY_FRAMES
        self.velocityY = [0] * MAX_VELOCITY_FRAMES
        self.currentVelocityFrame = 0
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
            self.on_init
            return #exit early if there are no hands
        
            
        hand = frame.hands.rightmost
        #get latest data
        #x = hand.palm_position[0] + 150
        xRatio = als.SCREEN_WIDTH/(X_LEAP_MOTION_MAX - X_LEAP_MOTION_MIN)
        yRatio = als.SCREEN_HEIGHT/(Y_LEAP_MOTION_MAX - Y_LEAP_MOTION_MIN)

        leapx = hand.palm_position[0] 
        
        if(leapx < X_LEAP_MOTION_MIN):
            leapx = X_LEAP_MOTION_MIN
        elif (leapx > X_LEAP_MOTION_MAX):
            leapx = X_LEAP_MOTION_MAX;
        leapx = leapx
        
        leapy = hand.palm_position[1]
        if(leapy < Y_LEAP_MOTION_MIN):
            leapy = Y_LEAP_MOTION_MIN
        elif(leapy> Y_LEAP_MOTION_MAX):
            leapy = Y_LEAP_MOTION_MAX
            
        if (self.oldX[0] == 0):
            self.oldX = [leapx]* MAX_FRAMES #(hand.palm_position[0] + 150) *( als.SCREEN_WIDTH/300)
            self.oldY = [leapy]* MAX_FRAMES
        else:
            self.oldX[self.currentFrame] = leapx #(hand.palm_position[0] + 150) *( als.SCREEN_WIDTH/300)
            self.oldY[self.currentFrame] = leapy 
        
            
            
        #self.oldY[self.currentFrame] = hand.palm_position[1] #als.SCREEN_HEIGHT - (hand.palm_position[1] * (als.SCREEN_HEIGHT / 175))
        self.velocityX[self.currentVelocityFrame] = hand.palm_velocity[0]
        self.velocityY[self.currentVelocityFrame] = hand.palm_velocity[1]

        #print("x location: "+ str(hand.palm_position[0]))
        
        #determine the current velocity
        #print ("x: " + str(max(self.velocityX))) 
        #print ("y: " + str(hand.palm_velocity[1])) 
#        velocity  = sum(self.velocityX) / MAX_FRAMES
        
        
        x =  als.SCREEN_WIDTH + ((self.weightedAverage(self.oldX,self.oldestFrame) + X_LEAP_MOTION_MIN)*xRatio)
        y =  als.SCREEN_HEIGHT-  ((self.weightedAverage(self.oldY,self.oldestFrame)-(Y_LEAP_MOTION_MAX - Y_LEAP_MOTION_MIN))*yRatio) 

        # reset current frame
        self.oldestFrame = self.oldestFrame + 1
        if(self.oldestFrame == MAX_FRAMES):
            self.oldestFrame = 0
            
            
        self.currentFrame = self.currentFrame + 1
        if(self.currentFrame == MAX_FRAMES):
            self.currentFrame = 0
            
        if(self.currentVelocityFrame == MAX_VELOCITY_FRAMES):
            self.currentVelocityFrame = 0
        #update array with locations

        # Calculate the hands grab strength
        strength = hand.grab_strength

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

        
        
        #if((self.weightedAverage(self.velocityX,self.currentVelocityFrame) > MINIMUM_VELOCITY) or (self.weightedAverage(self.velocityY,self.currentVelocityFrame) > MINIMUM_VELOCITY)):
        
        #slow down the movement by restricting how far the pointer can move in a single refresh
        mouse = als.getMousePos()
        x = (mouse[0]*39.0 + x) / 40.0
        y = (mouse[1]*39.0 + y) / 40.0
        #x=  x - ( mouse[0] -x) 
        #y = mouse[1] + ((mouse[1] - y) * .25)
        
        
        als.mouse(x, y)
        
 

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
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


if __name__ == "__main__":
    main()
