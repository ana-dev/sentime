from .enums import *
from models.base_model import db, BaseModel, validatable
from models.vocabulary import Vocabulary
from models.word import Word
from .embedding_method import EmbeddingMethod
from .embedding_method_param import EmbeddingMethodParam
from .embedding_method_param_value import EmbeddingMethodParamValue
from .embedding_model import EmbeddingModel
from .model_word_vector import ModelWordVector
from .file import File
from .assotiations import vocabulary_file, embedding_model_file, net_file
from .net_module import NetModule
from .net_module_param import NetModuleParam
from .net import Net
from .net_module_param_value import NetModuleParamValue
from .net_epoch import Epoch
from .epoch_confusion_matrix import EpochConfusionMatrix
from .text import Text, FileText, LinkText
from .text_set import TextSet
from .link import Link
from .text_set_file import TextSetFile
from .text_set_link import TextSetLink


def init_app(app):
    db.init_app(app)


