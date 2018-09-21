#!coding=utf-8
from ....src.intent.intent import Intent
class IntentManager(object):
    def __init__(self):
        self.intent = Intent()
    def getDialogIntent(self,userQuery,id):
        """根据用户输入文本返回一个意图/无意图

        Args:
            userQuery,用户输入的文本
            id,用户id

        Returns:
            {
                "code":"no_intent/has_intent",
                'intent':"hello",
                'confidence':0.87
            }

        """
        data = {}
        _result = self.intent.getIntent(userQuery, id)
        ## 根据需要处理
        _code = _result['code']
        if("no_intent" == _code):
            data['code'] = "no_intent"
        elif("confirm_intent" == _code):
            data['code'] = "has_intent"
            _content = _result['content'][0]
            data['intent'] = _content['intent']
            data['confidence'] = _content['confidence']
        elif("suggest_intent" == _code):
            data['code'] = "no_intent"
        return data