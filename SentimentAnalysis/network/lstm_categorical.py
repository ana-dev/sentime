from keras import Sequential
from keras.backend import clear_session
from keras.layers import Embedding, LSTM, Dense, Dropout, Conv1D, MaxPooling1D
from keras.utils.np_utils import to_categorical
from network.logging_callback import LoggingCallback

import numpy as np

from network.validation_callback import ValidationCallback


class LSTMCategorical:
    def __init__(self, lstm_out, doc_len, dropout, batch_size, epoch_num, word_num=None, word_len=None, embedding_matrix=None):
        clear_session()

        if embedding_matrix is not None:
            word_num = embedding_matrix.shape[0]
            word_len = embedding_matrix.shape[1]

        model = Sequential()
        if embedding_matrix is not None:
            model.add(Embedding(word_num, word_len, weights=[embedding_matrix], trainable=False, input_length=doc_len))
        else:
            model.add(Embedding(word_num, word_len, input_length=doc_len))
        self.dropout = dropout/100
        model.add(Dropout(self.dropout))
        model.add(Conv1D(64, 5, activation='relu'))
        model.add(MaxPooling1D(pool_size=4))
        model.add(LSTM(lstm_out))
        categories_num = 2
        model.add(Dense(categories_num, activation='sigmoid'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        self.model = model
        self.word_num = word_num
        self.word_len = word_len
        self.doc_len = doc_len
        self.lstm_out = lstm_out
        self.batch_size = batch_size
        self.epoch_num = epoch_num
        self.history = None
        self.test_count = 0
        self.train_count = 0
        self.class_tag = {}
        self.name = 'lstm_conv'
        self.categories_num = categories_num
        self.epoch_logger = LoggingCallback()
        self.valid_callback = ValidationCallback()

    def get_epoch_predictions(self):
        epoch_target_tags = \
            {e: [self.class_tag[cls] for cls in clses] for e, clses in self.valid_callback.epoch_targets.items()}
        epoch_predicted_tags = \
            {e: [self.class_tag[cls] for cls in clses] for e, clses in self.valid_callback.epoch_outputs.items()}
        return epoch_target_tags, epoch_predicted_tags

    def train_by_sequences(self, train_sequences, train_tags, test_sequences, test_tags):
        # map model classes to valid tags
        unique_tags = set(train_tags + test_tags)
        self.class_tag = {}
        for tag, i in enumerate(sorted(unique_tags)):
            self.class_tag[i] = tag
        train_tags = to_categorical(train_tags)
        test_tags = to_categorical(test_tags)
        train_sequences = np.array(train_sequences)
        test_sequences = np.array(test_sequences)
        train_tags = np.array(train_tags)
        test_tags = np.array(test_tags)
        self.model.fit(train_sequences, train_tags,
                       validation_data=(test_sequences, test_tags), batch_size=self.batch_size, epochs=self.epoch_num,
                       callbacks=[self.epoch_logger, self.valid_callback])
