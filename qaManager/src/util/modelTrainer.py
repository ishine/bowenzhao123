# -*- coding: utf-8 -*-
# @Time : 2018/9/4 2:09 PM
# @Author : ZHAOBOWEN467@pingan.com.cn
# @File : modelTrainer.py
# @Software: PyCharm
# @desc:

from keras.callbacks import EarlyStopping, ModelCheckpoint

class ModelTrainer(object):
    """ 构造一个基本的train函数
    Attributes:
        model: 构建好的网络模型
        savePath: 训练好的模型保存位置
    """
    def __init__(self,model,savePath,epochs,batch_size):

        self.model = model
        self.savePath = savePath
        self.epochs = epochs
        self.batch_size = batch_size


    def trainModel(self,feed_dict,target,validation_data=None):
        """ 训练并保存模型

        Args:
            feed_dict: 训练数据的自变量
            target: 训练数据标签
        Return:
        """
        early_stopping = EarlyStopping(monitor='val_loss', patience=8)
        checkpoint = ModelCheckpoint(
            filepath=self.savePath,
            monitor='val_acc',
            save_best_only=True,
            save_weights_only=True,
            mode='auto')
        if validation_data is None:
            self.model.fit(feed_dict, target, shuffle=True,
                           epochs=self.epochs, validation_split=.2, batch_size=self.batch_size,
                           callbacks=[early_stopping, checkpoint])
        else:
            self.model.fit(feed_dict, target, shuffle=True,
                           epochs=self.epochs, validation_data=validation_data, batch_size=self.batch_size,
                           callbacks=[early_stopping, checkpoint])
