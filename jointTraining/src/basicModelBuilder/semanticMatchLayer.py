# -*- coding: utf-8 -*-
# @Time : 2018/9/4 1:41 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : comAggFact.py
# @Software: PyCharm
# @desc:

import keras.backend as K
from keras.models import Model
from keras.layers.wrappers import Bidirectional, TimeDistributed
from keras.layers import Input, Dense, concatenate
from keras.layers.core import Dropout, Lambda, Permute
from keras.layers.normalization import BatchNormalization
from keras.layers.embeddings import Embedding
from keras import initializers
from keras.layers.recurrent import LSTM, GRU


from src.dataConstructor.dataProcessor import DataProcessor
from src.dataConstructor.embeddingInitiate import EmbeddingInit

from config import *


class ComparedAggFactor(object):
    """ 构造compared Aggregate Factorized模型
    来源文献: A Compare-Propagate Architecture with Alignment Factorization for Natural Language Inference
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
        self.dropout = modelParamSetting.dropout
        self.recurrent_dropout = modelParamSetting.recurrent_dropout
        self.dense_dim = modelParamSetting.dense_dim
        self.model_type = modelParamSetting.model_type
        self.merge_type = modelParamSetting.merge_type
        self.loadw2v = loadw2v
        pass

    def _cosine_similarity(self, inputs):
        """

        Args:  余弦相似度计算层
            inputs:

        Returns: 余弦相似度矩阵

        """

        size = 2 * self.cellNum[0]
        seqQ = inputs[:, :, 0:size]
        seqA = inputs[:, :, size:2 * size]
        ret = K.batch_dot(seqQ, Permute((2, 1))(seqA))
        return ret

    def _permutation(self, inputs):
        """

        Args:  改变tensor形状
            inputs:

        Returns: 变更形状后的tensor

        """
        return K.permute_dimensions(inputs, pattern=[0, 2, 1])
        # x.shape = （1,2,3）
        # x = [[[1,2,3],[4,5,6]]]
        #### x2 = K.permute_dimensions(x, pattern=[0, 2, 1])
        # x2 = x.reshape((-1,3,2))
        # x2.shape = (1,3,2)
        # x2 = [[[1,4],[2,5],[3,6]]]
        # x2 = [[[1,2],[3,4],[5,6]]]

    def _batchDot(self, inputs):

        size = self.dataProcessor.senMaxLen + 2 * self.cellNum[0]
        Weight = inputs[:, :, 0:self.dataProcessor.senMaxLen]
        sentence = inputs[:, :, self.dataProcessor.senMaxLen:size]
        return K.batch_dot(Weight, sentence)

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

        if self.loadw2v:
            #  词embedding层的创建，使用预训练好的word2vec初始化

            sharedEmbeddingLayer = Embedding(input_dim=self.dataProcessor.wordVocabSize,
                                             output_dim=self.embeddingDim, input_length=self.dataProcessor.senMaxLen,
                                             name='embeddingLayer', mask_zero=True, trainable=False,
                                             embeddings_initializer=EmbeddingInit().pretrainedWord2Vec)
        else:
            sharedEmbeddingLayer = Embedding(input_dim=self.dataProcessor.wordVocabSize,
                                             output_dim=self.embeddingDim, input_length=self.dataProcessor.senMaxLen,
                                             name='embeddingLayer', mask_zero=True, trainable=False)
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

        sharedBiGRU1 = Bidirectional(GRU(units=self.cellNum[0],
                                         return_sequences=True,
                                         dropout=self.dropout,
                                         recurrent_dropout=self.recurrent_dropout))

        LSTM1SenA = sharedBiGRU1(EmbeddingA)
        LSTM1SenA = TimeDistributed(BatchNormalization())(LSTM1SenA)

        LSTM1SenB = sharedBiGRU1(EmbeddingB)
        LSTM1SenB = TimeDistributed(BatchNormalization())(LSTM1SenB)

        inputs = concatenate([LSTM1SenA, LSTM1SenB], axis=-1, name='inputs')

        #  相似度矩阵 ********************************************
        cosine_similarity = Lambda(self._cosine_similarity)
        cosin_matrix = cosine_similarity(inputs)

        inner_att_A = cosine_similarity(concatenate([LSTM1SenA, LSTM1SenA], axis=-1))
        inner_att_A = Lambda(K.softmax)(inner_att_A)

        inner_att_B = cosine_similarity(concatenate([LSTM1SenB, LSTM1SenB], axis=-1))
        inner_att_B = Lambda(K.softmax)(inner_att_B)
        # Alpha最后一个维度对应A的一个单词，Q中的每个单词对A的重要性,最终得到A的重新表征
        # Beta第三个个维度对应Q中的一个单词，A中的每个单词对Q的重要性
        # Alpha/Beta shape: [batch_size, Q_length, A_length]

        Alpha = Lambda(K.softmax)(cosin_matrix)

        permute = Lambda(self._permutation)
        cosin_matrix_T = permute(cosin_matrix)

        Beta = Lambda(K.softmax)(cosin_matrix_T)

        batch_product = Lambda(self._batchDot)

        #  计算attention后的语句的新的表征
        AttLSTM1SenA = concatenate([Alpha, LSTM1SenB], axis=-1)
        AttLSTM1SenB = concatenate([Beta, LSTM1SenA], axis=-1)

        Att_LSTM1SenA = batch_product(AttLSTM1SenA)
        Att_LSTM1SenB = batch_product(AttLSTM1SenB)

        #  计算self attention后的句子表征
        selfAttLSTM1SenA = concatenate([inner_att_A, LSTM1SenA], axis=-1)
        selfAttLSTM1SenB = concatenate([inner_att_B, LSTM1SenB], axis=-1)

        selfAttLSTM1SenA = batch_product(selfAttLSTM1SenA)
        selfAttLSTM1SenB = batch_product(selfAttLSTM1SenB)

        mergedVectorA = concatenate([selfAttLSTM1SenA, Att_LSTM1SenA], axis=-1, name='mergedVectorA')
        mergedVectorB = concatenate([selfAttLSTM1SenB, Att_LSTM1SenB], axis=-1,name='mergedVectorB')

        #  计算新的句子和经过attention后的句子的交互
        cross = Dense(units=64, activation="relu",name = 'cross')

        mergedVectorA = TimeDistributed(cross)(mergedVectorA)
        mergedVectorA = TimeDistributed(BatchNormalization())(mergedVectorA)

        mergedVectorB = TimeDistributed(cross)(mergedVectorB)
        mergedVectorB = TimeDistributed(BatchNormalization())(mergedVectorB)

        #  构造聚合层，选择maxpooling, meanpooling
        #  构造聚合层，可选maxpooling, meanpooling以及BiLSTM
        sharedLSTM2 = Bidirectional(LSTM(units=self.cellNum[1],
                                         dropout=self.dropout,
                                         recurrent_dropout=self.recurrent_dropout,name='sharedLSTM2'))

        VecA = sharedLSTM2(mergedVectorA)
        VecB = sharedLSTM2(mergedVectorB)

        #  将聚合后的两个向量在最后一个维度上拼接
        Vec = concatenate([VecA, VecB], axis=-1, name='Vec')

        #  经过全连接层计算语义相似度
        dense = Dense(self.dense_dim, activation="relu", name="dense")(Vec)
        dense = Dropout(self.dropout)(dense)
        dense = BatchNormalization()(dense)
        outputlayer = Dense(2, activation="softmax", name="outputlayer")(dense)

        myModel = Model(inputs=[senA, senB, CharA, CharB], outputs=outputlayer)

        myModel.compile(optimizer="adam",
                        loss="binary_crossentropy",
                        metrics=["accuracy"]
                        )

        return myModel


