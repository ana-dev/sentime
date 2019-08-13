from gensim.models import Word2Vec
from time import time
from embedding_methods_plugins.base_embedding import BaseEmbedding


class EmbeddingModel(BaseEmbedding):
    def __init__(self, docs_tokens, emb_dim, iters, window):
        self.time = 0.

        self.time = time()

        word_model = Word2Vec(docs_tokens, size=emb_dim, window=window, iter=iters, sg=0, cbow_mean=1)

        self.time = time() - self.time

        word_to_index = {word: i for i, word in enumerate(word_model.wv.index2word)}
        embedding_dictionary = {word: word_model.wv.get_vector(word) for word, i in word_to_index.items()}
        super(EmbeddingModel, self).get_from_data(embedding_dictionary, emb_dim, word_to_index, self)

        self.name = 'w2v_cbow'


