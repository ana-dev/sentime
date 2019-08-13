from threading import Thread
from time import sleep

import flask

from dataio.csv import read_samples
from helpers.helpers import shuffle_and_get_parts
from models import Net, NetStatus, db, File, EmbeddingModelStatus, Epoch, EpochConfusionMatrix, TextSet

import logic.vocabulary as vocabulary_logic
import logic.embedding_model as embedding_model_logic
import logic.file as file_logic
import netword_metrics.confusion_matrix as net_metrics
from network.lstm_categorical import LSTMCategorical


def get(net_id):
    net = db.session.query(Net).get(net_id)  # type: Net
    if net is None:
        raise ValueError("No net found by id {0}".format(net_id))
    return net


def change_status(net_id, new_status: NetStatus):
    net = get(net_id)
    net.status = new_status
    db.session.commit()
    return net


def train(net_id, app):
    with app.app_context():

        train_count = 1700
        test_count = 300
        lstm_out = 100
        batch_size = 32
        net_epochs = 10
        dropout = 20

        net = get(net_id)

        if net.embedding_model.status == EmbeddingModelStatus.created:
            embedding_model_logic.train(net.embedding_model_id, app)
        elif net.embedding_model.status == EmbeddingModelStatus.training:
            while True:
                db.session.refresh(net)
                if net.embedding_model.status == EmbeddingModelStatus.trained:
                    break
                sleep(30)

        net = change_status(net_id, NetStatus.training)
        samples = []
        tags = []
        for file in net.files:
            n, p = read_samples(file.path, file.separator, file.tag_column-1, file.negative_tag, file.positive_tag, file.text_column-1)
            samples.extend([sample for sample, tag in n])
            tags.extend([0 for sample, tag in n])
            samples.extend([sample for sample, tag in p])
            tags.extend([1 for sample, tag in p])

        vocabulary = net.embedding_model.vocabulary
        samples = vocabulary_logic.get_tokens_by_vocabulary(vocabulary, samples)

        [train_set, test_set] = shuffle_and_get_parts(samples, tags, [train_count, test_count])
        train_samples_tokens = train_set[0]
        train_samples_tags = train_set[1]
        test_samples_tokens = test_set[0]
        test_samples_tags = test_set[1]

        max_doc_len = max([len(tokens) for tokens in train_samples_tokens + test_samples_tokens])
        train_sequences = embedding_model_logic.get_sequences(net.embedding_model_id, train_samples_tokens, max_doc_len)
        test_sequences = embedding_model_logic.get_sequences(net.embedding_model_id, test_samples_tokens, max_doc_len)

        embedding_matrix = embedding_model_logic.get_embedding_matrix(net.embedding_model.id)
        doc_len = max([len(tokens) for tokens in train_samples_tokens+test_samples_tokens])
        net_model = LSTMCategorical(lstm_out, doc_len, dropout=dropout, batch_size=batch_size, epoch_num=net_epochs,
                                    embedding_matrix=embedding_matrix)
        net_model.train_by_sequences(train_sequences, train_samples_tags, test_sequences, test_samples_tags)

        epoch_true_tags, epoch_pred_tags = net_model.get_epoch_predictions()
        for epoch_num, true_tags in epoch_true_tags.items():
            pred_tags = epoch_pred_tags[epoch_num]
            epoch = Epoch()
            epoch.order_number = epoch_num
            epoch.training_time = net_model.epoch_logger.epoch_time_dic[epoch_num]
            epoch.train_accurancy = net_model.epoch_logger.epoch_acc_dic[epoch_num].item()
            epoch.train_loss = net_model.epoch_logger.epoch_loss_dic[epoch_num].item()
            epoch.test_accurancy = net_model.epoch_logger.epoch_val_acc_dic[epoch_num].item()
            epoch.test_loss = net_model.epoch_logger.epoch_val_loss_dic[epoch_num].item()
            confusion_matrix = net_metrics.get_confusion_matrix(true_tags=true_tags, predicted_tags=pred_tags)
            for true_tag, pred_tags in confusion_matrix.items():
                for pred_tag, count in pred_tags.items():
                    matrix = EpochConfusionMatrix()
                    matrix.true_tag = true_tag
                    matrix.predicted_tag = pred_tag
                    matrix.count = count
                    epoch.epoch_confusion_matrix.append(matrix)
            net.epochs.append(epoch)

        net_filename = '/home/nastya/ftp_files/{0}.h5'.format(net.name)

        net_model.model.save('/home/nastya/ftp_files/{0}.h5'.format(net.name))
        net.net_file_path = net_filename
        db.session.commit()

        net = change_status(net_id, NetStatus.trained)
        db.session.commit()


def init_training(net_id, file_ids, extend_vocabulary):
    net = change_status(net_id, NetStatus.created)  # type: Net
    for file_id in file_ids:
        file = file_logic.get(file_id)
        if not any(net_file for net_file in net.files if net_file.id == file_id):
            net.files.append(file)
        if not any(model_file for model_file in net.embedding_model.files if model_file.id not in file_ids):
            net.embedding_model.files.append(file)
            if extend_vocabulary and not any(voc_file for voc_file in net.embedding_model.vocabulary.files if voc_file.id == file_id):
                net.embedding_model.vocabulary.files.append(file)
        db.session.commit()

    Thread(target=train, args=(net_id, flask.current_app._get_current_object(),)).start()
    return net


def get_confusion_matrix(epoch_id):
    epoch = db.session.query(Epoch).get(epoch_id)  # type: Epoch
    matrix = {}
    for element in epoch.epoch_confusion_matrix:  # type: EpochConfusionMatrix
        if element.true_tag not in matrix:
            matrix[element.true_tag] = {}
        matrix[element.true_tag][element.predicted_tag] = element.count
    return matrix


def delete(net_id):
    net = get(net_id)
    for text_set in db.session.query(TextSet).filter(TextSet.net_id == net_id):
        text_set.net_id = None
    for epoch in net.epochs:
        for confusion_matrix in epoch.epoch_confusion_matrix:
            db.session.delete(confusion_matrix)
        db.session.delete(epoch)
    db.session.delete(net)
    db.session.commit()
