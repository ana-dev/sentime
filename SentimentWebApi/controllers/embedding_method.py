from flask import Blueprint, request, jsonify
from models import EmbeddingMethod, db

embedding_method_bp = Blueprint('embedding-method', __name__)


@embedding_method_bp.route("/", methods=["GET", "POST"])
def get_all():
    methods = db.session.query(EmbeddingMethod).all()
    return jsonify([method.to_dict(_hide=[]) for method in methods])




