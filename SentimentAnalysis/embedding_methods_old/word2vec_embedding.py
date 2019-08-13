from gensim.models import Word2Vec
from embedding_methods_old.one_hot import OneHot
from embedding_methods_old.base_embedding import BaseEmbedding
import numpy as np
from time import time


class Word2VecEmbedding(BaseEmbedding):
    def __init__(self, embedding_dictionary_file, word_to_index_file, docs_tokens, doc_len, word_len, iters, cbow):
        self.time = 0.
        if embedding_dictionary_file is not None and word_to_index_file is not None:
            super(Word2VecEmbedding, self).get_from_files(embedding_dictionary_file, word_to_index_file, doc_len, self)
        else:
            self.time = time()
            word_model = Word2Vec(docs_tokens, size=word_len, window=2, iter=iters,
                                  sg=(0 if cbow else 1), cbow_mean=(1 if cbow else 0))
            self.time = time() - self.time
            word_to_index = {word: i for i, word in enumerate(word_model.wv.index2word)}
            embedding_dictionary = {word: word_model.wv.get_vector(word) for word, i in word_to_index.items()}
            embedding_dim = word_len
            super(Word2VecEmbedding, self).get_from_data(embedding_dictionary, embedding_dim, word_to_index, doc_len, self)
        self.name = 'w2v_cbow' if cbow else 'w2v_skipgram'
        self.iters = iters
