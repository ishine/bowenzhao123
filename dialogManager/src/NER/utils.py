import logging, sys, argparse
from ...src.NER.data import tag2label


def str2bool(v):
    # copy from StackOverflow
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')



def get_label_to_tagName(label):

    for key in tag2label.keys():
        #print(key,label)
        if tag2label[key] == label:

            return key


def get_entity_dic(tag_seq,char_seq):

    '''
    取出预测序列中的所有entity

    :param tag_seq:
    :param char_seq:
    :return:
    '''
    entityDic = {}

    last_label = 'O'
    last_boudary = 'O'
    _word = ''

    for i in range(len(tag_seq)):
        _tag = tag_seq[i]
        _char = char_seq[i]


        if _tag == '0' or _tag == 0 or _tag == 'O':


            #如果之前有没有压进字典的实体的话， 将它压进字典
            if _word != '':
                if last_label not in entityDic:
                    entityDic[last_label] = []
                entityDic[last_label].append(_word)
                _word = ''

            last_boudary = _tag
            last_label = _tag

            continue

        boundary, label = _tag.split('_')
        if label not in entityDic:
            entityDic[label] = []



        if boundary == 'B':
            if _word != '':
                if last_label not in entityDic:
                    entityDic[last_label] = []
                entityDic[last_label].append(_word)
                _word = ''

            _word = _char

        elif label == last_label:
            _word = _word + _char

        elif label!=last_label:
            if _word != '':
                if last_label not in entityDic:
                    entityDic[last_label] = []
                entityDic[last_label].append(_word)
            _word = _char

        if boundary == 'E' and label == last_label:
            entityDic[label].append(_word)
            _word = '' #_word清空

        last_boudary = boundary
        last_label = label

    if _word!='':
        if last_label not in entityDic:
            entityDic[last_label] = []
        entityDic[last_label].append(_word)
        _word = ''
    return entityDic

def entityLinking(tag_seq, char_seq):

        '''
        将BIOE标签合并成词并且找到其上下文
        :param res: list，命名实体模型识别结果,命名实体开始下标，命名实体结束下标
        res = {LOCATION:[('上海'，0,2)]}

        '''

        entityDic = {}

        last_label = '0'
        _word = ''

        start_index = 0
        end_index = 0

        for i in range(len(tag_seq)):
            _tag = tag_seq[i]
            _char = char_seq[i]

            if _tag == '0' or _tag == 0 or _tag == 'O':

                # 如果之前有没有压进字典的实体的话， 将它压进字典
                if _word != '':

                    end_index = i

                    if last_label not in entityDic:
                        entityDic[last_label] = []
                    entityDic[last_label].append((_word, start_index, end_index))
                    _word = ''
                last_label = _tag
                continue

            boundary, label = _tag.split('_')
            if label not in entityDic:
                entityDic[label] = []

            if boundary == 'B':
                # start_index = i
                if _word != '':
                    if last_label not in entityDic:
                        entityDic[last_label] = []
                    end_index = i
                    entityDic[last_label].append((_word, start_index, end_index))
                    _word = ''
                else:
                    start_index = i
                _word = _char

            elif label == last_label:
                _word = _word + _char

            elif label != last_label:
                if _word != '':
                    if last_label not in entityDic:
                        entityDic[last_label] = []
                    end_index = i
                    entityDic[last_label].append((_word, start_index, end_index))

                start_index = i
                _word = _char

            if boundary == 'E' and label == last_label:
                end_index = i
                entityDic[label].append((_word, start_index, end_index))
                _word = ''  # _word清空

            last_label = label

        if _word != '':
            end_index = len(tag_seq)-1
            if last_label not in entityDic:
                entityDic[last_label] = []
            entityDic[last_label].append((_word,start_index,end_index))
            _word = ''
        return entityDic


def get_logger(filename):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    handler = logging.FileHandler(filename)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logging.getLogger().addHandler(handler)
    return logger
