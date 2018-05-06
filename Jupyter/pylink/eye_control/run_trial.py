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
import click

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
    eye_used = getEYELINK().eyeAvailable() #determine which eye(s) are available 
	if eye_used == RIGHT_EYE:
		getEYELINK().sendMessage("EYE_USED 1 RIGHT")
	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
		getEYELINK().sendMessage("EYE_USED 0 LEFT")
		eye_used = LEFT_EYE
	else:
		print("Error in getting the eye information!")
		return TRIAL_ERROR
	
	getEYELINK().flushKeybuttons(0)
	buttons =(0, 0)
	last_draw_time = currentTime()
    while 1:
		error = getEYELINK().isRecording()  # First check if recording is aborted 
		if error!=0:
			end_trial()
			return error

		if (currentTime() -startTime) > DURATION:  #Writres out a time out message if no response is made
			getEYELINK().sendMessage("TIMEOUT")
			end_trial()
			buttons =(0, 0)
			break
		
		if(getEYELINK().breakPressed()):        # Checks for program termination or ALT-F4 or CTRL-C keys
			end_trial()
			return ABORT_EXPT
		elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)
			end_trial()
			return SKIP_TRIAL
			
		buttons = getEYELINK().getLastButtonPress() # Checks for eye-tracker buttons pressed
		if(buttons[0] != 0):
			getEYELINK().sendMessage("ENDBUTTON %d"%(buttons[0]))
			end_trial()
			break           
			
		dt = getEYELINK().getNewestSample() # check for new sample update
		if(dt != None):
			last_draw_time = currentTime()
			# Gets the gaze position of the latest sample,
			if eye_used == RIGHT_EYE and dt.isRightSample():
				gaze_position = dt.getRightEye().getGaze()
			elif eye_used == LEFT_EYE and dt.isLeftSample():
				gaze_position = dt.getLeftEye().getGaze()

			gaze_position= (gaze_position[0]- cursorsize[0]/2),(gaze_position[1]- cursorsize[1]/2) #center the size
			surf.blit(bgbm,(0,0)) #draw the background
			surf.blit(fgbm, (gaze_position[0],gaze_position[1]),(gaze_position[0],gaze_position[1],cursorsize[0],cursorsize[1]))   #Draws and shows the cursor content;
			display.flip()


    
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