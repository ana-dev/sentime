import re
from threading import Thread

import flask
from flask import Blueprint, request, jsonify

from sqlalchemy import or_

import logic.file as file_logic
import logic.text_set as text_set_logic

from models import db, File, TextSet, Text, LinkText, FileText, TextSetFile, TextSetLink

text_set_bp = Blueprint('text-set', __name__)


@text_set_bp.route("/", methods=["GET"])
def get_all():
    from_index = request.args.get('from', 0, type=int)
    to_index = request.args.get('to', 9, type=int)
    if from_index > to_index:
        tmp_index = from_index
        from_index = to_index
        to_index = tmp_index
    if to_index - from_index > 50:
        raise ValueError('Can not return more than 50 net records')

    direction = request.args.get('sort_direction', 'asc')
    if direction != 'asc' and direction != 'desc':
        raise ValueError('Direction {} is not allowed'.format(direction))

    sort_field_name = request.args.get('sort_field', 'id')
    if sort_field_name not in ('name', 'id'):
        raise ValueError('Sort field {} is not allowed'.format(sort_field_name))

    name = request.args.get('name', default=None)

    text_sets = db.session.query(TextSet)
    if name is not None and name:
        text_sets = text_sets.filter(TextSet.name.contains(name))

    text_sets = {
        ('name', 'desc'): text_sets.order_by(TextSet.name.desc()),
        ('name', 'asc'): text_sets.order_by(TextSet.name.asc()),
        ('id', 'desc'): text_sets.order_by(TextSet.id.desc()),
        ('id', 'asc'): text_sets.order_by(TextSet.id.asc()),
    }[(sort_field_name, direction)]
    all_count = text_sets.count()
    text_sets = text_sets.limit(to_index-from_index).offset(from_index)
    return jsonify({'count': all_count,
                    'text_sets': [text_set.to_dict(_hide=["files", "links"]) for text_set in text_sets]})


@text_set_bp.route('/<text_set_id>', methods=["GET"])
def get(text_set_id):
    text_set_id = int(text_set_id)
    text_set = text_set_logic.get(text_set_id)
    text_set_info = text_set.to_dict(_hide=["files", "links"])
    return jsonify(text_set_info)


@text_set_bp.route('/texts/<text_set_id>', methods=["GET"])
def get_texts(text_set_id):
    text_set_id = int(text_set_id)

    from_index = request.args.get("from", 0, type=int)
    count = request.args.get("count", 50, type=int)

    direction = request.args.get('sort_direction', 'asc')
    direction = direction if direction else 'asc'
    if direction != 'asc' and direction != 'desc':
        raise ValueError('Direction {} is not allowed'.format(direction))

    sort_field_name = request.args.get('sort_field', 'source')
    sort_field_name = sort_field_name if sort_field_name else 'source'
    if sort_field_name not in ('text', 'tag', 'source'):
        raise ValueError('Sort field {} is not allowed'.format(sort_field_name))

    tag_key = request.args.get('tag', default=-1, type=int)
    if tag_key not in (-1, 0, 1, 2):
        raise ValueError('Tag {} is not allowed'.format(tag_key))
    source_key = request.args.get('source', default='')

    texts = db.session.query(Text).with_polymorphic([FileText, LinkText])\
        .outerjoin(TextSetFile, FileText.text_set_file).outerjoin(TextSetLink, LinkText.text_set_link)\
        .filter(or_(TextSetFile.text_set_id == text_set_id, TextSetLink.text_set_id == text_set_id))

    all_count = texts.count()
    positive_count = texts.filter(Text.negative_probability < Text.positive_probability).count()
    negative_count = texts.filter(Text.negative_probability > Text.positive_probability).count()

    if tag_key == 0:
        texts = texts.filter(Text.negative_probability > Text.positive_probability)
    if tag_key == 1:
        texts = texts.filter(Text.negative_probability < Text.positive_probability)
    if tag_key == 2:
        texts = texts.filter(Text.negative_probability == Text.positive_probability)
    if source_key:
        texts = texts.filter(or_(
            TextSetFile.file.name.contains(source_key),
            TextSetLink.link.url.contains(source_key)
        ))

    if sort_field_name == 'text' and direction == 'asc':
        texts = texts.order_by(Text.text.asc())
    if sort_field_name == 'text' and direction == 'desc':
        texts = texts.order_by(Text.text.desc())

    filtered_count = texts.count()
    texts = texts.limit(count).offset(from_index)
    texts_data = []
    for text in texts:
        text_data = {
            'id': text.id,
            'text': text.text,
            'positive_probability': text.positive_probability,
            'negative_probability': text.negative_probability
        }
        if isinstance(text, FileText):
            text_data['file'] = text.text_set_file.file.to_dict(_hide=[])
        if isinstance(text, LinkText):
            text_data['link'] = text.text_set_link.link.to_dict(_hide=[])
        texts_data.append(text_data)
    response = {
        'all_count': all_count,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'filtered_count': filtered_count,
        'filtered_texts': texts_data
    }
    return jsonify(response)


@text_set_bp.route("/create", methods=["PUT"])
def create():
    text_set = TextSet()
    text_set.from_dict(**request.json)
    db.session.add(text_set)
    db.session.commit()
    return jsonify(text_set.to_dict(_hide=[]))


@text_set_bp.route('/<text_set_id>', methods=["DELETE"])
def delete(text_set_id):
    text_set_id = int(text_set_id)
    try:
        net = text_set_logic.delete(text_set_id)
    except:
        return jsonify({'success': False})
    return jsonify({'success': True})


@text_set_bp.route("/add-urls/<text_set_id>", methods=["POST"])
def add_urls(text_set_id):
    text_set_id = int(text_set_id)
    text_set = text_set_logic.get(text_set_id)
    urls = request.json.get("urls", None)
    if urls is None:
        raise ValueError("No URLs provided")
    text_set_logic.add_urls_to_text_set(text_set_id, urls)
    return jsonify(text_set.to_dict(_hide=[]))


@text_set_bp.route("/add-files/<text_set_id>", methods=["POST"])
def add_files(text_set_id):
    text_set_id = int(text_set_id)
    text_set = text_set_logic.get(text_set_id)

    uploaded_files = []
    for filename, file_stream in request.files.items():
        fileindex = re.search("file\\[(?P<index>\d+)\\]", filename).group('index')
        text_column = request.form.get("text_column[{}]".format(fileindex), '')
        text_column = int(text_column) if text_column else 1
        separator = request.form.get("separator[{}]".format(fileindex), '')
        separator = separator if separator else ','
        file = File()
        file.separator = separator
        file.text_column = text_column
        uploaded_files.append(file_logic.save(file, file_stream))
    text_set_logic.add_files_to_text_set(text_set_id, [file.id for file in uploaded_files])
    return jsonify(text_set.to_dict(_hide=[]))


@text_set_bp.route("/analyze/<text_set_id>", methods=["POST"])
def extend(text_set_id):
    text_set_id = int(text_set_id)
    text_set = text_set_logic.get(text_set_id)
    Thread(target=text_set_logic.extend, args=(text_set_id, flask.current_app._get_current_object(),)).start()
    return jsonify(text_set.to_dict(_hide=[]))
