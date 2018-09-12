# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:08 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : topicClassify.py
# @Software: PyCharm
# @desc:

import fasttext
from src.util.util import processText

from src.dataConstructor.dataSetCreate import DataSetCreator

from config import *

class TopicClassify(object):
    """ 用户输入语句主题识别
    Attributes:
            classifer: 分类模型
            trainClassifierFile: 分类模型训练数据
            w2vdim: 词向量维度
            trainClassifierEpoch: 分类模型迭代次数
            trainw2vepoch: 词向量模型训练时的迭代次数
            saveVectorFile: 词向量存放文件名，不加.vec
            classifierModel: 分类模型保存位置
    """
    def __init__(self):

        self.classifier = None
        self.combinedDataSaveFile = dataParamSetting.targetClassifyDataFile
        self.trainClassifierFile = classifyParamSetting.trainClassifierFile
        self.w2vdim = classifyParamSetting.w2vdim
        self.trainClassifierEpoch = classifyParamSetting.trainClassifierEpoch
        self.trainw2vepoch = classifyParamSetting.trainw2vepoch
        self.saveVectorFile = classifyParamSetting.saveVectorFile
        self.classifierModel = classifyParamSetting.classifierModel

        pass

    def createClassifier(self):
        """ 构造并训练fasttext模型，保存到'/classifier.model.bin'中

        Return:
        """

        dataSetCreator = DataSetCreator()

        if not os.path.exists(self.saveVectorFile + '.vec'):
            fasttext.cbow(self.combinedDataSaveFile,
                          self.saveVectorFile,
                          dim=self.w2vdim,
                          epoch=self.trainw2vepoch)

        if not os.path.exists(self.trainClassifierFile):
            dataSetCreator.dataSetforClassify(self.trainClassifierFile)

        self.classifier = fasttext.supervised(self.trainClassifierFile,
                                        self.classifierModel,
                                        dim = self.w2vdim,
                                        epoch = self.trainClassifierEpoch,
                                        label_prefix = '__label__',
                                        pretrained_vectors=self.saveVectorFile+'.vec')


    def load_model(self):
        if not os.path.exists(self.classifierModel+'.bin'):
            raise Exception('没有分类模型！')
        self.classifier = fasttext.load_model(self.classifierModel+'.bin',label_prefix='__label__')

    def findClass(self,sentence):
        """ 载入分类模型，确定用户输入语句的主题

        Args:
            sentence: 列表：用户输入语句
        Return:
            init:所属主题
        """

        # 判断输入是否已经经过分词处理
        if isinstance(sentence,str):
            sentence = processText(sentence)

        # 判断是否存在分类模型
        if not os.path.exists(self.classifierModel+'.bin'):
            self.createClassifier()

        # 判断是否已加载预训练模型
        if self.classifierModel is None:
            self.load_model()

        return self.classifier.predict([sentence])[0][0]
