# -*- coding: utf-8 -*-
# @Time : 2018/08/15 14:00
# @Author : zhoutaotao
# @File : sceneInfoManager.py
# @Software: dialogManagerServerNewDM
# @Desc:场景信息管理类
from ....src.dataStructure.sceneInfo import SceneInfo
from ....src.sceneInfo import sceneInfoExtractor
from ....src.dataStructure.sceneState import SceneState
from ....src.slot.slotInterfaceCall import SlotInterfaceCall

import copy
import traceback

class SceneInfoManager(object):
    def __init__(self):
        self.sceneInfo = {}
        self.sceneInfoExtractor = sceneInfoExtractor.SceneInfoExtractor()
        self.slotInterfaceCall = SlotInterfaceCall()

    def setSceneInfo(self,id, sceneInfoValue):
        """ 设置槽位信息值,

        Args:
            id,用户id
            sceneInfoValue,要设置的值
        Returns:
            无
        """
        self.sceneInfo[id] = sceneInfoValue

    def getSceneInfo(self,id):
        """ 获取槽位信息值,

        Args:
            id,用户id,slotInfo是用户所独有
        Returns:
            slotInfoValue ,返回用户id对应的槽位信息值
        """
        if id in self.sceneInfo:
            return self.sceneInfo[id]
        else:
            return SceneInfo()

    def sceneInfoExtract(self,sceneName, id):
        """根据场景值和应用id提取对应的场景信息

        Args:
            sceneName,场景名称
            id,应用id

        Returns:
            self.sceneInfo,返回填充好的当前场景信息
        """

        _sceneInfo = self.sceneInfoExtractor.extractSceneInfo(sceneName=sceneName,id=id)
        self.setSceneInfo(id, _sceneInfo)

    def slotFill(self,nerResult,state, id):
        """槽位填充

        Args:
            nerResult,命名实体识别结果
            {
                "LOCATION":
                         [
                             {
                                 "NERValue":"上海"，
                                  "preContext":["从"],
                                  "sufContext":["到"]
                             }
                         ]
            }
            state,当前的state信息
            id, 用户id

        Returns:
            填充好槽的当前state
            {
                "parallelSlot":[
                    #{'slotName':'loc','receiveEntityType':'LOCATION','isFilled':'xx','slotFiller':'user/interface','slotValue':'xxx'}
                ],
                "dependentSlot":[

                ]
            }
        """
        # 新建一个state值，用于填槽的返回
        _state = copy.deepcopy(state)
        try:
            # 根据槽位信息，新建一个slotInfo(跟state数据结构中slotInfo数据结构相同)
            _slotPairs = _state.slotInfo[state.currentIntent]
           #  _slotPairs = [
           #         # {'slotName': 'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
           # ]


            _fillSlotIndex = [] #记录哪个槽的index已经填充
            _sceneInfo = self.getSceneInfo(id=id)
            _slotInfo = _sceneInfo.intentInfo[state.currentIntent]

            #  根据NER结果填槽
            for slotItemIndex in range(len(_slotInfo.slot)):
                _receiveEntityType = _slotInfo.slot[slotItemIndex]['receiveEntityType']
                _slotName = _slotInfo.slot[slotItemIndex]['slotName']

                _NERTypeTimes = 0
                # if nerResult.has_key('_receiveEntityType'):
                if _receiveEntityType in nerResult:
                    _NERTypeTimes = len(nerResult[_receiveEntityType])

                # 当匹配的_receiveEntityType的次数超过0次
                if _NERTypeTimes > 0:
                    # 选择符合槽位信息里该槽位的上下文特征的一个结果进行填充
                    # 取_slotInfo的前后缀
                    _preContextSlotList = []
                    _sufContextSlotList = []
                    # if (_slotInfo.slot[slotItemIndex]['context'].has_key('preContext')):
                    if 'preContext' in _slotInfo.slot[slotItemIndex]['context']:
                        _preContextSlotList = _slotInfo.slot[slotItemIndex]['context']['preContext']
                    # if (_slotInfo.slot[slotItemIndex]['context'].has_key('sufContext')):
                    if 'sufContext' in _slotInfo.slot[slotItemIndex]['context']:
                        _sufContextSlotList = _slotInfo.slot[slotItemIndex]['context']['sufContext']

                    # 遍历命名实体结果，选择符合槽位信息里该槽位的上下文特征的一个结果进行填充
                    for nerItemIndex in range(len(nerResult[_receiveEntityType])):
                        # 取出nerResult的前后缀
                        _preContextNER = '_preDefault'
                        _sufContextNER = '_sufDefault'
                        # if (nerResult[_receiveEntityType][nerItemIndex].has_key('preContext')):
                        if 'preContext' in _slotInfo.slot[slotItemIndex]['context']:
                            _preContextNER = nerResult[_receiveEntityType][nerItemIndex]['preContext']
                        # if (nerResult[_receiveEntityType][nerItemIndex].has_key('sufContext')):
                        if 'sufContext' in _slotInfo.slot[slotItemIndex]['context']:
                            _sufContextNER = nerResult[_receiveEntityType][nerItemIndex]['sufContext']

                        # 判断是否符合槽位信息里该槽位的上下文特征
                        isPreMatch = False
                        isSufMatch = False
                        if _preContextSlotList:
                            for _preItem in _preContextSlotList:
                                if _preContextNER.find(_preItem) > -1:
                                    isPreMatch = True
                        else:
                            isPreMatch = True
                        if _sufContextSlotList:
                            for _sufItem in _sufContextSlotList:
                                if _sufContextNER.find(_sufItem) > -1:
                                    isSufMatch = True
                        else:
                            isSufMatch = True

                        if isPreMatch == True and isSufMatch == True:
                            # 将这个命名实体识别结果填充到该slot-pairs里该槽位
                            tmpSlotPairs = {}
                            tmpSlotPairs['slotName'] = _slotName
                            tmpSlotPairs['isFilled'] = True
                            tmpSlotPairs['slotFiller'] = 'user'
                            tmpSlotPairs['slotValue'] = nerResult[_receiveEntityType][nerItemIndex]['NERValue']
                            nerResult[_receiveEntityType][nerItemIndex]['isUse'] = True

                            # if _state.slotInfo[_slotName]
                            # 假如有槽覆盖，设置slot_updated字段值为True
                            _stateIntent = _state.slotInfo[state.currentIntent]
                            for intentSlotIndex in range(len(_stateIntent)):
                                if _stateIntent[intentSlotIndex]['slotName'] == _slotName:
                                    if _stateIntent[intentSlotIndex]['isFilled'] == True:
                                        _state.slot_updated = True
                            # _slotPairs.append(tmpSlotPairs)
                            _slotPairs[slotItemIndex] = tmpSlotPairs
                            _fillSlotIndex.append(slotItemIndex)

                            break


            # 根据接口填槽
            # 遍历还没有被填充的槽
            for slotItemIndex in range(len(_slotInfo.slot)):
                if slotItemIndex not in _fillSlotIndex:
                    _slotName = _slotInfo.slot[slotItemIndex]['slotName']
                    if _slotInfo.slot[slotItemIndex]['Interface'] != 'None':
                        # 将这个命名实体识别结果填充到该slot-pairs里该槽位
                        tmpSlotPairs = {}
                        tmpSlotPairs['slotName'] = _slotName
                        tmpSlotPairs['isFilled'] = True
                        tmpSlotPairs['slotFiller'] = 'script'
                        # 反射的方法实现
                        # tmpSlotPairs['slotValue'] = nerResult[mulTimesIndex]['NERValue']
                        # result = getattr('class','fun')(args)

                        interfaceReuslt = getattr(self.slotInterfaceCall,_slotInfo.slot[slotItemIndex]['Interface'])()
                        tmpSlotPairs['slotValue'] = str(interfaceReuslt)
                        # _slotPairs.append(tmpSlotPairs)
                        _slotPairs[slotItemIndex] = tmpSlotPairs
                        _fillSlotIndex.append(slotItemIndex)

            # 根据默认值填槽
            # 遍历还没有填充的槽
            for slotItemIndex in range(len(_slotInfo.slot)):
                if slotItemIndex not in _fillSlotIndex:
                    _slotName = _slotInfo.slot[slotItemIndex]['slotName']
                    if _slotInfo.slot[slotItemIndex]['compulsory'] == 'False':
                        # 将这个命名实体识别结果填充到该slot-pairs里该槽位
                        tmpSlotPairs = {}
                        tmpSlotPairs['slotName'] = _slotName
                        tmpSlotPairs['isFilled'] = True
                        tmpSlotPairs['slotFiller'] = 'defalut'
                        tmpSlotPairs['slotValue'] = _slotInfo.slot[slotItemIndex]['defaultValue']
                        # _slotPairs.append(tmpSlotPairs)
                        _slotPairs[slotItemIndex] = tmpSlotPairs
                        _fillSlotIndex.append(slotItemIndex)

            # 更新_state状态并返回
            if _slotPairs:
                _state.slotInfo[state.currentIntent] = _slotPairs
            return _state
        except:
            traceback.print_exc()
            return _state



if __name__ == "__main__":
    from utils.dialogManager.src.DM.manager.stateManager import StateManager
    from utils.dialogManager.src.dataStructure.sceneInfo import Intent
    # from .stateManager import StateManager
    _stateManager = StateManager()

    # slotFill(self,nerResult,state, id)
    _nerResult = {"LOC1":[
                    {
                        "NERValue":"上海",
                        "preContext":"将从",
                        "sufContext":"到"
                    }
              ]
            }
    state = SceneState()
    state.sceneName = "001" # 场景名称
    state.slot_updated = False#是否有槽更新/覆盖
    state.currentState = ""#当前状态
    state.currentIntent = "intentName1"#当前意图
    state.slotInfo = {
        "intentName1": [
               {'slotName': 'loc1','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
       ],
        "intentName2": [
               {'slotName':'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
       ],
    }

    _stateManager.setStateValue("001",state)
    _sceneInfo = SceneInfo()

    _intent = Intent()
    _intent.slot = [
        {
            'slotName':'loc1',
            'compulsory':'True',# 是否不使用默认值
            'defaultValue':'深圳',
            'receiveEntityType':'LOC',
            'Interface':'getCurrentLoc',
            'context':{
                'preContext':["在","从"],
                'sufContext':[],
                },
            'dependentSlot':'',
            'clarification':'请问从哪个城市出发?'
        }
    ]
    _sceneInfo.intentInfo = {
            "intentName1":_intent
        }

    _sceneInfoManager = SceneInfoManager()
    _sceneInfoManager.setSceneInfo(id="001",sceneInfoValue=_sceneInfo)

    _state = _stateManager.getStateValue(id="001")
    slotFillState = _sceneInfoManager.slotFill(nerResult=_nerResult,state=_state,id="001")


    pass


