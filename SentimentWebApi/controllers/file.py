from flask import Blueprint, jsonify, send_file

import logic.file as file_logic

file_bp = Blueprint('file', __name__)


@file_bp.route('/<file_id>', methods=["GET"])
def get(file_id):
    file_id = int(file_id)
    file = file_logic.get(file_id)
    return jsonify(file.to_dict())


@file_bp.route('/download/<file_id>', methods=["GET"])
def download(file_id):
    file_id = int(file_id)
    file = file_logic.get(file_id)
    return send_file(file.path, file.mimetype, True, file.name)
