from enum import Enum


class Language(Enum):
    russian = 1
    english = 2


class Normalization(Enum):
    stemming = 1
    lemmatisation = 2


class NetStatus(Enum):
    created = 1
    training = 2
    trained = 3
    error = 4


class EmbeddingModelStatus(Enum):
    created = 1
    training = 2
    trained = 3
    error = 4


class VocabularyStatus(Enum):
    created = 1
    extending = 2
    ready = 3
    error = 4
