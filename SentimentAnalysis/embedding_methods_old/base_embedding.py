from dataio.csv import read_embedding_dictionary, read_word_to_index
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from embedding_methods_old.one_hot import OneHot


class BaseEmbedding:
    pad_word = "<<PAD>>"
    unknown_word = "<<UNKNOWN>>"

    def __init__(self, embedding_dictionary, embedding_dim, word_to_index, doc_len):
        self.name = 'base'
        self.doc_len = doc_len
        self.embedding_dim = embedding_dim
        self.embedding_dictionary = embedding_dictionary
        self.word_to_index = word_to_index
        self.complete_dictionary_with_pad()
        self.complete_dictionary_with_unknown()
        self.word_num = len(word_to_index)
        self.embedding_matrix = self.get_embedding_matrix()

    def get_word_dictionary(self):
        word_dictionary = {}
        for word, index in self.word_to_index.items():
            word_dictionary[word] = (index, self.embedding_matrix[index])
        return word_dictionary

    def complete_dictionary_with_pad(self, pad_index=0):
        if self.pad_word in self.word_to_index.keys():
            old_pad_index = self.word_to_index[self.pad_word]
        else:
            old_pad_index = sorted(self.word_to_index.values())[-1] + 1
        if old_pad_index > pad_index:
            for word, index in self.word_to_index.items():
                if pad_index <= index < old_pad_index:
                    self.word_to_index[word] = index + 1
        elif old_pad_index > pad_index:
            for word, index in self.word_to_index.items():
                if old_pad_index < index <= pad_index:
                    self.word_to_index[word] = index - 1
        self.word_to_index[self.pad_word] = pad_index

    def complete_dictionary_with_unknown(self, unknown_index=1):
        if self.unknown_word in self.word_to_index.keys():
            old_unknown_index = self.word_to_index[self.unknown_word]
        else:
            old_unknown_index = sorted(self.word_to_index.values())[-1] + 1
        if old_unknown_index > unknown_index:
            for word, index in self.word_to_index.items():
                if unknown_index <= index < old_unknown_index:
                    self.word_to_index[word] = index + 1
        elif old_unknown_index > unknown_index:
            for word, index in self.word_to_index.items():
                if old_unknown_index < index <= unknown_index:
                    self.word_to_index[word] = index - 1
        self.word_to_index[self.unknown_word] = unknown_index

    def get_embedding_matrix(self):
        embedding_dictionary = self.embedding_dictionary
        word_to_index = self.word_to_index
        word_num = self.word_num
        embedding_dim = self.embedding_dim
        embedding_matrix = np.zeros((word_num, embedding_dim))
        for word, i in word_to_index.items():
            embedding_vector = embedding_dictionary.get(word, None)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector
        return embedding_matrix

    def get_sequence(self, tokens):
        unknown_word_index = self.word_to_index.get(self.unknown_word, None)
        if unknown_word_index is None:
            raise Exception('UNKNOWN TOKEN IS NOT DEFINED')
        return pad_sequences(
            [[self.word_to_index.get(token, unknown_word_index) for token in tokens]], maxlen=self.doc_len
        )[0]

    def __get_sequence__(self, tokens):
        unknown_word_index = self.word_to_index.get(self.unknown_word, None)
        if unknown_word_index is None:
            raise Exception('UNKNOWN TOKEN IS NOT DEFINED')
        return [self.word_to_index.get(token, unknown_word_index) for token in tokens]

    def get_docs_sequences(self, docs_tokens):
        return pad_sequences([self.get_sequence(tokens) for tokens in docs_tokens], maxlen=self.doc_len)

    @staticmethod
    def get_from_files(embedding_dictionary_file, word_to_index_file, doc_len, self=None):
        embedding_dictionary, embedding_dim = read_embedding_dictionary(embedding_dictionary_file)
        word_to_index = read_word_to_index(word_to_index_file)
        if self is None:
            return BaseEmbedding(embedding_dictionary, embedding_dim, word_to_index, doc_len)
        else:
            BaseEmbedding.__init__(self, embedding_dictionary, embedding_dim, word_to_index, doc_len)

    @staticmethod
    def get_from_data(embedding_dictionary, embedding_dim, word_to_index, doc_len, self=None):
        if self is None:
            return BaseEmbedding(embedding_dictionary, embedding_dim, word_to_index, doc_len)
        else:
            BaseEmbedding.__init__(self, embedding_dictionary, embedding_dim, word_to_index, doc_len)
