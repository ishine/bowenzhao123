#!coding=utf-8
import time
class SlotInterfaceCall(object):
    def __init__(self):
        pass

    def getCurrentTime(self):
        currentTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        return str(currentTime)
    def getCurrentLoc(self,loc="深圳"):
        return loc