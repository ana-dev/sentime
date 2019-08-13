from flask.json import jsonify
from sqlalchemy.exc import IntegrityError, DBAPIError

from validation.error_codes import ErrorCode
from validation.errorinfo import ObjectError, ErrorInfo
from .file import file_bp
from .vocabulary import vocabulary_bp
from .enum_data import enumdata_bp
from .embedding_method import embedding_method_bp
from .embedding_model import embedding_model_bp
from .net import net_bp
from .text_set import text_set_bp


def object_error_handler(error: ObjectError):
    response = jsonify(message=error.to_dict())
    response.status_code = 500
    return response


def sql_alchemy_error_handler(error: DBAPIError):
    if error.orig is None:
        response = jsonify(message=ErrorInfo(ErrorCode.UnknownError).to_dict(), orig=str(error))
        response.status_code = 500
        return response
    if error.orig.args[0] == 1062:  # not unique mysql error
        response = jsonify(message=ErrorInfo(ErrorCode.NotUniqueError).to_dict(), orig=error.orig.args[1])
    else:
        response = jsonify(message=ErrorInfo(ErrorCode.UnknownError).to_dict(), orig=error.orig.args[1])
    response.status_code = 500
    return response


def unknown_error_handler(error: Exception):
    response = jsonify(message=ErrorInfo(ErrorCode.UnknownError).to_dict(), orig=str(error))
    response.status_code = 500
    return response


def init_error_handlers(app):
    app.errorhandler(ObjectError)(object_error_handler)
    app.errorhandler(DBAPIError)(sql_alchemy_error_handler)
    app.errorhandler(Exception)(unknown_error_handler)


def init_app(app):
    app.register_blueprint(vocabulary_bp, url_prefix="/vocabulary")
    app.register_blueprint(enumdata_bp, url_prefix="/enum")
    app.register_blueprint(embedding_method_bp, url_prefix="/embedding-method")
    app.register_blueprint(embedding_model_bp, url_prefix="/embedding-model")
    app.register_blueprint(file_bp, url_prefix="/file")
    app.register_blueprint(net_bp, url_prefix="/net")
    app.register_blueprint(text_set_bp, url_prefix="/text-set")
    init_error_handlers(app)

