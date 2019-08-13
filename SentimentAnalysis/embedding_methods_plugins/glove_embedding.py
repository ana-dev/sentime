import glove
from time import time
from embedding_methods_plugins.base_embedding import BaseEmbedding


class EmbeddingModel(BaseEmbedding):
    def __init__(self, docs_tokens, emb_dim, iters, window, learn_rate):
        self.time = 0.

        self.time = time()

        corpus_model = glove.Corpus()
        corpus_model.fit(docs_tokens, window=window)
        glove_model = glove.Glove(no_components=emb_dim, learning_rate=learn_rate)
        glove_model.fit(corpus_model.matrix, epochs=iters, no_threads=4)
        glove_model.add_dictionary(corpus_model.dictionary)

        self.time = time() - self.time

        word_to_index = glove_model.dictionary
        index_word = glove_model.inverse_dictionary
        embedding_dictionary = {index_word[i]: vector for i, vector in enumerate(glove_model.word_vectors)}

        super(EmbeddingModel, self).get_from_data(embedding_dictionary, emb_dim, word_to_index, self)

        self.name = 'glove'


