# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:51:56 2017

@author: Li
"""
import pylink as pylink, pygame
from psychopy import visual, core, event
from pygame.locals import *

# 步骤一：连接眼动仪
tk = pylink.Eyelink('100.1.1.1')

#获取眼动仪相关信息
print tk.getTrackerVersionString()
print pylink.getEYELINK().getTrackerVersionString()
disp = pylink.getDisplayInformation()
print disp.width, disp.height, disp.bits, disp.refresh

# 步骤二：打开pylink图像
scnSize = (1920, 1080)
pygame.init()
scn = pygame.display.set_mode(scnSize, FULLSCREEN|DOUBLEBUFF|HWSURFACE)
pylink.openGraphics()

# 步骤三：打开EDF文件
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

#### Now let's run a 1-trial experiment

# STEP 5: 设置摄像头并校准眼动仪
# 每个block前进行操作
tk.doTrackerSetup()

def runTrial():
    # 每一trail开始前进行漂移检测
    try:                        
        error = tk.doDriftCorrect(scnSize[0]/2, scnSize[1]/2, 1, 1)
    except:
        tk.doTrackerSetup()

    # force off-line mode first to prevent eyelink freeze, just for precaution
    pylink.flushGetkeyQueue() # clear all cached button responses
    
    tk.setOfflineMode()
    pylink.pumpDelay(100);

    # start recording
    error = tk.startRecording(1,1,1,1)
    if error: print error
    pylink.pumpDelay(100);      # wait for 100 ms to make all data of interests is recorded

    # Always send a TRIALID message before starting to record.
    msg = "TRIALID %s"%('1-trial exp')
    tk.sendMessage(msg);
            
    # send the "SYNCTIME" message to mark the zero time of a trial
    tk.sendMessage("SYNCTIME %d" % pylink.currentTime());

    # show a black window, show the gaze position as your eyes move
    # show the image for 5 sec
    startTime = pylink.currentTime()
    while not pylink.currentTime() >= startTime + 5000:
        # check for which eye is tracked, 0~LEFT, 1-RIGHT, 2-BINOCULAR
        eyeTracked = tk.eyeAvailable()
        dt = tk.getNewestSample() # check for new sample update
        if(dt != None):
            if eyeTracked == 1 and dt.isRightSample():
                gazePos = dt.getRightEye().getGaze()
            elif eyeTracked == 0 and dt.isLeftSample():
                gazePos = dt.getLeftEye().getGaze()
            # update the cursor
            scn.fill((0,0,0))
            pygame.draw.circle(scn, (255,0,0), (int(gazePos[0]), int(gazePos[1])), 5)
        pygame.display.flip()

    # trial ends here
    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()
    
# STEP 6: run a block of trial
for i in xrange(1):
    runTrial()
    
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
pylink.closeGraphics()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()
