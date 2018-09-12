#-*-coding:utf-8-*-
import pandas as pd
import pickle
import numpy as np
from keras.utils import to_categorical
import jieba


class DataProcessor(object):
    """

    数据预处理，对训练集和测试集的数据进行onehot编码，label转化为哑变量
    Args:
        vocabBuidMinCount: 可以作为登录词的最小词频
        wordVocabPath: 基于词的词典保存路径
        charVocabPath: 基于字的词典保存路径

    """

    def __init__(self):
        self.vocabBuidMinCount = 1
        self.wordVocabPath = 'model_save/word2id.pkl'
        self.charVocabPath = 'model_save/char2id.pkl'
        self.senMaxLen = 32
        self.word2id, self.wordVocabSize = self.loadVocab(self.wordVocabPath)
        self.char2id, self.charVocabSize = self.loadVocab(self.charVocabPath)


    def readData(self,path):

        """

        读取数据
        Args:
            path: 数据存放路径

        Returns: dataframe格式的数据

        """

        df = pd.read_csv(path)
        return df

    def loadVocab(self,path):
        """

        载入词典
        Args:
            path: 词典路径

        Returns: 词典，词典长度

        """

        with open(path, 'rb') as fr:
            word2id = pickle.load(fr)
        return word2id, len(word2id)




    def vocabBuild(self, data,vocabpath):
        """

        构建词典
        Args:
            data: 用于构建词典的语料

        """


        word2id = {}


        for sent_ in data:

            cut_sent = jieba.cut(sent_)

            for word in cut_sent:

                if word in [',','。','.','?','!',' ']:
                    continue

                #是否是数字
                if word.isdigit():
                    word = '<NUM>'

                #是否是英文
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

        with open(self.wordVocabPath, 'wb') as fw:
            pickle.dump(word2id, fw)



    def sentence2id(self, data,lookUpTable):
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
            for word in sent:
                if word in [',','。','.','?','!',' ']:
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


    def pad_sequences(self, sequences, pad_mark=0):

        """

        如果句子长度不足self.senMaxLen，则补0。如果句子大于self.senMaxLen，则截取
        Args:
            sequences: onehot编码句子
            pad_mark: 填补数字

        Returns:

        """

        seq_list, seq_len_list = [], []
        for seq in sequences:
            seq = list(seq)
            seq_ = seq[:self.senMaxLen] + [pad_mark] * max(self.senMaxLen - len(seq), 0)
            seq_list.append(seq_)
            seq_len_list.append(min(len(seq), self.senMaxLen))
        return seq_list, seq_len_list


    def generateData(self,path):
        """

        生成网络接收的测试数据
        Args:
            path: 文本路径

        Returns: onehot编码文本

        """

        sequenceData = self.readData(path)

        text1 = self.sentence2id(np.array(sequenceData['text1']),self.word2id)

        text1WordID, text1SeqLenList = self.pad_sequences(text1)

        text2 = self.sentence2id(np.array(sequenceData['text2']),self.word2id)
        text2WordID, text2SeqLenList = self.pad_sequences(text2)

        text = np.concatenate(text1,text2)

        return np.asarray(text)




if __name__ == '__main__':

    myDataProcessor = DataProcessor()

    trainDf = myDataProcessor.readData('data/task3_train.csv')
    devDf = myDataProcessor.readData('data/task3_dev.csv')
    l1 = np.array(trainDf['text1']).tolist()
    l2 = np.array(trainDf['text2']).tolist()
    l3 = devDf['text1'].tolist()
    l4 = devDf['text2'].tolist()
    l1.extend(l2)
    l1.extend(l3)
    l1.extend(l4)


