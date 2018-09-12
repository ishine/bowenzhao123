# -*- coding: utf-8 -*-
# @Time : 2018/9/4 2:47 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : dataSetCreate.py
# @Software: PyCharm
# @desc:

import pandas as pd
import numpy as np

import jieba
import os
import re

from src.dataConstructor.dataProcessor import DataProcessor
from src.dataConstructor.getUserData import GetUserData, CreateInput

from config import *
from src.util.util import readData


class DataSetCreator(object):
    """  用于构造训练、测试样本、分类样本的生成
    Attributes:
        createInput: 调用数据生成的模块
        dataProcessor: 调用数据清洗和onehot编码模块
        srcFastClassifyFile: 分类模型存放路径
        trainW2VFile: 训练词向量模型的文件存放路径

    """

    def __init__(self):
        self.dataProcessor = DataProcessor()
        self.createInput = CreateInput()
        self.srcFastClassifyFile = self.createInput.targetDataFile
        self.trainW2VFile = self.createInput.combinedDataSaveFile
        # 判断是否有训练集/测试集
        if not os.path.exists(self.trainW2VFile):
            self.createInput.combineSourceTargetData()
        self.transferModelTrainfile = dataParamSetting.transferModelTrainfile
        self.transferModleTestfile = dataParamSetting.transferModleTestfile
        self.trainTransferModelData = dataParamSetting.trainTransferModelData
        if not os.path.exists(self.transferModelTrainfile):
            self.createInput.genRawInputData(self.transferModelTrainfile,self.transferModleTestfile,split=.7)
        # 判断是否有最终用于训练迁移模型的数据
        if not os.path.exists(self.trainTransferModelData):
            self.createInput.genRawInputData(self.trainTransferModelData,None,1)

    def trainDataSetCreator(self, sourcefile):
        """   生成模型训练的输入数据

        Args:
            sourcefile: 源文件
        Return:
            基于词向量的onehot编码
            基于字向量的onehot编码
            数据label
        """

        text1, text2, label = self.dataProcessor.genW2VDataforModelInput(sourcefile)
        char1, char2 = self.dataProcessor.genCharDataforModelInput(sourcefile)
        return text1,text2, label, char1, char2


    def dataSetforClassify(self,writefile):
        """  生成用于训练分类模型的文本

        Args:
            writefile: 写入文件，txt格式
        Return:
        """

        data = readData(self.srcFastClassifyFile)
        ans = []
        for sent_, label in zip(data['text'], data["label"]):
            sent_ = ''.join(re.findall(r'[\u4e00-\u9fa5]', sent_))
            cut_sent = jieba.cut(sent_)
            outline = '__label__' + str(label) + '\t' + ' '.join(cut_sent) + '\n'
            ans.append(outline)

        ans = np.array(ans)

        with open(writefile) as f:
            for line in ans:
                f.write(line)
