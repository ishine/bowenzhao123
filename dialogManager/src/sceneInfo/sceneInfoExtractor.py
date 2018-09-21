# -*- coding: utf-8 -*-
# @Time : 2018/08/15 14:00
# @Author : zhoutaotao
# @File : sceneInfoExtractor.py
# @Software: dialogManagerServerNewDM
# @Desc:场景信息提取类

from ..database.loadData import LoadData
class SceneInfoExtractor(object):

    def __init__(self):
        pass


    def extractSceneInfo(self,sceneName,id):
        """提取场景信息

        Args:
            sceneName: 场景名称
            id: 用户id

        Returns:
            返回场景配置信息
            {
                "triggerIntent":["xxxx", "xxx"]#可出发此场景的意图
                # 场景的意图信息
                "intentInfo":{
                    "intentName1":Intent(),
                    }
                # 场景流程配置
                "flowConfig" :[{
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
            }
        """
        return LoadData().loadSceneInfoData(userId=id, sceneName=sceneName)

    def initSlotInfo(self):

        '''
        初始化单个槽位信息的数据结构
        :return:
        '''
        pass

if __name__ == '__main__':
    pass


