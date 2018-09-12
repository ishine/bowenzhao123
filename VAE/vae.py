import keras
import numpy as np
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import backend as K
from keras.models import Sequential, Model
from keras.layers import Input, LSTM, RepeatVector
from keras.layers.core import Flatten, Dense, Dropout, Lambda
from keras import objectives
from keras.layers.wrappers import Bidirectional
from keras.layers.embeddings import Embedding
from data import DataProcessor
from embeddingInit import pretrainedWord2Vec


class VAE(object):
    """

    使用基于LSTM的VAE进行数据增强
    Args:


    """


    def __init__(self):

        self.embeddingDim = 64
        self.batch_size = 64
        self.intermediate_dim = 32
        self.latent_dim = 100
        self.epsilon_std = 1.
        self.dataProcessor = DataProcessor()
        self.epochNum = 50

    def sampling(self, args):
        z_mean, z_log_sigma = args
        epsilon = K.random_normal(shape=(self.batch_size, self.latent_dim),
                                  mean=0., stddev=self.epsilon_std)
        return z_mean + z_log_sigma * epsilon

    def build(self):
        """
        Creates an LSTM Variational Autoencoder (VAE). Returns VAE, Encoder, Generator.

        # Arguments
            input_dim: int.
            timesteps: int, input timestep dimension.
            batch_size: int.
            intermediate_dim: int, output shape of LSTM.
            latent_dim: int, latent z-layer shape.
            epsilon_std: float, z-layer sigma.


        # References
            - [Building Autoencoders in Keras](https://blog.keras.io/building-autoencoders-in-keras.html)
            - [Generating sentences from a continuous space](https://arxiv.org/abs/1511.06349)
        """
        input = Input(shape=(self.dataProcessor.senMaxLen,),name='input')

        x = Embedding(input_dim=self.dataProcessor.wordVocabSize,
                                         output_dim=self.embeddingDim, input_length=self.dataProcessor.senMaxLen,
                                         name='embeddingLayer', mask_zero=True, trainable=False,
                                         embeddings_initializer=pretrainedWord2Vec)(input)

        # LSTM encoding
        h = Bidirectional(LSTM(self.intermediate_dim))(x)

        # VAE Z layer
        z_mean = Dense(self.latent_dim)(h)
        z_log_sigma = Dense(self.latent_dim)(h)


        # note that "output_shape" isn't necessary with the TensorFlow backend
        # so you could write `Lambda(sampling)([z_mean, z_log_sigma])`
        z = Lambda(self.sampling)([z_mean, z_log_sigma])

        # decoded LSTM layer
        decoder_h = LSTM(self.intermediate_dim, return_sequences=True)
        decoder_mean = LSTM(self.embeddingDim, return_sequences=True)

        h_decoded = RepeatVector(self.dataProcessor.senMaxLen)(z)
        h_decoded = decoder_h(h_decoded)

        # decoded layer
        x_decoded_mean = decoder_mean(h_decoded)

        # end-to-end autoencoder
        vae = Model(input, x_decoded_mean)

        def vae_loss(x, x_decoded_mean):
            xent_loss = objectives.mse(x, x_decoded_mean)
            kl_loss = - 0.5 * K.mean(1 + z_log_sigma - K.square(z_mean) - K.exp(z_log_sigma))
            loss = xent_loss + kl_loss
            return loss

        vae.compile(optimizer='adam', loss=vae_loss)

        return vae

    def train(self):
        """

        :return:
        """

        text1 = self.dataProcessor.generateData('task3_dev.csv')
        text2 = self.dataProcessor.generateData('task3_train.csv')
        text3 = self.dataProcessor.generateData('train.csv')
        text4 = self.dataProcessor.generateData('test.csv')
        text = np.concatenate((text1,text2,text3,text4),axis=0)

        early_stopping = EarlyStopping(monitor='val_loss', patience=8)
        checkpoint = ModelCheckpoint(filepath='{vae.h5',
                                     monitor='val_acc',
                                     save_best_only=True,
                                     save_weights_only=True,
                                     mode='auto')
        model = self.build()
        model.fit(text,text,epochs=self.epochNum,batch_size=self.batch_size,callbacks=[early_stopping,checkpoint])
