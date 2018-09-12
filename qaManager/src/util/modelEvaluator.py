# -*- coding: utf-8 -*-
# @Time : 2018/9/4 2:34 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : modelEvaluator.py
# @Software: PyCharm
# @desc:

import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score


class Evaluator(object):
    """  模型评估
    Attributes:
        model: 待评估的模型
    """

    def __init__(self,model):
        self.model = model

    def basicEvaluator(self,feed_dict,test_label):
        """ 模型测试集的acc,f1,recall

        Args:
            feed_dict: evaluate数据的自变量
            test_label: evaluate数据标签
        Return:
        """

        test_probs = self.model.predict(feed_dict)
        test_pred = np.argmax(test_probs, axis=1)

        f1 = f1_score(test_pred, test_label)
        r1 = recall_score(test_pred, test_label)
        acc = precision_score(test_pred, test_label)

        print('f1:{first} ****** precision:{second} ******recall:{third}'.format(first=f1, second=acc, third=r1))
