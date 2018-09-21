# -*- coding: utf-8 -*-
# @Time : 2018/08/15 14:00
# @Author : zhoutaotao
# @File : sceneState.py
# @Software: dialogManagerServerNewDM
# @Desc:负责流程控制场景状态类
import datetime
class SceneState(object):
    """ 保存场景状态
    """
    def __init__(self):
        """
        初始化
        """
        self.sceneName = "" # 场景名称
        self.receiveUserQuery = False # 是否接收用户文本
        self.updateTime = datetime.datetime.now() #更新时间
        self.slot_updated = False#是否有槽更新/覆盖
        self.currentState = ""#当前状态
        self.currentFlow = None
        self.dialogFinish = True#对话是否完成
        self.unresponsiveCount = 0#未响应次数
        self.currentIntent = ""#当前意图
        self.exceptState = ""#期望状态
        self.triggerIntent = []#可触发的意图
        self.globalParams = {}#流程控制中的全局变量
        self.slotInfo = {
            # "intentName1": [
            #        {'slotName': 'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
           # ],
           #  "intentName2": [
           #         {'slotName':'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
           # ],
        }
