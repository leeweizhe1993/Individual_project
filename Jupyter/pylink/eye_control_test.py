# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:51:56 2017

@author: Li
"""
from pymouse import PyMouse as pm
import pylink, time, gc, sys

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
tk.sendCommand('sample_rate 1000')
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
    mouse = pm()


    while not pylink.currentTime() >= startTime + 5000:
        #eyeTracked = tk.eyeAvailable()
        newSample = tk.getNewestSample()
        if(newSample != None):
        	#pylinlk.currentTime()    #(当前时间-上次消失时间)=0的次数>200则鼠标按下；再次出现则鼠标抬起
            if (newSample.isRightSample() - newSample.isLeftSample()) == 1:    #左眼闭合检测
                gazePos = newSample.getRightEye().getGaze()
                mouse.position()  #获取当前坐标的位置
                mouse.move(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
                mouse.click(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
            elif (newSample.isLeftSample() - newSample.isRightSample()) == 1:    #右眼闭合检测
                gazePos = newSample.getLeftEye().getGaze()
                mouse.position()  #获取当前坐标的位置
                mouse.move(int(gazePos[0]),int(gazePos[1]))  #鼠标移动到(x,y)位置
            else:
                gazePos = newSample.getLeftEye().getAverageGaze()
                mouse.position()  #获取当前坐标的位置
                mouse.move(int(gazePos[0]),int(gazePos[1]))  #鼠标移动到(x,y)位置
    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()

def click_down(miss_count_r, miss_count_l, gazePos):
    if miss_count > 100:
        mouse.move(int(gazePos[0]),int(gazePos[1]))
        mouse.click(int(gazePos[0]),int(gazePos[1]))
	else:
        locate()

def locate(gazePos):
        if (newSample.isRightSample() - newSample.isLeftSample()) == 1:    #左眼闭合检测
            gazePos = newSample.getRightEye().getGaze()
            mouse.position()  #获取当前坐标的位置
            mouse.move(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
            mouse.click(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
        elif (newSample.isLeftSample() - newSample.isRightSample()) == 1:    #右眼闭合检测
            gazePos = newSample.getLeftEye().getGaze()
            mouse.position()  #获取当前坐标的位置
            mouse.move(int(gazePos[0]),int(gazePos[1]))  #鼠标移动到(x,y)位置
	pass

def click_up():
	pass


for i in xrange(1):
    runTrial()
    pylink.pumpDelay(100) # ISI of 1000 ms
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()