#!coding=utf-8
from ..dataStructure.sceneInfo import Intent, SceneInfo
# from utils.dialogManager.src.dataStructure.sceneInfo import Intent,SceneInfo
from dialogManagerapp.mongoModels import intent, slot, intentCommandExecute
from dialogManagerapp.mongoModels import userDefineEntity
from dialogManagerapp.mongoModels import systemDefineEntity

from dialogManagerapp.mongoModels import sceneInfo
from mongoengine.queryset.visitor import Q
import traceback
class LoadData(object):
    """加载数据类

    从用户配置中(配置文件/数据库)加载需要的数据
    """
    def __init__(self):
        """初始化"""
        pass

    def loadIntentData(self,intentName,userId):
        """提取意图信息

        Args:
            userId:用户id
            intentName: 意图名称

        Returns:
            返回意图信息数据结构
            {
                "intent":'' #意图ID,
                "intentMatch":['xxxx'],
                "slot": [{}]
            }
        """
        intentInfo = Intent()

        intentResult = intent.objects(Q(userId=userId) & Q(intentName=intentName)).first()
        if(intentResult is not None):
            intentInfo.intent = intentResult.intentName

            #获取intentMatch
            intentInfo.intentMatch = []
            for item in intentResult.intentMatch:
                intentInfo.intentMatch.append(item)
            # slotInfo.intentMatch = intentResult.intentMatch
            #获取slot
            intentInfo.slot = []
            for i in range(len(intentResult.slot)):
                temp = {}
                temp['slotName'] = intentResult.slot[i]['slotName']
                temp['slotDescription'] = intentResult.slot[i]['slotDescription']
                temp['compulsory'] = intentResult.slot[i]['slotCompulsory']
                temp['defaultValue'] = intentResult.slot[i]['slotDefaultValue']
                temp['receiveEntityType'] = intentResult.slot[i]['slotReceiveEntityType']
                temp['Interface'] = intentResult.slot[i]['slotInterface']
                temp['context'] = {}
                temp['context']['preContext'] = intentResult.slot[i]['slotPreContext']
                temp['context']['sufContext'] = intentResult.slot[i]['slotSufContext']
                temp['dependentSlot'] = intentResult.slot[i]['slotDependentSlot']
                temp['clarification'] = intentResult.slot[i]['slotClarification']
                intentInfo.slot.append(temp)
        return intentInfo

    def loadSceneInfoData(self, userId, sceneName):
        """加载用户配置的槽位信息

        Args:
            userId:string,用户id
            sceneName:场景名称

        Returns:
            返回用户的槽位信息,json格式
            scene_info={
                'triggerIntent':[],
                'intentInfo':{'intentName1':Intent()}
                'flowConfig':[{}]
            }
        """
        _sceneInfo = SceneInfo()

        sceneResult = sceneInfo.objects(Q(userId=userId) & Q(sceneName=sceneName)).first()
        if(sceneResult is not None):
            sceneResultDict = sceneResult.to_mongo().to_dict()
            _sceneInfo.sceneName = sceneResultDict['sceneName']
            _sceneInfo.triggerIntent = sceneResultDict['triggerIntent']
            _sceneInfo.flowConfig = sceneResultDict['flowConfig']
            _sceneInfo.intentYesNoMatch = sceneResultDict['intentYesNoMatch']
            _sceneInfo.intentInfo = {}
            for key in sceneResultDict['triggerIntent']:
                _sceneInfo.intentInfo[key] = self.loadIntentData(intentName=key, userId=userId)


            yesIntentInfo = Intent()
            yesIntentInfo.intent = 'INTENT_YES'
            yesIntentInfo.intentMatch = []
            yesIntentInfo.slot = []
            _sceneInfo.intentInfo['INTENT_YES'] = yesIntentInfo

            noIntentInfo = Intent()
            noIntentInfo.intent = 'INTENT_NO'
            noIntentInfo.intentMatch = []
            noIntentInfo.slot = []
            _sceneInfo.intentInfo['INTENT_NO'] = noIntentInfo
        return _sceneInfo

    def loadIntentMatchData(self, userId):
        """加载用户配置的意图匹配规则

        Args:
            userId:string,用户id

        Returns:
            返回用户匹配的意图匹配规则json
            {
                "取钱": ['.*取.*(?:钱|款|现).*'],
                "股票查询": ['.*股票查询$', '.*股价查询.*', '.*查.*(?:股票|股价)'],
            }
        """
        ruleDict = {}
        intentReuslt = intent.objects(userId=userId).all()
        for item in intentReuslt:
            if(len(item.intentMatch)>0):
                _tmep = []
                for ruleItme in item.intentMatch:
                    _str = ruleItme.replace("*", ".*")
                    _str = _str.replace("(", "(?:")
                    _tmep.append(_str)
                ruleDict[item.intentName] = _tmep
        return ruleDict

    def loadUserDictEntityData(self, userId):
        """加载用户配置的词典实体数据

        Args:
            userId:string,用户id
        Returns:
            返回用户配置的词典实体数据 json
            entityDict = {
                "PRODUCT":["平安一账通"，"快乐平安"],
                "ORGANIZATION":["中国平安","平安银行"]
            }
        """
        ret = {}
        userDefineEntityResult = userDefineEntity.objects(userId=userId).all()
        if userDefineEntityResult is not None:
            for item in userDefineEntityResult:
                if(len(item.userDictEntityValue)>0):
                    ret[item.entityName] = item.userDictEntityValue
        return ret

    def loadUserSystemEntityData(self,userId, receiveEntityType):
        """加载用户配置的系统组合实体/系统预定义组合实体数据

        Args:
            userId:用户id
            receiveEntityType:当前意图可接收的实体类型列表

        Returns:
            返回用户配置的系统组合实体数据/系统预定义组合实体数据,json
            entityDict = {
                "MONEY":"user_number",
                "INTEGER":"user_number"
            }
        """
        ret = {}

        userDefineEntityResult = userDefineEntity.objects(userId=userId).all()
        if userDefineEntityResult is not None:
            for item in userDefineEntityResult:
                if (len(item.userSystemEntityValue) > 0 and item.entityName in receiveEntityType):
                    for it in item.userSystemEntityValue:
                        ret[it] = item.entityName
        systemDefineEntityResult = systemDefineEntity.objects().all()
        if systemDefineEntityResult is not None:
            for item in systemDefineEntityResult:
                if (len(item.entityValue) > 0 and item.entityName in receiveEntityType):
                    for it in item.entityValue:
                        ret[it] = item.entityName
        return ret

    def hasUserIntent(self,userId,intentName):
        """判断用户意图是否存在

        Args:
            userId:用户id
            intentName:意图名称

        Returns:
            True/False
        """
        intentResult = intent.objects(Q(userId=userId) & Q(intentName=intentName)).first()
        if(intentResult is not None):
            return True
        else:
            return False

    def hasTriggerScene(self,intentName,id):
        """意图是否匹配到场景

        Args:
            intentName: 意图名称
            id: 用户id

        Returns:
            返回是否匹配到场景,匹配到返回场景名字
            {
                "isTrigger":True,
                "sceneName":"xxx"
            }
        """
        ret = {}
        try:
            sceneInfoResult = sceneInfo.objects(Q(userId=id) & Q(triggerIntent__contains=intentName)).first()
            if sceneInfoResult is not None:
                ret['isTrigger'] = True
                ret['sceneName'] = sceneInfoResult['sceneName']
            else:
                ret['isTrigger'] = False
                ret['sceneName'] = ""
        except:
            traceback.print_exc()
            ret['isTrigger'] = False
            ret['sceneName'] = ""
        return ret


if __name__ == "__main__":
    userId = "user111"
    sceneName = "SCENE_ADJUST_QUOTA"
    sceneResult = sceneInfo.objects(Q(userId=userId) & Q(sceneName=sceneName)).first()
    if(sceneResult is not None):
        sceneResultDict = sceneResult.to_mongo().to_dict()
        triggerIntent = sceneResultDict['triggerIntent']
        flowConfig = sceneResultDict['flowConfig']
        intentInfo = {}
        for key in triggerIntent:
            intentInfo[key] = LoadData().loadIntentData(intentName=key, userId=userId)
