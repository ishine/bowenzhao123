import gensim
import re
import time
import numpy as np
import datetime


class NamedEntityNormalization():
    __instance = None
    __first_init = True
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            orig = super(NamedEntityNormalization, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return cls.__instance
    def __init__(self):
        if self.__first_init:
            #加载词向量模型

            #词向量模型待替换
            self.wordVecModel = gensim.models.KeyedVectors.load_word2vec_format(
                'utils/dialogManager/model/NER/wiki.zh.vector.bin', binary=True)


            self.index2Week = {0:'星期一',1:'星期二',2:'星期三',3:'星期四',4:'星期五',5:'星期六',6:'星期天'}
            self.week2Index = {'星期一':0,'星期二':1,'星期三':2,'星期四':3,'星期五':4,'星期六':5,'星期天':6}
            self.date2Index = {'今天':0,'明天':1,'后天':2,'昨天':-1}
            self.__class__.__first_init = False




    def norDate(self,ent):

        '''
        对日期这个命名实体进行归一化
        :param ent:识别出来的日期命名实体，字符串
        :return:标准格式 xxx年xx月xx日
        '''
        threshold = 0.6
        #满足格式要求的命名实体直接返回
        matchObject = re.match('\d{4}年\d{1,2}月\d{1,2}[日,号]$',ent)
        if matchObject !=None:
            return ent

        currentTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        currentDate = currentTime.split(' ')[0].split('-')
        currentWeekDay = datetime.datetime.now().weekday()


        #部分格式满足要求的获取缺失值
        #1. 满足 xx日/号的情况，自动补全当前年份和当前月份
        matchObject = re.match('\d{1,2}[日,号]$',ent)
        if matchObject != None:
            return currentDate[0]+'年'+currentDate[1]+'月'+ ent

        matchObject = re.match('\d{1,2}月\d{1,2}[日,号]$',ent)
        if matchObject != None:
            return currentDate[0]+'年'+ent


        #将"今天"和它的同义词转化为具体时间
        if ent in self.wordVecModel:
            wEnt = self.wordVecModel[ent]
        else:
            wEnt = np.zeros(128)
            return ent

        wordSim = 0.6
        entDateIndex = None

        #找出ent 是今天，明天，后天中的哪一个
        for key in self.date2Index:
            tmp = self.calWordSim(wEnt,self.wordVecModel[key])
            if tmp >= wordSim:
                wordSim = tmp
                entDateIndex = self.date2Index[key]

        if entDateIndex != None:
            entTime = float(time.time()) + entDateIndex*24*60*60
            tmp = time.strftime("%Y-%m-%d", time.localtime(entTime))
            entDate = tmp.split('-')
            return entDate[0] + '年' + entDate[1] + '月' + entDate[2] + '日'

        #找出ent是星期几
        wordSim = 0.6
        entWeekIndex = None
        for i in range(len(self.index2Week)):
            tmp = self.calWordSim(wEnt,self.wordVecModel[self.index2Week[i]])
            if tmp >= wordSim:
                wordSim = tmp
                entWeekIndex = i

        if entWeekIndex!=None:

            daysNum = ((entWeekIndex + 7)-currentWeekDay)%7

            #需要处理月份日期溢出的情况
            entTime = float(time.time()) + daysNum * 24 * 60 * 60
            tmp = time.strftime("%Y-%m-%d", time.localtime(entTime))
            entDate = tmp.split('-')
            return entDate[0] + '年' + entDate[1] + '月' + entDate[2] + '日'


        #归一化失败，依然返回没有归一化的命名实体识别结果
        return ent


    def loadInfo(self):
        pass

    def checkDate(self):
        pass



    def calWordSim(self,w1,w2):

        return w1.dot(w2)/((np.sqrt(w1.dot(w1))) * (np.sqrt(w2.dot(w2))))



    def norEntities(self,entities):

        for entName in entities:
            if entName == 'DATE':
                for ent in entities[entName]:
                    ent['NERValue'] = self.norDate(ent['NERValue'])


        return entities





'''
if __name__  == '__main__':
    myObject = NamedEntityNormalization()
    myObject.norDate('昨天')
'''


