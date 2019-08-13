from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences


class OneHot:
    def __init__(self, docs_tokens, max_doc_len):
        self.tokenizer = Tokenizer(split=None, lower=False, filters=None, oov_token=True)
        self.tokenizer.fit_on_texts(docs_tokens)
        unknown_index = self.tokenizer.word_index.get('<<UNKNOWN>>', None)
        if unknown_index is not None:
            self.tokenizer.word_index.pop('<<UNKNOWN>>', None)
        self.tokenizer.word_index.pop(True, None)
        self.tokenizer.word_index.update({'<<UNKNOWN>>': 1})
        if unknown_index is not None:
            for word, id in self.tokenizer.word_index.items():
                if id > unknown_index:
                    self.tokenizer.word_index[word] = id - 1
        self.tokenizer.oov_token = '<<UNKNOWN>>'
        self.max_doc_len = max_doc_len
        self.max_word_num = self.tokenizer.num_words

    def get_sequence(self, tokens):
        return pad_sequences(self.tokenizer.texts_to_sequences([tokens]), maxlen=self.max_doc_len)[0]

    def get_docs_sequences(self, docs_tokens):
        return pad_sequences(self.tokenizer.texts_to_sequences(docs_tokens), maxlen=self.max_doc_len)

    def get_tokens(self, sequence):
        return self.tokenizer.sequences_to_texts([sequence])[0]

    def get_docs_tokens(self, docs_sequences):
        return self.tokenizer.sequences_to_texts(docs_sequences)

    def get_word_indexes(self):
        return self.tokenizer.word_index
