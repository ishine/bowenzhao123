# -*- coding: utf-8 -*-
import numpy as np
import os, time, sys
import tensorflow as tf
from tensorflow.contrib.rnn import LSTMCell
from tensorflow.contrib.crf import crf_log_likelihood
from tensorflow.contrib.crf import viterbi_decode
from ...src.NER.data import pad_sequences, batch_yield, pad_pos_mat
from ...src.NER.utils import get_logger
from ...src.NER.eval import conlleval
# from stanfordcorenlp import StanfordCoreNLP



class BiLSTM_CRF(object):
    def __init__(self, embeddings, tag2label, vocab):
        self.batch_size = 64
        self.epoch_num = 40
        self.hidden_dim = 300
        self.embeddings = embeddings
        self.CRF = True
        self.update_embedding = True
        self.dropout_keep_prob = 0.5
        self.optimizer = 'Adam'
        self.lr = 0.001
        self.clip_grad = 5.0
        self.tag2label = tag2label
        self.num_tags = len(tag2label)
        self.vocab = vocab
        self.shuffle = True
        self.model_path = 'data/'
        self.summary_path = 'data/'
        self.logger = 'data/'
        self.result_path = 'data/'
        print ("I am loading the stanford model....\n")
        '''
        self.stanford_model = StanfordCoreNLP(r'model/NER/stanford-corenlp/',
                                         lang='zh')
        '''
        print('loading success!\n')


    def build_graph(self):
        self.add_placeholders()
        self.lookup_layer_op() #embedding层操作
        self.merge_layer_op() #连接字向量与词性词边界向量操作
        self.biLSTM_layer_op() #双向LSTM
        self.softmax_pred_op()
        self.loss_op()         #计算loss
        self.trainstep_op()
        self.init_op()

    def add_placeholders(self):

        #placeholder作用：接收网络的输入数据

        #word_ids 用来查找返回word_embedding层中的哪些列的权重
        self.word_ids = tf.placeholder(tf.int32, shape=[None, None], name="word_ids")

        #接收label信息
        self.labels = tf.placeholder(tf.int32, shape=[None, None], name="labels")

        #接收序列长度序列
        self.sequence_lengths = tf.placeholder(tf.int32, shape=[None], name="sequence_lengths")

        #接收词性词边界信息 ******** 自己添加的,最后一维一定要指定确定的数值
        self.posBoundary = tf.placeholder(tf.float32,shape=[None,None,189],name="posBoundary")

        self.dropout_pl = tf.placeholder(dtype=tf.float32, shape=[], name="dropout")
        self.lr_pl = tf.placeholder(dtype=tf.float32, shape=[], name="lr")


    def lookup_layer_op(self):
        with tf.variable_scope("words"):

            #self.embeddings 初始化的值，默认随机初始化，也可以使用预训练的值
            #update_embedding 布尔值，在训练时是否更新embedding层的权重

            _word_embeddings = tf.Variable(self.embeddings,
                                           dtype=tf.float32,
                                           trainable=self.update_embedding,
                                           name="_word_embeddings")

            #params embedding层的初始权重
            #ids token的ID，用来查找返回word_embedding里的权重

            word_embeddings = tf.nn.embedding_lookup(params=_word_embeddings,
                                                     ids=self.word_ids,
                                                     name="word_embeddings")
        #随机断开链接，增加泛化能力
        self.word_embeddings =  tf.nn.dropout(word_embeddings, self.dropout_pl)


    def merge_layer_op(self):

        '''
        ***************
        自己增加的层，目的：将字向量与词性词边界向量拼接起来
        ***************
        :return:
        '''
        with tf.variable_scope('merge'):

            #将embedding的字向量和词性词边界向量进行连接
            self.mergedTensor = tf.concat([self.word_embeddings,self.posBoundary],axis=-1)







    def biLSTM_layer_op(self):
        with tf.variable_scope("bi-lstm"):

            #前向LSTM
            cell_fw = LSTMCell(self.hidden_dim)
            #后向LSTM
            cell_bw = LSTMCell(self.hidden_dim)

            (output_fw_seq, output_bw_seq), _ = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cell_fw,
                cell_bw=cell_bw,

                #不加入外部信息
                #inputs=self.word_embeddings,

                #加入外部信息
                inputs=self.mergedTensor,

                sequence_length=self.sequence_lengths,

                dtype=tf.float32)

            #前向和后向LSTM的中间输出进行连接操作
            output = tf.concat([output_fw_seq, output_bw_seq], axis=-1)

            #随机断开self.dropout_pl比例的连接，增加模型的泛化能力
            output = tf.nn.dropout(output, self.dropout_pl)


        #softmax层，预测当前位点的字或者词在每个类别的概率
        with tf.variable_scope("proj"):
            W = tf.get_variable(name="W",
                                shape=[2 * self.hidden_dim, self.num_tags],
                                initializer=tf.contrib.layers.xavier_initializer(),
                                dtype=tf.float32)

            b = tf.get_variable(name="b",
                                shape=[self.num_tags],
                                initializer=tf.zeros_initializer(),
                                dtype=tf.float32)

            s = tf.shape(output)
            output = tf.reshape(output, [-1, 2*self.hidden_dim])
            pred = tf.matmul(output, W) + b

            self.logits = tf.reshape(pred, [-1, s[1], self.num_tags])

    def loss_op(self):

        #计算loss值

        if self.CRF:
            #biLSTM后接CRF的情况，用crf_log_likelihood来计算损失
            log_likelihood, self.transition_params = crf_log_likelihood(inputs=self.logits,
                                                                   tag_indices=self.labels,
                                                                   sequence_lengths=self.sequence_lengths)
            self.loss = -tf.reduce_mean(log_likelihood)

        else:
            #biLSTM后不接CRF的情况，直接用交叉熵来计算损失。
            losses = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=self.logits,
                                                                    labels=self.labels)
            mask = tf.sequence_mask(self.sequence_lengths)
            losses = tf.boolean_mask(losses, mask)
            self.loss = tf.reduce_mean(losses)

        tf.summary.scalar("loss", self.loss)

    def softmax_pred_op(self):

        # 在biLSTM后不接CRF的情况：直接对biLSTM的输出进行分类

        if not self.CRF:

            #返回概率值最大的那个类别的概率
            self.labels_softmax_ = tf.argmax(self.logits, axis=-1)

            #转化数据格式，转成int型
            self.labels_softmax_ = tf.cast(self.labels_softmax_, tf.int32)

    def trainstep_op(self):
        with tf.variable_scope("train_step"):

            # 优化算法选择
            self.global_step = tf.Variable(0, name="global_step", trainable=False)
            if self.optimizer == 'Adam':
                optim = tf.train.AdamOptimizer(learning_rate=self.lr_pl)
            elif self.optimizer == 'Adadelta':
                optim = tf.train.AdadeltaOptimizer(learning_rate=self.lr_pl)
            elif self.optimizer == 'Adagrad':
                optim = tf.train.AdagradOptimizer(learning_rate=self.lr_pl)
            elif self.optimizer == 'RMSProp':
                optim = tf.train.RMSPropOptimizer(learning_rate=self.lr_pl)
            elif self.optimizer == 'Momentum':
                optim = tf.train.MomentumOptimizer(learning_rate=self.lr_pl, momentum=0.9)
            elif self.optimizer == 'SGD':
                optim = tf.train.GradientDescentOptimizer(learning_rate=self.lr_pl)
            else:
                optim = tf.train.GradientDescentOptimizer(learning_rate=self.lr_pl)

            grads_and_vars = optim.compute_gradients(self.loss)
            grads_and_vars_clip = [[tf.clip_by_value(g, -self.clip_grad, self.clip_grad), v] for g, v in grads_and_vars]
            self.train_op = optim.apply_gradients(grads_and_vars_clip, global_step=self.global_step)

    def init_op(self):
        self.init_op = tf.global_variables_initializer()

    def add_summary(self, sess):
        """

        :param sess:
        :return:
        """
        self.merged = tf.summary.merge_all()
        self.file_writer = tf.summary.FileWriter(self.summary_path, sess.graph)

    def train(self, train, dev):
        """

        :param train:
        :param dev:
        :return:
        """

        '''
        Saver类提供了向checkpoints文件保存和从checkpoints文件中恢复变量的相关方法。
        
        Checkpoints文件是一个二进制文件，它把变量名映射到对应的tensor值 。
        
        只要提供一个计数器，当计数器触发时，Saver类可以自动的生成checkpoint文件。这让我们可以在训练过程中保存多个中间结果。例如，我们可以保存每一步训练的结果。
        为了避免填满整个磁盘，
        
        Saver可以自动的管理Checkpoints文件。例如，我们可以指定保存最近的N个Checkpoints文件。

        '''
        saver = tf.train.Saver(tf.global_variables())

        with tf.Session() as sess:
            sess.run(self.init_op)
            self.add_summary(sess)

            #迭代训练模型
            for epoch in range(self.epoch_num):
                #一次迭代训练模型
                self.run_one_epoch(sess, train, dev, self.tag2label, epoch, saver)

    def test(self, test):
        saver = tf.train.Saver()
        with tf.Session() as sess:
            self.logger.info('=========== testing ===========')
            #加载训练好的模型
            saver.restore(sess, self.model_path)
            label_list, seq_len_list = self.dev_one_epoch(sess, test)
            self.evaluate(label_list, seq_len_list, test)

    def demo_one(self, sess, sent):
        """

        :param sess:
        :param sent: 
        :return:
        """
        label_list = []
        for seqs, labels,pos_info in batch_yield(sent, self.batch_size, self.vocab, self.tag2label,shuffle=False):
            label_list_, _ = self.predict_one_batch(sess, seqs,pos_info=pos_info)
            label_list.extend(label_list_)
        label2tag = {}
        for tag, label in self.tag2label.items():
            label2tag[label] = tag if label != 0 else label
        tag = [label2tag[label] for label in label_list[0]]
        return tag

    def run_one_epoch(self, sess, train, dev, tag2label, epoch, saver):
        """

        :param sess:
        :param train:
        :param dev:
        :param tag2label:
        :param epoch:
        :param saver:
        :return:
        """

        #将训练集分成多少个batch
        num_batches = (len(train) + self.batch_size - 1) // self.batch_size

        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        #将训练集生成batch输入数据
        batches = batch_yield(train, self.batch_size, self.vocab, self.tag2label,shuffle=self.shuffle)
        for step, (seqs, labels, pos_info) in enumerate(batches):

            sys.stdout.write(' processing: {} batch / {} batches.'.format(step + 1, num_batches) + '\r')
            step_num = epoch * num_batches + step + 1
            feed_dict, _ = self.get_feed_dict(seqs, pos_info, labels, self.lr, self.dropout_keep_prob)

            _, loss_train, summary, step_num_ = sess.run([self.train_op, self.loss, self.merged, self.global_step],
                                                         feed_dict=feed_dict)
            if step + 1 == 1 or (step + 1) % 300 == 0 or step + 1 == num_batches:
                self.logger.info(
                    '{} epoch {}, step {}, loss: {:.4}, global_step: {}'.format(start_time, epoch + 1, step + 1,
                                                                                loss_train, step_num))

            self.file_writer.add_summary(summary, step_num)

            if step + 1 == num_batches:
                saver.save(sess, self.model_path, global_step=step_num)

        self.logger.info('===========validation / test===========')
        label_list_dev, seq_len_list_dev = self.dev_one_epoch(sess, dev)
        self.evaluate(label_list_dev, seq_len_list_dev, dev, epoch)

    def get_feed_dict(self, seqs, pos_info,labels=None, lr=None, dropout=None):
        """

        :param seqs:
        :param labels:
        :param lr:
        :param dropout:
        :return: feed_dict
        """
        word_ids, seq_len_list = pad_sequences(seqs, pad_mark=0)
        #print(word_ids)
        feed_dict = {self.word_ids: word_ids,
                     self.sequence_lengths: seq_len_list,
                     }
        if labels is not None:

            #按照batch里序列长度最长的那个序列长度，给label补0, why???

            labels_, _ = pad_sequences(labels, pad_mark=0)

            feed_dict[self.labels] = labels_

        #增加词性词边界矩阵信息，并进行填充
        #if pos_info is not None:

        mat = pad_pos_mat(pos_info)
        feed_dict[self.posBoundary] = np.asarray(mat)
        #print('!'*20)
        #print(feed_dict[self.posBoundary].shape)




        if lr is not None:
            feed_dict[self.lr_pl] = lr
        if dropout is not None:
            feed_dict[self.dropout_pl] = dropout

        return feed_dict, seq_len_list

    def dev_one_epoch(self, sess, dev):
        """

        :param sess:
        :param dev:
        :return:
        """
        label_list, seq_len_list = [], []

        #按照batch来进行预测

        for seqs, labels,pos_info in batch_yield(dev, self.batch_size, self.vocab, self.tag2label,shuffle=False):
            label_list_, seq_len_list_ = self.predict_one_batch(sess, seqs,pos_info)
            label_list.extend(label_list_)
            seq_len_list.extend(seq_len_list_)
        return label_list, seq_len_list

    def predict_one_batch(self, sess, seqs,pos_info):
        """

        :param sess:
        :param seqs:
        :return: label_list
                 seq_len_list
        """
        feed_dict, seq_len_list = self.get_feed_dict(seqs, pos_info=pos_info,dropout=1.0)

        if self.CRF:
            logits, transition_params = sess.run([self.logits, self.transition_params],
                                                 feed_dict=feed_dict)
            label_list = []
            for logit, seq_len in zip(logits, seq_len_list):
                viterbi_seq, _ = viterbi_decode(logit[:seq_len], transition_params)
                label_list.append(viterbi_seq)
            return label_list, seq_len_list

        else:
            label_list = sess.run(self.labels_softmax_, feed_dict=feed_dict)
            return label_list, seq_len_list

    def evaluate(self, label_list, seq_len_list, data, epoch=None):
        """

        :param label_list:
        :param seq_len_list:
        :param data:
        :param epoch:
        :return:
        """
        label2tag = {}
        for tag, label in self.tag2label.items():
            label2tag[label] = tag if label != 0 else label

        model_predict = []
        for label_, (sent, tag) in zip(label_list, data):
            tag_ = [label2tag[label__] for label__ in label_]
            sent_res = []
            if  len(label_) != len(sent):
                print(sent)
                print(len(label_))
                print(tag)
            for i in range(len(sent)):
                sent_res.append([sent[i], tag[i], tag_[i]])
            model_predict.append(sent_res)
        epoch_num = str(epoch+1) if epoch != None else 'test'
        label_path = os.path.join(self.result_path, 'label_' + epoch_num)
        metric_path = os.path.join(self.result_path, 'result_metric_' + epoch_num)
        for _ in conlleval(model_predict, label_path, metric_path):
            self.logger.info(_)

