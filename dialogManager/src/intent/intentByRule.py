import re
from dialogManagerapp.mongoModels import intent
from ...src.database.loadData import LoadData
class IntentClassifier(object):

    def __init__(self):

        self.rules = \
            {
                "取钱": ['.*取.*(?:钱|款|现).*'],
                #"天气": ['查询.*天气', '查.*天气', '.*天气$','.*天气查询'],
                #"机票": ['我要[订,买,预订].*机票', '.*[订,买,预订,查询].*机票.*'],
                "股票查询": ['.*股票查询$', '.*股价查询.*', '.*查.*(?:股票|股价)'],
                "转账": ['.*转账', '给.*(?:转|汇).*钱'],
                "汇率": ['.*(?:查|看|了解|想知道).*汇率.*', '.*汇率(?:是多少|怎么样|查询).*'],
                "提取外币": ['.*(?:取|换|提|拿).*(?:外币|港币|美元|日元|英镑|欧元|韩元|加元).*'],
                "办理信用卡": ['.*(?:办|弄|搞|申请).*信用卡', '.*信用卡(?:申请|办理).*'],
                "信用卡还款": ['.*信用卡.*还款.*'],
                "注销银行卡": ['.*(?:注销|取消).*卡.*', '.*卡.*(?:注销|取消).*'],
                "查询信用卡": ['.*信用卡.*(?:账单|明细|流水).*']

            }
        pass

    def intentclassify(self,sent,id):
        """意图规则匹配
        Args:
            sent: 用户文本
            id: 用户id

        Returns:
            返回匹配到的意图名称,没有匹配到返回''
        """

        ruleDict = {}
        ruleDict = LoadData().loadIntentMatchData(userId=id)
        """
        intentReuslt = intent.objects(userId=id).all()
        for item in intentReuslt:
            if(len(item.intentMatch)>0):
                _tmep = []
                for ruleItme in item.intentMatch:
                    _str = ruleItme.replace("*", ".*")
                    _str = _str.replace("(", "(?:")
                    _tmep.append(_str)
                ruleDict[item.intentName] = _tmep
        """
        for intentName in ruleDict:

            for _rule in ruleDict[intentName]:
                res = re.match(_rule,sent)
                if res!=None:
                    return intentName

        return ''


if __name__ == '__main__':
    myClassifier = IntentClassifier()
    res = myClassifier.intentclassify('啦啦啦啦啦')
    print(res)