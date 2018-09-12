# -*- coding: utf-8 -*-
# @Time : 2018/9/4 1:41 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : decompAtt.py
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
from keras.layers.recurrent import LSTM

from src.dataConstructor.dataProcessor import DataProcessor
from src.dataConstructor.embeddingInitiate import EmbeddingInit
from config import *

class DecomAtt(object):
    """  构造decomposed attention模型
    来源文献:A Decomposable Attention Model for Natural Language Inference
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

    def _batchDot(self, inputs):
        """
        Args:  向量点积
            inputs:

        Returns:
        """
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

        inputs = concatenate([LSTM1SenA, LSTM1SenB], axis=-1, name='inputs')

        #  相似度矩阵
        cosine_similarity = Lambda(self._cosine_similarity)
        cosin_matrix = cosine_similarity(inputs)

        # Alpha最后一个维度对应A的一个单词，Q中的每个单词对A的重要性,最终得到A的重新表征
        # Beta第三个个维度对应Q中的一个单词，A中的每个单词对Q的重要性
        # Alpha/Beta shape: [batch_size, Q_length, A_length]

        Alpha = Lambda(K.softmax)(cosin_matrix)

        permute = Lambda(self._permutation)
        cosin_matrix_T = permute(cosin_matrix)

        Beta = Lambda(K.softmax)(cosin_matrix_T)

        #  计算attention后的语句的新的表征
        batch_product = Lambda(self._batchDot)

        AttLSTM1SenA = concatenate([Alpha, LSTM1SenB], axis=-1)
        AttLSTM1SenB = concatenate([Beta, LSTM1SenA], axis=-1)

        Att_LSTM1SenA = batch_product(AttLSTM1SenA)
        Att_LSTM1SenB = batch_product(AttLSTM1SenB)

        #  将原始的句子和经过attention后的句子在最后一个维度拼接
        mergedVectorA = concatenate([LSTM1SenA, Att_LSTM1SenA], axis=-1, name='concatLayerA')
        mergedVectorB = concatenate([LSTM1SenB, Att_LSTM1SenB], axis=-1, name='concatLayerB')

        #  计算新的句子和经过attention后的句子的交互
        cross = Dense(units=64, activation="relu")

        mergedVectorA = TimeDistributed(cross)(mergedVectorA)
        mergedVectorA = TimeDistributed(BatchNormalization())(mergedVectorA)

        mergedVectorB = TimeDistributed(cross)(mergedVectorB)
        mergedVectorB = TimeDistributed(BatchNormalization())(mergedVectorB)

        #  构造聚合层，可选maxpooling, meanpooling以及BiLSTM
        if self.model_type == "maxpooling":
            MaxPooling = Lambda(self.maxpooling)

            VecA = MaxPooling(mergedVectorA)
            VecB = MaxPooling(mergedVectorB)

        elif self.model_type == "meanpooling":
            Meanpooling = Lambda(self.meanpooling)
            VecA = Meanpooling(mergedVectorA)
            VecB = Meanpooling(mergedVectorB)

        else:
            sharedLSTM2 = Bidirectional(LSTM(units=self.cellNum[1],
                                             dropout=self.dropout,
                                             recurrent_dropout=self.recurrent_dropout))

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

