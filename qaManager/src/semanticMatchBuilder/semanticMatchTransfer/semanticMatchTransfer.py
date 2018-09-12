# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:07 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : semanticMatchTransfer.py
# @Software: PyCharm
# @desc:

import pandas as pd
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.backend.tensorflow_backend import set_session
import os
from sklearn.metrics import f1_score, precision_score, recall_score
from keras.layers import Input, Dense, concatenate
from keras.layers.core import Dropout, Lambda, Permute

from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.utils import to_categorical

from src.semanticMatchBuilder.semanticMatch.comAggFact.comAggFact import ComparedAggFactor

from src.util.modelTrainer import ModelTrainer
from src.util.modelEvaluator import Evaluator

from src.dataConstructor.dataSetCreate import DataSetCreator

from config import *



class TransferModel(object):
    """
    使用迁移学习的方法，将预训练的模型用于小数据集。
    Attributes:
        transferbatchSize: batch_size大小
        model: 迁移模型初始化
        basemode: 预训练模型
        trainedModelByCAFE: 预训练模型载入位置
        tranferepochNum: 迁移模型迭代次数
        transferModelPath: 迁移模型存放位置
        transferModelTrainfile: 训练数据存放路径
        transferModelTestfile: 测试数据存放路径

    """

    def __init__(self,test=True):

        self.transferbatchSize = transferParamSetting.transferbatchSize
        self.model = ComparedAggFactor(False)
        self.basemodel = self.model.build()
        self.trainedModelByCAFE = sysParamSetting._trainedModelByCAFE
        self.tranferepochNum = transferParamSetting.tranferepochNum
        self.transferModelPath = transferParamSetting.transferModelPath
        self.transferModelTrainfile = dataParamSetting.transferModelTrainfile
        self.transferModelTestfile = dataParamSetting.transferModleTestfile
        self.trainTransferModelData = dataParamSetting.trainTransferModelData
        self.transferDenseLayerUnits = transferParamSetting.transferDenseLayerUnits
        self.test = test

        if os.path.exists(self.trainedModelByCAFE):
            self.basemodel.load_weights(self.trainedModelByCAFE)
        else:
            raise Exception('没有预训练的模型！')

    def transferModelBuilder(self):
        """

        将预训练好的模型的embedding层，第一个BiLSTM层固定，matching layer和第二个BiLSTM层的权重进行更新，全连接层的units减小到16
        Returns: 迁移的模型结构

        """

        for i,layer in enumerate(self.basemodel.layers):
            # 固定matching layer前面的层的权重
            if i < 26:
                layer.trainable = False # False

        # 取出经第二个Bilstm层输出后的结果
        Vec = self.basemodel.get_layer("Vec").output

        # 重新构建全连接层
        dense = Dense(self.transferDenseLayerUnits, activation="relu", name="dense")(Vec)
        dense = Dropout(.4)(dense)
        dense = BatchNormalization()(dense)

        outputlayer = Dense(2, activation="softmax", name="outputlayer")(dense)

        model = Model(inputs = self.basemodel.input,outputs=outputlayer)

        model.compile(optimizer="adam",loss="binary_crossentropy",metrics=["accuracy"])

        return model

    def trainTransferModel(self):
        """ 训练模型
        Returns:

        """

        model = self.transferModelBuilder()
        train = ModelTrainer(model,
                             self.transferModelPath,
                             self.tranferepochNum,
                             self.transferbatchSize)  # 模型训练

        # 构造训练样本
        datasetCreator = DataSetCreator()

        contextA, contextB, tlabel, charA, charB = datasetCreator.trainDataSetCreator(self.transferModelTrainfile)
        tlabelCategory = to_categorical(tlabel, num_classes=2)

        testA,testB,testlabel,testCharA,testCharB = datasetCreator.trainDataSetCreator(self.transferModelTestfile)
        testlabel = to_categorical(testlabel,num_classes=2)

        validation_data = ([testA,testB,testCharA,testCharB],testlabel)
        #  训练验证模型
        train.trainModel({"senA":contextA,"senB":contextB,"CharA":charA,"CharB":charB},tlabelCategory,validation_data)
                    
        #  测试模型
        evaluate = Evaluator(model)

        evaluate.basicEvaluator({'senA': contextA, 'senB': contextB, 'CharA': charA, 'CharB': charB},tlabel)

        if os.path.exists(self.transferModelPath):
            os.remove(self.transferModelPath)
        contextA, contextB, tlabel, charA, charB = datasetCreator.trainDataSetCreator(self.trainTransferModelData)
        tlabel = to_categorical(tlabel, num_classes=2)
        train.trainModel({"senA": contextA, "senB": contextB, "CharA": charA, "CharB": charB}, tlabel)
