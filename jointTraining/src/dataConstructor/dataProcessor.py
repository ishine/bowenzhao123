# -*- coding: utf-8 -*-
# @Time : 2018/9/3 7:47 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : dataProcessor.py
# @Software: PyCharm
# @desc:

import pandas as pd
import pickle
import numpy as np
from keras.utils import to_categorical
import jieba
from src.dataConstructor.vocbaBuilder import VocabBuilder
import os

from config import *

from src.util.util import readData

class DataProcessor(object):
    """

    数据预处理，对训练集和测试集的数据进行onehot编码，label转化为哑变量
    Attributes:
        vocabBuidMinCount: 可以作为登录词的最小词频
        wordVocabPath: 基于词的词典保存路径
        charVocabPath: 基于字的词典保存路径
        senMaxLen: embedding最大长度

    """

    def __init__(self):
        self.vocabBuidMinCount = sysParamSetting._wordVocabPath
        self.wordVocabPath = sysParamSetting._wordVocabPath
        self.charVocabPath = sysParamSetting._charVocabPath
        self.senMaxLen = sysParamSetting._senMaxLen
        # 调用字典构造模块
        vocabInitializer = VocabBuilder()

        if not os.path.exists(self.wordVocabPath):  # 如果没有字典，则构造字典
            vocabInitializer.vocabBuild()
        # 载入字典
        self.word2id, self.wordVocabSize = vocabInitializer.loadVocab(self.wordVocabPath)
        self.char2id, self.charVocabSize = vocabInitializer.loadVocab(self.charVocabPath)


    def sentence2id(self,data,lookUpTable):
        """

        给句子里的每个词，都找到word2id里对应的序列标号

        Args:
            data: 预处理的文本
            lookUpTable: 字典

        Returns: 句子onehot编码

        """

        sentenceID = []

        for i in range(data.shape[0]):
            _tmp = []
            sent = data[i]
            for word in sent:
                if word in [',', '。', '.', '?', '!', ' ']:
                    continue

                if word.isdigit():
                    word = '<NUM>'
                elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
                    word = '<ENG>'

                if word not in self.word2id:
                    word = '<UNK>'

                _tmp.append(lookUpTable[word])

            sentenceID.append(_tmp)

        return sentenceID

    def padSequences(self, sequences, pad_mark=0):

        """

        如果句子长度不足self.senMaxLen，则补0。如果句子大于self.senMaxLen，则截取
        Args:
            sequences: onehot编码句子
            pad_mark: 填补数字

        Returns:
            二维列表[字典最大长度,最大长度]
        """

        seq_list, seq_len_list = [], []
        for seq in sequences:
            seq = list(seq)
            seq_ = seq[:self.senMaxLen] + [pad_mark] * max(self.senMaxLen - len(seq), 0)
            seq_list.append(seq_)
            seq_len_list.append(min(len(seq), self.senMaxLen))
        return seq_list, seq_len_list


    def genW2VDataforModelInput(self,path):
        """  生成网络接收的训练数据，句子长度list和类标
        Args:
            path: 文本路径

        Returns: onehot编码文本, 哑变量label

        """

        sequenceData = readData(path)
        text1 = self.sentence2id(np.array(sequenceData['text1']), self.word2id)
        text1WordID, text1SeqLenList = self.padSequences(text1)

        text2 = self.sentence2id(np.array(sequenceData['text2']), self.word2id)
        text2WordID, text2SeqLenList = self.padSequences(text2)

        return np.asarray(text1WordID), np.asarray(text2WordID), sequenceData['label']


    def genCharDataforModelInput(self,path):

        """

        生成基于字的网络接收的训练数据，句子长度list
        Args:
            path: 文本路径

        Returns: onehot编码文本

        """

        sequenceData = readData(path)
        charID1 = self.sentence2id(np.array(sequenceData['text1']),self.char2id)
        charID1, text1SeqLenList = self.padSequences(charID1)

        charID2 = self.sentence2id(np.array(sequenceData['text2']),self.char2id)
        charID2, text1SeqLenList = self.padSequences(charID2)

        return np.asarray(charID1),np.asarray(charID2)


    def trainDataSetCreator(self, sourcefile):
        """   生成模型训练的输入数据

        Args:
            sourcefile: 源文件
        Return:
            基于词向量的onehot编码
            基于字向量的onehot编码
            数据label
        """

        text1, text2, label = self.genW2VDataforModelInput(sourcefile)
        char1, char2 = self.genCharDataforModelInput(sourcefile)
        label = to_categorical(label,num_classes=2)
        return text1,text2, label, char1, char2

    def genCombineData(self, textA, textB, CharA, CharB, slabel, index):

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
