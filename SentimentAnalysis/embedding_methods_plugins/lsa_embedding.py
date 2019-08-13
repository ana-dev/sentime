from gensim.corpora import Dictionary
from gensim.models import LsiModel, TfidfModel
from time import time
from embedding_methods_plugins.base_embedding import BaseEmbedding


class EmbeddingModel(BaseEmbedding):
    def __init__(self, docs_tokens, emb_dim, iters):
        self.time = 0.

        self.time = time()

        word_dictionary = Dictionary(docs_tokens)
        word_to_index = word_dictionary.token2id
        docs_term_matrix = [word_dictionary.doc2bow(tokens) for tokens in docs_tokens]
        tfidfmodel = TfidfModel(docs_term_matrix, id2word=word_dictionary)
        corpus = [tfidfmodel[doc] for doc in docs_term_matrix]
        lsamodel = LsiModel(corpus, num_topics=emb_dim, id2word=word_dictionary, power_iters=iters)
        self.time = time() - self.time

        embedding_matrix = lsamodel.get_topics().transpose()
        embedding_dictionary = {}
        embedding_dim = None
        for word, i in word_to_index.items():
            embedding_dictionary[word] = embedding_matrix[i]
            if embedding_dim is None:
                embedding_dim = len(embedding_matrix[i])

        super(EmbeddingModel, self).get_from_data(embedding_dictionary, embedding_dim, word_to_index, self)

        self.name = 'lsa'
