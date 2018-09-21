# -*- coding: utf-8 -*-
import sys, pickle, os, random
import numpy as np
import jieba.posseg as pseg


## tags, BIEO
'''
tag2label = {"O": 0,
             "B-PER": 1, "I-PER": 2,
             "B-LOC": 3, "I-LOC": 4,
             "B-ORG": 5, "I-ORG": 6
             }

'''
tag2label = {"O": 0,
"B_INTEGER": 1,
"I_INTEGER": 2,
"E_INTEGER": 3,
"B_ORDINAL": 4,
"I_ORDINAL": 5,
"E_ORDINAL": 6,
"B_LOCATION": 7,
"I_LOCATION": 8,
"E_LOCATION": 9,
"B_DATE": 10,
"I_DATE": 11,
"E_DATE": 12,
"B_ORGANIZATION": 13,
"I_ORGANIZATION": 14,
"E_ORGANIZATION": 15,
"B_PERSON": 16,
"I_PERSON": 17,
"E_PERSON": 18,
"B_MONEY": 19,
"I_MONEY": 20,
"E_MONEY": 21,
"B_DURATION": 22,
"I_DURATION": 23,
"E_DURATION": 24,
"B_TIME": 25,
"I_TIME": 26,
"E_TIME": 27,
"B_LENGTH": 28,
"I_LENGTH": 29,
"E_LENGTH": 30,
"B_AGE": 31,
"I_AGE": 32,
"E_AGE": 33,
"B_FREQUENCY": 34,
"I_FREQUENCY": 35,
"E_FREQUENCY": 36,
"B_ANGLE": 37,
"I_ANGLE": 38,
"E_ANGLE": 39,
"B_PHONE": 40,
"I_PHONE": 41,
"E_PHONE": 42,
"B_PERCENT": 43,
"I_PERCENT": 44,
"E_PERCENT": 45,
"B_FRACTION": 46,
"I_FRACTION": 47,
"E_FRACTION": 48,
"B_WEIGHT": 49,
"I_WEIGHT": 50,
"E_WEIGHT": 51,
"B_AREA": 52,
"I_AREA": 53,
"E_AREA": 54,
"B_CAPACTITY": 55,
"I_CAPACTITY": 56,
"E_CAPACTITY": 57,
"B_DECIMAL": 58,
"I_DECIMAL": 59,
"E_DECIMAL": 60,
"B_MEASURE": 61,
"I_MEASURE": 62,
"E_MEASURE": 63,
"B_SPEED": 64,
"I_SPEED": 65,
"E_SPEED": 66,
"B_TEMPERATURE": 67,
"I_TEMPERATURE": 68,
"E_TEMPERATURE": 69,
"B_POSTALCODE": 70,
"I_POSTALCODE": 71,
"E_POSTALCODE": 72,
"B_RATE": 73,
"I_RATE": 74,
"E_RATE": 75,
"B_WWW": 76,
"I_WWW": 77,
"E_WWW": 78,
             }

posBondary2index = {'E_s': 111, 'E_r': 107, 'E_q': 103, 'E_p': 99, 'E_w': 143, 'E_v': 131,
                    'E_u': 123, 'E_t': 119, 'O_y': 148, 'E_y': 151, 'E_x': 147, 'E_ns': 83,
                    'E_c': 23, 'E_b': 19, 'E_a': 7, 'E_ad': 11, 'E_g': 43, 'E_f': 39, 'E_e': 35,
                    'E_d': 31, 'E_k': 59, 'E_j': 55, 'E_i': 51, 'I_dg': 26, 'E_o': 95, 'E_n': 75,
                    'E_m': 67, 'E_l': 63, 'I_o': 94, 'I_n': 74, 'I_m': 66, 'I_l': 62, 'I_k': 58,
                    'I_j': 54, 'I_i': 50, 'I_h': 46, 'I_g': 42, 'I_f': 38, 'I_e': 34, 'I_d': 30,
                    'I_c': 22, 'I_b': 18, 'I_a': 6, 'B_ad': 9, 'I_y': 150, 'I_x': 146, 'I_w': 142,
                    'I_v': 130, 'I_u': 122, 'E_dg': 27, 'I_s': 110, 'I_r': 106, 'I_q': 102, 'I_p': 98,
                    'I_zg': 178, 'B_mq': 185, 'B_vg': 125, 'B_vd': 133, 'E_Ng': 71, 'B_vn': 137,
                    'B_un': 157, 'B_nrt': 165, 'O_zg': 176, 'O_x': 144, 'B_ul': 173, 'B_m': 65,
                    'B_uj': 161, 'O_vd': 132, 'I_un': 158, 'O_vg': 124, 'O_ad': 8, 'E_nrt': 167,
                    'O_vn': 136, 'I_ud': 182, 'O_an': 12, 'I_nr': 78, 'I_ns': 82, 'I_nt': 86,
                    'E_an': 15, 'I_nz': 90, 'I_nrfg': 170, 'B_ud': 181, 'E_h': 47, 'O_Ng': 68,
                    'E_Ag': 3, 'B_Ag': 1, 'I_tg': 114, 'I_nrt': 166, 'I_mq': 186, 'O_nrfg': 168,
                    'B_tg': 113, 'B_h': 45, 'B_i': 49, 'B_j': 53, 'B_k': 57, 'B_l': 61, 'I_Ng': 70,
                    'B_n': 73, 'B_o': 93, 'B_a': 5, 'B_b': 17, 'B_c': 21, 'B_d': 29, 'B_e': 33,
                    'B_f': 37, 'B_g': 41, 'B_x': 145, 'B_y': 149, 'B_z': 153, 'B_p': 97, 'B_q': 101,
                    'B_r': 105, 'B_s': 109, 'B_t': 117, 'B_u': 121, 'B_v': 129, 'B_w': 141, 'I_Ag': 2,
                    'O_tg': 112, 'I_ul': 174, 'I_uj': 162, 'E_uj': 163, 'E_un': 159, 'E_ul': 175,
                    'E_ud': 183, 'E_nrfg': 171, 'I_z': 154, 'B_nrfg': 169, 'I_vn': 138, 'I_vg': 126,
                    'I_vd': 134, 'B_an': 13, 'O_nz': 88, 'O_nt': 84, 'O_nr': 76, 'O_ns': 80,
                    'I_t': 118, 'O_Ag': 0, 'E_tg': 115, 'B_zg': 177, 'E_z': 155, 'O_mq': 184, 'B_nz': 89,
                    'B_dg': 25, 'B_ns': 81, 'B_nr': 77, 'B_nt': 85, 'O_u': 120, 'O_t': 116, 'O_w': 140,
                    'O_v': 128, 'E_nz': 91, 'O_p': 96, 'O_s': 108, 'I_ad': 10, 'E_nt': 87, 'E_nr': 79,
                    'I_an': 14, 'O_z': 152, 'O_e': 32, 'O_d': 28, 'O_g': 40, 'O_f': 36, 'O_a': 4,
                    'O_c': 20, 'O_b': 16, 'O_m': 64, 'O_l': 60, 'O_o': 92, 'O_n': 72, 'O_i': 48,
                    'O_h': 44, 'O_k': 56, 'O_j': 52, 'O_ul': 172, 'O_un': 156, 'O_uj': 160, 'O_ud': 180,
                    'O_q': 100, 'E_mq': 187, 'O_r': 104, 'B_Ng': 69, 'E_zg': 179, 'E_vg': 127, 'E_vd': 135,
                    'O_dg': 24, 'E_vn': 139, 'O_nrt': 164,'uk':188}

'''
posBondary2index = {'I_DER': 34, 'I_M': 70, 'I_DEV': 38, 'B_CS': 21, 'I_DEC': 26, 'I_DEG': 30, 'B_CD': 17, 'B_CC': 13, 'E_P': 99, 'E_PN': 103, 'E_PU': 107, 'E_ON': 95, 'E_OD': 91, 'E_M': 71, 'E_VC': 123, 'O_PU': 104, 'I_LB': 62, 'I_LC': 66, 'I_DT': 42, 'I_SP': 114, 'B_LC': 65, 'B_LB': 61, 'O_PN': 100, 'I_SB': 110, 'I_MSP': 74, 'E_NT': 87, 'E_NR': 83, 'E_NN': 79, 'E_FW': 51, 'O_VA': 116, 'B_DT': 41, 'O_ETC': 44, 'O_NN': 76, 'I_ON': 94, 'E_AS': 7, 'B_IJ': 53, 'B_AS': 5, 'I_VA': 118, 'I_VE': 126, 'E_AD': 3, 'B_MSP': 73, 'O_NT': 84, 'E_SB': 111, 'I_VV': 130, 'O_NR': 80, 'O_AD': 0, 'E_IJ': 55, 'I_PN': 102, 'I_P': 98, 'O_VE': 124, 'B_M': 69, 'O_VC': 120, 'I_NN': 78, 'I_FW': 50, 'B_SB': 109, 'B_JJ': 57, 'I_NR': 82, 'O_AS': 4, 'O_IJ': 52, 'I_NT': 86, 'B_P': 97, 'B_SP': 113, 'B_BA': 9, 'O_FW': 48, 'E_ETC': 47, 'O_VV': 128, 'B_ETC': 45, 'B_PU': 105, 'I_IJ': 54, 'I_PU': 106, 'B_ON': 93, 'O_LB': 60, 'O_LC': 64, 'B_OD': 89, 'E_CS': 23, 'E_CD': 19, 'B_PN': 101, 'E_CC': 15, 'B_VV': 129, 'I_AD': 2, 'I_AS': 6, 'I_OD': 90, 'O_ON': 92, 'O_DEV': 36, 'O_OD': 88, 'O_DER': 32, 'E_BA': 11, 'O_DEG': 28, 'O_DEC': 24, 'E_JJ': 59, 'O_DT': 40, 'B_DEV': 37, 'B_DER': 33, 'B_DEG': 29, 'E_SP': 115, 'B_DEC': 25, 'O_P': 96, 'E_DEG': 31, 'E_DEC': 27, 'B_VC': 121, 'O_M': 68, 'B_VA': 117, 'O_MSP': 72, 'B_VE': 125, 'E_DEV': 39, 'I_VC': 122, 'O_JJ': 56, 'O_SP': 112, 'E_DER': 35, 'E_VV': 131, 'O_CS': 20, 'I_CC': 14, 'I_ETC': 46, 'I_CD': 18, 'E_VE': 127, 'B_AD': 1, 'E_VA': 119, 'O_CC': 12, 'E_MSP': 75, 'I_CS': 22, 'O_CD': 16, 'O_SB': 108, 'B_NN': 77, 'E_DT': 43, 'B_NR': 81, 'I_JJ': 58, 'B_NT': 85, 'I_BA': 10, 'E_LB': 63, 'E_LC': 67, 'B_FW': 49, 'O_BA': 8,'uk':132}
'''

LENGTH_OF_POSBOUNDARY = 189



def read_corpus(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    with open(corpus_path+'.txt', encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            [char, label] = line.strip().split()
            sent_.append(char)
            tag_.append(label)
        else:
            data.append((sent_, tag_))
            sent_, tag_ = [], []

    return data


def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <='\u005a') or ('\u0061' <= word <='\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id)+1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

    #print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):

    """
    给句子里的每个词，都找到word2id里对应的序列标号
    :param sent:
    :param word2id:
    :return:
    """

    sentence_id = []
    for word in sent:
        if word.isdigit():
            word = '<NUM>'
        elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
            word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])



    return sentence_id


def read_dictionary(vocab_path):
    """

    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    #print('vocab_size:', len(word2id))
    return word2id


def random_embedding(vocab, embedding_dim):
    """

    :param vocab:
    :param embedding_dim:
    :return:
    """
    #embedding层的输入是整个词袋大小，输出为为自己设定的参数值，embedding_dim
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))

    embedding_mat = np.float32(embedding_mat)

    return embedding_mat


def pad_sequences(sequences, pad_mark=0):

    """
    将一个batch里的label全都按照序列长度最长的序列进行补全。补全值：0
    :param sequences:labels
    :param pad_mark:
    :return:
    """

    max_len = max(map(lambda x : len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def getPosBoundary(sent):

    '''
    对sentence产生 pos&bondary 特征
    :param sent:
    :return:句子中每一个字对应的词性词边界词典中的ID

    '''

    posBoundaryIndex = []
    sent = ''.join(sent)

    #jieba进行分词
    res = pseg.cut(sent)

    #stanfordcoreNLP进行分词和词性标注
    #res = posModel.pos_tag(sent)
    #print('sent',sent)
    #print('res',res)
    for w in res:

        #jieba分词和词性标注
        _word = w.word
        posTag = w.flag
        #print('w',w)


        '''
        #stanford分词和词性标注
        _word = w[0]
        posTag = w[1]
        '''


        for k in range(len(_word)):

            #print('_word',_word)

            _char = _word[k]
            if len(_word) == 1:
                _tag = 'O'+'_'+posTag
            elif k == 0:
                _tag = 'B'+'_'+posTag
            elif k == len(_word)-1:
                _tag = 'E'+'_'+posTag
            else:
                _tag = 'I'+'_'+posTag
            if _tag not in posBondary2index:
                #print('_tag',_tag)
                _tag = 'uk'
            index = posBondary2index[_tag]
            posBoundaryIndex.append(index)

    #print(posBoundaryIndex)
    return posBoundaryIndex


def generatePosBoundaryMatrix(posBoundaryID):

    '''
    根据id生成词性词边界矩阵
    :return:[字1词性词边界向量，字2词性词边界向量，....，字l词性词边界向量]
    [字1词性词边界行向量，
    字2词性词边界行向量，
    ...,
    字l词性词边界向量]
    '''

    length = len(posBoundaryID)
    _mat = []

    for i in range(len(posBoundaryID)):

        index = posBoundaryID[i]
        _vec = np.zeros((LENGTH_OF_POSBOUNDARY)) #生成一个行向量
        _vec[index] = 1                         #激活代表特征的对应维度
        _mat.append(_vec)

    mat = _mat

    #print('mat.shape',len(mat),len(mat[0]))

    return mat


def pad_pos_mat(_pos_mat):

    '''
    填充词性词边界特征矩阵
    :param _pos_mat:
    :return:
    '''

    max_len = max(map(lambda x : len(x), _pos_mat))
    mat = []
    #print('shape',np.asarray(_pos_mat).shape)
    #print('len',len(_pos_mat[0][0]))

    #print('_pos_mat_shape',len(_pos_mat),len(_pos_mat[0]),len(_pos_mat[0][0]))

    for i in range(len(_pos_mat)):
        # 第i个样本
        if len(_pos_mat[i]) == max_len:

            mat.append(_pos_mat[i])
            continue
        tmp = _pos_mat[i]

        for j in range(max_len-len(_pos_mat[i])):
            tmp.append(np.zeros(LENGTH_OF_POSBOUNDARY))

        mat.append(tmp)

    return mat

























def batch_yield(data, batch_size, vocab, tag2label,shuffle=False):


    """
    给原始的训练数据中的句子中的每个词找到它的word2id里的id
    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """

    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    pos_info = []
    for (sent_, tag_) in data:

        # 生成词性词边界信息
        posID = getPosBoundary(sent=sent_)

        sent_ = sentence2id(sent_, vocab)


        pos_mat = generatePosBoundaryMatrix(posID)

        label_ = [tag2label[tag] for tag in tag_]

        if len(seqs) == batch_size:
            yield seqs, labels, pos_info
            seqs, labels = [], []
            pos_info = []

        seqs.append(sent_)
        labels.append(label_)
        pos_info.append(pos_mat)

    if len(seqs) != 0:
        yield seqs, labels, pos_info


