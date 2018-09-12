# -*- coding: utf-8 -*-
# @Time : 2018/9/7 3:08 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : config.py
# @Software: PyCharm
# @desc:

import os

class sysParamSetting(object):

    _wordVocabPath = 'Admin/model/word2id.pkl'  # 基于词的词典
    _charVocabPath = 'Admin/model/char2id.pkl'  # 基于字的词典
    _senMaxLen = 32  # embedding长度
    _basicModelTrainData = 'Admin/data/task3_train.csv'  # 大的语料库，用于预训练模型
    _basicModelTestData = 'Admin/data/task3_dev.csv'  # 大的语料库，用于预训练模型
    _trainedModelByCAFE = 'Admin/model/cafeLWC.h5' #  模型存放位置
    _vocabBuidMinCount = 1  # 词典中的词最小词频
    _sourceDataSentenceList = 'Admin/data/sourceDataSentenceList.csv'  # 用于构造词向量的数据存放位置
    _W2Vfilepath = 'Admin/data/LargeW2V.bin'


class dataParamSetting(object):
    """ 生成的训练文本的参数设置

    """

    jointTaskModelTrainfile = 'Users/data/modelTrainFile.csv'  # 迁移模型训练数据
    jointTaskModleTestfile = 'Users/data/modelTestFile.csv'  # 迁移模型测试数据
    trainModelData = 'Users/data/trainTransferModelData.csv' # 最终训练迁移模型时候的训练数据


class modelParamSetting(object):
    """ 语义相似度模型参数设置

    """
    embeddingDim = 64  # 词向量维度
    cellNum = [50,32]  # lstm unit参数
    mp_dim = 16  # mulit-perspective的matching layer输出维度
    dropout = .4  # dropout
    recurrent_dropout = .4  # rnn层间dropout
    dense_dim = 64  # 全连接层uit
    model_type = 'lstm'
    merge_type = 'single'
    basicModelEpochNum = 150  # 预训练模型迭代次数
    basicModelBatchSize = 56  # 预训练模型batch_size



class jointTaskParamSetting(object):
    """ 迁移模型参数设置

    """
    SpecialTaskAUnits = 32
    SpecialTaskBUnits = 16
    SharedTaskUnits = 32
    jointTaskbatchSize = 56  #  迁移模型batch_size
    jointTaskModelPath = 'Users/model/joinTask.h5'  #  预训练模型保存路径
    jointTaskepochNum = 80  #  迁移模型迭代次数
    jointTaskdropout = .4
    SpecialTaskALSTMUnits = 32
    SpecialTaskBLSTMUnits = 16
    SharedTaskLSTMUnits = 32
