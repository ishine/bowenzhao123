#!coding=utf-8
import os
import sys
class tianqi(object):
    def __init__(self):
        pass

    
    def handler(self,msg):
        ret = {}
        ret['text']="自定义handler"
        return ret