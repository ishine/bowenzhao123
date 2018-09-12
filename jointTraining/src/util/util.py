# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:30 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : util.py
# @Software: PyCharm
# @desc:

import jieba
import re
import pandas as pd


def processText(sentence):
    """ 将用户输入的字符串转化为可以被模型识别的输入

    Args:
        sentence: 字符串
    Return:
        经分词后生成的列表
    """
    text = ''.join(re.findall(r'[\u4e00-\u9fa5]', sentence))
    text = jieba.cut(text)
    text = ' '.join(text)
    return text


def readData(filepath):
    """ 读取数据返回list/dataframe

    Args:
        filepath: 文件路径
    Return:
        列表/数据框
    """

    if filepath.endswith('csv'):
        data = pd.read_csv(filepath)
        return data

    elif filepath.endswith('txt'):
        data = []
        with open(filepath) as f:
            lines = f.readlines()
            for line in lines:
                data.append(line)
        return data

    elif filepath.endswith('json'):  # json文本处理模块
        pass

    else:
        raise Exception('请输入json,txt,csv格式的文本')

def dataClean(data,dictionary = None):
    """ 对输入的数据去除停用词，分词

    Args:
        data: 列表/数据框[str1,str2,...]
        dictionary: 字典，用于筛选不在字典中的词
    Return:
         二维listbiao[list1,list2..], 每一个子list为经去除停用词、分词后的列表
    """
    charList = []

    for sent in data:
        _tmp = []
        for char in sent:
            if char in [',', '。', '.', '?', '!', ' ']:
                continue
            if char.isdigit():
                char = '<NUM>'

            if ('\u0041' <= char <= '\u005a') or ('\u0061' <= char <= '\u007a'):
                char = '<ENG>'
            if dictionary is not None:
                if char not in dictionary:
                    char = '<UNK>'
                _tmp.append(char)
            else:
                _tmp.append(char)
            charList.append(_tmp)

    return charList

