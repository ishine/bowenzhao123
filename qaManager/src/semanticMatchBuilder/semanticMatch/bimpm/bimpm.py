# -*- coding: utf-8 -*-
# @Time : 2018/9/4 1:47 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : bimpm.py
# @Software: PyCharm
# @desc:

from keras.models import Model
from keras.layers.core import Dropout, Lambda
from keras.layers import Input, Dense, concatenate
from keras.layers.embeddings import Embedding
from keras.layers.wrappers import Bidirectional, TimeDistributed
from keras.layers.recurrent import LSTM
from keras import backend as K
from keras.layers.normalization import BatchNormalization
from keras import initializers
from multi_perspective import MultiPerspective


from src.dataConstructor.dataProcessor import DataProcessor
from src.dataConstructor.embeddingInitiate import EmbeddingInit

from config import *


class BiMPM(object):
    """构造BiMPM模型
    来源文献: Bilateral Multi-Perspective Matching for Natural Language Sentences

    Attributes:
        dataProcessor: 数据预处理模块
        embeddingDim: embedding维度
        cellNum: Bilstm units
        mp_dim: mathicng layer输出维度
        dropout: dropout
        recurrent_dropout: recurrent_dropout
        dense_dim: 全连接层units
        model_type: 聚合方法，包括LSTM, maxpooling, meanpooling
        merge_type: 向量拼接方法
        myModel: 构造的模型

    """

    def __init__(self,loadw2v=True):

        self.dataProcessor = DataProcessor()
        self.embeddingDim = modelParamSetting.embeddingDim
        self.cellNum = modelParamSetting.cellNum
        self.mp_dim = modelParamSetting.mp_dim
        self.dropout = modelParamSetting.dropout
        self.recurrent_dropout = modelParamSetting.recurrent_dropout
        self.dense_dim = modelParamSetting.dense_dim
        self.model_type = modelParamSetting.model_type
        self.merge_type = modelParamSetting.merge_type
        self.loadw2v = loadw2v
        pass

    def maxpooling(self, inputs):
        """
        Args: 构造maxpooling层
            inputs:

        Returns: maxpooling后的向量

        """
        return K.max(inputs, axis=-1)

    def meanpooling(self, inputs):
        """

        Args: 构造meanpooling层
            inputs:

        Returns: meanpooling后的向量

        """
        return K.mean(inputs, axis=-1)

    def absminus(self, inputs):
        """

        Args: 向量pairwise相减并取绝对值
            inputs:

        Returns: 两个向量pairwise相减并取绝对值后得到的新的向量

        """
        if self.model_type == "maxpooling":
            size = self.dataProcessor.senMaxLen
        if self.model_type == "lstm":
            size = 2 * self.cellNum[-1]
        v1 = inputs[:, 0:size]
        v2 = inputs[:, size:2 * size]
        return K.abs(v1 - v2)

    def pairwisemul(self, inputs):
        """

        Args: 向量pairwise相乘
            inputs:

        Returns: 两个向量pairswie相乘后的新向量

        """
        if self.model_type == "maxpooling":
            size = self.dataProcessor.senMaxLen
        if self.model_type == "lstm":
            size = 2 * self.cellNum[-1]
        v1 = inputs[:, 0:size]
        v2 = inputs[:, size:2 * size]
        return v1 * v2

    def build(self):

        """
        Args: 词向量 + LSTM + Attention模型
            inputs:

        Returns: 编辑后的模型

        """
        #  定义输入层
        senA = Input(shape=(self.dataProcessor.senMaxLen,), name='senA')
        senB = Input(shape=(self.dataProcessor.senMaxLen,), name='senB')
        CharA = Input(shape=(self.dataProcessor.senMaxLen,), name='CharA')
        CharB = Input(shape=(self.dataProcessor.senMaxLen,), name='CharB')

        #  词embedding层的创建，使用预训练好的word2vec初始化
        if self.loadw2v:
            #  词embedding层的创建，使用预训练好的word2vec初始化

            sharedEmbeddingLayer = Embedding(input_dim=self.dataProcessor.wordVocabSize,
                                             output_dim=self.embeddingDim, input_length=self.dataProcessor.senMaxLen,
                                             name='embeddingLayer', mask_zero=True, trainable=False,
                                             embeddings_initializer=EmbeddingInit.pretrainedWord2Vec)
        else:
            sharedEmbeddingLayer = Embedding(input_dim=self.dataProcessor.wordVocabSize,
                                             output_dim=self.embeddingDim, input_length=self.dataProcessor.senMaxLen,
                                             name='embeddingLayer', mask_zero=True, trainable=False
                                             )

        #  连接embedding层与输入层

        embeddingSenA = sharedEmbeddingLayer(senA)
        embeddingSenB = sharedEmbeddingLayer(senB)

        # 共享字向量embedding层的创建，随机初始化

        sharedEmbeddingChar = Embedding(input_dim=self.dataProcessor.charVocabSize,
                                        output_dim=self.embeddingDim,
                                        input_length=self.dataProcessor.senMaxLen,
                                        name="sharedembeddingChar",
                                        mask_zero=True, trainable=True,
                                        # embeddings_initializer=pretrainedChar2Vec
                                        embeddings_initializer=initializers.RandomNormal(mean=0.0, stddev=.05)
                                        )

        #  连接embedding层与输入层
        embeddingCharA = sharedEmbeddingChar(CharA)
        embeddingCharB = sharedEmbeddingChar(CharB)

        #  在最后一个维度拼接字和词的embedding层

        EmbeddingA = concatenate([embeddingSenA, embeddingCharA], axis=-1, name="EmbeddingA")
        EmbeddingB = concatenate([embeddingSenB, embeddingCharB], axis=-1, name="EmbeddingB")

        # 使用BiLSTM分别对embedding层的输出进行表征

        sharedBiLSTM1 = Bidirectional(LSTM(units=self.cellNum[0],
                                           return_sequences=True,
                                           dropout=self.dropout,
                                           recurrent_dropout=self.recurrent_dropout))
        LSTM1SenA = sharedBiLSTM1(EmbeddingA)
        LSTM1SenA = TimeDistributed(BatchNormalization())(LSTM1SenA)

        LSTM1SenB = sharedBiLSTM1(EmbeddingB)
        LSTM1SenB = TimeDistributed(BatchNormalization())(LSTM1SenB)

        #  构造匹配层，可使用fullmatching, maxmatching, average_attention, max_attention对两个表征后的句子进行交叉匹配

        matching_layer = MultiPerspective(self.mp_dim).build()
        matching1 = matching_layer([LSTM1SenA, LSTM1SenB])
        matching2 = matching_layer([LSTM1SenB, LSTM1SenA])

        #  构造聚合层，可选maxpooling, meanpooling以及BiLSTM

        if self.model_type == "maxpooling":
            MaxPooling = Lambda(self.maxpooling)

            LSTM2SenA = MaxPooling(matching1)
            LSTM2SenB = MaxPooling(matching2)

        elif self.model_type == "meanpooling":
            Meanpooling = Lambda(self.meanpooling)

            LSTM2SenA = Meanpooling(matching1)
            LSTM2SenB = Meanpooling(matching2)

        else:
            sharedLSTM2 = Bidirectional(LSTM(units=self.cellNum[1],
                                             dropout=self.dropout,
                                             recurrent_dropout=self.recurrent_dropout))

            LSTM2SenA = sharedLSTM2(matching1)
            LSTM2SenB = sharedLSTM2(matching2)

        #  将聚合后的两个向量在最后一个维度上拼接
        mergedVector = concatenate([LSTM2SenA, LSTM2SenB], axis=-1, name='concatLayer')

        #  加入向量相减，相乘的向量并在最后一个维度上拼接

        if self.merge_type == "diff":  # 只加入相减后的向量
            minus = Lambda(self.absminus)
            vector = minus(mergedVector)
            mergedVector = concatenate([mergedVector, vector], axis=-1, name='diffconcatLayer')

        if self.merge_type == "mul":  # 只加入相乘后的向量
            mutiply = Lambda(self.pairwisemul)
            vector = mutiply(mergedVector)
            mergedVector = concatenate([mergedVector, vector], axis=-1, name='mulconcatLayer')

        if self.merge_type == "complex":  # 同时加入相减，相乘后的向量
            minus = Lambda(self.absminus)
            vector1 = minus(mergedVector)

            mutiply = Lambda(self.pairwisemul)
            vector2 = mutiply(mergedVector)

            mergedVector = concatenate([mergedVector, vector1, vector2], axis=-1, name='complexconcatLayer')

        #  经过全连接层计算语义相似度

        dense1 = Dense(self.dense_dim, activation='relu', name='dense1')(mergedVector)
        dense1 = Dropout(self.dropout)(dense1)
        dense1 = BatchNormalization()(dense1)

        outputLayer = Dense(2, activation='softmax', name='outputLayer')(dense1)

        myModel = Model(inputs=[senA, senB, CharA, CharB], outputs=outputLayer)

        myModel.compile(optimizer='adam',
                        loss='binary_crossentropy',
                        metrics=['accuracy'])

        return myModel

