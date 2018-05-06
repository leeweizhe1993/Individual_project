# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:51:56 2017

@author: Li
"""
from pymouse import PyMouse
import pylink
import win32api,win32con
import time

# 步骤一：连接眼动仪
tk = pylink.EyeLink('100.1.1.1')

#获取眼动仪相关信息
print tk.getTrackerVersionString()
print pylink.getEYELINK().getTrackerVersionString()
disp = pylink.getDisplayInformation()
print disp.width, disp.height, disp.bits, disp.refresh

pylink.openGraphics()

edfFileName = 'test.edf'
tk.openDataFile(edfFileName)

# 步骤四：使用'sendCommand'方法设置眼动仪参数
tk.sendCommand('sample_rate 500')
# 设定校准屏幕的主题颜色
pylink.setCalibrationColors((255,255,255), (0,0,0))
# 设定在线分析程序
# 0--> 标准 (认知实验); 1--> 敏感 (神经心理学)
tk.sendCommand('select_parser_configuration 0')
# 设置EDF文件存储内容（事件相关：左、右、注视、扫视、眨眼、消息、按键）
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")     
# 设置连接参数（用于视线追随）
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
#tk.setLinkSampleData("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET") # you can also use the setXXX comand
tk.sendCommand("calibration_type = HV9")
#设定九点校准
tk.getEventDataFlags()


def runTrial():
    '''漂移校正'''
    try:                        
        error = tk.doDriftCorrect(scnSize[0]/2, scnSize[1]/2, 1, 1)
    except:
        tk.doTrackerSetup()

    # 强制离线模式防止视线漂移 
    pylink.flushGetkeyQueue() # clear all cached button responses

    tk.setOfflineMode()
    pylink.pumpDelay(100);

    # 开始记录
    error = tk.startRecording(1,1,1,1)
    if error: print error
    pylink.pumpDelay(100);      # wait for 100 ms to make all data of interests is recorded
    pylink.closeGraphics()
    # Always send a TRIALID message before starting to record.
    msg = "TRIALID %s"%('1-trial exp')
    tk.sendMessage(msg);
            
    # 同步时间
    tk.sendMessage("SYNCTIME %d" % pylink.currentTime());
    #设置控制参数
    startTime = pylink.currentTime()
    # tk.sendMessage("Gaze-contingent search")
    # tk.sendCommand("draw_cross %d %d %d"%(500,600, 3))
    
    press = 0
    miss_count_l = 0
    miss_count_r = 0
    gazePos = (0, 0)
    temp_gazePosL = (0, 0)
    temp_gazePosR = (0, 0)
    
    while not pylink.currentTime() >= startTime + 60000:
        #eyeTracked = tk.eyeAvailable()
        time.sleep(0.04)
        locate(press)
        click_down(miss_count_l, miss_count_r, gazePos)
        click_up(miss_count_l, miss_count_r, temp_gazePosL, temp_gazePosR)
    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()
# m.click(x,y,button,n) –鼠标点击 
# x,y –是坐标位置 
# button –1表示左键，2表示点击右键 
# n –点击次数，默认是1次，2表示双击


def locate(press):
    global miss_count_l
    global miss_count_r
    global gazePos
    mouse = PyMouse()
    newSample = tk.getNewestSample()
    if press:
        click_up(mcl, mcr, temp_gazePosL, temp_gazePosR, 1)
    elif (newSample.isBinocular() and (newSample.getLeftEye().getGaze()[0] <= 960)):    #眼睛注视左侧
        gazePos = newSample.getLeftEye().getGaze()
        mouse.position()    #获取当前坐标的位置
        mouse.move(int(gazePos[0]),int(gazePos[1]))    #鼠标移动到(x,y)位置
        miss_count_l = 0
        miss_count_r = 0 
    elif (newSample.isBinocular() and (newSample.getLeftEye().getGaze()[0] > 960)):    #眼睛注视右侧
        gazePos = newSample.getRightEye().getGaze()
        mouse.position()    #获取当前坐标的位置
        mouse.move(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
        newSample = tk.getNewestSample()
        miss_count_l = 0
        miss_count_r = 0 
    elif (newSample.isRightSample() - newSample.isLeftSample()) == 1:    #左眼闭合检测
        gazePos = newSample.getRightEye().getGaze()
        mouse.position()    #获取当前坐标的位置
        mouse.move(int(gazePos[0]),int(gazePos[1]))    #鼠标移动到(x,y)位置
        miss_count_l += 1
    elif (newSample.isLeftSample() - newSample.isRightSample()) == 1:    #右眼闭合检测
        gazePos = newSample.getLeftEye().getGaze()
        mouse.position()    #获取当前坐标的位置
        mouse.move(int(gazePos[0]),int(gazePos[1]))    #鼠标移动到(x,y)位置
        miss_count_r += 1


def click_down(mcl, mcr, gazePos):
    global temp_gazePosL
    global temp_gazePosR
    global press
    mouse = PyMouse()
    if mcl == 10:
        temp_gazePosL = (int(gazePos[0]),int(gazePos[1]))
        mouse.move(int(gazePos[0]),int(gazePos[1]))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,int(gazePos[0]), int(gazePos[1]))
        press = 1
    if mcr == 10:
        temp_gazePosR = (int(gazePos[0]),int(gazePos[1]))
        mouse.move(int(gazePos[0]),int(gazePos[1]))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,int(gazePos[0]), int(gazePos[1]))
        press = 1

    if mcl > 10:
        mouse.position()
        mouse.move(int(gazePos[0]),int(gazePos[1]))
    elif mcr > 10:
        mouse.position()
        mouse.move(int(gazePos[0]),int(gazePos[1]))
    else:
        pass


def click_up(mcl, mcr, temp_gazePosL, temp_gazePosR):
    global press
    newSample = tk.getNewestSample()
    mouse = PyMouse()
    if newSample.isBinocular():
        if mcl > mcr:
            gazePos = newSample.getRightEye().getGaze()
            gazePos = (int(gazePos[0]),int(gazePos[1]))
            width = temp_gazePosL[0] - gazePos[0]
            height = temp_gazePosL[1] - gazePos[1]
            if (abs(width) > 50 and abs(height) > 50):
                mouse.move(gazePos[0],gazePos[1])
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,gazePos[0],gazePos[1])
                press = 0
            else:
                mouse.move(temp_gazePosL[0],temp_gazePosL[1])
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,temp_gazePosL[0],temp_gazePosL[1])
                press = 0
        elif mcl < mcr:
            gazePos = newSample.getLeftEye().getGaze()
            gazePos = (int(gazePos[0]),int(gazePos[1]))
            width = temp_gazePosR[0] - gazePos[0]
            height = temp_gazePosR[1] - gazePos[1]
            if (abs(width) > 50 and abs(height) > 50):
                mouse.move(gazePos[0],gazePos[1])
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,gazePos[0],gazePos[1])
                press = 0
            else:
                mouse.move(temp_gazePosR[0],temp_gazePosR[1])
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,temp_gazePosR[0],temp_gazePosR[1])
                press = 0
        else:
            pass
    else:
        pass


runTrial()
pylink.pumpDelay(100) # ISI of 1000 ms
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()