from typing import List, Tuple, Dict

from time import sleep

import numpy as np
from threading import Thread

import flask
from keras_preprocessing.sequence import pad_sequences

from dataio.csv import read_samples
from helpers.helpers import shuffle_and_get_parts
from models import EmbeddingModel, EmbeddingModelStatus, db, File, EmbeddingMethod, EmbeddingMethodParamValue, \
    ModelWordVector, VocabularyStatus

import logic.vocabulary as vocabulary_logic
import logic.file as file_logic


def get(model_id):
    model = db.session.query(EmbeddingModel).get(model_id)  # type: EmbeddingModel
    if model is None:
        raise ValueError("No embedding model found by id {0}".format(model_id))
    return model


def change_status(model_id, new_status: EmbeddingModelStatus):
    model = get(model_id)
    model.status = new_status
    db.session.commit()
    return model


def add_word_vectors(model_id, word_dictionary: Dict[str, Tuple[int, List[float]]]):
    model = get(model_id)
    vocabulary_token_word_dict = {word.token: word for word in model.vocabulary.words}
    for token, (index, vector) in word_dictionary.items():
        word = vocabulary_token_word_dict.get(token, None)
        if word is None:
            continue
        model_word_vector = ModelWordVector()
        model_word_vector.word = word
        model_word_vector.index = index
        model_word_vector.vector = '\t'.join([str(val) for val in vector])
        model.model_word_vectors.append(model_word_vector)
    db.session.commit()


def tsne(model_id):
    from sklearn.manifold import TSNE
    model = get(model_id)
    tsne = TSNE(n_components=2)
    embedding_matrix = get_embedding_matrix(model_id)
    tsne_matrix = tsne.fit_transform(embedding_matrix)
    for word_vector in model.model_word_vectors:  # type: ModelWordVector
        word_vector.x = tsne_matrix[word_vector.index][0].item()
        word_vector.y = tsne_matrix[word_vector.index][1].item()
    db.session.commit()


def train(model_id, app):
    with app.app_context():
        model = get(model_id)
        if model.vocabulary.status == VocabularyStatus.created:
            vocabulary_logic.extend(model.vocabulary_id, app)
        elif model.vocabulary.status == VocabularyStatus.extending:
            while True:
                db.session.refresh(model)
                if model.vocabulary.status == VocabularyStatus.ready:
                    break
                sleep(30)
        # if model.vocabulary.status != VocabularyStatus.ready:
        #     raise ValueError('Vocabulary has {} status (not ready)'.format(model.vocabulary.status))
        model = change_status(model_id, EmbeddingModelStatus.training)
        samples = []
        tags = []
        for file in model.files:
            n, p = read_samples(file.path, file.separator, file.tag_column - 1, file.negative_tag, file.positive_tag,
                                file.text_column - 1)
            samples.extend([sample for sample, tag in n])
            tags.extend([0 for sample, tag in n])
            samples.extend([sample for sample, tag in p])
            tags.extend([1 for sample, tag in p])

        vocabulary = model.vocabulary
        samples = vocabulary_logic.get_tokens_by_vocabulary(vocabulary, samples)

        random_emd_samples_part = shuffle_and_get_parts(samples, tags)[0]
        emb_samples_tokens = random_emd_samples_part[0]

        method = model.embedding_method  # type: EmbeddingMethod
        import importlib.util
        method_module_spec = importlib.util.spec_from_file_location(method.name, method.plugin_path)
        method_module = importlib.util.module_from_spec(method_module_spec)
        method_module_spec.loader.exec_module(method_module)

        max_doc_len = max([len(tokens) for tokens in emb_samples_tokens])
        from pydoc import locate
        additional_params = {}
        for param_value in model.embedding_params:
            name = param_value.embedding_method_param.name
            param_type = locate(param_value.embedding_method_param.type)
            value = param_type(param_value.value)
            additional_params[name] = value
        embedding_model = method_module.EmbeddingModel(
            emb_samples_tokens,
            emb_dim=model.embedding_dim,
            **additional_params
        )
        word_dictionary = embedding_model.get_word_dictionary()
        add_word_vectors(model_id, word_dictionary)
        tsne(model_id)
        change_status(model_id, EmbeddingModelStatus.trained)


def init_training(model_id, file_ids, extend_vocabulary):
    model = change_status(model_id, EmbeddingModelStatus.created)

    for file_id in file_ids:
        file = file_logic.get(file_id)
        if not any(model_file for model_file in model.files if model_file.id == file_id):
            model.files.append(file)
        if extend_vocabulary and not any(voc_file for voc_file in model.vocabulary.files if voc_file.id == file_id):
            model.vocabulary.files.append(file)
        db.session.commit()

    Thread(target=train, args=(model_id, flask.current_app._get_current_object(),)).start()
    return model


def get_sequences(model_id, text_tokens, seq_len):
    model = get(model_id)
    token_index = {word_vector.word.token: word_vector.index for word_vector in model.model_word_vectors}
    sequences = []
    for tokens in text_tokens:
        sequence = pad_sequences([[token_index.get(token, 1) for token in tokens]], maxlen=seq_len)[0]
        sequences.append(sequence)
    return sequences


def get_vector_from_str(vec_string):
    return [float(i) for i in vec_string.split('\t')]


def get_embedding_matrix(model_id):
    model = get(model_id)
    word_dic = {word_vector.word.token: (word_vector.index, get_vector_from_str(word_vector.vector))
                for word_vector in model.model_word_vectors}
    word_num = len(word_dic) + 2
    embedding_dim = model.embedding_dim
    embedding_matrix = np.zeros((word_num, embedding_dim))
    for word, (i, vector) in word_dic.items():
        embedding_matrix[i] = vector
    return embedding_matrix


def delete(model_id):
    model = get(model_id)
    for param in model.embedding_params:
        db.session.delete(param)
    for word_vector in model.model_word_vectors:
        db.session.delete(word_vector)
    db.session.delete(model)
