from flask import Blueprint, request, jsonify

import logic.file as file_logic
import logic.embedding_model as emb_model_logic

from models import EmbeddingModel, db, File, ModelWordVector

embedding_model_bp = Blueprint('embedding-model', __name__)


@embedding_model_bp.route("/", methods=["GET"])
def get_all():
    methods = db.session.query(EmbeddingModel).all()
    data = [method.to_dict(_hide=[]) for method in methods]
    response = jsonify(data)
    return response


@embedding_model_bp.route('/<model_id>', methods=["GET"])
def get(model_id):
    model_id = int(model_id)
    model = emb_model_logic.get(model_id)
    return jsonify(model.to_dict(_hide=[]))


@embedding_model_bp.route("/", methods=["PUT"])
def create():
    model = EmbeddingModel()
    json = request.json
    for param in json['embedding_params']:
        param['value'] = float(param['value'])
    model.from_dict(**request.json)
    db.session.add(model)
    db.session.commit()
    return jsonify(model.to_dict())


@embedding_model_bp.route("/train", methods=["POST"])
def train():
    model_id = int(request.form["model_id"])
    model = db.session.query(EmbeddingModel).get(model_id)  # type: EmbeddingModel
    if model is None:
        raise ValueError("No embedding model found by id {0}".format(model_id))

    separator = request.form["separator"]
    text_column = int(request.form["text_column"])
    tag_column = int(request.form["tag_column"])
    positive_tag = request.form["positive_tag"]
    negative_tag = request.form["negative_tag"]
    uploaded_files = []
    for filename, file_stream in request.files.items():
        file = File()
        file.separator = separator
        file.text_column = text_column
        file.tag_column = tag_column
        file.positive_tag = positive_tag
        file.negative_tag = negative_tag
        uploaded_files.append(file_logic.save(file, file_stream))

    extend_vocabulary = True if request.form["extend_vocabulary"] == "true" else False

    model = emb_model_logic.init_training(model_id, [file.id for file in uploaded_files], extend_vocabulary)

    return jsonify(model.to_dict())


@embedding_model_bp.route("/t-sne", methods=["GET"])
def vector2d_all():
    for model in db.session.query(EmbeddingModel):
        emb_model_logic.tsne(model.id)


@embedding_model_bp.route("/vectors/<model_id>", methods=["GET"])
def get_vectors(model_id):
    model_id = int(model_id)
    word_vectors = db.session.query(ModelWordVector).filter(ModelWordVector.embedding_model_id == model_id)
    response = []
    for word_vector in word_vectors:
        response.append((word_vector.word.token, word_vector.x, word_vector.y))
    return jsonify(response)
