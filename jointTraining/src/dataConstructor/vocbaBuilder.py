# -*- coding: utf-8 -*-
# @Time : 2018/9/4 9:57 AM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : vocbaBuilder.py
# @Software: PyCharm
# @desc:

import jieba
import pandas as pd
import numpy as np
import pickle
import os

from config import *

from src.util.util import readData


class VocabBuilder(object):
    """  构建onehot编码的字典

    用于getUserData,trainSetCrate，userTestDataCreate的调用，来生成语义匹配模型的输入

    Attributes:
        vocabBuidMinCount: 录入词典单词出现最低频次
        wordVocabPath: 基于词的词典存放路径
        charVocabPath: 基于字的词典存放路径
        senMaxLen: 句子onehot编码最大长度

    """

    def __init__(self):

        self.vocabBuidMinCount = sysParamSetting._vocabBuidMinCount
        self.wordVocabPath = sysParamSetting._wordVocabPath
        self.charVocabPath = sysParamSetting._charVocabPath
        self.senMaxLen = sysParamSetting._senMaxLen
        self.defaultVocabPath1 = sysParamSetting._basicModelTrainData
        self.defaultVocabPath2 = sysParamSetting._basicModelTestData

        pass

    def loadVocab(self, path):
        """

        载入词典
        Args:
            path: 词典路径

        Returns: 词典，词典长度

        """

        with open(path, 'rb') as fr:
            word2id = pickle.load(fr)
        return word2id, len(word2id)

    def getVocabInput(self,path=None):
        """ 读取文本，生成字典

        Args:
            path:  生成字典需要的文本名称
        Return:
            列表[str1,str2,..]
        """

        if os.path.exists(path):  # 判断是否存在构建字典的文件
            try:
                data = readData(path)
                if isinstance(data,pd.DataFrame):
                    data = pd.read_csv(path).ix[:, 0].tolist()
            except:
                print('无法读取文本！')


        else:  # 如果不存在，判断是否有微众银行的数据
            if os.path.exists(self.defaultVocabPath1):
                data_1 = pd.read_csv(self.defaultVocabPath1)
                data_2 = pd.read_csv(self.defaultVocabPath2)
                data = pd.concat([data_1['text1'], data_1['text2'], data_2['text1'], data_2['text2']]).tolist()

            else:
                raise Exception('没有用于构造词典的语料，请将语料存放System/data/sourceDataSentenceList.csv')
        return data

    def vocabBuild(self):
        """

        构建词典
        Args:
            data: 用于构建词典的语料的列表
        Return:
        """
        filename = input('请输生成字典的源文件名称:')  # 获取文件名称

        data = self.getVocabInput(filename)

        word2id = {}

        for sent_ in data:

            cut_sent = jieba.cut(sent_)

            for word in cut_sent:

                if word in [',', '。', '.', '?', '!', ' ']:
                    continue

                # 是否是数字
                if word.isdigit():
                    word = '<NUM>'

                # 是否是英文
                elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
                    word = '<ENG>'

                if word not in word2id:
                    word2id[word] = [len(word2id) + 1, 1]
                else:
                    word2id[word][1] += 1

        low_freq_words = []
        for word, [word_id, word_freq] in word2id.items():
            if word_freq < self.vocabBuidMinCount and word != '<NUM>' and word != '<ENG>':
                low_freq_words.append(word)
        for word in low_freq_words:
            del word2id[word]

        new_id = 1
        for word in word2id.keys():
            word2id[word] = new_id
            new_id += 1
        word2id['<UNK>'] = new_id
        word2id['<PAD>'] = 0

        #  写入字典
        with open(self.wordVocabPath, 'wb') as fw:
            pickle.dump(word2id, fw)

if __name__ == "__main__":
    s = VocabBuilder()
    a1,a2 = s.loadVocab('../../System/lib/word2id.pkl')
    print(a2)
