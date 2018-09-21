#!coding=utf-8
from ....src.dataStructure.sceneState import SceneState
import queue
import datetime
import copy
import traceback
from ...database.loadData import LoadData
from .policyManager import PolicyManager

class StateManager(object):
    def __init__(self):
        self.state = {}
        # self.TIME_THRESHOLD = 120
        self.TIME_THRESHOLD = 480
        self.UNRESPONSIVE_THRESHOLD = 2
    def setStateValue(self,id,stateValue):
        """设置多轮对话状态

        Args:
            id,用户id,state是用户自己拥有的
            stateValue,要设置的state值
        Returns:
            无
        """
        self.state[id] = stateValue

    def getStateValue(self,id):
        """获取多轮对话状态

        Args:
            id,用户id,state是用户自己拥有的
        Returns:
            stateValue,id对应的state值
        """
        if id in self.state:
            return self.state[id]
        else:
            return SceneState()

    def stateManagerClear(self, id='001'):
        """state维护模块-定期清空state

            是否接收用户文本,对话是否结束,是否填槽等信息初始和清空
            根据时间,超时进行清空操作

        Args:
            无
        Returns:
            无
        """
        _curDateTime = datetime.datetime.now()
        _updateTime = self.getStateValue(id).updateTime
        timedelta = (_curDateTime - _updateTime).seconds
        if timedelta > self.TIME_THRESHOLD:
            self.stateManagerReset(id)

    def stateManagerInit(self,currentIntentName, sceneInfo,id='001'):
        """state维护模块-state基本信息初始化
            设置接收用户文本
            更新当前state意图配置
            重置非当前意图的状态

        Args:
            currentIntentName当前意图名称
            sceneInfo,当前场景信息

        Returns:
            无
            self.state
        """
        try:
            # 判断当前state是否是有场景信息，没有场景信息则需要初始化场景信息，如果有就需要继承场景信息内容
            _state = self.getStateValue(id)

            if _state.sceneName == "":
                _state.sceneName = sceneInfo.sceneName
                _state.receiveUserQuery = True
                _state.currentIntent = currentIntentName
                _state.currentState = ""

                _state.triggerIntent = sceneInfo.triggerIntent
                # state槽位信息添加
                for intentItem in sceneInfo.triggerIntent:
                    _intentItemSlot = []
                    _slotInfo = sceneInfo.intentInfo[intentItem]
                    for slotItemIndex in range(len(_slotInfo.slot)):
                    # for intentSlotInfoItem in _slotInfo.slot:
                        tmpSlotItem = {}
                        # {'slotName': 'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
                        tmpSlotItem["slotName"] = _slotInfo.slot[slotItemIndex]["slotName"]
                        tmpSlotItem["isFilled"] = False
                        tmpSlotItem["slotFiller"] = ""
                        tmpSlotItem["slotValue"] = ""
                        _intentItemSlot.append(tmpSlotItem)
                    _state.slotInfo[intentItem] = _intentItemSlot
                _state.slotInfo['INTENT_YES'] = []
                _state.slotInfo['INTENT_NO'] = []

            else:
                # 假如state.currentIntent与currentIntentName不一致,将state.expState清空
                if _state.currentIntent != currentIntentName:
                    _state.exceptState = ""
                # 设置接收用户文本
                # 更新当前state意图配置
                _state.receiveUserQuery = True
                _state.currentIntent = currentIntentName
                # 重置非当前意图的状态
                for intentItem in _state.slotInfo:
                    if intentItem == currentIntentName:
                        pass
                    else:
                        _intentItemSlot = []
                        _slotInfo = sceneInfo.intentInfo[intentItem]
                        for slotItemIndex in range(len(_slotInfo.slot)):
                            tmpSlotItem = {}
                            if 'slotName' in _slotInfo.slot[slotItemIndex]:
                                tmpSlotItem["slotName"] = _slotInfo.slot[slotItemIndex]["slotName"]
                                tmpSlotItem["isFilled"] = False
                                tmpSlotItem["slotFiller"] = ""
                                tmpSlotItem["slotValue"] = ""
                                _intentItemSlot.append(tmpSlotItem)
                        _state.slotInfo[intentItem] = _intentItemSlot

                self.setStateValue(id=id, stateValue=_state)
        except:
            traceback.print_exc()




    def stateManagerUpdate(self, slotFillResult, id='001'):
        """state维护模块-更新state信息

        Args:
            slotFillResult,槽位填充的结果
            {
                "parallelSlot":[
                    #{'slotName':'loc','receiveEntityType':'LOCATION','isFilled':'xx','slotFiller':'user/interface','slotValue':'xxx'}
                ],
                "dependentSlot":[

                ]
            }

        Returns:
            无
        """


    def stateManagerReset(self, id):
        """state重置模块-重置state信息

        Args:
            state 信息

        Returns:
            无
        """
        _state = self.getStateValue(id=id)
        _state.sceneName = "" # 场景名称
        _state.receiveUserQuery = False # 是否接收用户文本
        _state.updateTime = datetime.datetime.now() #更新时间
        _state.slot_updated = False#是否有槽更新/覆盖
        _state.currentState = ""#当前状态
        _state.currentFlow = None
        _state.dialogFinish = True#对话是否完成
        _state.unresponsiveCount = 0#未响应次数
        _state.currentIntent = ""#当前意图
        _state.exceptState = ""#期望状态
        _state.triggerIntent = []#可触发的意图
        _state.globalParams = {}#流程控制中的全局变量
        _state.slotInfo = {
            # "intentName1": [
            #        {'slotName': 'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
           # ],
           #  "intentName2": [
           #         {'slotName':'loc','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx'}
           # ],
        }
        self.setStateValue(id=id, stateValue=_state)

    def _intentUpdateInit(self,id='001'):
        """意图切换时，进行state的初始化操作

        """



    def stateManagerRejectIntentUpdate(self,id='001'):
        """state维护模块-拒绝意图更新state信息

            设置对话结束状态
            设置不接收用户文本
            ....

        Args:
            无

        Returns:
            无
        """
        self.stateManagerReset(id=id)


    def dialogPolicy(self,slotInfo,id='001'):
        """根据当前state,返回决策结果

        Args:
            state,当前状态
            slotInfo,槽位信息

        Returns:
            {
                "type":"fillDone/fillCountout/fillNext/fillAgain/joinChat",
                "fillDone":{"intent":"xxx","slot_pairs":[{'slotName':'loc','slotValue':'xxx'}]},
                "fillNext":{'slotName':'loc','slotValue':'xxx',"clarification":"请问那个城市"}
                "fillAgain":{'slotName':'loc','slotValue':'xxx',"clarification":"请问那个城市"}
            }

        """


    def dealClarification(self,sceneInfo,id='001'):
        """澄清模块,(定位当前流程/话术执行/state更新)
        Args:
            sceneInfo,场景信息
        Returns:
            没填槽的槽位对应的信息(槽名称,槽值,澄清话术)
            {
                "status":"200",
                "clarification":"请问那个城市"
            }
        """
        ret = {}
        _state = self.getStateValue(id=id)
        _state.slot_updated = False
        _state.unresponsiveCount += 1
        if _state.unresponsiveCount > self.UNRESPONSIVE_THRESHOLD:
            self.stateManagerReset(id=id)
            ret['status'] = "203"
            ret['clarification'] = "澄清次数过多,进入闲聊"
        else:
            currentFlow = _state.currentFlow
            # _, ttsText = PolicyManager().flowAction(state=_state, flow=currentFlow)
            ttsText = PolicyManager().getFlowClarificationTTSText(state=_state,flow=currentFlow)
            ret['status'] = "200"
            ret['clarification'] = ttsText
            self.setStateValue(id=id, stateValue=_state)
        return ret



    def isTriggerScene(self, intentResult, id):
        """

        Args:
            intentResult: 当前意图数据结构
            {
                "code":"no_intent/has_intent",
                'intent':"hello",
                'confidence':0.87
            }
            id: 用户id

        Returns:
            返回是否匹配到场景,匹配到返回场景名字
            {
                "isTrigger":True,
                "sceneName":"xxx"
            }
        """
        intentName = intentResult['intent']
        return LoadData().hasTriggerScene(intentName=intentName, id=id)


    def isCurrentScene(self,sceneName,id):
        """是否当前场景

        Args:
            sceneName: 当前可触发场景名称
            id:用户id

        Returns:
            是否当前场景
            True/False
        """
        _state = self.getStateValue(id=id)
        if(_state.sceneName == sceneName and sceneName !=""):
            return True
        else:
            return False

if __name__ == "__main__":
    stateManager = StateManager()

    state = SceneState()
    state.sceneName = "查机票" # 场景名称
    state.slot_updated = False#是否有槽更新/覆盖
    state.currentState = ""#当前状态
    state.exceptState = "002" #期待状态
    state.currentIntent = "intent2"#当前意图
    state.slotInfo = {
        "intent1": [
               {'slotName': 'loc1','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx1'},
               {'slotName': 'loc2','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx2'},
       ],
        "intent2": [
               {'slotName':'loc3','isFilled': False,'slotFiller':'user/script/default','slotValue':'xxx3'}
       ],
    }

    stateManager.setStateValue("001",state)

    # stateManager.stateManagerReset(id="001")

    from utils.dialogManager.src.dataStructure.sceneInfo import SceneInfo
    from utils.dialogManager.src.dataStructure.sceneInfo import Intent
    sceneInfo = SceneInfo()
    sceneInfo.sceneName = "查机票"
    sceneInfo.triggerIntent = ["intent1","intent2"]
    _intent = Intent()
    _intent2 = Intent()
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
        },
        {
            'slotName':'loc2',
            'compulsory':'True',# 是否不使用默认值
            'defaultValue':'上海',
            'receiveEntityType':'LOC',
            'Interface':'None',
            'context':{
                'preContext':["在","从"],
                'sufContext':[],
                },
            'dependentSlot':'',
            'clarification':'请问从哪个城市出发?'
        },
        {
            'slotName':'loc66',
            'compulsory':'True',# 是否不使用默认值
            'defaultValue':'上海',
            'receiveEntityType':'LOC',
            'Interface':'None',
            'context':{
                'preContext':["在","从"],
                'sufContext':[],
                },
            'dependentSlot':'',
            'clarification':'请问从哪个城市出发?'
        }
    ]
    _intent2.slot = [
        {
            'slotName':'loc3',
            'compulsory':'True',# 是否不使用默认值
            'defaultValue':'广州',
            'receiveEntityType':'LOC',
            'Interface':'getCurrentLoc',
            'context':{
                'preContext':["在","从"],
                'sufContext':[],
                },
            'dependentSlot':'',
            'clarification':'请问从哪个城市出发?'
        },
    ]
    sceneInfo.intentInfo = {
        "intent1":_intent,
        "intent2":_intent2
    }

    from utils.dialogManager.src.DM.manager.sceneInfoManager import SceneInfoManager
    _sceneInfoManager = SceneInfoManager()
    _sceneInfoManager.setSceneInfo(id="001",sceneInfoValue=sceneInfo)

    stateManager.stateManagerInit("intent1",_sceneInfoManager.getSceneInfo(id="001"),id="001")
    state = stateManager.getStateValue(id="001")


    pass