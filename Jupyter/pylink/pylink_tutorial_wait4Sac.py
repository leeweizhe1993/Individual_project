import pylink, pygame, random
from pygame.locals import *
from math import sqrt

# STEP 1: set up a link with the tracker
tk = pylink.EyeLink('100.1.1.1') # or '' or None (for dummy mode)

# here we show how to get info about the tracker
print tk.getTrackerVersionString()
print pylink.getEYELINK().getTrackerVersionString()
disp = pylink.getDisplayInformation()
print disp.width, disp.height, disp.bits, disp.refresh

# STEP 2: open Pylink graphic
scnSize = (1920, 1080)
pygame.init()
scn = pygame.display.set_mode(scnSize, FULLSCREEN|DOUBLEBUF|HWSURFACE)
# we need pylink graphic for camera setup and drift correction
pylink.openGraphics() 

# STEP 3: open an EDF data file
edfFileName = 'test.edf'
tk.openDataFile(edfFileName)

# STEP 4: set up tracking parameters using the 'sendCommand' method
# for possible parameters, see the .INI files in the ECEL/EXE folder
tk.sendCommand('sample_rate 500')
# change the color theme of the calibration display
pylink.setCalibrationColors((255,255,255), (0,0,0))
# set up the online parser
# 0--> standard (cognitive); 1--> sensitive (psychophysical)
tk.sendCommand('select_parser_configuration 0')
# set EDF file contents
tk.sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET")     
# set Link data (used for gaze cursor)
tk.sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON")
tk.sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET")
#tk.setLinkSampleData("LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET") # you can also use the setXXX comand

#### Now let's run a 1-trial experiment

# STEP 5: setup the camera and calibrate the tracker
# this needs to be done at the beginning of each block
tk.doTrackerSetup()

# function to wait for saccades
def wait4Sac(duration, tarPos, sacThresh=40, terminateUponResp = False):
    """ My wait4Sac() function."""
    # check recording eye
    eye_used = tk.eyeAvailable(); #determine which eye(s) are available 
    if eye_used in [0, 2]: eye_used = 0
    # flush keys
    pylink.flushGetkeyQueue();
    waitStartTime = tk.trackerTime()
    timeOut = False; gotSac = False;
    while (not timeOut):
        # check for time out
        if tk.trackerTime() >= (duration + waitStartTime): timeOut = True;   
        # check for saccade
        d = tk.getNextData()
        if (d == 6) and (not gotSac):
            newEvent = tk.getFloatData()
            if newEvent and (eye_used == newEvent.getEye()):
                startTime   = newEvent.getStartTime()
                endTime     = newEvent.getEndTime()
                startX, startY   = newEvent.getStartGaze()
                endX, endY       = newEvent.getEndGaze()
                sacDist = sqrt((startX - endX)**2 + (startY - endY)**2)
                landErr = sqrt((tarPos[0] - endX)**2 + (tarPos[1] - endY)**2)
                if sacDist >= sacThresh: gotSac = True
        if terminateUponResp == True and gotSac: break                                        
    if gotSac == True:
        data = [True, waitStartTime] + [startTime, endTime, int(startX), int(startY),
                                 int(endX), int(endY), int(sacDist), int(landErr)]
    else:
        data = [False, waitStartTime] + [None]*8
    return data


def runTrial():
    # The following does drift correction at the begin of each trial
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

    # present a fixation and a target
    fix_loc = (960, 540)
    tar_loc = (960 + random.choice([-1,1])*400, 540)
    pygame.draw.circle(scn, (255,255,255), fix_loc, 10)
    pygame.draw.circle(scn, (255,0,0), tar_loc, 30)
    pygame.display.flip()
    resp = wait4Sac(2000, tar_loc, sacThresh=40, terminateUponResp = True)

    # give some feedback
    if resp[0]==False:
        msg = "No EM detected!"
    else:
        if resp[-1] > 80:
            msg = "Eyes missed the target too FAR!"
        else:
            msg = "Eyes hit the target!"
    print msg

    # trial ends here
    tk.sendMessage('TRIAL OK')
    pylink.pumpDelay(100)
    tk.stopRecording()
    
# STEP 6: run a block of trial
for i in xrange(3):
    runTrial()
    
# STEP 7: File transfer and cleanup!
tk.setOfflineMode();                          
pylink.pumpDelay(100);
tk.closeDataFile()
pylink.closeGraphics()
tk.receiveDataFile(edfFileName, edfFileName)
tk.close()
