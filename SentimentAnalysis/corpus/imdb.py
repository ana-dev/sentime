import keras.datasets.imdb as imdb

INDEX_FROM = 3


def get_imdb_corpus():
    (x_train, y_train), (y_test, y_test) = imdb.load_data()  # num_words = vocabulary_size

    word2id = {word: (i + INDEX_FROM) for word, i in imdb.get_word_index().items()}
    id2word = {i: word for word, i in word2id.items()}

    train_samples = [[id2word.get(i, '<<UNKNOWN>>') for i in sample if i >= 2] for sample in x_train]
    train_tags = y_train

    test_samples = [[id2word.get(i, '<<UNKNOWN>>') for i in sample if i >= 2] for sample in x_train]
    test_tags = y_test

    return (train_samples, train_tags), (test_samples, test_samples)
