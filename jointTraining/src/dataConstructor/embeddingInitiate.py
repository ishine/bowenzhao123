# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:01 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : embeddingInitiate.py
# @Software: PyCharm
# @desc:

import gensim
from gensim.models.word2vec import Word2Vec
import numpy as np
import jieba
import pickle
import os
from src.dataConstructor.dataProcessor import DataProcessor

from config import *

from src.util.util import readData, dataClean


class W2V(object):
    """ 训练或再训练词向量模型
    Attributes:

       wordVocabPath: 基于词的词典存放路径
       charVocabPath: 基于字的词典存放路径
       sourceDataSentenceList: 训练词向量的文件路径
       W2Vdim: 词向量长度

    """

    def __init__(self):
        self.wordVocabPath = sysParamSetting._wordVocabPath
        self.charVocabPath = sysParamSetting._charVocabPath
        self.sourceDataSentenceList = sysParamSetting._sourceDataSentenceList
        self.W2Vdim = modelParamSetting.embeddingDim

        pass

    def trainW2V(self,sentence,modelpath=None):
        """

        Args: 再训练word2vec模型
            modelpath: 预训练的词向量模型存放路径
            sentence: 已预处理的中文文本list

        Returns:
            模型文件

        """
        if modelpath and os.path.exists(modelpath):
            model = gensim.models.KeyedVectors.load(modelpath)
            model.train(sentence)

        else:
            model = Word2Vec(min_count=3, size=self.W2Vdim)
            model.build_vocab(sentence)
            model.train(sentence, total_examples=model.corpus_count, epochs=model.iter)
        return model


    def creatW2V(self,W2VsavePath):
        """ 训练词向量，并保存

        Args:
            W2VsavePath: 词向量保存文件名称

        Return:

        """
        with open(self.wordVocabPath, 'rb') as f:
            Charvocab = pickle.load(f).keys()

        trainW2VData = readData(self.sourceDataSentenceList)
        trainW2VData = dataClean(trainW2VData,Charvocab)


        model = self.trainW2V(trainW2VData)
        model.wv.save_word2vec_format(W2VsavePath, binary=True)


class EmbeddingInit(object):
    """  使用Word2Vector初始化embeddign层
    Attributes:
        W2Vfilepath: 词向量文件

    """
    def __init__(self):
        self.W2Vfilepath = 'System/data/LargeW2V.bin'
        self.wordVocabPath = sysParamSetting._wordVocabPath
        self.charVocabPath = sysParamSetting._charVocabPath
        self.W2Vdim = modelParamSetting.embeddingDim
        pass


    def pretrainedWord2Vec(self,shape):
        """

        Args: 使用预训练的word2vec初始化embedding层
            shape: [time_step,embedding_dim]

        Returns:
            embedding matrix

        """

        mat = np.zeros(shape=shape)
        print(mat.shape)

        if not os.path.exists(self.W2Vfilepath): # 如果预训练的词向量，则训练词向量
            w2v = W2V()
            w2v.creatW2V(self.W2Vfilepath)

        word2Vec = gensim.models.KeyedVectors.load_word2vec_format(self.W2Vfilepath, binary=True)

        with open(self.wordVocabPath, 'rb') as fr:
            word2id = pickle.load(fr)

        for _word in word2id:

            _word = str(_word)
            index = int(word2id[_word])

            if _word in word2Vec:
                mat[index] = word2Vec[_word].T
            else:
                _tmp = np.random.uniform(-0.25, 0.25, (1, shape[-1]))
                mat[index] = _tmp

        return mat
