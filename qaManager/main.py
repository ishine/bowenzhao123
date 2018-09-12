# -*- coding: utf-8 -*-
# @Time : 2018/9/3 4:09 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : main.py
# @Software: PyCharm
# @desc:

import os
from config import *

from src.semanticMatchBuilder.semanticMatch.trainByLargCorpus import TrainByLargeCorpus
from src.semanticMatchBuilder.semanticMatchTransfer.semanticMatchTransfer import TransferModel

from src.semanticMatchBuilder.topicClassify.topicClassify import TopicClassify

from src.answerCreater.answerSelect import AnswerSelect


if __name__ == "__main__":
    # 判断是否存在预训练模型
    if not os.path.exists('Admin/model/cafeLWC.h5'):
        train_base = TrainByLargeCorpus()
        train_base.trainModelByLargCorpus()

    if not os.path.exists('Users/model/classifier.model.bin'):
        topiclassify = TopicClassify()
        topiclassify.createClassifier()

    # 判断是否存在业务上的预训练好的迁移模型
    if not os.path.exists('Users/model/model.h5'):
        transfermodel = TransferModel()
        transfermodel.trainTransferModel()

    # 初始化测试
    answerGenerator = AnswerSelect()

    # 在线运行
    while True:
        text = input('请输入问句：')
        answerGenerator.getAnswer(text)