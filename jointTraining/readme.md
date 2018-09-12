# 联合训练
* 该模型使用keras库进行编写，基础模型使用语义匹配的CompAggFact模型。
* 文献参考：Adversarial Multi-task Learning for Text Classification

## 配置
* Python3.6
* Tensorflow-gpu 1.2.1
* Numpy 1.14.5
* Keras 2.2.0
* jieba 0.39

## 使用
1. 参数配置：参数配置文件在主文件中的config.py中。
2. 训练并测试模型，使用main.py直接运行即可

## 文件

1. main.py 主程序接口
2. config.py 参数配置文件，主要包括：<font color=gray,size=2>
<br>sysParamSetting # 用户不能更改的参数
<br>dataParamSetting  # 数据存放路径参数
<br>modelParamSetting  # 基础模练参数
<br>jointTaskParamSetting  # 联合学习模型参数
<br>batch_size </font>

3. dataConstructor:用于数据生成和预处理
    * vocbaBuilder: 构建字典
    * dataProcessor: onehot编码
    * embeddingInitiate: 训练/加载词向量
4. basicModelBuilder: 基础模型
    * semanticMatchLayer:构造预训练模型(comAggFact)
    * trainByLargCorpus: 模型在源数据集上的预训练
5. util: 辅助模块
    * modelTrainer: 基础的模型训练模块
    * modelEvaluator: 模型预测模块
    * util:辅助函数
6. 