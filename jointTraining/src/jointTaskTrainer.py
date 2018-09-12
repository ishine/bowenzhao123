# -*- coding: utf-8 -*-
# @Time : 2018/9/7 7:26 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : jointTaskTrainer.py
# @Software: PyCharm
# @desc:

import numpy as np
import pandas as pd
from config import *
from src.dataConstructor.dataProcessor import DataProcessor
from keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard
from keras.backend.tensorflow_backend import set_session
import os
from sklearn.metrics import f1_score, precision_score, recall_score
import tensorflow as tf
from keras.utils import to_categorical


class JointTaskTrainer(object):

    def __init__(self):
        self.dataProcessor = DataProcessor()
        # 判断是否有训练集/测试集
        self.jointTaskModelTrainfile = dataParamSetting.jointTaskModelTrainfile
        self.jointTaskModleTestfile = dataParamSetting.jointTaskModleTestfile
        self.trainTransferModelData = dataParamSetting.trainModelData
        if not os.path.exists(self.jointTaskModelTrainfile) or os.path.exists(self.jointTaskModleTestfile):
            raise Exception('没有训练/测试文件！')
        if not os.path.exists(self.trainTransferModelData):
            raise Exception('没有最终训练文件！')


    def generatInputData(self, textA, textB, CharA, CharB, slabel, index):

        train1 = textA[index]

        char1 = CharA[index]

        train2 = textB[index]

        char2 = CharB[index]

        starget = slabel[index]

        # 在column维度上拼接
        # target = np.concatenate([starget,tlabel],axis=-1)

        # 0号为source, 1号为target,在column维度上拼接

        taskLable1 = np.array([0] * len(index))
        taskLabel1 = to_categorical(taskLable1, 2)

        taskLabel2 = np.array([1] * len(index))
        taskLabel2 = to_categorical(taskLabel2, 2)

        # 与原先的分类标签在column维度拼接,先任务类别标签tasklabel,再特定任务下的分类标签label
        # trainLabel = np.concatenate([taskLabel,target], axis=-1)

        return train1, train2, char1, char2, starget, taskLabel1, taskLabel2

