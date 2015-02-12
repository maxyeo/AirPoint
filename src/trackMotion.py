################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import os, sys, inspect, thread, time, socket
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/win/x64' if sys.maxsize > 2**32 else '../lib/win/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import json,httplib

# Custom imports
import als

MIN_DISTANCE_CHANGE = 15
MAX_FRAMES = 400
MINIMUM_VELOCITY = .3
X_LEAP_MOTION_MAX = 75#125.00 # in millimeters
X_LEAP_MOTION_MIN = -75#-125.00 # in millimeters
Y_LEAP_MOTION_MIN = 70#150.00 # in millimeters
Y_LEAP_MOTION_MAX = 100#250.00 # in millimeters
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
        
        self.weightprevious = .90

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

        arm = hand.arm
        leapx = 0
        leapy = 0
        if(arm.is_valid): # The arm is almost always going to be valid
            leapx = arm.wrist_position[0]
            leapy = arm.wrist_position[1]
        else:#this would only happen if we grabbed an invalid (non-existent) hand
            leapx = hand.palm_position[0] # leaving this here for posterity sake anyway
            leapy = hand.palm_position[1]
        
        if(leapx < X_LEAP_MOTION_MIN):
            leapx = X_LEAP_MOTION_MIN
        elif (leapx > X_LEAP_MOTION_MAX):
            leapx = X_LEAP_MOTION_MAX;
        
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

    try:
        # Create a sample listener and controller
        listener = SampleListener()
        controller = Leap.Controller()

        # Have the sample listener receive events from the controller
        controller.add_listener(listener)

        try:
            #attempt to log statistics
            connection = httplib.HTTPSConnection('api.parse.com', 443)
            connection.connect()
            connection.request('POST', '/1/events/AppOpened', json.dumps({
            }), {
              "X-Parse-Application-Id": "PxAVa0vycI8JxrlaHJrQtzExiQYSekWPpcSZfzAo",
              "X-Parse-REST-API-Key": "JfoBw0Q4pz8LSVjytME1OckCU0afUfT1TEptr2iE",
              "Content-Type": "application/json"
            })
        except socket.gaierror:
            print ("Not connected to the internet. No statistics will be generated.")
        except Exception as e:
            print ("Unknown exception: ")
            print (type(e))
            print (e)
            print ("Continuing without statistics.")
        # Keep this process running until Enter is pressed
        print "Press Enter to quit..."
    
        raw_input()

    except Exception as e:
        print ("Unknown Exception:")
        print (e)
        try: #attempt to log the exception
            connection.connect()
            connection.request('POST', '/1/functions/email', json.dumps({
                }), {
                  "X-Parse-Application-Id": "PxAVa0vycI8JxrlaHJrQtzExiQYSekWPpcSZfzAo",
                  "X-Parse-REST-API-Key": "JfoBw0Q4pz8LSVjytME1OckCU0afUfT1TEptr2iE",
                  "Content-Type": "application/json"
                })
            result = json.loads(connection.getresponse().read())
            print ("Results: " + str(result))
        except socket.gaierror:
            print ("Not connected to the internet. Cannot log error.")
        except httplib.HTTPException, e:
            print ("HTTP lib error:")
            print (e)
        
        
    finally:
        #Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
