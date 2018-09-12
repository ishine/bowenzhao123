# 语义相似度匹配
* 该模型使用keras库进行编写，用于基于BiLSTM+静态注意力机制的语义相似度匹配。

## 配置
* Python3.6
* Tensorflow-gpu 1.2.1
* Numpy 1.14.5
* Keras 2.2.0
* jieba 0.39

## 使用
1. 下载data并存放于data文件夹中，data文件夹中预存放有task3_train.csv, task3_dev.csv, 分别是语义相似度的训练和测试文件。以及行政问答文件target.csv
2. 参数配置：参数配置文件在主文件中的config.py中。
3. 训练并测试模型，使用main.py直接运行即可

## 文件

1. main.py 主程序接口
2. config.py 参数配置文件，主要包括：<font color=gray,size=2>
<br>sysParamSetting # 用户不能更改的参数
<br>dataParamSetting  # 数据存放路径参数
<br>modelParamSetting  # 基础模练参数
<br>transferParamSetting  # 迁移学习模型参数
<br>classifyParamSetting  # 分类模型参数
<br>batch_size </font>

3. answerCreater 模型测试程序，包括getCandidateSet(获取候选集),AnswerSimilarity(相似度排序)，getAnswer(获取答案)1. trainWord2Vec.py：生成词向量模型
4. dataConstructor:用于数据生成和预处理
    * vocbaBuilder: 构建字典
    * getUserData: 获取用户数据，构建用于训练模型的文件
    * dataProcessor: onehot编码
    * dataSetCreate: 生成模型训练的Input数据
    * embeddingInitiate: 训练/加载词向量
    * candidateManager: 获取候选集
5. semanticMatchBuilder: 模型文件
    * semanticMatch: 构造基础模型
        * Bilateral Multi-perspective模型(bimpm)
        * compare Aggregate Factorized模型(comAggFact)
        * decomposable Attention模型(decompAtt)
        * trainByLargCorpus: 模型训练
    * semanticMatchTransfer:构造迁移模型
    * topicClassify: 构造分类模型
6. util: 辅助模块
    * modelTrainer: 基础的模型训练模块
    * modelEvaluator: 模型预测模块
    * util:辅助函数