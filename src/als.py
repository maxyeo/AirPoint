#-------------------------------------------------------------------------------
# Name:         winterface
# Purpose:      Simulate mouse/keyboard through Python
#
# Author:       Jordan Matelsky (2012 - 2013)
#-------------------------------------------------------------------------------
import win32api, win32con, win32gui, win32clipboard
from win32api import GetSystemMetrics
import time
import subprocess
import os
import win32com.client as comclt



class Point():
    x = 0
    y = 0
    def __init__(this, x, y):
        this.x = x
        this.y = y
    def click(this):
        click(this.x, this.y)
    def pixelAt(this):
        return pixelAt(this.x, this.y)


#def scrapeText

def pixelAt(x, y):
    """Return a pixel color at (x, y) --> Hex"""
    return hex(win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), x , y))

def abortCheck(delay = 3):
    """Wait <delay> seconds, and quit on mouse move."""
    p = getMousePos()
    time.sleep(delay)
    if (p != getMousePos()):
        os.system("pause")
        sys.exit()

def moveOnPixelChange(x, y, delay = 0):
    """Return from function when the pixel changes color [after <delay> seconds]"""
    init = pixelAt(x, y)
    while pixelAt(x, y) == init:
        pass
    time.sleep(delay)

def drag(x0, y0, x1, y1, delay=0):
    """Click and drag x0 y0 to x1 y1"""
    click(x0, y0, click=False)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x0,y0,0,0)
    time.sleep(delay)
    click(x1, y1, click=False)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x1,y1,0,0)
        

def click(x, y, click=True, left=True):
    """Click at (x, y) (default left click)"""
    if (click == True):
        win32api.SetCursorPos((x,y))
        if (left == True):
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    else:
        win32api.SetCursorPos((x,y))

def mouse(x1, y1, click1=False, left=True, speed='fast'):
    while True:
        if speed == 'slow':
            time.sleep(0.005)
            Tspeed = 2
        if speed == 'fast':
            time.sleep(0.001)
            Tspeed = 5
        if speed == 0:
            time.sleep(0.001)
            Tspeed = 3

        x = getMousePos()[0]
        y = getMousePos()[1]
        if abs(x-x1) < 5:
            if abs(y-y1) < 5:
                break

        if x1 < x:
            x -= Tspeed
        if x1 > x:
            x += Tspeed
        if y1 < y:
            y -= Tspeed
        if y1 > y:
            y += Tspeed
        click(x, y, False, False)
    if (click1 == True):
        if (left == True):
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        else:
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    else:
        win32api.SetCursorPos((x,y))


def dokey(key1,key2=None):
    """Simulate the typing of ascii key1"""
    win32api.keybd_event(key1,0,0,0)
    if key2!=None:
        win32api.keybd_event(key2,0,0,0)
        win32api.keybd_event(key2,0,2,0)
        win32api.keybd_event(key1,0,2,0)

def doSkey(key1,key2=None):
    """Simulate the typing of char key1"""
    key1 = int(ca(key1))
    if key2: key2 = ca(key2)
    win32api.keybd_event(key1,0,0,0)
    if key2!=None:
        win32api.keybd_event(key2,0,0,0)
        win32api.keybd_event(key2,0,2,0)
        win32api.keybd_event(key1,0,2,0)

def ctrlAlt(key3):
    win32api.keybd_event(CTRL,0,0,0)
    win32api.keybd_event(ALT,0,0,0)
    win32api.keybd_event(key3,0,0,0)
    win32api.keybd_event(key3,0,2,0)
    win32api.keybd_event(ALT,0,2,0)
    win32api.keybd_event(CTRL,0,2,0)

def do3Key(key1, key2, key3):
    win32api.keybd_event(key1,0,0,0)
    win32api.keybd_event(key2,0,0,0)
    win32api.keybd_event(key3,0,0,0)
    win32api.keybd_event(key3,0,2,0)
    win32api.keybd_event(key2,0,2,0)
    win32api.keybd_event(key1,0,2,0)

def ca(s):
    """Return the integer version of some char s"""
    return int(hex(ord(s)), 16)

def type_string(s):
    """Type a string s"""
    wsh= comclt.Dispatch("WScript.Shell")
    wsh.SendKeys(s)

def getMousePos(delay = 0):
    """Get the mouse (x, y) after <delay> seconds"""
    time.sleep(delay)
    return win32api.GetCursorPos()

def clipTextAt(x0, y0, x1, y1):
    """Copies the text to the clipboard (and returns it)"""
    drag(x0, y0, x1, y1)
    dokey(CTRL, ca("C"))
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    print (data)


SCREEN_WIDTH = GetSystemMetrics(0)
SCREEN_HEIGHT = GetSystemMetrics(1)

ENTER = 13
TAB = 9
SHIFT = 16
CTRL = 17
ALT = 18
BACKSPACE = 9
LEFT = 37
UP = 38
RIGHT = 39
DOWN = 40
WIN = 91

F6 = 117
F11 = 122

NUM1 = 97
NUM2 = 98
NUM3 = 99
NUM4 = 100

START_BUTTON = Point(27, 880)

mouse(50,30)
click(50,30)