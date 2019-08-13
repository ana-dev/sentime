from flask import Blueprint, request, jsonify
from models import Vocabulary, db, File

import logic.file as file_logic
import logic.vocabulary as vocabulary_logic

vocabulary_bp = Blueprint('vocabulary', __name__)


@vocabulary_bp.route("/<vocabulary_id>", methods=["GET"])
def get_by_id(vocabulary_id):
    vocabulary_id = int(vocabulary_id)
    vocabulary = vocabulary_logic.get(vocabulary_id)
    return jsonify(vocabulary.to_dict(_hide=[]))


@vocabulary_bp.route("/", methods=["GET"])
def get_all():
    try:
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

        sort_field_name = request.args.get('sort_field', 'updated_time')
        if sort_field_name not in ('name', 'updated_time'):
            raise ValueError('Sort field {} is not allowed'.format(sort_field_name))

        name = request.args.get('name', default=None)

        text_sets = db.session.query(Vocabulary)
        if name is not None and name:
            text_sets = text_sets.filter(Vocabulary.name.contains(name))

        text_sets = {
            ('name', 'desc'): text_sets.order_by(Vocabulary.name.desc()),
            ('name', 'asc'): text_sets.order_by(Vocabulary.name.asc()),
            ('updated_time', 'desc'): text_sets.order_by(Vocabulary.updated_time.desc()),
            ('updated_time', 'asc'): text_sets.order_by(Vocabulary.updated_time.asc()),
        }[(sort_field_name, direction)]
        all_count = text_sets.count()
        text_sets = text_sets.limit(to_index-from_index).offset(from_index)
        return jsonify({'count': all_count, 'vocabularies': [text_set.to_dict(_hide=["words"]) for text_set in text_sets]})
    except Exception as ex:
        return jsonify({'success': False, 'errors': [str(ex)]})


@vocabulary_bp.route("/", methods=["PUT"])
def create():
    vocabulary = Vocabulary()
    vocabulary.from_dict(**request.json)
    db.session.add(vocabulary)
    db.session.flush()
    db.session.commit()
    return jsonify(vocabulary.to_dict())


@vocabulary_bp.route("/extend", methods=["POST"])
def extend():
    vocabulary_id = request.form["vocabulary_id"]

    separator = request.form["file"]["separator"]
    text_column = request.form["file"]["text_column"]
    tag_column = request.form["file"]["tag_column"]
    positive_tag = request.form["file"]["positive_tag"]
    negative_tag = request.form["file"]["negative_tag"]
    uploaded_files = []
    for filename, file_stream in request.files.items():
        file = File()
        file.separator = separator
        file.text_column = text_column
        file.tag_column = tag_column
        file.positive_tag = positive_tag
        file.negative_tag = negative_tag
        uploaded_files.append(file_logic.save(file, file_stream))

    vocabulary = vocabulary_logic.init_extending(vocabulary_id, [file.id for file in uploaded_files])
    return jsonify(vocabulary.to_dict())
