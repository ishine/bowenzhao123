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



    def sentence2id(self,data,lookUpTable,CharBase = False):
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
            if not CharBase and isinstance(sent,str):
                sent = list(jieba.cut(sent))
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
        text1 = self.sentence2id(np.array(sequenceData['text1']), self.word2id, CharBase=False)
        text1WordID, text1SeqLenList = self.padSequences(text1)

        text2 = self.sentence2id(np.array(sequenceData['text2']), self.word2id, CharBase=False)
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
        charID1 = self.sentence2id(np.array(sequenceData['text1']),self.char2id, CharBase=True)
        charID1, text1SeqLenList = self.padSequences(charID1)

        charID2 = self.sentence2id(np.array(sequenceData['text2']),self.char2id, CharBase=True)
        charID2, text1SeqLenList = self.padSequences(charID2)

        return np.asarray(charID1),np.asarray(charID2)
