# -*- coding: utf-8 -*-
# @Time : 2018/08/15 16:45 
# @Author : zhoutaotao
# @File : sceneInfo.py.py
# @Software: dialogManagerServerDev
# @Desc:场景配置信息

class Intent(object):
    """意图类
    """
    def __init__(self):
        """初始化
        """
        self.intent = '' #意图ID,
        self.intentMatch = [],
        self.slot = [
            {
                'slotName':'',
                'slotDescription':'',
                'compulsory':'True',# 是否不使用默认值
                'defaultValue':'深圳',
                'receiveEntityType':'LOC',
                'Interface':'script',
                'context':{
                    'preContext':[],
                    'sufContext':[],
                    },
                'dependentSlot':'',
                'clarification':'请问从哪个城市出发?'
            }
        ]

class SceneInfo(object):
    """场景配置信息类
    """

    def __init__(self):
        """初始化
        """
        self.sceneName = ""
        self.triggerIntent = ["xxxx", "xxx"]#可出发此场景的意图
        # 场景的意图信息
        self.intentInfo = {
            #"intentName1":Intent()
        }
        self.intentYesNoMatch = {}
        # 场景流程配置
        self.flowConfig = [{
            "output": [
              {
                "assertion": [],
                "result": [
                  {
                    "type": "tts",
                    "value": "好的王女士，您是想续订{%name%}的{%type%}吗？"
                  }
                ],
                "session": {
                  "context": {},
                  "state": "006"
                }
              }
            ],
            "params": [
              {
                "name": "type",
                "type": "slot_val",
                "value": "user_package_type"
              },
              {
                "name": "name",
                "type": "slot_val",
                "value": "user_package_name"
              }
            ],
            "trigger": {
              "intent": "INTENT_BOOK_DATA_PACKAGE",
              "slots": [
                "user_package_type",
                "user_package_name"
              ],
              "state": "005"
            }
        }]
