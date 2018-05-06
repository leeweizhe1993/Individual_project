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
tk.sendCommand("screen_pixel_coords =  0 0 %d %d" %(surf.get_rect().w - 1, surf.get_rect().h - 1))
tk.sendMessage("DISPLAY_COORDS  0 0 %d %d" %(surf.get_rect().w - 1, surf.get_rect().h - 1))
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")  
tk.sendCommand("heuristic_filter=ON")
# 设置连接参数（用于视线追随）
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
#tk.setLinkSampleData("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET") # you can also use the setXXX comand
tk.sendCommand("calibration_type = HV9")
#设定九点校准
tk.getEventDataFlags()

'''
变量命名说明：
press - 0则识别为click_down, 1则为click_up
miss_count_l - 左眼消失计数
miss_count_r - 右眼消失计数
temp_gazePos* - 缓存当前注视位置
'''

RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2
count = 0
press = 0
miss_count_l = 0
miss_count_r = 0
gazePos = (0, 0)
temp_gazePosL = (0, 0)
temp_gazePosR = (0, 0)
eye_used = getEYELINK().eyeAvailable() #determine which eye(s) are available 

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
    # Always send a TRIALID message before starting to record.
    msg = "TRIALID %s"%('1-trial exp')
    tk.sendMessage(msg);
            
    # 同步时间
    tk.sendMessage("SYNCTIME %d" % pylink.currentTime());
    #设置控制参数
    startTime = pylink.currentTime()
    # tk.sendMessage("Gaze-contingent search")
    # tk.sendCommand("draw_cross %d %d %d"%(500,600, 3))

    
    while not pylink.currentTime() >= startTime + 30000:
        #eyeTracked = tk.eyeAvailable()
        time.sleep(0.06)
        locate(press)
        click_down(miss_count_l, miss_count_r, gazePos)
        click_up(miss_count_l, miss_count_r, temp_gazePosL, temp_gazePosR)
    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()

def locate(press):
	'''
	函数作用——定位注视点
	'''
    global miss_count_l
    global miss_count_r
    global gazePos
    global count
    mouse = PyMouse()
    newSample = tk.getNewestSample()
    count += 1
    if press:
        click_up(mcl, mcr, temp_gazePosL, temp_gazePosR)
    elif (newSample.isBinocular() and (newSample.getLeftEye().getGaze()[0] <= 960)):    #眼睛注视左侧
        gazePos = newSample.getLeftEye().getGaze()
        if detect(gazePos):
            #mouse.position()
            autopy.mouse.smooth_move(int(gazePos[0]),int(gazePos[1]))    #鼠标移动到(x,y)位置
        else:
            pass
        #print count, 'double-l', tk.eyeAvailable()
        miss_count_l = 0
        miss_count_r = 0 
    elif (newSample.isBinocular() and (newSample.getLeftEye().getGaze()[0] > 960)):    #眼睛注视右侧
        gazePos = newSample.getRightEye().getGaze()
        if detect(gazePos):
            #mouse.position()    #获取当前坐标的位置
            autopy.mouse.smooth_move(int(gazePos[0]),int(gazePos[1])) #鼠标移动到(x,y)位置
        else:
            pass
        #print count, 'double-r', tk.eyeAvailable()
        miss_count_l = 0
        miss_count_r = 0 
    elif newSample.isRightSample() - newSample.isLefttSample() == 1:    #左眼闭合检测
        gazePos = newSample.getRightEye().getGaze()
        if detect(gazePos):
            #mouse.position()    #获取当前坐标的位置
            autopy.mouse.smooth_move(int(gazePos[0]), int(gazePos[1]))    #鼠标移动到(x,y)位置
        else:
            pass
        #print count, 'l-close', tk.eyeAvailable()
        miss_count_l += 1    #记录闭合时间
    elif newSample.isLeftSample() - newSample.isRightSample() == 1:    #右眼闭合检测
        gazePos = newSample.getLeftEye().getGaze()
        if detect(gazePos):
            #mouse.position()    #获取当前坐标的位置
            autopy.mouse.smooth_move(int(gazePos[0]), int(gazePos[1]))    #鼠标移动到(x,y)位置
        else:
            pass
        #print count, 'r-close', tk.eyeAvailable()
        miss_count_r += 1
    else:
        print newSample.isBinocular()
        print newSample.isRightSample()
        print newSample.isLefttSample()
        pass


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

    
def detect(gaze):
	'''
	注视屏幕外侧时autopy报错，此函数用于注视屏内时保证函数运行
	'''
    if (gaze[0] > 0 and gaze[0] < 1920 and gaze[1] > 0 and gaze[1] < 1080):
        return 1
    else:
        return 0

runTrial()
pylink.pumpDelay(100) # ISI of 1000 ms
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()