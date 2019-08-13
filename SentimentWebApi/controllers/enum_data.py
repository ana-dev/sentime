from flask import Blueprint, request, jsonify
from models import Language, Normalization

enumdata_bp = Blueprint('enum', __name__)


@enumdata_bp.route("/languages", methods=["GET"])
def get_languages():
    return jsonify([language.name for language in Language])


@enumdata_bp.route("/normalizations", methods=["GET"])
def get_normalizations():
    return jsonify([normalization.name for normalization in Normalization])


