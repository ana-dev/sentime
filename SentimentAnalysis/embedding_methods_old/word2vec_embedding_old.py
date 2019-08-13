from gensim.models import Word2Vec
from embedding_methods_old.one_hot import OneHot
import numpy as np
from time import time


class Word2VecEmbedding:
    def __init__(self, embedding_dictionary_file, docs_tokens, doc_len, word_count, word_len, iters):
        self.embedding_dictionary_file = embedding_dictionary_file
        self.docs_tokens = docs_tokens
        self.doc_len = doc_len
        self.word_num = word_count
        self.word_len = word_len
        self.iters = iters

        self.embedding_dim = self.word_len
        self.embedding_dictionary = None

        self.time = time()
        word_model = Word2Vec(self.docs_tokens, size=self.embedding_dim, window=2, iter=self.iters, sg=1, cbow_mean=0)
        self.time = time() - self.time

        word_to_index_dic = {word: i for i, word in enumerate(word_model.wv.index2word)}
        self.embedding_dictionary = {word: word_model.wv.get_vector(word) for word, i in word_to_index_dic.items()}
        if '<<UNKNOWN>>' in self.embedding_dictionary:
            self.embedding_dictionary.pop('<<UNKNOWN>>', None)
        self.embedding_dictionary['<<UNKNOWN>>'] = np.zeros(word_len)

        self.one_hot = None
        self.embedding_matrix = None
        self.get_embedding_matrix()

    def get_embedding_matrix(self):
        self.one_hot = OneHot(self.docs_tokens, max_doc_len=self.doc_len)
        self.word_to_index_dic = self.one_hot.get_word_indexes()
        word_index = self.one_hot.get_word_indexes()
        embedding_matrix = np.zeros((len(word_index)+1, self.embedding_dim))
        for word, i in word_index.items():
        # for i in range(1, self.word_num):
        #     word = self.one_hot.tokenizer.index_word[i]
            embedding_vector = self.embedding_dictionary.get(word, None)
            if embedding_vector is not None:
                # words not found in embedding index will be all-zeros.
                embedding_matrix[i] = embedding_vector
        self.embedding_matrix = embedding_matrix


    def get_sequence(self, tokens, unknown_word_index=None):
        return self.one_hot.get_sequence(tokens)

    def get_docs_sequences(self, docs_tokens):
        return self.one_hot.get_docs_sequences(docs_tokens)

    def get_tokens(self, sequence):
        return self.one_hot.get_tokens(sequence)

    def get_docs_tokens(self, docs_sequences):
        return self.one_hot.get_docs_tokens(docs_sequences)
