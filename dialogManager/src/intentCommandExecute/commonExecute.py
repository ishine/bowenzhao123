#!coding=utf-8
from . import stock
import traceback
import random
class CommonExecute(object):
    def __init__(self):
        pass

    def tianqi(self,intentInfo):
        """查询天气
        Args:
            intentInfo,NLP,语义理解输出内容,包括意图,及意图对应的槽信息
            {
                    "intent":"xxx",
                    "slot_pairs":[{
                                    'slotName':'loc',
                                    'slotValue':'xxx'
                                }]
            },
        """
        ret = {'text':'接口获取天气,天气很好'}
        return ret
    def withdraw(self,intentInfo):
        ret = {'text':'执行,你好有钱'}
        _slotInfo = intentInfo['slotInfo']
        withdrawNumber = _slotInfo['withdrawNumber']
        withdrawType = _slotInfo['withdrawType']
        import re
        try:
            withdrawNumberInt = int(re.sub("\D", "", withdrawNumber))
        except:
            traceback.print_exc()
            withdrawNumberInt = 1
        if "十" in withdrawNumber:
            withdrawNumberInt = withdrawNumberInt*10
        if "百" in withdrawNumber:
            withdrawNumberInt = withdrawNumberInt*100
        if "千" in withdrawNumber:
            withdrawNumberInt = withdrawNumberInt*1000
        if "万" in withdrawNumber:
            withdrawNumberInt = withdrawNumberInt*10000

        if(withdrawNumberInt < 20000 and "银行卡" in withdrawType ):
            ret['text'] = "您可以前往ATM机自助领取现金，这样比较方便快捷哦"
        else:
            ret['text'] = "请您备好银行卡（存折）和有效身份证前往柜台办理业务"
        return ret
    def transformoney(self,intentInfo):
        ret = {'text':'执行,钱多,随便转'}
        _slotInfo = intentInfo['slotInfo']
        transferNumber = _slotInfo['transferNumber']
        whichBank = _slotInfo['whichBank']
        monetaryfrom = _slotInfo['monetaryfrom']
        import re
        try:
            transferNumberInt = int(re.sub("\D", "", transferNumber))
        except:
            traceback.print_exc()
            transferNumberInt = 1
        if "十" in transferNumber:
            transferNumberInt = transferNumberInt*10
        if "百" in transferNumber:
            transferNumberInt = transferNumberInt*100
        if "千" in transferNumber:
            transferNumberInt = transferNumberInt*1000
        if "万" in transferNumber:
            transferNumberInt = transferNumberInt*10000


        #逻辑
        if whichBank in ["跨行","另一个行","其他行","他行"] and monetaryfrom in ["现金"]:
            ret['text'] = "很抱歉，我行不能直接用现金进行跨行汇款或转账哦，请先将现金存入银行卡中"
        elif transferNumberInt > 5000:
            ret['text'] = "请您备好银行卡（存折）和有效身份证前往柜台办理业务"
        else:
            ret['text'] = "您可以前往ATM机自助办理，这样比较方便快捷哦"
        return ret

    def ExchangeRateInquiry(self, intentInfo):
        ret = {'text':'汇率查询还未上线,敬请期待!'}
        _slotInfo = intentInfo['slotInfo']
        currencyType = _slotInfo['currencyType']
        return ret

    def currencyTake(self, intentInfo):
        """换外币
        """
        ret = {'text':'执行,换外币'}
        _slotInfo = intentInfo['slotInfo']
        currencyType = _slotInfo['currencyType']
        currencyNumber = _slotInfo['currencyNumber']
        appointment = _slotInfo['appointment']
        accountOwnerShip = _slotInfo['accountOwnerShip']
        import re
        try:
            currencyNumberInt = int(re.sub("\D", "", currencyNumber))
        except:
            traceback.print_exc()
            currencyNumberInt = 1
        if "十" in currencyNumber:
            currencyNumberInt = currencyNumberInt*10
        if "百" in currencyNumber:
            currencyNumberInt = currencyNumberInt*100
        if "千" in currencyNumber:
            currencyNumberInt = currencyNumberInt*1000
        if "万" in currencyNumber:
            currencyNumberInt = currencyNumberInt*10000

        if(currencyNumberInt<3000):
            ret['text'] = "请您携带您的有效身份证及银行卡前往柜台进行兑换"
        else:
            if(appointment in ["没有预约","未预约","没预约","没约","没有"]):
                if accountOwnerShip in ["本地","本地账户"]:
                    ret['text'] = "您可以通过我行网银、客服热线或前台导购处进行预约取汇业务，于预约日携带您的有效身份证及银行卡前往自助机器进行兑换"
                else:
                    ret['text'] = "您可以通过我行网银、客服热线或前台导购处进行预约取汇业务，于预约日携带您的有效身份证、银行卡及取汇申请单前往柜台进行业务办理"
            else:
                if accountOwnerShip in ["本地","本地账户"]:
                    ret['text'] = "请您携带您的有效身份证及银行卡前往自助机器进行兑换"
                else:
                    ret['text'] = "请您先填写取汇申请单，随后携带您的有效身份证、银行卡及取汇申请单前往柜台进行业务办理"
        return ret

    def creditCardApply(self,intentInfo):
        """信用卡申请
        """
        ret = {'text':'执行,信用卡申请'}
        _slotInfo = intentInfo['slotInfo']
        creditCardType = _slotInfo['creditCardType']
        creditCardMode = _slotInfo['creditCardMode']
        if(creditCardType in ["新用户"] and creditCardMode in ["自助"]):
            ret['text'] = "请点击屏幕中的“信用卡业务”按钮，找到自助办卡业务，按申请步骤完成申请。待您收到信用卡后，请前往任意支行进行激活"
        if(creditCardType in ["新用户"] and creditCardMode in ["柜台"]):
            ret['text'] = "请您携带信用卡申请书、身份证正反面复印件和单位开具的工作证明文件前往理财经理处办理业务"
        if(creditCardType in ["加办"] and creditCardMode in ["自助"]):
            ret['text'] = "请点击屏幕中的“信用卡业务”按钮，找到自助办卡业务，按申请步骤完成申请，请备注您已有主卡。待您收到新卡后，请前往任意支行进行激活"
        if(creditCardType in ["加办"] and creditCardMode in ["柜台"]):
            ret['text'] = "请您携带信用卡申请书前往理财经理处办理业务，无需再次提供工作证明和身份证明文件"
        if(creditCardType in ["附属卡"] and creditCardMode in ["自助"]):
            ret['text'] = "请点击屏幕中的“信用卡业务”按钮，找到自助办卡业务，按申请步骤完成主卡、附属卡同步申请，请在申请时勾选附属卡"
        if(creditCardType in ["附属卡"] and creditCardMode in ["柜台"]):
            ret['text'] = "请主卡人须携带本人及附属卡人的身份证明文件前往理财经理处办理业务，附属卡人不必同往"
        if(creditCardType in ["白金卡","金卡"] and creditCardMode in ["自助"]):
            ret["text"] = "很抱歉，暂不能自主申请我行白金卡或金卡"
        if(creditCardType in ["白金卡","金卡"] and creditCardMode in ["柜台"]):
            ret['text'] = "请携带您的身份证明原件、工作证明和财力证明文件前往理财经理处办理业务。"
        return ret

    def creditCardPayment(self,intentInfo):
        """信用卡还款
        """
        ret = {'text':'执行,信用卡还款'}
        _slotInfo = intentInfo['slotInfo']
        creditCardPaymentType = _slotInfo['creditCardPaymentType']
        if creditCardPaymentType in ["自动"]:
            ret['text'] = "您可以通过我行网银、客服热线或柜台开通信用卡自动还款，此方法仅支持本行储蓄卡绑定，将在每月到期还款日的17时～24时从您的指定账户扣款一次"
        elif creditCardPaymentType in ["自助"]:
            ret['text'] = "请前往ATM机，进入“信用卡还款”功能为您的信用卡存款，仅支持人民币现金或任意银行的借记卡转账还款"
        elif creditCardPaymentType in ["手机银行"]:
            ret['text'] = "您可以登陆手机银行，选择转账方式进行还款"
        elif creditCardPaymentType in ["便利店"]:
            ret['text'] = "在每月还款日前，您可以前往超市和便利店的第三方支付平台（例如拉卡啦等）推出的支付终端，进行信用卡还款。"
        return ret

    def closeCreditCard(self,intentInfo):
        """信用卡注销
        """
        ret = {'text':'执行,信用卡注销'}
        _slotInfo = intentInfo['slotInfo']
        isCardArrears = _slotInfo['isCardArrears']
        if isCardArrears in ["未欠费","没有欠费","不欠费"]:
            ret['text'] = "若您的卡内无欠费，请拨打行内热线电话进行注销；但若您有超出信用额度的金额，请携带信用卡前往柜台进行领取并注销"
        else:
            ret['text'] = "请您前往柜台办理注销业务"
        return ret

    def creditCardPaymentInquiry(self,intentInfo):
        """信用卡查询
        """
        ret = {'text':'执行,信用卡查询'}
        _slotInfo = intentInfo['slotInfo']
        creditCardPaymentInquiryType = _slotInfo['creditCardPaymentInquiryType']
        if creditCardPaymentInquiryType in ["微信"]:
            ret['text'] = '您可以进入“平安银行信用卡”官方微信账户，选择“查账”服务了解账单明细'
        elif creditCardPaymentInquiryType in ["网银", "网上"]:
            ret['text'] = '您可以登录信用卡网上银行，并点击“账户管理”→“账户查询”，查询信用卡账单明细记录。'
        elif creditCardPaymentInquiryType in ["短信"]:
            ret['text'] = '您可以编辑短信“ZD”到发送到9551186，立即查询账单明细'
        elif creditCardPaymentInquiryType in ["电话"]:
            ret['text'] = '您可以致电24小时客户服务热线95511-2进行查询'
        return ret

    def stockInquiry(self,intentInfo):
        """股票查询
        """
        ret = {'text':'执行,股票查询'}
        _slotInfo = intentInfo['slotInfo']
        organization = _slotInfo['organization']
        result = stock.getStockUrl(organization)
        if(result == ""):
            ret['text'] = "股票名称不对,请换一种方式描述您要查询的股票名称!"
        else:
            ret['text'] = "请点击查看股票详情: "+"<a href=\\\""+result+"\\\">股票详情</a>"
        return ret

    def demo_get_package_options(self, type):
        """ 获取话费查询充值的操作类型

        Args:
            type:
            {
                "type":"XXX"
            }

        Returns:

        """
        ret = "1、 10元100M 2、 20元300M 3、50元1G"
        return ret

    def demo_get_cellular_data_usage(self, time):
        """查询用户已经使用流量

        Args:
            time:
            {
                "time":"2018-08-16 12:00:02:058828"
            }

        Returns:
            ret:流量值
        """

        ret = str(random.randint(1,2))
        return ret

    def demo_get_cellular_data_left(self, time):
        """查询用户剩余流量

        Args:
            time:
            {
                "time":"2018-08-16 12:00:02:058828"
            }

        Returns:
            ret:流量值
        """
        ret = str(random.randint(0, 1))
        # ret = str(0)
        return ret