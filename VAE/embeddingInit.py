import gensim
import pickle
import numpy as np

def pretrainedWord2Vec(shape,dtype=None):
    """

    Args: 使用预训练的word2vec初始化embedding层
        shape: [batch_size,time_step,embedding_dim]
        dtype: float64

    Returns: embedding matrix

    """

    mat = np.zeros(shape=shape)

    # 该位置载入预训练的词向量
    word2Vec = gensim.models.KeyedVectors.load_word2vec_format('model_save/news_12g_baidubaike_20g_novel_90g_embedding_64.bin',binary=True)

    with open('model_save/word2id.pkl', 'rb') as fr:
            word2id = pickle.load(fr)

    for _word in word2id:

        _word = str(_word)
        index = int(word2id[_word])

        if _word in word2Vec:
            mat[index] = word2Vec[_word].T
        else:
            _tmp = np.random.uniform(-0.25,0.25,(1,shape[-1]))
            mat[index] =_tmp

    return mat


def pretrainedChar2Vec(shape,dtype=None):
    """

    Args: 使用预训练的字向量初始化embedding层
        shape: [batch_size,time_step,embedding_dim]
        dtype: float64

    Returns: embedding matrix

    """

    mat = np.zeros(shape=shape)

    # 载入预训练好的基于字的word2vec模型
    word2Vec = gensim.models.KeyedVectors.load_word2vec_format('model_save/myChar2vec.bin.gz',binary=True)


    with open('model_save/char2id.pkl', 'rb') as fr:
            word2id = pickle.load(fr)

    for _word in word2id:

        _word = str(_word)
        index = int(word2id[_word])

        if _word in word2Vec:
            mat[index] = word2Vec[_word].T
        else:
            _tmp = np.random.uniform(-0.25,0.25,(1,shape[-1]))
            mat[index] =_tmp

    return mat 





