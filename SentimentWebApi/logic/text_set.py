from typing import List

from keras.backend import clear_session
from keras.engine.saving import load_model
from sqlalchemy import or_
from sqlalchemy.util import symbol

from dataio.csv import read_texts_from_file
from models import db, TextSet, Link, TextSetLink, TextSetFile, Net, LinkText, FileText, Text
from InstagramAPI import InstagramAPI

import logic.file as file_logic
import logic.vocabulary as vocabulary_logic
import insta_api
from network.lstm_categorical import LSTMCategorical
import logic.embedding_model as embedding_model_logic

import numpy as np


def get(text_set_id):
    text_set = db.session.query(TextSet).get(text_set_id)  # type: TextSet
    if text_set is None:
        raise ValueError("No text set found by id {0}".format(text_set_id))
    return text_set

def add_urls_to_text_set(text_set_id, urls: List[str]):
    text_set = get(text_set_id)
    for url in urls:
        link = Link()
        link.url = url
        text_set_link = TextSetLink()
        text_set_link.link = link
        text_set.links.append(text_set_link)
    db.session.commit()


def add_files_to_text_set(text_set_id, file_ids):
    text_set = get(text_set_id)  # type: TextSet
    for file_id in file_ids:
        file = file_logic.get(file_id)
        if any(text_set_file for text_set_file in text_set.files if text_set_file.file.id == file.id):
            continue
        text_set_file = TextSetFile()
        text_set_file.file = file
        text_set.files.append(text_set_file)
    db.session.commit()


def extend(text_set_id, app):
    with app.app_context():
        text_set = get(text_set_id)
        net = text_set.net  # type: Net
        vocabulary = net.embedding_model.vocabulary
        clear_session()
        classifier_model = load_model(net.net_file_path)
        doc_len = classifier_model.get_layer(index=0).input_length
        for text_set_link in text_set.links:  # type: TextSetLink
            comments = insta_api.get_all_comments(text_set_link.link.url)
            comments = [comment['text'] for comment in comments]
            comment_tokens = vocabulary_logic.get_tokens_by_vocabulary(vocabulary, comments)
            comment_sequences = np.array(embedding_model_logic.get_sequences(net.embedding_model_id, comment_tokens, doc_len))
            predictions = classifier_model.predict(comment_sequences)
            for comment, comment_sequence, prediction in zip(comments, comment_sequences, predictions):
                link_text = LinkText()
                link_text.id_from_link = 1
                link_text.negative_probability = prediction[0].item()
                link_text.positive_probability = prediction[1].item()
                link_text.text = comment
                text_set_link.texts.append(link_text)
        for text_set_file in text_set.files:  # type: TextSetFile
            # text do not need to be quoted if file is text file (text per line), without separators
            comments = read_texts_from_file(
                file=text_set_file.file.path,
                quoted_fields=text_set_file.file.separator,
                separator=text_set_file.file.separator,
                text_col=text_set_file.file.text_column
            )
            comment_tokens = vocabulary_logic.get_tokens_by_vocabulary(vocabulary, comments)
            comment_sequences = np.array(embedding_model_logic.get_sequences(net.embedding_model_id, comment_tokens, doc_len))
            predictions = classifier_model.predict(comment_sequences)
            for comment, comment_sequence, prediction in zip(comments, comment_sequences, predictions):
                file_text = FileText()
                file_text.negative_probability = prediction[0].item()
                file_text.positive_probability = prediction[1].item()
                file_text.text = comment
                text_set_file.texts.append(file_text)
        db.session.commit()


def wwwinit_add_urls_to_text_set(text_set_id, urls):
    text_set = get(text_set_id)
    for url in urls:
        link = Link()
        link.url = url
        text_set_link = TextSetLink()
        text_set_link.link = link
        text_set.links.append(text_set_link)
    db.session.commit()


def delete(text_set_id):

    texts = db.session.query(Text).with_polymorphic([FileText, LinkText])\
        .outerjoin(TextSetFile, FileText.text_set_file).outerjoin(TextSetLink, LinkText.text_set_link)\
        .filter(or_(TextSetFile.text_set_id == text_set_id, TextSetLink.text_set_id == text_set_id))
    for text in texts:
        db.session.delete(text)

    text_set = get(text_set_id)
    for file in text_set.files:  # type: TextSetFile
        db.session.delete(file)
    for link in text_set.links:  # type: TextSetLink
        db.session.delete(link)
    db.session.delete(text_set)
    db.session.commit()
