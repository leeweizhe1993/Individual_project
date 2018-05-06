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

# 步骤一：连接眼动仪
tk = pylink.EyeLink('100.1.1.1')

#获取眼动仪相关信息
print tk.getTrackerVersionString()
print pylink.getEYELINK().getTrackerVersionString()

#### Zhiguo: This will open an SDL graphics window, so you can use it to calibrate the tracker
disp = pylink.getDisplayInformation()
print disp.width, disp.height, disp.bits, disp.refresh
pylink.openGraphics()

#### Zhiguo: With your mouse implementation, this is totally unnecessary, but it doesn't hurt to store
#### some data on the Host PC
edfFileName = 'test.edf'
tk.openDataFile(edfFileName)

# 步骤四：使用'sendCommand'方法设置眼动仪参数
tk.sendCommand('sample_rate 500')
# 设定校准屏幕的主题颜色
pylink.setCalibrationColors((255,255,255), (0,0,0))

#### Zhiguo: These paramters are for specifying what data will be stored and can be accessed online
#### The file_event_filter etc are unnecessary for your purposes, I believe
#### The link_sample_data link_event_filter parameters are vital
# 设定在线分析程序
# 0--> 标准 (认知实验); 1--> 敏感 (神经心理学)
tk.sendCommand('select_parser_configuration 0')
# 设置EDF文件存储内容（事件相关：左、右、注视、扫视、眨眼、消息、按键）
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")  
tk.sendCommand("heuristic_filter=ON")
# 设置连接参数（用于视线追随）
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,FIXUPDATE,MESSAGE,BUTTON")
tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
#tk.setLinkSampleData("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET") # you can also use the setXXX comand
tk.sendCommand("calibration_type = HV9")
#设定九点校准

#### Zhiguo: Make sure the tracker knows the size of the display
tk.sendCommand("screen_pixel_coords = 0 0 %d %d" % (disp.width-1, disp.height-1))

#### Zhiguo: Make sure the tracker is tracking in binocular mode
tk.sendCommand("binocular_enabled = YES")


#####?????? Not sure why you have this line of code here.
#tk.getEventDataFlags()

'''
变量命名说明：
press - 0则识别为click_down, 1则为click_up
miss_count_l - 左眼消失计数
miss_count_r - 右眼消失计数
temp_gazePos* - 缓存当前注视位置
'''
count = 0
press = 0
miss_count_l = 0
miss_count_r = 0
gazePos = (0, 0)
temp_gazePosL = (0, 0)
temp_gazePosR = (0, 0)

def runTrial():
    '''校正程序'''
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
    
##    # Always send a TRIALID message before starting to record.
##    msg = "TRIALID %s"%('1-trial exp')
##    tk.sendMessage(msg);
##            
##    # 同步时间
##    tk.sendMessage("SYNCTIME %d" % pylink.currentTime());
##    #设置控制参数
    startTime = pylink.currentTime()
##    # tk.sendMessage("Gaze-contingent search")
##    # tk.sendCommand("draw_cross %d %d %d"%(500,600, 3))

    my_mouse = EyeMouse(tk)
    
    while not pylink.currentTime() >= startTime + 30000:
        my_mouse.updateMouse()
        
##    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()

class EyeMouse():
    ''' using the eyes to control the mouse on Windows machine'''

    
    def __init__(self, eyelinkTracker):
        self.mouse = PyMouse()
        self.tracker = eyelinkTracker
        self.pos = self.mouse.position()
        self.states = [False, False] # left & right buttons are both up

    def updateMouse(self):
        ''' update the mouse postion'''
        #if self.tracker.eyeAvailable()>0: # 0-Left,1-Right,2-Binocular, -1-No eye
        newEvent = self.tracker.getNextData()
        if newEvent >0:
            tmpData = self.tracker.getFloatData()

            # use the fixation update event to detect mouse position change, then move the mouse
            if tmpData and newEvent== pylink.FIXUPDATE:
                self.pos = map(int, tmpData.getAverageGaze())

            # use the blink events to change the mouse states, blink = button down, blink end = button up
            if tmpData and newEvent == pylink.STARTBLINK:
                if tmpData.getEye() == 0: # left eye=left button down
                    self.states[0]=True
                if tmpData.getEye() == 1: # right eye = right button down
                    self.states[1]=True
            if tmpData and newEvent == pylink.ENDBLINK:
                if tmpData.getEye() == 0: # left eye=left button down
                    self.states[0]=False
                if tmpData.getEye() == 1: # right eye = right button down
                    self.states[1]=False

            # change the mouse states with autopy
            for b in self.states:
                autopy.mouse.toggle(b, autopy.mouse.LEFT_BUTTON)
            # change the cursor position with autopy
            if self.pos[0] > 0 and self.pos[0] < 1920 and self.pos[1] > 0 and self.pos[1] < 1080:
                autopy.mouse.move(self.pos[0], self.pos[1])


runTrial()
pylink.pumpDelay(100) # ISI of 1000 ms
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()
