#!coding=utf-8
from .manager.stateManager import StateManager
from .manager.intentManager import IntentManager
from .manager.sceneInfoManager import SceneInfoManager
from .manager.nerManager import NERManager
from .manager.policyManager import PolicyManager
from .manager.executeManager import ExecuteManager
from ..database.loadData import LoadData
import traceback
import logging
import time
class DialogManager(object):
    __instance = None
    __first_init = True
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            orig = super(DialogManager, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return cls.__instance
    def __init__(self):
        if self.__first_init:
            self.intentManager = None
            self.stateManager = None
            self.sceneInfoManager = None
            self.nerManager = None
            self.policyManager = None
            self.DialogManagerInit()
            DialogManager.__first_init = False

    def DialogManagerInit(self):

        self.intentManager = IntentManager()
        self.stateManager = StateManager()
        self.sceneInfoManager = SceneInfoManager()
        self.nerManager = NERManager()
        self.policyManager = PolicyManager()

    def policyDialog(self,userQuery,id):
        """
        Args:
            userQuery: 用户输入文本
            id: 用户id

        Returns:
            返回对话结果
            status,data
        """
        status = "200"
        data = {}
        try:
            triggerResult = self.policyManager.flowTrigger(state=self.stateManager.getStateValue(id=id),
                                                           sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
            print("是否匹配到flow: ", triggerResult)
            if(triggerResult['isTriggerSuccess']):
                #提取trigger模块的Params
                _params = self.policyManager.getFlowParams(state=self.stateManager.getStateValue(id=id),
                                                           flow=triggerResult['msg'])
                print("params 获取结果: ",_params)
                _state = self.stateManager.getStateValue(id=id)
                _state.globalParams = _params
                _state.currentFlow = triggerResult['msg']
                self.stateManager.setStateValue(id=id, stateValue=_state)
                newState,ttsText = self.policyManager.flowAction(state=_state,
                                                        flow=triggerResult['msg'])
                print("flowAction结果: ",newState,ttsText)
                self.stateManager.setStateValue(id=id, stateValue=newState)

                # 判断当前是否INTENT_YES意图
                if newState.currentIntent == 'INTENT_YES':
                    # 设置state的currIntent等于期待state对应的Intent
                    changeState = self.policyManager.setCurrentIntentToExpIntent(state=self.stateManager.getStateValue(id=id),
                                                                   sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
                    if 'INTENT_YES' == changeState.currentIntent or 'INTENT_NO' == changeState.currentIntent:
                        _state = self.stateManager.getStateValue(id=id)
                        _state.currentIntent = ""
                        self.stateManager.setStateValue(id=id, stateValue=_state)
                    else:
                        self.stateManager.setStateValue(id=id, stateValue=changeState)
                    status = "200"
                    data['text'] = ttsText
                elif newState.currentIntent == 'INTENT_NO':
                    changeState = self.policyManager.setCurrentIntentToExpIntent(state=self.stateManager.getStateValue(id=id),
                                                                   sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
                    if 'INTENT_YES' == changeState.currentIntent or 'INTENT_NO' == changeState.currentIntent:
                        _state = self.stateManager.getStateValue(id=id)
                        _state.currentIntent = ""
                        self.stateManager.setStateValue(id=id, stateValue=_state)
                    status = "200"
                    data['text'] = ttsText
                else:
                    #期待state的trigger是否能匹配上
                    isExceptFlowTrigger = self.policyManager.isExceptFlowTrigger(state=_state,
                                                                                 sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
                    if(isExceptFlowTrigger['isTriggerSuccess']):
                        status, data = self.policyDialog(userQuery=userQuery, id=id)
                    else:
                        status = "200"
                        data['text'] = ttsText
            else:
                _state = self.stateManager.getStateValue(id=id)
                if(_state.slot_updated):
                    _state.exceptState = _state.currentState
                    _state.slot_updated = False
                    status, data = self.policyDialog(userQuery=userQuery, id=id)
                else:
                    clarificationResult = self.stateManager.dealClarification(sceneInfo=self.sceneInfoManager.getSceneInfo(id=id), id=id)
                    status = clarificationResult['status']
                    data['text'] = clarificationResult['clarification']

            # 设置slot_updated为False; 判断exceptState是否存在，不存在说明对话结束，resetstate ,存在不操作
            retState = self.stateManager.getStateValue(id=id)
            retState.slot_updated = False
            _isHasExceptState = self.policyManager.isHasExceptState(exceptState=retState.exceptState,
                                                                    sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
            if _isHasExceptState:
                pass
            else:
                self.stateManager.stateManagerReset(id=id)
        except:
            traceback.print_exc()
            status = "404"
            data['text'] = "程序异常"

        return status, data

    def commonDeal(self, userQuery, id):
        """公共程序部分

        Args:
            userQuery: 用户输入文本
            id: 用户id

        Returns:
            status,data
        """
        #命名实体识别
        _state = self.stateManager.getStateValue(id=id)
        _currentIntent = _state.currentIntent

        slotFillState = self.stateManager.getStateValue(id=id)
        if("" != _currentIntent):
            nerResult = self.nerManager.getNamedEntityRecog(userQuery=userQuery,
                                                            # slotInfo=_state.slotInfo[_currentIntent],
                                                            slotInfo=self.sceneInfoManager.getSceneInfo(id).intentInfo[_currentIntent],
                                                            id=id)
            print("命名实体结果:", nerResult)
            #槽填充
            slotFillState = self.sceneInfoManager.slotFill(nerResult=nerResult,
                                                           state=self.stateManager.getStateValue(id=id),
                                                           id=id)
        print("槽填充结果:", slotFillState)
        self.stateManager.setStateValue(id=id, stateValue=slotFillState)
        #决策模块
        status, data = self.policyDialog(userQuery=userQuery, id=id)
        return status, data


    def getDialogAnswer(self, userQuery, id='001'):
        """根据用户输入文本,计算回复的对话内容

        Args:
            userQuery,用户输入的文本
            id,用户id

        Returns:
            {
                "status":"200",
                "msg":{
                    "text":"正常回复"
                }
            }
            200:正常回复,
            201:拒绝意图结束,进入闲聊.
            202:对话完成,不在接受文本,进入闲聊,
            203:多次没有填充成功,进入闲聊,
            204:对话结束,进入一次没有提取到相关信息,进入闲聊
            404:程序异常

        """
        total_start =time.time()
        status = "200"
        result = {}
        data = {}
        try:
            # state维护模块-定期清空state
            intent_start =time.time()
            self.stateManager.stateManagerClear(id)
            intentResult = self.intentManager.getDialogIntent(userQuery, id)
            intent_end =time.time()
            print('intent Running time: %s Seconds'%(intent_end-intent_start))
            # 有意图分支
            if (intentResult['code'] == 'has_intent'):
                # 是否拒绝意图
                if (intentResult['intent'] == '拒绝'):
                    self.stateManager.stateManagerRejectIntentUpdate(id)
                    status = '201'
                    data['text'] = '拒绝意图，对话结束'
                else:
                    #能否触发场景
                    isTriggerScene = self.stateManager.isTriggerScene(intentResult, id)
                    print("能否触发场景: ", isTriggerScene)
                    if(isTriggerScene['isTrigger']):
                        sceneName = isTriggerScene['sceneName']
                        #是否当前场景
                        isCurrentScene = self.stateManager.isCurrentScene(sceneName, id=id)
                        print("是否当前场景: ", isCurrentScene)
                        if(isCurrentScene is False):
                            self.stateManager.stateManagerReset(id=id)
                            self.sceneInfoManager.sceneInfoExtract(sceneName=sceneName, id=id)
                        self.stateManager.stateManagerInit(currentIntentName=intentResult['intent'],
                                                           sceneInfo=self.sceneInfoManager.getSceneInfo(id),
                                                           id=id)
                        status, data = self.commonDeal(userQuery=userQuery, id=id)
                    else:
                        status = '202'
                        data['text'] = '进入闲聊'

            # 无意图分支
            else:
                if self.stateManager.getStateValue(id=id).receiveUserQuery:
                    isExceptIntentYesOrNo = self.intentManager.intent.isExceptIntentYesOrNo(state=self.stateManager.getStateValue(id=id),
                                                                                            sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
                    if isExceptIntentYesOrNo is False:
                        status, data = self.commonDeal(userQuery=userQuery, id=id)
                    else:
                        getYesOrNoIntentResult = self.intentManager.intent.getYesOrNoIntent(userQuery=userQuery, sceneInfo=self.sceneInfoManager.getSceneInfo(id=id))
                        print("INTENT_YES/NO判断结果: ",getYesOrNoIntentResult)
                        if "" == getYesOrNoIntentResult:
                            # clarificationResult = self.stateManager.dealClarification(sceneInfo=self.sceneInfoManager.getSceneInfo(id=id), id=id)
                            # status = clarificationResult['status']
                            # data['text'] = clarificationResult['clarification']
                            status, data = self.commonDeal(userQuery=userQuery, id=id)
                        else:
                            _state = self.stateManager.getStateValue(id=id)
                            _state.currentIntent = getYesOrNoIntentResult
                            _state.unresponsiveCount = 0
                            self.stateManager.setStateValue(id=id, stateValue=_state)
                            status, data = self.policyDialog(userQuery=userQuery, id=id)
                else:
                    status = '202'
                    data['text'] = '进入闲聊'

        except Exception as e:
            status = '404'
            data['text'] = '程序异常'
            traceback.print_exc()
            logging.error(traceback.format_exc())

        result['status'] = status
        result['msg'] = data
        total_end =time.time()
        print('total Running time: %s Seconds'%(total_end-total_start))
        logging.info(result)
        return result