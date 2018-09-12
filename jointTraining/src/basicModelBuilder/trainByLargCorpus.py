# -*- coding: utf-8 -*-
# @Time : 2018/9/4 1:58 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : trainByLargCorpus.py
# @Software: PyCharm
# @desc:


from keras.utils import to_categorical

from src.basicModelBuilder.semanticMatchLayer import ComparedAggFactor

from src.util.modelTrainer import ModelTrainer

from src.dataConstructor.dataProcessor import DataProcessor

from config import *

class TrainByLargeCorpus(object):
    """ 基于大量语料训练模型，用于以后迁移训练的基础模型

    Attributes:
        basicModelEpochNum: 迭代次数
        basicModelBatchSize: batch_size
        model: 模型结构
        basicModelSavePath: 模型存放路径
        basicModelTrainData: 用于训练基本模型的数据

    """

    def __init__(self):
        self.basicModelEpochNum = modelParamSetting.basicModelEpochNum
        self.basicModelBatchSize = modelParamSetting.basicModelBatchSize
        self.model = ComparedAggFactor().build()
        self.basicModelSavePath = sysParamSetting._trainedModelByCAFE
        self.basicModelTrainData = sysParamSetting._basicModelTrainData
        pass

    def trainModelByLargCorpus(self):
        """ 训练模型,保存在sysParamSetting._basicModelTrainData中
        Returns:

        """

        train = ModelTrainer(self.model,
                             self.basicModelSavePath,
                             self.basicModelEpochNum,
                             self.basicModelBatchSize)  # 模型训练

        # 构造训练样本
        datasetCreator = DataProcessor()
        contextA, contextB, tlabel, charA, charB = datasetCreator.trainDataSetCreator(self.basicModelTrainData)

        tlabel = to_categorical(tlabel,num_classes=2)


        #  训练模型
        train.trainModel({"senA": contextA, "senB": contextB, "CharA": charA, "CharB": charB}, tlabel)
