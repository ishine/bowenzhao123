# -*- coding: utf-8 -*-

import tensorflow as tf
import numpy as np
import os, argparse, time, random
from dialogManagerapp.mongoModels import userRuleEntity
from ...src.NER.model import BiLSTM_CRF
from ...src.NER.utils import str2bool, get_logger,get_entity_dic,entityLinking
from ...src.NER.data import read_corpus, read_dictionary, tag2label, random_embedding
from xml.dom.minidom import parse
import re
from ...src.database.loadData import LoadData




class NERProcessor(object):
    __instance = None
    __first_init = True
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            orig = super(NERProcessor, cls)
            cls.__instance = orig.__new__(cls, *args, **kwargs)
        return cls.__instance
    def __init__(self):
        if self.__first_init:
            self.model, self.sess = self.initModels()
            self.PATH = {}
            self.PATH['PRODUCT'] = 'utils/dialogManager/data/product.txt'
            self.PATH['LOCATION'] = 'utils/dialogManager/data/location.txt'
            self.PATH['CARDTYPE'] = 'utils/dialogManager/data/cardtype.txt'
            self.PATH['ACCOUNTBANK'] = 'utils/dialogManager/data/accountbank.txt'
            self.PATH['MONETARYFORM'] = 'utils/dialogManager/data/monetaryform.txt'
            self.PATH['CURRENCYTYPE'] = 'utils/dialogManager/data/currencyType.txt'
            self.PATH['APPOINTMENT'] = 'utils/dialogManager/data/appointment.txt'
            self.PATH['ACCOUNTOWNERSHIP'] = 'utils/dialogManager/data/accountOwnership.txt'
            self.PATH['CREDITCARDTYPE'] = 'utils/dialogManager/data/creditCardType.txt'
            self.PATH['CREDITCARDMODE'] = 'utils/dialogManager/data/creditCardMode.txt'
            self.PATH['CREDITCARDPAYMENTTYPE'] = 'utils/dialogManager/data/creditCardPaymentType.txt'
            self.PATH['CARDARREARSSTATUS'] = 'utils/dialogManager/data/cardArrearsStatus.txt'
            self.PATH['CREDITCARDPAYMENTINQUIRYTYPE'] = 'utils/dialogManager/data/creditCardPaymentInquiryType.txt'
            self.PATH['ORGANIZATION'] = 'utils/dialogManager/data/organization.txt'

            self.mappingPath = 'utils/dialogManager/data/namedEntityMapping.txt'

            self.ruleEntitis = []
            self.rules = []
            # self.ruleEntitis, self.rules = self.loadRules(userId='')

            self.mappingDict = self.loadMappingRules()
            NERProcessor.__first_init = False


    def loadMappingRules(self):

        '''
        按照用户配置的命名实体转换规则


        {
            "INTERGER":"NUMX" 将系统里的INTEGER命名实体转化成用户配置的"NUMX
        }

        :return:
        '''

        mappingDict = {}

        dom = parse(self.mappingPath)
        root = dom.documentElement
        mappings = root.getElementsByTagName('namedEntity')
        for i in range(len(mappings)):
            usrEntityName = mappings[i].getAttribute('name')
            ne = mappings[i].getElementsByTagName('n')
            for j in range(len(ne)):
                #print(ne[j].firstChild.data)
                _tmp = ne[j].firstChild.data
                if _tmp not in mappingDict:
                    mappingDict[_tmp] = usrEntityName


        #print(mappingDict)
        return mappingDict



    def mapEntities(self,entities, slotInfo, id):
        """将entity里的命名实体替换成用户配置的命名实体

        Args:
            entities: 模型识别的命名实体结果,{'LOCATION':[('北京',0,1)]}
            slotInfo: 当前意图的槽位信息
            id: 用户id

        Returns:
            返回用户可用的命名实体类型
            {'user_number':[('500',1,3)]}
        """
        receiveEntityType=[]
        for slotitem in slotInfo.slot:
            receiveEntityType.append(slotitem['receiveEntityType'])

        userMapingDictResult = LoadData().loadUserSystemEntityData(userId=id, receiveEntityType=receiveEntityType)

        mappedEntity = {}
        for ent in entities:
            #print('ent',ent)
            if ent in userMapingDictResult:
                newEnt = userMapingDictResult[ent]
            else:
                newEnt = ent

            #print('newEnt',newEnt)

            if newEnt not in mappedEntity:
                mappedEntity[newEnt] = []

            for item in entities[ent]:
                mappedEntity[newEnt].append(item)

        return mappedEntity


    def initModels(self):
        '''
        加载保存了的BiLSTM+CRF模型
        :return:model,sess
        '''

        word2id = read_dictionary(os.path.join('utils/dialogManager/model/NER/word2id.pkl'))
        embeddings = random_embedding(word2id, 300)
        model_path = 'utils/dialogManager/model/NER/1524105856/checkpoints/'
        model = BiLSTM_CRF(embeddings, tag2label, word2id)
        model.build_graph()
        saver = tf.train.Saver()
        ckpt_file = tf.train.latest_checkpoint(model_path)
        sess = tf.Session()
        saver.restore(sess, ckpt_file)

        return model, sess

    def NERByModel(self,sent):
        demo_sent = list(sent.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = self.model.demo_one(self.sess, demo_data)
        entityDic = entityLinking(tag, demo_sent)
        print('模型输出命名实体结果:',entityDic)

        return entityDic

    def NERByDic(self,sent,id):
        '''

        :param sent:
        :return:res = {LOCATION:[('平安一账通'，0，4)]}
        '''

        res = {}
        entityDict = LoadData().loadUserDictEntityData(userId=id)
        for entName in entityDict:


            j = len(sent)
            while j>=0:
                i = 0
                while i<j:
                    _word = sent[i:j]
                    if _word in entityDict[entName]:
                        if entName not in res:
                            res[entName] = []
                        res[entName].append((_word,i,j-1))
                        j = i+1
                        break
                    i = i + 1
                j = j - 1
        return res


    def NERByRules(self,sent,id):
        '''
        根据用户配置的规则进行命名实体识别
        :return:res = {LOCATION:[('北京'，0，1)]}
        '''
        #print('sent: ',sent)

        self.ruleEntitis, self.rules = self.loadRules(userId=id)
        entities = {}

        for i in range(len(self.rules)):
            p = self.rules[i]
            res = re.findall(p,sent)
            #print(p)
            #print(res)
            if res!= []:
                for j in range(len(self.ruleEntitis[i])):
                    entName = self.ruleEntitis[i][j]
                    if len(self.ruleEntitis[i]) > 1:
                        _ent = res[0][j]
                    else:
                        _ent = res[0]

                    #print(i,j,_ent)
                    if entName not in entities:
                        entities[entName] = []
                    #print(_ent,sent)


                    _tmp = re.search(_ent,sent).span()
                    entities[entName].append((_ent,_tmp[0],_tmp[1]-1))


        return entities








    def loadRules(self,userId):

        '''
        加载用户配置的规则，并把它们转换成正则表达式
        :return:Rules = ['','',]
        '''

        # path = '/home/hairui/gitProject/newServer/NLPResearch/030_Experimental/dialogManager/dialogManagerServerDev/utils/dialogManager/data/userTemplate.txt'
        # # path = 'utils/dialogManager/data/userTemplate.txt'
        # dom = parse(path)
        # root = dom.documentElement
        # templateList = root.getElementsByTagName('template')


        templateList = []
        # _userRuleEntityResult = userRuleEntity.objects.all()
        _userRuleEntityResult = userRuleEntity.objects.filter(userId=userId)
        try:

            for userRuleEtyItem in _userRuleEntityResult:
                ruleTemplates = userRuleEtyItem.ruleTemplate
                for templateItem in ruleTemplates:
                    # print(templateItem.template)
                    templateList.append(templateItem.template)
        except Exception as e:
            print(e)


        ruleList = []
        entList = []

        for item in templateList:
            # if item.nodeType != item.ELEMENT_NODE:
            #     continue
            p = '\([^()]*\)'
            # ruleData = item.firstChild.data
            ruleData = item
            entities = re.findall(p,ruleData)
            tmp = []
            _norRule = ruleData
            for ent in entities:

                _ent = ent.replace('(','').replace(')','')
                tmp.append(_ent)

                if _ent == "DATE":
                    _norRule = re.sub('\(DATE\)','(.{2,12})',_norRule)
                elif _ent == 'PHONE':
                    _norRule = re.sub('\(PHONE\)','(\\d{8,11})',_norRule)
                elif _ent == 'PERSON':
                    _norRule = re.sub('\(PERSON\)','(.{2,4})',_norRule)
                elif _ent == 'LOCATION':
                    _norRule = re.sub('\(LOCATION\)','(.+?)',_norRule)
                else:
                    _norRule = re.sub('\('+_ent+'\)','(.+?)',_norRule)

            _norRule = _norRule.replace("*", ".*")
            entList.append(tmp)
            ruleList.append(_norRule)


        return entList,ruleList








        #print(entList)
        #print(ruleList)


        pass



    def mergeNamedEntities(self,sent,entitiesByModel,entitiesByDict):

        '''
        将模型识别的命名实体和字典识别的命名实体进行合并，优先级：规则>字典>模型
        :param entitiesByModel:
        :param entitiesByDict:
        :return:
        '''

        entitiyDict = {}



        #检测两种方法识别结果是否有冲突
        flagList = [0]*len(sent)

        #复制字典识别结果
        for entName in entitiesByDict:
            for item in entitiesByDict[entName]:
                #print(item)
                #print(item[1],item[2])
                for i in range(item[1],item[2]+1):
                    flagList[i] = 1


        _entitiesByModel = {}

        #模型识别结果如果和字典识别结果有重复或者冲突，则删除模型识别结果
        for entName in entitiesByModel:
            _entitiesByModel[entName] = []
            for i in range(len(entitiesByModel[entName])):
                startIndex = entitiesByModel[entName][i][1]
                endIndex = entitiesByModel[entName][i][2]
                flag = 1
                for j in range(startIndex,endIndex+1):
                   #print(j,flagList[j])
                    if flagList[j] == 1:
                        flag = 0
                if flag == 1:
                    _entitiesByModel[entName].append(entitiesByModel[entName][i])

        entitiesByModel = _entitiesByModel
        #print('entitiesByModel',entitiesByModel)

        #合并识别结果
        for entName in entitiesByDict:
            entitiyDict[entName] = entitiesByDict[entName]
            if entName in entitiesByModel:

                '''
                print('entityDict[entName]')
                print(entitiyDict[entName])
                print('entitiesByModel[entName]')
                print(entitiesByModel[entName])
                '''
                if entitiesByModel[entName] == []:
                    continue
                entitiyDict[entName].extends(entitiesByModel[entName])

        for entName in entitiesByModel:
            if entName not in entitiyDict:
                entitiyDict[entName] = entitiesByModel[entName]


        #print(entitiyDict)
        return entitiyDict



if __name__ == '__main__':
    myNERProcessor = NERProcessor()
    # myNERProcessor.NERByDic('我想买一张从上海到深圳的机票')
    myNERProcessor.loadRules()