# -*- coding: utf-8 -*-
# @Time : 2018/9/7 3:17 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : jointTaskModelBuilder.py
# @Software: PyCharm
# @desc:

import keras.backend as K
from keras.models import Model
from keras.layers import Input, Dense, concatenate
from keras.layers.core import Dropout, Lambda, Permute
from keras.layers.normalization import BatchNormalization
from keras.layers.embeddings import Embedding
from keras.layers.wrappers import Bidirectional, TimeDistributed
from keras.layers.recurrent import LSTM,GRU
from src.basicModelBuilder.semanticMatchLayer import ComparedAggFactor
from config import *
from src.dataConstructor.dataProcessor import DataProcessor
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint


class JointTask(object):
    """  基于基础模型构造联合训练模型
    来源文章: "Adversarial Multi-task Learning for Text Classification"

    Attributes:
        transferbatchSize: batch_size
        dataProcessor: 加载数据预处理模块
        basemodelA: 预训练模型(用于接收源数据，仅使用第一层BiLSTM以及其之前的层)
        basemodelB: 预训练模型(与baseodelA相似，用于接收目标数据，仅使用第一层BiLSTM以及其之前的层)
        trainedModelByCAFE: 预训练模型存放路径
        tranferepochNum: 训练迭代次数
        jiontTaskModelPath: 联合训练保存路径
        trainModelData: 目标数据
        basicModelTrainData: 源数据
        cellNum: LSTM units
        senMaxLen: 序列最大长度
        dropout: dropout

    """

    def __init__(self):
        self.transferbatchSize = jointTaskParamSetting.jointTaskbatchSize
        self.dataProcessor = DataProcessor()
        self.model = ComparedAggFactor(False)
        self.basemodelA = self.model.build()
        self.basemodelB = self.model.build()
        self.trainedModelByCAFE = sysParamSetting._trainedModelByCAFE
        self.tranferepochNum = jointTaskParamSetting.jointTaskepochNum
        self.jiontTaskModelPath = jointTaskParamSetting.jointTaskModelPath
        self.trainModelData = dataParamSetting.trainModelData
        self.basicModelTrainData = sysParamSetting._basicModelTrainData
        self.cellNum = self.model.cellNum
        self.senMaxLen = sysParamSetting._senMaxLen
        self.dropout = jointTaskParamSetting.jointTaskdropout
        if os.path.exists(self.trainedModelByCAFE):
            self.basemodelA.load_weights(self.trainedModelByCAFE)
            self.basemodelB.load_weights(self.trainedModelByCAFE)
        else:
            raise Exception('没有预训练的模型！')
        pass

    def sumloss(self,y_true,y_pred):
        """ 绝对值损失函数

        Args:
            y_true: 真实值
            y_pred: 预测值
        Return: 损失值
        """

        return K.sum(abs(y_true-y_pred),axis=-1)

    def diff_loss(self,inputs):
        """  计算协方差矩阵的Frobenius范数

        Args:
            inputs: 源数据/目标数据的共享层相应输出和独有层相应输出
        Return: 协方差矩阵的Frobenius范数
        """

        size = K.shape(inputs)[-1].value//2
        task_feat = inputs[:, 0:size]
        shared_feat = inputs[:, size:2 * size]

        shared_feat -= K.mean(shared_feat, axis=0)
        task_feat -= K.mean(task_feat, axis=0)

        shared_feat = K.l2_normalize(shared_feat, axis=1)
        task_feat = K.l2_normalize(task_feat, axis=1)

        correlation_matrix = K.dot(task_feat, K.permute_dimensions(shared_feat, pattern=[1, 0]))
        cost = K.sum(K.square(correlation_matrix), axis=-1)*0.1

        return K.expand_dims(cost,axis=1)


    def build(self):
        """  构造联合训练模型

        模型框架采用:embedding+BiLSTM语义表征+全连接层compare self-attention和attention +BiLSTM Align + Dense layer + softmax
        其中embedding和第一个BiLSTM和comapre层共享，且模型参数不可训练。
        从compared之后，分为三个BiLSTM, 分为为源数据独享，源数据和目标数据共享，目标数据独享。
        模型损失包括: 基于任务的损失，adversary损失，基于协方差的损失
        Return: 联合训练模型
        """
        senA = Input(shape=(self.senMaxLen,), name='senA')
        senB = Input(shape=(self.senMaxLen,), name='senB')
        CharA = Input(shape=(self.senMaxLen,), name='CharA')
        CharB = Input(shape=(self.senMaxLen,), name='CharB')

        senA1 = Input(shape=(self.senMaxLen,), name='senA1')
        senB1 = Input(shape=(self.senMaxLen,), name='senB1')
        CharA1 = Input(shape=(self.senMaxLen,), name='CharA1')
        CharB1 = Input(shape=(self.senMaxLen,), name='CharB1')

        i = 0
        for layerA, layerB in zip(self.basemodelA.layers,self.basemodelB.layers):
            # 固定matching layer前面的层的权重
            if i < 26:
                layerA.trainable = False
                layerB.trainable = False
            i+=1
            print(layerA.name)

        mergedVectorA = self.basemodelA.get_layer('mergedVectorA').output
        mergedVectorB = self.basemodelA.get_layer('mergedVectorB').output

        _mergedVectorA = self.basemodelB.get_layer('mergedVectorA').output
        _mergedVectorB = self.basemodelB.get_layer('mergedVectorA').output

        cross = self.basemodelA.get_layer('cross')
        cross.trainable = False

        mergedVectorA = TimeDistributed(cross)(mergedVectorA)
        mergedVectorA = TimeDistributed(BatchNormalization())(mergedVectorA)

        mergedVectorB = TimeDistributed(cross)(mergedVectorB)
        mergedVectorB = TimeDistributed(BatchNormalization())(mergedVectorB)

        _mergedVectorA = TimeDistributed(BatchNormalization())(_mergedVectorA)
        _mergedVectorA = TimeDistributed(cross)(_mergedVectorA)

        _mergedVectorB = TimeDistributed(BatchNormalization())(_mergedVectorB)
        _mergedVectorB = TimeDistributed(cross)(_mergedVectorB)

        # 构造共享BiLSTM context layer

        sharedBiLSTM = self.basemodelA.get_layer('bidirectional_2')
        special1BiLSTM = self.basemodelA.get_layer('bidirectional_2')

        special2BiLSTM = Bidirectional(LSTM(units=jointTaskParamSetting.SharedTaskLSTMUnits,
                                           return_sequences=False,
                                           dropout=self.dropout,
                                           recurrent_dropout=self.dropout))

        # ********************************************************************
        sharedLSTMSenA = sharedBiLSTM(mergedVectorA)


        sharedLSTMSenB = sharedBiLSTM(mergedVectorB)

        _sharedLSTMSenA = sharedBiLSTM(_mergedVectorA)

        _sharedLSTMSenB = sharedBiLSTM(_mergedVectorB)

        # *********************************************************************
        specialLSTMSenA = special1BiLSTM(mergedVectorA)

        specialLSTMSenB = sharedBiLSTM(mergedVectorB)

        # *********************************************************************
        _specialLSTMSenA = special2BiLSTM(_mergedVectorA)

        _specialLSTMSenB = special2BiLSTM(_mergedVectorB)

        # **********************************************************************

        # 合并生成不同task的input

        task1Input = concatenate([specialLSTMSenA, specialLSTMSenB, sharedLSTMSenA, sharedLSTMSenB], axis=-1,
                                 name="taskInput1")

        task2Input = concatenate([_specialLSTMSenA, _specialLSTMSenB, _sharedLSTMSenA, _sharedLSTMSenB], axis=-1,
                                 name="taskInput2")

        # *************************************************=
        SpecialTask1 = Dense(jointTaskParamSetting.SpecialTaskAUnits, activation="relu")(task1Input)
        SpecialTask1 = Dropout(self.dropout)(SpecialTask1)
        SpecialTask1 = BatchNormalization()(SpecialTask1)

        SpecialTask2 = Dense(jointTaskParamSetting.SpecialTaskBUnits, activation="relu")(task2Input)
        SpecialTask2 = Dropout(self.dropout)(SpecialTask2)
        SpecialTask2 = BatchNormalization()(SpecialTask2)

        # 构造一个分类器，用于判断接收的数据来自于源数据还是目标数据。
        # 详见论文：Adversarial Multi-task Learning for Text Classification中adversarial loss部分
        sharedDenseLayer = Dense(units=jointTaskParamSetting.SharedTaskUnits,activation='relu')


        SharedTask1 = sharedDenseLayer(concatenate([sharedLSTMSenA,sharedLSTMSenB],axis=-1,name='share1Input'))
        SharedTask1 = Dropout(self.dropout)(SharedTask1)
        SharedTask1 = BatchNormalization()(SharedTask1)


        SharedTask2 = sharedDenseLayer(concatenate([_sharedLSTMSenA,_sharedLSTMSenB],axis=-1,name='share2Input'))
        SharedTask2 = Dropout(self.dropout)(SharedTask2)
        SharedTask2 = BatchNormalization()(SharedTask2)

        # *************************************************************

        # feature1用于计算 task1 的loss; task1对应于原任务
        feature1 = concatenate([SpecialTask1, SharedTask1], axis=-1)
        logits1 = Dense(2, activation="softmax",name="taskAloss")(feature1)

        # feature2用于计算 task2的 loss； task2对应于目标任务
        feature2 = concatenate([SpecialTask2, SharedTask2], axis=-1)
        logits2 = Dense(2, activation="softmax",name="taskBloss")(feature2)

        # 计算GAN损失
        ganLayer = Dense(2,activation='softmax',name='GAN')
        tasklabel1 = ganLayer(SharedTask1)
        tasklabel2 = ganLayer(SharedTask2)

        # 计算基于协方差矩阵的loss
        diff_loss = Lambda(self.diff_loss,name="diff_loss")

        dif1 = diff_loss(task1Input)
        dif2 = diff_loss(task2Input)

        # 参数说明：
        # SpecialTask1: 任务1 special task的output
        # SpecialTask2: 任务2 special task的output
        # SharedTaks1: 任务1 shared task的output
        # SharedTaks2: 任务2 shared task的output
        # logits1: 任务1分类标签
        # logits2: 任务2分类标签

        myModel = Model(inputs=[senA,senB,CharA,CharB,senA1,senB1,CharA1,CharB1],outputs=[logits1,logits2,tasklabel1,tasklabel2,dif1,dif2])

        myModel.compile(optimizer="adam",
                        loss={"taskAloss":"mse",
                              "taskBloss":"mse",
                              "GAN":"mse",
                              "diff_loss":self.sumloss},
                        loss_weights={"taskAloss":1.,
                                      "taskBloss":.2,
                                      "GAN":.5,
                                      "diff_loss":1},
                        metrics=["accuracy"])

        print(myModel.summary())
        return myModel


    def trainModel(self):
        """  用于训练模型

        """

        model = self.build()
        # 读入source data
        traintext1, traintext2, trainLabel,slabel,Char1, Char2 = self.dataProcessor.trainDataSetCreator(self.basicModelTrainData)

        # 读入target data
        contextA, contextB, tlabel, charA, charB = self.dataProcessor.trainDataSetCreator(self.trainModelData)


        early_stopping = EarlyStopping(monitor='val_loss', patience=8)
        checkpoint = ModelCheckpoint(
            filepath='{first}{second}.h5'.format(first=self.jiontTaskModelPath, second=self.jiontTaskModelPath),
            monitor='val_loss',
            save_best_only=True,
            save_weights_only=True,
            mode='auto')

        # 划分验证集和训练集

        # ********************************************************************
        # 从source task随机抽选一定size的数据集
        ind = np.random.choice(len(traintext1), size=30 * contextA.shape[0], replace=True)

        # 训练集index
        # target数据
        train_index = np.random.choice(contextA.shape[0], size=int(contextA.shape[0] * .8), replace=True)
        # source数据
        train_index1 = np.random.choice(ind, size=30 * int(contextA.shape[0] * .8), replace=True)

        # 验证集index
        # target数据
        val_index = np.array(list(filter(lambda x: x not in train_index, np.arange(contextA.shape[0]))))
        # source数据
        val_index1 = np.array(list(filter(lambda x: x not in train_index1, ind)))


        # *******************************************************************
        # 构造target task训练集
        train_contextA, train_contextB, train_tlabel, train_charA, train_charB = \
            contextA[train_index], contextB[train_index], tlabel[train_index],charA[train_index], charB[train_index]

        # 复制target数据
        train_contextA, train_contextB, train_tlabel = \
            train_contextA.repeat(30, axis=0), train_contextB.repeat(30,axis=0), train_tlabel.repeat(30, axis=0)

        train_charA, train_charB = train_charA.repeat(30, axis=0), train_charB.repeat(30, axis=0)

        # shuffle
        index1 = np.random.permutation(len(train_contextA))
        train_contextA, train_contextB, train_tlabel, train_charA, train_charB = \
            train_contextA[index1],train_contextB[index1],train_tlabel[index1], train_charA[index1], train_charB[index1]

        # 这个仅仅是为了方便计算diff_loss(基于协方差F范数的loss)
        train_diff1 = np.zeros(shape=(train_contextA.shape[0]))


        # *******************************************************************
        # 构造source task训练集
        train_train1, train_train2, train_char1, train_char2, train_slabel, train_tasklabel1, train_tasklabel2 = \
            self.dataProcessor.genCombineData(traintext1, traintext2, Char1, Char2, trainLabel, train_index1)


        # *******************************************************************
        # 构造target task验证集
        val_contextA, val_contextB, val_tlabel, val_charA, val_charB = \
            contextA[val_index], contextB[val_index], tlabel[val_index], charA[val_index], charB[val_index]

        val_contextA, val_contextB, val_tlabel = \
            val_contextA.repeat(30, axis=0), val_contextB.repeat(30, axis=0), val_tlabel.repeat(30, axis=0)

        val_charA, val_charB = val_charA.repeat(30, axis=0), val_charB.repeat(30, axis=0)

        # shuffle
        index2 = np.random.permutation(len(val_contextA))
        val_contextA, val_contextB, val_tlabel, val_charA, val_charB = \
            val_contextA[index2], val_contextB[index2],val_tlabel[index2], val_charA[index2], val_charB[index2]

        val_diff1 = np.zeros(shape=(val_contextA.shape[0]))

        # ********************************************************************
        # 构造source task验证集

        val_train1, val_train2, val_char1, val_char2, val_slabel, val_tasklabel1, val_tasklabel2 = \
            self.dataProcessor.genCombineData(traintext1, traintext2, Char1, Char2, trainLabel, val_index1)

        # *********************************************************************
        # 构造验证集
        X = [val_train1, val_train2,val_char1,val_char2,val_contextA, val_contextB,val_charA,val_charB]
        y = [val_slabel, val_tlabel, val_tasklabel1, val_tasklabel2, val_diff1, val_diff1]
        validation_data = (X, y)

        # *********************************************************************
        # 模型训练
        model.fit({'senA': train_train1, 'senB': train_train2, 'CharA':train_char1, 'CharB':train_char2,
                   'senA1': train_contextA, 'senB1': train_contextB, 'CharA1':train_charA, 'CharB1':train_charB},
                  [train_slabel, train_tlabel, train_tasklabel1, train_tasklabel2, train_diff1, train_diff1],
                  epochs=self.tranferepochNum, shuffle=True, batch_size=self.transferbatchSize,
                  validation_data=validation_data,callbacks=[early_stopping, checkpoint])
