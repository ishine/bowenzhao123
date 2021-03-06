# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:09 PM
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

class inputSetting(object):
    """ 用户输入语料库的配置

    """
    targetDataDir = 'Users/data/target/' #Users/data/SourceData/'  # 用户输入的数据存放文件夹


class dataParamSetting(object):
    """ 生成的训练文本的参数设置

    """

    transferModelTrainfile = 'Users/data/modelTrainFile.csv'  # 迁移模型训练数据
    transferModleTestfile = 'Users/data/modelTestFile.csv'  # 迁移模型测试数据
    targetClassifyDataFile = 'Users/data/targetClassifyDataFile.csv'  # 分类模型训练数据
    combinedDataSaveFile = 'Users/data/combinedDataSaveFile.txt'  # fasttext的w2v模型训练文本
    trainTransferModelData = 'Users/data/trainTransferModelData.csv' # 最终训练迁移模型时候的训练数据
    #trainTransferModelData = 'Users/data/train_cls.csv'

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



class transferParamSetting(object):
    """ 迁移模型参数设置

    """
    transferbatchSize = 56  #  迁移模型batch_size
    transferModelPath = 'Users/model/model.h5'  #  预训练模型保存路径
    tranferepochNum = 80  #  迁移模型迭代次数
    transferDenseLayerUnits = 16



class classifyParamSetting(object):
    """ 分类模型参数设置

    """
    trainClassifierFile = 'Users/data/trainClassifier.txt'  # 分类模型数据存放路径
    saveVectorFile = 'Users/model/w2vwithNgram'  # fasttext预训练词向量存放路径
    classifierModel = 'Users/model/classifier.model'  # 分类模型存放路径
    w2vdim = 200  # fasttext词向量维度
    trainClassifierEpoch = 20  # 分类模型迭代次数
    trainw2vepoch = 20  # fasttext 词向量模型迭代次数


class userQuestion(object):
    """ 用户用来控制参数

    """
    def __init__(self):
        self.transferparamsetting = transferParamSetting()
        self.classifyparamsetting = classifyParamSetting()

        pass

    def setInputSetting(self,file):

        inputsetting = inputSetting()
        inputsetting.targetDataDir = file

    def setDataParam(self,feed_dict):

        pass

    def setTransferParam(self,feed_dict):
        filepath = self.transferparamsetting.transferModelPath
        os.remove(filepath)
        pass

    def setClassifyParam(self,feed_dict):
        filepath = self.classifyparamsetting.classifierModel
        os.remove(filepath)
        pass
