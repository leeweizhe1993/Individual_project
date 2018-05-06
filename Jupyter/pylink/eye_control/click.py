# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:51:56 2017

@author: Li
"""
from pymouse import PyMouse
import autopy
import pylink
import win32api,win32con
import time

def click_down(mcl, mcr, gazePos):
    global temp_gazePosL
    global temp_gazePosR
    global press
    mouse = PyMouse()
    if mcl == 4:    #超过4次计数则识别为click_down
        temp_gazePosL = (int(gazePos[0]),int(gazePos[1]))
        if detect(temp_gazePosL):
            #mouse.position()
            autopy.mouse.smooth_move(int(gazePos[0]),int(gazePos[1]))
            mouse.click(int(gazePos[0]),int(gazePos[1]), 1, True)    #按下左键
            press = 1    #按键状态为 click_cown
        else:
            pass
    if mcr == 4:
        temp_gazePosR = (int(gazePos[0]),int(gazePos[1]))
        if detect(temp_gazePosR):
            #mouse.position()
            autopy.mouse.smooth_move(int(gazePos[0]),int(gazePos[1]))
            mouse.click(int(gazePos[0]),int(gazePos[1]), 2, True)    #按下右键
            press = 1
        else:
            pass
    else:
        pass


def click_up(mcl, mcr, temp_gazePosL, temp_gazePosR):
    global press
    newSample = tk.getNewestSample()
    mouse = PyMouse()
    if newSample.isBinocular():    #重新识别出双眼时，按键开始抬起
        if mcl > mcr:
            gazePos = newSample.getRightEye().getGaze()
            gazePos = (int(gazePos[0]),int(gazePos[1]))
            width = temp_gazePosL[0] - gazePos[0]
            height = temp_gazePosL[1] - gazePos[1]
            if (abs(width) > 50 and abs(height) > 50):    #当新注视点在缓存注视点50px以外时，使用新注视点位置，防止因视线抖动造成点击不稳
                mouse.position()
                autopy.mouse.smooth_move
                mouse.click(int(gazePos[0]),int(gazePos[1]), 1, False)    #抬起左键
                press = 0
            else:
                if detect(temp_gazePosL):
                    mouse.position()
                    autopy.mouse.smooth_move
                    mouse.click(temp_gazePosL[0],temp_gazePosL[1], 1, False)
                    press = 0
                else:
                    pass
        elif mcl < mcr:
            gazePos = newSample.getLeftEye().getGaze()
            gazePos = (int(gazePos[0]),int(gazePos[1]))
            width = temp_gazePosR[0] - gazePos[0]
            height = temp_gazePosR[1] - gazePos[1]
            if (abs(width) > 50 and abs(height) > 50):
                mouse.position()
                autopy.mouse.smooth_move
                mouse.click(int(gazePos[0]),int(gazePos[1]), 2, False)    #抬起右键
                press = 0
            else:
                if detect(temp_gazePosR):
                    mouse.position()
                    utopy.mouse.smooth_move
                    mouse.click(temp_gazePosL[0],temp_gazePosL[1], 2, False)
                    press = 0
                else:
                    pass
        else:
            pass
    else:
        pass