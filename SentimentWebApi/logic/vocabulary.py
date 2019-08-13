from threading import Thread

import flask
from sqlalchemy.orm import sessionmaker, scoped_session

from dataio.csv import read_texts_from_file
from models import Vocabulary, Word, Normalization, Language, db, File, VocabularyStatus
from tokenizing import remove_stopwords_from_text, remove_stop_words, tokenize, stem_en, stem_ru
import logic.file as file_logic


def get_token_count_dict(tokens):
    token_count_dic = {}
    for token in tokens:
        db_token = token.replace
        token_count_dic[token] = token_count_dic.get(token, 0) + 1
    return token_count_dic


def get_next_token_id(vocabulary):
    if vocabulary.words:
        return max(vocabulary.words, key=lambda x: x.token_id).token_id + 1
    else:
        return 1


def add_tokens_to_vocabulary(vocab: Vocabulary, tokens=None):
    if not tokens:
        return vocab
    token_count = get_token_count_dict(tokens)
    next_token_id = get_next_token_id(vocab)
    words = db.session.query(Word).filter_by(vocabulary_id=vocab.id)
    # increase count for already existing
    for word in words:
        if word.token in token_count:
            word.count += token_count[word.token]
            token_count[word.token] = 0
    # add new for not existing
    for token, count in token_count.items():
        if count == 0:
            continue
        try:
            word = Word(next_token_id, token, count)
        except ValueError:
            continue
        word.vocabulary = vocab
        next_token_id += 1
    return vocab


def get_tokens_by_vocabulary(vocab: Vocabulary, texts):
    if not texts:
        return None
    texts_tokens = []
    vocab_word_id = {word.token: word.id for word in vocab.words}
    for text in texts:
        text = remove_stopwords_from_text(text)
        vocab.lower_cased = True
        text_tokens = tokenize(text)
        if vocab.punctuation_removed:
            text_tokens = remove_stop_words(text_tokens)
        if vocab.normalization_method == Normalization.stemming:
            if vocab.language == Language.russian:
                text_tokens = stem_ru(text_tokens)
            if vocab.language == Language.english:
                text_tokens = stem_en(text_tokens)
        texts_tokens.append([token if token in vocab_word_id else "<<UNKNOWN>>" for token in text_tokens])
    return texts_tokens


def add_texts_to_vocabulary(vocab: Vocabulary, texts):
    if not texts:
        return None
    tokens = []
    for text in texts:
        text = remove_stopwords_from_text(text)
        vocab.lower_cased = True
        text_tokens = tokenize(text)
        if vocab.punctuation_removed:
            text_tokens = remove_stop_words(text_tokens)
        if vocab.normalization_method == Normalization.stemming:
            if vocab.language == Language.russian:
                text_tokens = stem_ru(text_tokens)
            if vocab.language == Language.english:
                text_tokens = stem_en(text_tokens)
        tokens.extend(text_tokens)
    tokens = list(set(tokens))
    return add_tokens_to_vocabulary(vocab, tokens)


def extend(vocabulary_id, app):
    with app.app_context():
        change_status(vocabulary_id, VocabularyStatus.extending)
        vocabulary = get(vocabulary_id)
        for file in vocabulary.files:
            # text do not need to be quoted if file is text file (text per line), without separators
            texts = read_texts_from_file(
                file=file.file.path,
                quoted_fields=file.file.separator,
                separator=file.file.separator,
                text_col=file.file.text_column
            )
            add_texts_to_vocabulary(vocabulary, texts)
        change_status(vocabulary_id, VocabularyStatus.ready)


def init_extending(vocabulary_id, file_ids):
    vocabulary = get(vocabulary_id)
    for file_id in file_ids:
        if any(voc_file for voc_file in vocabulary.files if voc_file.id == file_id):
            continue
        file = file_logic.get(file_id)
        vocabulary.files.append(file)
    db.session.commit()
    Thread(target=extend, args=(vocabulary_id, flask.current_app._get_current_object(),)).start()
    return vocabulary


def get(vocabulary_id):
    vocabulary = db.session.query(Vocabulary).get(vocabulary_id)
    if vocabulary is None:
        raise ValueError("No vocabulary found by id {}".format(vocabulary_id))
    return vocabulary


def change_status(vocabulary_id, status: VocabularyStatus):
    vocabulary = get(vocabulary_id)
    vocabulary.status = status
    db.session.commit()
    return vocabulary

