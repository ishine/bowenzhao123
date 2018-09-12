# -*- coding: utf-8 -*-
# @Time : 2018/9/7 3:08 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : main.py
# @Software: PyCharm
# @desc:

from src.jointTaskModelBuilder.jointTaskModelBuilder import JointTask
from src.basicModelBuilder.trainByLargCorpus import TrainByLargeCorpus
from config import *

if __name__ == "__main__":

    # 判断是否存在预训练模型
    if not os.path.exists(sysParamSetting._trainedModelByCAFE):
        TrainByLargeCorpus().trainModelByLargCorpus()

    # 判断是否存在业务上的预训练好的迁移模型
    if not os.path.exists('Users/model/model.h5'):
        JointTask().trainModel()
