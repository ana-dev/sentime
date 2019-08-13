from nltk.tokenize import TweetTokenizer
from Stemmer import Stemmer
import re

stop_words = {
    '*', '+', '^', '&', '.', ':', '!', '_', '-', '`', '$', "'", '\\', ';', '~', '@',
    '{', '/', '=', '?', '>', '%', '"', '|', '#', '<', '}', ','
}

stemmer_ru = Stemmer('russian')
stemmer_en = Stemmer('english')

stop_words_regexes = [
    r'https?://.*[\r\n]*'  # links have not semantic
]

tokenizer = TweetTokenizer(preserve_case=False, reduce_len=True, strip_handles=True)


def tokenize(text):
    return tokenizer.tokenize(text)


def remove_stopwords_from_text(text):
    for stop_word_regex in stop_words_regexes:
        text = re.sub(stop_word_regex, '', text)
    return text


def remove_stop_words(tokens):
    return [token for token in tokens if token not in stop_words]


def stem_ru(tokens):
    return stemmer_ru.stemWords(tokens)


def stem_en(tokens):
    return stemmer_en.stemWords(tokens)


