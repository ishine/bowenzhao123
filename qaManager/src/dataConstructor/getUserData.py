# -*- coding: utf-8 -*-
# @Time : 2018/9/3 3:57 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : getUserData.py
# @Software: PyCharm
# @desc:

import numpy as np
import pandas as pd
import os
import collections
from config import *
from src.util.util import dataClean, processText


class GetUserData(object):
    """  将用户原始文件合并生成标准文本,以供后续训练
    Attributes:
        targetDataDir: 用户数据存放的文件夹, 文件夹下方还有不同的文件夹，分别对应不同的意图

    """

    def __init__(self):
        self.targetDataDir = inputSetting.targetDataDir
        if not os.path.exists(self.targetDataDir):
            raise Exception('系统内没有待训练文件!')
        pass

    def getDataFileLists(self):
        """ 获取文件所在文件夹，以及文件名称列表

        Return:
            文件夹-文件字典{文件夹:文件列表}
        """

        dirlists = [] 
        for x in os.listdir(self.targetDataDir):
            if not x.startswith('.'):
                dirlists.append(x)
        dic = {}
        for directory in dirlists:
            dic[directory] = []
            filelists = os.listdir(self.targetDataDir+directory)
            for filename in filelists:
                if filename.endswith('txt'):
                    dic[directory].append(filename)
        return dic

    def createLabledTargetData(self,savefile=None):
        """ 根据原始输入文件集合，构建分类文本

        :param savefile: 保存文件
        :return:
        """
        text = []
        label = []
        index = 0
        FileDic = self.getDataFileLists()
        for directory in FileDic.keys():
            for file in FileDic[directory]:
                df = np.array(list(pd.read_csv(self.targetDataDir+directory +'/'+ file, header=None, sep="\n")[0]))
                text = np.concatenate((text, df), axis=0)
                label = np.concatenate((label, [index] * len(df)), axis=0)
            index += 1

        newtext = []
        for sentence in text:
            newtext.append(processText(sentence))
        data = pd.DataFrame({'text': newtext, 'label': label})
        data = data.sample(frac=1)
        data.to_csv(savefile, index=False)


    def generatePosNegData(self,file1,file2,split=.7):
        """构造已分类的正负样本
        Args:
            file1: 训练数据保存文件
            file2: 测试数据保存文件
            split: 测试集和训练集分裂比例

        Returns:

        """
        groupRule = self.getDataFileLists()

        label = []
        text1 = []
        text2 = []
        label_ = []
        text1_ = []
        text2_ = []
        # 分类
        for directory in groupRule.keys():
            temp = collections.Counter()
            temp_ = collections.Counter()

            for filename in groupRule[directory]:
                df = np.array(list(pd.read_csv(self.targetDataDir+directory +'/'+ filename, header=None, sep="\n")[0]))
                ind = np.random.choice(len(df), size=int(len(df) * split), replace=False)

                df1 = df[ind]
                df2 = df[list(filter(lambda x: x not in ind, np.arange(len(df))))]

                temp[filename] = df1
                temp_[filename] = df2

            text_1, text_2, label1 = self.genPosData(temp)
            textA, textB, label0 = self.genNegData(temp)

            text1 = np.concatenate((text1, text_1, textA), axis=0)
            text2 = np.concatenate((text2, text_2, textB), axis=0)
            label = np.concatenate((label, label1, label0), axis=0)

            text_1_, text_2_, label1_ = self.genPosData(temp_)
            textA_, textB_, label0_ = self.genNegData(temp_)

            text1_ = np.concatenate((text1_, text_1_, textA_), axis=0)
            text2_ = np.concatenate((text2_, text_2_, textB_), axis=0)
            label_ = np.concatenate((label_, label1_, label0_), axis=0)

        df = pd.DataFrame({'text1': text1, 'text2': text2, 'label': label})
        df = df.sample(frac=1)
        df.to_csv(file1, index=False)

        if len(text1_) > 0 and file2:
            df_ = pd.DataFrame({'text1': text1_, 'text2': text2_, 'label': label_})
            df_ = df_.sample(frac=1)
            df_.to_csv(file2, index=False)


    def genPosData(self,temp):
        """

            构造负样本
            Args:
                temp: dict
                i: int

            Returns: 负样本

            """
        text_1 = []
        text_2 = []
        ind = []

        for key in temp.keys():
            temp_1 = []
            temp_2 = []
            temp_label = []
            value = temp[key]
            for i in range(1, len(value)):
                for j in range(i):
                    temp_1.append(value[i])
                    temp_2.append(value[j])
                    temp_label.extend([1])
            if len(temp_1) == 0:
                continue
            else:
                index = np.random.choice(len(temp_1), size=min(10, len(temp_1)), replace=False)
            text_1.extend([temp_1[x] for x in index])
            text_2.extend([temp_2[x] for x in index])
            ind.extend([temp_label[x] for x in index])

        return np.array(text_1), np.array(text_2), np.array(ind)

    def genNegData(self,temp):
        """

           构造负样本
           Args:
               temp: dict
               i: int

           Returns: 负样本

           """
        text_1 = []
        text_2 = []
        ind = []
        for key in temp.keys():
            ans = []
            for k in temp.keys():
                if k != key:
                    ans.extend(temp[k])
            size = len(temp[key]) * (len(temp[key]) - 1) // 2
            size = min(10,size)
            if len(temp[key]) == 0 or len(ans) == 0:
                continue
            else:
                index1 = np.random.choice(len(temp[key]), size=size, replace=True)
                index2 = np.random.choice(len(ans), size=size, replace=False if len(ans) >= size else True)
                text_1.extend([ans[x] for x in index2])
                text_2.extend([temp[key][x] for x in index1])
                ind.extend([0] * min(10, size))
        return text_1, text_2, ind


class CreateInput(object):
    """ 生成用于训练模型的文件
    Args:
        getUserData: 调用获取用户数据模块
        sourceDataSentenceList: 训练w2v模型的数据源文件
        targetDataFile: 训练分类模型的数据源文件

    """

    def __init__(self):

        self.getUserData = GetUserData()
        self.sourceDataSentenceList = sysParamSetting._sourceDataSentenceList
        # sourceDataSentenceList 为二维列表[list1,list2,list3,...]，每个list对应一个句子的字符串
        self.targetDataFile = dataParamSetting.targetClassifyDataFile  # 数据形式{'text':字符串，'label':类别}

        #if not os.path.exists(self.sourceDataSentenceList):
            #raise Exception('没有基础的语料库！')

        if not os.path.exists(self.targetDataFile):
            self.getUserData.createLabledTargetData(self.targetDataFile)

        self.combinedDataSaveFile = dataParamSetting.combinedDataSaveFile
        

    def combineSourceTargetData(self):
        """ 合并source和target的语句

        Args:
            targetData: 目标文件所在位置
        Return:

        """

        srcdata = np.asarray(pd.read_csv(self.sourceDataSentenceList)['text'])
        tardata = np.asarray(pd.read_csv(self.targetDataFile)['text'])

        data = np.concatenate((srcdata, tardata), axis=0)
        with open(self.combinedDataSaveFile) as f:
            for line in data:
                f.write(line)


    def updataSourceData(self):
        """ 判断是否使用target数据更新源数据

        Args:
        Return:
        """
        tardata = np.asarray(pd.read_csv(self.targetDataFile)['text'])
        with open(self.sourceDataSentenceList,'a') as f:
            for line in tardata:
                f.write(line)


    def genRawInputData(self,trainfile,testfile,split=.7):
        """  生成模型训练和测试数据，并保存文件
        Args:
            trainfile: 训练数据存放路径
            testfile: 测试数据存放路径
        Return:

        """
        self.getUserData.generatePosNegData(trainfile,testfile,split)
