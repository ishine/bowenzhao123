# -*- coding: utf-8 -*-
# @Time : 2018/08/16 14:42 
# @Author : zhoutaotao
# @File : policyManager.py
# @Software: dialogManagerServerDev
# @Desc:决策模块类
import re
import copy
from .executeManager import ExecuteManager
class PolicyManager(object):
    """决策类
    """
    def __init__(self):
        """
        初始化
        """
        pass

    def flowTrigger(self,state,sceneInfo):
        """trigger匹配模块

        Args:
            state: 当前state
            sceneInfo: 当前场景信息

        Returns:
            是否匹配到某个flow,匹配到返回匹配到的flow
            {
                "isTriggerSuccess":True/False,
                "msg":{
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
            }
        """
        ret = {}
        exceptState = state.exceptState #期望state
        currentIntent = state.currentIntent #当前意图
        try:
            slotInfo = state.slotInfo[currentIntent] #当前意图对应的槽位填充信息
        except:
            slotInfo = []
            pass

        #已填充槽位列表
        slotFilledList = []
        for slotItem in slotInfo:
            if(slotItem['isFilled']):
                slotFilledList.append(slotItem['slotName'])


        maxTrigger = -1
        maxTriggerObj = None

        for item in sceneInfo.flowConfig:
            # 期望state满足条件
            if item['trigger']['state'] == exceptState and currentIntent == item['trigger']['intent']:
                slotTriggerCount = 0
                for slot in item['trigger']['slots']:
                    if slot in slotFilledList:
                        slotTriggerCount += 1
                    else:
                        slotTriggerCount = -1
                        break
                if slotTriggerCount != -1:
                    if slotTriggerCount > maxTrigger:
                        maxTriggerObj = item
        if maxTriggerObj is not None:
            ret['isTriggerSuccess'] = True
            ret['msg'] = maxTriggerObj
        else:
            ret['isTriggerSuccess'] = False
            ret['msg'] = maxTriggerObj
        return ret

    def getFlowParams(self, state, flow):
        """提取trigger模块的Params

        Args:
            state:当前state
            flow: 当前匹配到的trigger

        Returns:
            返回计算好的params
            {
                "name":"xxx",
                "name2":"xxxx"
            }
        """
        ret = {}
        currentIntent = state.currentIntent #当前意图
        slotInfo = state.slotInfo[currentIntent] #当前意图对应的槽位填充信息
        for item in flow['params']:
            type = item['type']
            name = item['name']
            value = item['value']
            if("slot_val" == type):
                """
                    {
                        "name": "type",
                        "type": "slot_val",
                        "value": "user_package_type"
                    }
                """

                for slotItem in slotInfo:
                    if slotItem['slotName'] == value:
                        ret[name] = slotItem['slotValue']
                        break

            elif("func_val" == type):
                """
                    {
                        "name": "options",
                        "type": "func_val",
                        "value": "demo_get_package_options:{%type%}"
                    }
                """
                _function = value.split(":")[0]
                _param = value.split(":")[1]

                _param = re.findall(r"{%(.+?)%}", _param)
                param = {}
                for paramItem in _param:
                    param[paramItem] = ret[paramItem]
                ret[name] = ExecuteManager().sceneFunDistribute(_function, param)
        return ret


    def isExceptFlowTrigger(self,state,sceneInfo):
        """是否有期待state的槽位已填,匹配到就直接跳到下一个Flow

        Args:
            state: 当前state
            sceneInfo: 当前场景信息

        Returns:
            {
                "isTriggerSuccess":True/False,
            }
        """
        return self.flowTrigger(state=state, sceneInfo=sceneInfo)

    def isMatchAssertion(self,assertion,globalParams):
        """是否匹配到条件

        Args:
            assertion: 条件
            globalParams: 变量值

        Returns:
            返回是否匹配到条件
        """
        isMathch = True
        for item in assertion:
            type = item['type']
            value = item['value']
            if("empty" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    if(globalParams[_key]==""):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("not_empty" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    if(globalParams[_key]!=""):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("in" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1:]
                    if(globalParams[_key] in _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("not_in" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1:]
                    if(globalParams[_key] not in _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("eq" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1]
                    if(globalParams[_key] == _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("gt" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1]
                    if(globalParams[_key] > _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("ge" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1]
                    if(globalParams[_key] >= _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("le" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1]
                    if(globalParams[_key] <= _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            elif("lt" == type):
                _paramList = re.findall(r"{%(.+?)%}", value)
                if len(_paramList)>0:
                    _key = _paramList[0]
                    _value = value.split(",")[1]
                    if(globalParams[_key] < _value):
                        isMathch = True
                    else:
                        isMathch =False
                        break
            else:
                isMathch =False
                break
        return isMathch

    def flowAction(self, state, flow):
        """流程执行模块
            (条件判断/state更新)

        Args:
            state: 当前state
            flow: 当前匹配到的trigger

        Returns:
            返回话术
        """
        newState = copy.deepcopy(state)
        ttsText = ""
        output = flow['output']
        # unresponsiveCount重置
        newState.unresponsiveCount = 0
        globalParams = state.globalParams
        for outputItem in output:
            assertion = outputItem['assertion']
            if self.isMatchAssertion(assertion, globalParams):
                result = outputItem['result'][0]
                session = outputItem['session']
                newState.currentState = newState.exceptState
                newState.exceptState = session['state']
                if("tts" == result['type']):
                    ttsTextRes = result['value']
                    ttsText = ""
                    if type(ttsTextRes) == list:
                        ttsText = ttsTextRes[0]
                    else:
                        ttsText = ttsTextRes
                    paList = re.findall(r"{%(.+?)%}", ttsText)
                    for paItem in paList:
                        _str = "{%"+paItem+"%}"
                        ttsText = ttsText.replace(_str, globalParams[paItem])
        return newState, ttsText



    def getFlowClarificationTTSText(self, state, flow):
        """获取当前flow的澄清话术
            (条件判断/state更新)

        Args:
            state: 当前state
            flow: 当前匹配到的trigger

        Returns:
            返回话术
        """
        ttsText = ""
        output = flow['output']
        globalParams = state.globalParams
        for outputItem in output:
            assertion = outputItem['assertion']
            if self.isMatchAssertion(assertion, globalParams):
                result = outputItem['result'][0]
                if("tts" == result['type']):
                    ttsTextRes = result['value']
                    ttsText = ""
                    if type(ttsTextRes) == list:
                        ttsText = ttsTextRes[0]
                    else:
                        ttsText = ttsTextRes
                    paList = re.findall(r"{%(.+?)%}", ttsText)
                    for paItem in paList:
                        _str = "{%"+paItem+"%}"
                        ttsText = ttsText.replace(_str, globalParams[paItem])
        return ttsText

    def setCurrentIntentToExpIntent(self, state, sceneInfo):
        """设置state当前意图为期待state的意图
            (条件判断/state更新)

        Args:
            state: 当前state
            sceneInfo: 当前场景信息

        Returns:
            state状态
        """
        _state = copy.deepcopy(state)
        exceptState = state.exceptState #期望state
        currentIntent = state.currentIntent #当前意图
        exceptIntent = currentIntent

        for item in sceneInfo.flowConfig:
            # 期望state满足条件
            if item['trigger']['state'] == exceptState:
                exceptIntent = item['trigger']['intent']

        _state.currentIntent = exceptIntent

        return _state

    def isHasExceptState(self,exceptState,sceneInfo):
        """期待state的是否存在

        Args:
            exceptState: 期待state
            sceneInfo: 当前场景信息

        Returns:
            True/False： True:期待state存在 False:期待state不存在

        """
        ret = False
        for item in sceneInfo.flowConfig:
            if item['trigger']['state'] == exceptState:
                ret = True

        return ret



