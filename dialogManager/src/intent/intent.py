#!coding=utf-8
from urllib import request
from urllib import parse
import json
import traceback
import logging
import re
from .intentByRule import IntentClassifier

class Intent(object):

    def __init__(self):
        self.intentByRule = IntentClassifier()

    def getIntent(self,userQuery,id):
        """ 根据用户输入文本判断意图

        Args:
            userQuery,用户输入的文本

        Returns:
            {
                "code":"no_intent/confirm_intent/suggest_intent",
                "content":[{'intent':"hello",'confidence':0.87}]
            }

        """
        # 请求意图识别服务
        ret = {}

        _ret = self.getIntentByRule(userQuery,id)
        if("no_intent" == _ret['code']):
            try:
                url = "http://101.132.189.160:8000/adQA/wordIntent4"
                data = {
                    "question": userQuery,
                    "topicN": '1',
                    "threshold": '0.9',
                    'typeN': '2'
                }

                params="?"
                for key in data:
                    params = params + key + "=" + data[key] + "&"
                # print("Get方法参数："+params)

                headers = {
                    #heard部分直接通过chrome部分request header部分
                    'Accept':'application/json, text/plain, */*',
                    'Accept-Encoding':'gzip, deflate',
                    'Accept-Language':'zh-CN,zh;q=0.8',
                    'Connection':'keep-alive',
                    # 'Content-Length':'100', #get方式提交的数据长度，如果是post方式，转成get方式：【id=wdb&pwd=wdb】
                    'Content-Type':'application/x-www-form-urlencoded',
                    'Referer':'http://10.1.2.151/',
                    'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'

                }

                data = parse.urlencode(data).encode('utf-8')
                req = request.Request(url, headers=headers, data=data)  #POST方法
                # req = request.Request(url+params)  # GET方法
                page = request.urlopen(req).read()
                page = page.decode('utf-8')
                print(page)
                """
                {
                    "errcode": "0",
                    "errmsg": "ok",
                    'data':{
                        "question":"天气",
                        "content": [{
                        "sen": "天气怎么样",
                        "typeNum": 2,
                        "intent": "天气",
                        "similarity": 0.8465130522555765
                        }]
                    }
                }
                """

                jsonData = json.loads(page)
                errcode = jsonData['errcode']
                if errcode == "0":
                    data = jsonData['data']['content'][0]
                    intent = data['intent']
                    similarity = data['similarity']
                    if similarity < 0.85:
                        ret['code'] = 'no_intent'
                    else:
                        if '拒绝' == intent:
                            ret['code'] = 'no_intent'
                        else:
                            ret['code'] = 'confirm_intent'
                            content = []
                            _temp = {}
                            _temp['intent'] = intent
                            _temp['confidence'] = similarity
                            content.append(_temp)
                            ret['content'] = content
                else:
                    ret['code'] = 'no_intent'
            except Exception as e:
                logging.info(traceback.format_exc())
                print(e)
        else:
            ret = _ret
        logging.info(ret)
        return ret
    def getIntentByRule(self,userQuery, id):
        """根据正则表达式判断意图
        """
        ret = {}
        result = self.intentByRule.intentclassify(userQuery,id)
        if('' == result):
            ret['code'] = 'no_intent'
        else:
            ret['code'] = 'confirm_intent'
            content = []
            _temp = {}
            _temp['intent'] = result
            _temp['confidence'] = 1.0
            content.append(_temp)
            ret['content'] = content
        return ret

    def getYesOrNoIntent(self,userQuery,sceneInfo):
        """YES/NO意图判断

        Args:
            userQuery: 用户文本
            sceneInfo: 场景信息

        Returns:
            返回用户文本匹配到的意图(INTENT_YES/INTENT_NO/'')

        """
        # ruleDict = {
        #     "INTENT_NO": ['.*(?:不需要|不可以|不行|不要|不好|不想|没有|没了|不用).*'],
        #     "INTENT_YES": ['.*(?:好的|没问题|可以|行|需要|是的|对的|可以|行的|没问题).*']
        # }
        ruleDict = {"INTENT_NO": [],"INTENT_YES":[]}
        _intentYesNoMatch = sceneInfo.intentYesNoMatch
        ruleDict['INTENT_NO'].append('.*(?:' + '|'.join(_intentYesNoMatch['intentNo']) + ').*')
        ruleDict['INTENT_YES'].append('.*(?:' + '|'.join(_intentYesNoMatch['intentYes']) + ').*')

        for intentName in ['INTENT_NO', 'INTENT_YES']:
            for _rule in ruleDict[intentName]:
                res = re.match(_rule, userQuery)
                if res!=None:
                    return intentName
        return ''

    def isExceptIntentYesOrNo(self, state, sceneInfo):
        """是否期待yes/no意图

        Args:
            state: 当前state
            sceneInfo: 当前sceneInfo

        Returns:
            True/False
        """
        ret = False
        exceptState = state.exceptState
        flowConfig = sceneInfo.flowConfig
        for flowItem in flowConfig:
            if flowItem['trigger']['state'] == exceptState:
                if "INTENT_YES".lower() in flowItem['trigger']['intent'].lower() or\
                   "INTENT_NO".lower() in flowItem['trigger']['intent'].lower():
                    ret = True
        return ret


