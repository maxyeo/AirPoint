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
X_LEAP_MOTION_MAX = 125.00 # in millimeters
X_LEAP_MOTION_MIN = -125.00 # in millimeters
Y_LEAP_MOTION_MIN = 150.00 # in millimeters
Y_LEAP_MOTION_MAX = 250.00 # in millimeters
MAX_VELOCITY_FRAMES = 200

MIN_CLENTCH_TO_CICK = .98
MIN_CLENTCH_TO_DISABLE = .8

class SampleListener(Leap.Listener):
    
    

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
        self.currentVelocityFrame = 0
        self.oldestFrame = MAX_FRAMES -1
        self.currentFrame = 0
        
        self.xprev = 0
        self.yprev = 0
        
        self.weightprevious = .97

    def setPreviousWeight(value):
        self.weightprevious = value

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
            
        if (self.xprev == 0):
            self.xprev = leapx
            self.yprev = leapy


        x =  als.SCREEN_WIDTH + ((leapx) + X_LEAP_MOTION_MIN)*xRatio
        y =  als.SCREEN_HEIGHT-  ((leapy)-( Y_LEAP_MOTION_MIN))*yRatio

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

        
        #slow down the movement by restricting how far the pointer can move in a single refresh
        mouse = als.getMousePos()
        
        x = (mouse[0]*self.weightprevious) + x*(1.0 - self.weightprevious) 
        if(x > (als.SCREEN_WIDTH/2)):
            x = x +1
        y = (mouse[1] *self.weightprevious) + y *(1.0 - self.weightprevious)
        if(y > (als.SCREEN_HEIGHT/2)):
            y = y +1
        

        if( strength < MIN_CLENTCH_TO_DISABLE):
            als.mouse(x, y)

        
        
        if (strength > MIN_CLENTCH_TO_CICK):
            if (als.CLICKED == False):
                als.click(int(x), int(y))
                als.CLICKED = True
        else:
            if (als.CLICKED):
                als.CLICKED = False
        
        
        if (x > als.SCREEN_WIDTH): 
            x = als.SCREEN_WIDTH
        elif (x < 0 ):
            x = 0

        if(y > als.SCREEN_HEIGHT):
            y = als.SCREEN_HEIGHT
        elif (y < 0):
            y = 0

        # Scrolling
        topTen = als.SCREEN_HEIGHT * 0.25
        bottomTen = als.SCREEN_HEIGHT - topTen

        pinchStrength= hand.pinch_strength

        if (pinchStrength > .7 and hand.palm_position[1] >= bottomTen):
            als.dokey(als.UP)
        if (pinchStrength > .7 and hand.palm_position[1] < topTen):
            als.dokey(als.DOWN)
        
 

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
