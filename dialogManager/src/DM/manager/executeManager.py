#!coding=utf-8
from ....src.intentCommandExecute.commonExecute import CommonExecute
import traceback
from ....src.intentCommandExecute.dynamicGenerationScript import DynamicGenerationScript
class ExecuteManager(object):
    """ 命令执行管理模块
    """
    def __init__(self):
        """
        初始化
        """
        self.commonExcecute = CommonExecute()


    def sceneFunDistribute(self,funName,param):
        """

        Args:
            funName: 函数名
            param: 参数
            {
            }

        Returns:
            底层公用函数返回的内容
        """
        return getattr(self.commonExcecute, funName)(param)

    def taskDistribute (self,intentInfo,IntentCommandExecute,stateManager,id):
        """ 根据决策模块结果和用户配置的响应行为,进行任务分发

        Args:
            intentInfo,经过对话获取的用户意图和槽位信息和值
                {
                    "intent":"xxx",
                    "slot_pairs":[{
                                    'slotName':'loc',
                                    'slotValue':'xxx'
                                }]
                },
            IntentCommandExecute,填槽完成后需要执行的行为/话术
                {
                    'type':'text/script',
                    'textValue':'',
                    'scriptValue':'funName'
                },
            guideIntent,是否需要引导意图的用户配置信息
                {
                    "hasGuide": 'yes',
                    "guideText": "请问您需要取钱吗",
                    "guideIntentName": "取钱"
                },
            stateManager,state对象
            id,用户id

        Returns:
            data,json格式的对象,具体格式还未确定
            {
                'text':'要生成的文本'
                'xxx':{}
            }
        """
        ret = {'text':'对话管理执行模块'}
        _slotDict = {}
        for slotItem in intentInfo['slot_pairs']:
            _slotDict[slotItem['slotName']]=slotItem['slotValue']
        intentInfo['slotInfo'] = _slotDict
        try:
            ret['text'] = "<b>[意图]: </b>"+intentInfo['intent']+"<br/>"
            for item in intentInfo['slot_pairs']:
                slotStr = ''
                slotStr = "<b>["+item['slotName']+"]: </b>"+item['slotValue']+"<br/>"
                ret['text'] = ret['text'] + slotStr
            if 'type' in IntentCommandExecute:
                if "text" == IntentCommandExecute['type']:
                    textValue = IntentCommandExecute['textValue']
                    # ret['text'] = ret['text']+"<b>[结果]: </b>"+textValue
                    ret['text'] = textValue
                elif "script" == IntentCommandExecute['type']:
                    scriptValue = IntentCommandExecute['scriptValue']
                    ret1 = getattr(self.commonExcecute,scriptValue)(intentInfo)
                    # ret['text'] = ret['text'] + "<b>[结果]: </b>"+ret1['text']
                    ret['text'] = ret1['text']
                elif "userFunction" == IntentCommandExecute['type']:
                    scriptValue = IntentCommandExecute['scriptValue']
                    ret['userFunction'] = scriptValue
                    ret['intentInfo'] = intentInfo
                elif "userHandler" == IntentCommandExecute['type']:
                    scriptValue = IntentCommandExecute['scriptValue']
                    ret = DynamicGenerationScript().callUserHandler(id=id,scriptName=scriptValue,msg=intentInfo)
            _state = stateManager.getStateValue(id)
            guideIntent = _state.guideIntent
            if 'hasGuide' in guideIntent:
                hasGuide = guideIntent['hasGuide']
                if("yes" == hasGuide):
                    guideText = guideIntent['guideText']
                    guideIntentName = guideIntent['guideIntentName']
                    ret['text'] = ret['text']+' ' + guideText
                    _state.guideIntent['hasGuide'] = 'no'
                    _state.guideIntent['exceptIntent'] = ['INTENT_YES','INTENT_NO']
                    stateManager.setStateValue(id=id,stateValue=_state)

        except Exception as e:
            traceback.print_exc()
            ret = {'text':'对话管理执行模块异常'}
        return ret

