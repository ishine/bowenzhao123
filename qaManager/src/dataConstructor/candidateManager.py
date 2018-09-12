# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:24 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : candidateManager.py
# @Software: PyCharm
# @desc:

import numpy as np
import pandas as pd
import os
from src.dataConstructor.dataProcessor import DataProcessor
from src.dataConstructor.getUserData import GetUserData
from config import *

class CandidateManager(object):
    """ 根据问句所属主题，返回该主题下所有的数据

    Attributes:

        dataProcessor: 调用数据onehot编码模块
        targetClassifyDataFile: 用于分类的文档存放路径
        targetData: 分类文档{'sentence':所属主题}，用于筛选候选集
    """

    def __init__(self):

        self.dataProcessor = DataProcessor()
        self.targetClassifyDataFile = dataParamSetting.targetClassifyDataFile
        if not os.path.exists(self.targetClassifyDataFile):
            getuserdata = GetUserData()
            getuserdata.createLabledTargetData(self.targetClassifyDataFile)
        self.targetData = pd.read_csv(self.targetClassifyDataFile)

    def createCandidate(self,text1,text2):
        """ 构造可训练/测试的数据集

        Args:
            text1: 一个列表(一条用户语句)或者一组列表(语句A)
            text2: 一组列表(语句B)
            label: 标签，表示相似/不相似
        Return: 数据框dataframe {'text1':句子A,
                                 'text2':句子B,
                                 'label':相似(1)/不相似(0)}

        """
        # 判断是一个句子还是一组测试语句
        if isinstance(text2, pd.DataFrame):
            sequenceData = pd.DataFrame(data={'text1': [text1] * text2.shape[0], 'text2': text2['text']})

        elif isinstance(text2,list):
            sequenceData = pd.DataFrame(data={'text1':[text1]*len(text2),'text2':text2})

        else:
            sequenceData = pd.DataFrame(data={"text1": [text1], "text2": [text2]})

        text1 = self.dataProcessor.sentence2id(np.array(sequenceData['text1']), self.dataProcessor.word2id)
        text1WordID, text1SeqLenList = self.dataProcessor.padSequences(text1)

        text2 = self.dataProcessor.sentence2id(np.array(sequenceData['text2']), self.dataProcessor.word2id)
        text2WordID, text2SeqLenList = self.dataProcessor.padSequences(text2)

        charID1 = self.dataProcessor.sentence2id(np.array(sequenceData['text1']), self.dataProcessor.char2id)
        charID1, text1SeqLenList = self.dataProcessor.padSequences(charID1)

        charID2 = self.dataProcessor.sentence2id(np.array(sequenceData['text2']), self.dataProcessor.char2id)
        charID2, text1SeqLenList = self.dataProcessor.padSequences(charID2)

        return np.asarray(text1WordID), np.asarray(text2WordID), np.asarray(charID1), np.asarray(charID2)



    def findAllCandidate(self,label):
        """ 返回该主题下所有的数据

        Args:
            label: init:主题
            dataWithinClass: 数据
        Return:
            主题下所有的数据:[list1,list2,list3....]

        """
        ans = []

        for i in range(len(self.targetData)):
            if int(self.targetData['label'][i]) == int(label):
                ans.append(self.targetData['text'][i])
        return ans
