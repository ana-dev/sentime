import numpy as np


class BaseEmbedding:
    pad_word = "<<PAD>>"
    unknown_word = "<<UNKNOWN>>"

    def __init__(self, embedding_dictionary, embedding_dim, word_to_index):
        self.name = 'base'
        self.embedding_dim = embedding_dim
        self.embedding_dictionary = embedding_dictionary
        self.word_to_index = word_to_index
        self.complete_dictionary_with_pad()
        self.complete_dictionary_with_unknown()
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
        word_num = len(word_to_index)
        embedding_dim = self.embedding_dim
        embedding_matrix = np.zeros((word_num, embedding_dim))
        for word, i in word_to_index.items():
            embedding_vector = embedding_dictionary.get(word, None)
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector
        return embedding_matrix

    @staticmethod
    def get_from_data(embedding_dictionary, embedding_dim, word_to_index, self=None):
        if self is None:
            return BaseEmbedding(embedding_dictionary, embedding_dim, word_to_index)
        else:
            BaseEmbedding.__init__(self, embedding_dictionary, embedding_dim, word_to_index)
