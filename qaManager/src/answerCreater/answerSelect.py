# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:19 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : answerSelect.py
# @Software: PyCharm
# @desc:

import pandas as pd
import numpy as np

from src.semanticMatchBuilder.topicClassify.topicClassify import TopicClassify
from src.semanticMatchBuilder.semanticMatchTransfer.semanticMatchTransfer import TransferModel

from src.dataConstructor.candidateManager import CandidateManager

from config import *

from src.util.util import processText


class AnswerSelect(object):
    """ 获取用户输入问句，返回最相思的答案

    Attributes:
        modelFile: 模型存放路径
        getManage: 调用获取候选集模块
        model: 初始化模型
        topicClassify: 调用分类模块

    """

    def __init__(self):

        self.modelFile = transferParamSetting.transferModelPath
        self.getManager = CandidateManager()
        self.model = TransferModel().transferModelBuilder()
        self.model.load_weights(self.modelFile)
        self.topicClassify = TopicClassify()
        self.topicClassify.load_model()
        pass

    def getCandidateSet(self,question):
        """ 获取用户问句，经过分词后，调用candidateManager，构造候选集

        Args:
            question: 字符串：用户输入问句
        Return:
            数据框dataframe:{'text1': 用户问句,'text2':候选问句}

        """

        # 分类,获取类标
        question = processText(question)
        label = self.topicClassify.findClass(question)
        print('属于主题:',label)
        # 获取类别下的所有候选集

        candidateData = self.getManager.findAllCandidate(label)

        text1,text2,char1,char2 = self.getManager.createCandidate(question,candidateData)
        candidateset = {'senA':text1,'senB':text2,'CharA':char1,'CharB':char2}

        return candidateset,candidateData

    def AnswerSimilarity(self,candidate):
        """ 加载模型，输入candidate, 返回相似度最高的问句

        Args:
            candidate: 数据框dataframe:候选集 {'text1': 用户问句,'text2':候选问句}
        Return:
            list:语句相似度列表

        """
        # 输入到模型中测试
        result = self.model.predict(candidate)
        return result


    def getAnswer(self,question):
        """ 根据用户输入语句，返回最相似的答案

        Args:
            question: 字符串：用户输入问句
        Return:
            str: 最相似的答案
        """
        candidate,candidateText = self.getCandidateSet(question)
        result = self.AnswerSimilarity(candidate)
        # 按照相似度排序，获取最相似的答案
        result = np.array(result)[:, 1]
        top1 = np.argsort(-result)[:1][0]
        print(top1)
        print('最可能的答案：')
        print(candidateText[top1])