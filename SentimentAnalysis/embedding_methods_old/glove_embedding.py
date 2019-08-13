import numpy as np
import glove
from embedding_methods_old.one_hot import OneHot
from embedding_methods_old.base_embedding import BaseEmbedding
from time import time
from dataio.csv import read_embedding_dictionary, read_word_to_index
from helpers.helpers import get_embedding_matrix_by_dictionary


class GloveEmbedding(BaseEmbedding):
    def __init__(self, embedding_dictionary_file, word_to_index_file, docs_tokens, doc_len, word_len, iters):
        self.time = 0.

        if embedding_dictionary_file is not None and word_to_index_file is not None:
            super(GloveEmbedding, self).get_from_files(embedding_dictionary_file, word_to_index_file, doc_len, self)
        else:
            embedding_dictionary, embedding_dim, word_to_index, self.time = \
                self.generate_embedding_dictionary(docs_tokens, word_len, iters)
            # one_hot = OneHot(docs_tokens, max_doc_len=self.doc_len)
            # word_to_index = one_hot.get_word_indexes()
            super(GloveEmbedding,self).get_from_data(embedding_dictionary, embedding_dim, word_to_index, doc_len, self)

        self.name = 'glove'
        self.iters = iters

    # def read_embedding_dictionary(self):
    #     return read_embedding_dictionary(self.embedding_dictionary_file)
    #
    # def read_word_to_index(self):
    #     return read_word_to_index(self.word_to_index_file)

    @staticmethod
    def generate_embedding_dictionary(docs_tokens, embedding_dim, iters, window=2, learning_rate=0.05):
        time_start = time()
        corpus_model = glove.Corpus()
        corpus_model.fit(docs_tokens, window=window)
        glove_model = glove.Glove(no_components=embedding_dim, learning_rate=learning_rate)
        glove_model.fit(corpus_model.matrix, epochs=iters, no_threads=4)
        end_time = time()
        glove_model.add_dictionary(corpus_model.dictionary)

        word_to_index = glove_model.dictionary
        index_word = glove_model.inverse_dictionary
        embedding_dictionary = {index_word[i]: vector for i, vector in enumerate(glove_model.word_vectors)}

        # embedding_dictionary["<<UNKNOWN>>"] = np.zeros(embedding_dim)

        return embedding_dictionary, embedding_dim, word_to_index, end_time - time_start

    # def get_sequence(self, tokens, unknown_word_index=None):
    #     unknown_word_index = self.word_to_index.get("<<UNKNOWN>>", None)
    #     if unknown_word_index is None:
    #         raise Exception('UNKNOWN TOKEN IS NOT DEFINED')
    #     return self.one_hot.get_sequence(tokens)
    #
    # def get_docs_sequences(self, docs_tokens):
    #     return self.one_hot.get_docs_sequences(docs_tokens)
    #
    # def get_tokens(self, sequence):
    #     return self.one_hot.get_tokens(sequence)
    #
    # def get_docs_tokens(self, docs_sequences):
    #     return self.one_hot.get_docs_tokens(docs_sequences)

    # def get_cooccur(self, window = 1):
    #     # # https://stackoverflow.com/questions/35562789/word-word-co-occurrence-matrix
    #     # #https://stackoverflow.com/questions/35867484/pass-tokens-to-countvectorizer
    #     # count_model = CountVectorizer(
    #     #     preprocessor=None,
    #     #     tokenizer=lambda x: x,
    #     #     lowercase=False,
    #     #     max_features=self.max_word_num,
    #     #     vocabulary = self.one_hot.get_word_indexes()
    #     # )
    #     # X = count_model.fit_transform(self.docs_tokens)
    #     # # X[X > 0] = 1 # run this line if you don't want extra within-text cooccurence (see below)
    #     # Xc = (X.T * X)  # this is co-occurrence matrix in sparse csr format
    #     # g = sp.diags(1. / Xc.diagonal())
    #     # Xc_norm = g * Xc  # normalized co-occurence matrix
    #     #
    #     sequences = self.one_hot.get_docs_sequences(self.docs_tokens)
    #     cooccur = {}
    #     for sequence in sequences:
    #         for i, word in enumerate(sequence):
    #             if i not in cooccur:
    #                 cooccur[i] = {}
    #             for j in range(max(0, i-window), min(i+window, len(sequence))):
    #                 if i == j:
    #                     continue
    #                 if j not in cooccur[i]:
    #                     cooccur[i][j] = 1
    #                 else:
    #                     cooccur[i][j] += 1
    #     return cooccur




